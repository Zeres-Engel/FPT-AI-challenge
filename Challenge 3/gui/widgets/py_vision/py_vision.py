import cv2
import glob
import os
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPixmap, Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
import pandas as pd
import numpy as np
from datetime import datetime

from FPTvision.utils import face_align

class ModelFunction(QWidget):
    def __init__(self, detection_model, recognition_model):
        super().__init__()

        # Khởi tạo mô hình phát hiện khuôn mặt
        self.detection_model = detection_model
        self.recognition_model = recognition_model

        #* Đọc các khuôn mặt có sẵn
        # Đường dẫn đến thư mục chứa các khuôn mặt đã aligned
        self.aligned_faces_dir = './gui/aligned'

        # Load danh sách các khuôn mặt đã aligned và trích xuất embedding
        self.faces_aligned = []  # List lưu đường dẫn và embedding
        aligned_face_dirs = glob.glob(self.aligned_faces_dir + '/*')
        for face_dir in aligned_face_dirs:
            name_file = os.path.join(face_dir)
            face_files = glob.glob(os.path.join(face_dir, '*.jpg'))
            if len(face_files) > 0:
                face_images = [cv2.imread(file) for file in face_files]
                face_embeddings = self.recognition_model.get_feat(face_images[0:])
                self.faces_aligned.append((name_file, face_embeddings))
        
        #* Mở camera
        # Kiểm tra trạng thái camera
        self.status = False
        self.cap = None
        self.open_webcam()
        
        # Khung hình hiển thị video từ webcam
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        
        # Tạo QVBoxLayout và thêm video_label vào layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        
        # Biến lưu trữ tên khuôn mặt đã nhận dạng
        self.recognized_label = ""

        # Bắt đầu vòng lặp video
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)
        
    def turn_on_off_model(self):
        if self.status is True:
            self.status = False
            self.display_image(".\gui\images\svg_images\CoffeeShop.svg")
            
            # Đọc vào file CSV
            df = pd.read_csv('./Attendance.csv')
            
            df.loc[df['Attendance'] == 'Processing', 'Attendance'] = 'Absent'
            
            #* Ghi lại dữ liệu đã cập nhật vào file CSV
            df.to_csv('./Attendance.csv', index=False)
        else:
            self.status = True

    def update_frame(self):
        self.display_image(".\gui\images\svg_images\CoffeeShop.svg")
        if self.status is True:
            # Mở webcam nếu chưa mở
            self.open_webcam()

            # Kiểm tra xem webcam đã mở thành công chưa
            if self.cap is None:
                return

            # Đọc khung hình từ webcam
            ret, frame = self.cap.read()

            # Lật ngược khung hình
            frame = cv2.flip(frame, 1)

            # Phát hiện khuôn mặt trong khung hình
            faces = self.detection_model.get(frame)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            index_face = 0
            for face in faces:
                bbox = face.bbox.astype(int)
                cv2.rectangle(frame_rgb, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (242, 111, 33), 2)
                # Lấy tọa độ các điểm landmark từ faces[0].kps
                landmarks = face.kps
                # Chọn chỉ số của 5 điểm landmark muốn vẽ
                landmark_indices = [0, 1, 2, 3, 4]
                # Vẽ các điểm landmark
                for index in landmark_indices:
                    x, y = landmarks[index]
                    cv2.circle(frame_rgb, (int(x), int(y)), 2, (0, 255, 0), -1)

                #! Thực hiện nhận diện cho từng khuôn mặt có det_score cao hơn 0.68
                if face.det_score > 0.68:
                    detected_embedding = self.recognition_model.get(frame, face)
                    recognized_face_name = ""
                    max_similarity = 0.0
                    for name, aligned_embedding in self.faces_aligned:
                        
                        aligned_embedding = np.array(aligned_embedding)

                        # Tính similarity
                        similarity = (self.recognition_model.compute_sim(aligned_embedding[0],detected_embedding) * 0.2
                                    + self.recognition_model.compute_sim(aligned_embedding[1],detected_embedding) * 0.2
                                    + self.recognition_model.compute_sim(aligned_embedding[2],detected_embedding) * 0.2
                                    + self.recognition_model.compute_sim(aligned_embedding[3],detected_embedding) * 0.2
                                    + self.recognition_model.compute_sim(aligned_embedding[4],detected_embedding) * 0.2)

                        if similarity > max_similarity:
                            max_similarity = similarity
                            recognized_face_name = name
                    if max_similarity > 0.5:
                        text = recognized_face_name.split("/")[-1].replace('_', ' ').split("\\")[1]
                        
                    
                        # Đọc vào file CSV
                        df = pd.read_csv('./Attendance.csv')
                        index_name = recognized_face_name.split("/")[-1].replace('_', ' ').split("\\")[1]

                        now = datetime.now()
                        #! Đánh dấu present cho gương mặt >= 0.5 và sẽ lấy gương mặt có tương quan cao nhất có thể
                        if max_similarity >= 0.5:
                            #* Kiểm tra và cập nhật cột "Check-in"
                            if df.loc[(df['Staff ID'] == index_name) & df['Check-in'].isna()].shape[0] > 0:
                                
                                path = recognized_face_name + '/in.png'
                                path = path.replace('\\','/')
                                df.loc[(df['Staff ID'] == index_name) & df['Check-in'].isna(), 'Check-in'] = str(path)
                                df.loc[(df['Staff ID'] == index_name), 'Time in'] = str(now.strftime("%H:%M:%S"))
                                face_image = face_align.norm_crop(frame, face.kps)  # Đảm bảo bạn có face_align và frame ở đây
                                cv2.imwrite(path, face_image)

                            #* Kiểm tra check out theo thời gian thực
                            path = recognized_face_name + '/out.png'
                            path = path.replace('\\','/')
                            df.loc[(df['Staff ID'] == index_name) & df['Check-out'].isna(), 'Check-out'] = str(path)
                            df.loc[(df['Staff ID'] == index_name), 'Time out'] = str(now.strftime("%H:%M:%S"))
                            face_image = face_align.norm_crop(frame, face.kps)  # Đảm bảo bạn có face_align và frame ở đây
                            cv2.imwrite(path, face_image)
                            if df.loc[(df['Staff ID'] == index_name) & ~df['Check-in'].isna() & ~df['Check-out'].isna()].shape[0] > 0:
                                df.loc[(df['Staff ID'] == index_name), 'Attendance'] = 'Present'
                                
                            time_in_str = str(df.loc[df['Staff ID'] == index_name, 'Time in'].iloc[0])
                            time_out_str = str(now.strftime("%H:%M:%S"))
                            # Chuyển đổi từ chuỗi sang định dạng thời gian
                            time_in = datetime.strptime(time_in_str, "%H:%M:%S")
                            time_out = datetime.strptime(time_out_str, "%H:%M:%S")

                            # Tính thời gian làm việc
                            working_duration = time_out - time_in
                            
                            # Chuyển đổi thời gian làm việc sang chuỗi và lưu vào DataFrame
                            df.loc[df['Staff ID'] == index_name, 'Working Duration'] = str(working_duration)
                            
                            #* Ghi lại dữ liệu đã cập nhật vào file CSV
                            df.to_csv('./Attendance.csv', index=False)
                        
                        cv2.putText(frame_rgb, text, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (242, 111, 33), 2)
                    else:
                        cv2.putText(frame_rgb, "Customer", (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (242, 111, 33), 2)
                        
                #! Thực hiện nhận diện cho từng khuôn mặt có det_score cao hơn 0.68
                else:
                    cv2.putText(frame_rgb, "Customer", (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (242, 111, 33), 2)
                    
            self.display_frame(frame_rgb)
        else:
            self.close_webcam()


    def open_webcam(self):
        if self.cap is None and self.status is True:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set frame width to 1280
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set frame height to 720
            self.cap.set(cv2.CAP_PROP_FPS, 60)  # Set frame rate to 60 FPS

    def close_webcam(self):
        if self.cap is not None and self.status is False:
            self.cap.release()
            self.cap = None


    def display_image(self, file_path):
        # Create a QLabel to display the image
        label = QLabel()

        # Load the image from the file path
        pixmap = QPixmap(file_path)

        if pixmap.isNull():
            # Handle the case where the image could not be loaded
            print(f"Error: Image not found at {file_path}")
            return
        # Scale the image to fit the QLabel while maintaining aspect ratio
        pixmap = pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio)

        # Set the pixmap on the QLabel
        self.video_label.setPixmap(pixmap)

    def display_frame(self, frame_rgb):
        # Chuyển đổi khung hình từ OpenCV BGR sang RGB để hiển thị trên QLabel
        image = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        # Dừng webcam và giải phóng tài nguyên khi đóng ứng dụng
        self.close_webcam()
        cv2.destroyAllWindows()
        super().closeEvent(event)