from . functions_main_window import *

from gui.widgets import PyIconButton, ModelFunction, PyTableWidget
from gui.core.json_settings import Settings
from gui.core.json_themes import Themes
from gui.widgets import PyGrips
from gui.core.functions import Functions

from PySide6.QtGui import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QHeaderView, QAbstractItemView, QTableWidgetItem

import FPTvision
import pandas as pd
 
class SetupMainWindow:
    def __init__(self):
        super().__init__()
        self.ui = UI_MainWindow()
        self.ui.setup_ui(self)
        
    add_left_menus = [
        {
            "btn_icon" : "icon_home.svg",
            "btn_id" : "btn_0",
            "btn_text" : "Home",
            "btn_tooltip" : "Home",
            "show_top" : True,
            "is_active" : True,
        }, 
        {
            "btn_icon" : "icon_add_user.svg",
            "btn_id" : "btn_1",
            "btn_text" : "Attendance Tracker Pro",
            "btn_tooltip" : "Attendance Tracker Pro",
            "show_top" : True,
            "is_active" : False,
        },
        {
            "btn_icon" : "icon_emoticons.svg",
            "btn_id" : "btn_2",
            "btn_text" : "FaceID Sentinel",
            "btn_tooltip" : "FaceID Sentinel",
            "show_top" : True,
            "is_active" : False
        }
    ]
    
    def setup_btns(self):
        if self.ui.title_bar.sender() != None:
            return self.ui.title_bar.sender()
        elif self.ui.left_menu.sender() != None:
            return self.ui.left_menu.sender()
        elif self.ui.left_column.sender() != None:
            return self.ui.left_column.sender()
        
    def setup_gui(self):
        self.setWindowTitle(self.settings["app_name"])
        
        if self.settings["custom_title_bar"]:
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
            
        if self.settings["custom_title_bar"]:
            self.left_grip = PyGrips(self, "left", self.hide_grips)
            self.right_grip = PyGrips(self, "right", self.hide_grips)
            self.top_grip = PyGrips(self, "top", self.hide_grips)
            self.bottom_grip = PyGrips(self, "bottom", self.hide_grips)
            self.top_left_grip = PyGrips(self, "top_left", self.hide_grips)
            self.top_right_grip = PyGrips(self, "top_right", self.hide_grips)
            self.bottom_left_grip = PyGrips(self, "bottom_left", self.hide_grips)
            self.bottom_right_grip = PyGrips(self, "bottom_right", self.hide_grips)
        self.ui.left_menu.add_menus(SetupMainWindow.add_left_menus)
        self.ui.left_menu.clicked.connect(self.btn_clicked)
        self.ui.left_menu.released.connect(self.btn_released)
        self.ui.title_bar.clicked.connect(self.btn_clicked)
        self.ui.title_bar.released.connect(self.btn_released)
        
        if self.settings["custom_title_bar"]:
            self.ui.title_bar.set_title(self.settings["app_name"])
        else:
            self.ui.title_bar.set_title("")
        self.ui.left_column.clicked.connect(self.btn_clicked)
        self.ui.left_column.released.connect(self.btn_released)
        
        MainFunctions.set_page(self, self.ui.load_pages.page_1)

        MainFunctions.set_left_column_menu(
            self,
            menu = self.ui.left_column.menus.menu_1,
            title = "Settings Left Column",
            icon_path = Functions.set_svg_icon("icon_settings.svg")
        )

        settings = Settings()
        self.settings = settings.items
        
        themes = Themes()
        self.themes = themes.items

        #Home page
        self.Home_logo = QSvgWidget(Functions.set_svg_image("Home.svg"))
        self.Home_logo.setFixedSize(700, 700)
        self.ui.load_pages.row_1_1layout.addWidget(self.Home_logo, Qt.AlignCenter | Qt.AlignCenter)

        self.btn_start = PyIconButton(
            icon_path = Functions.set_svg_icon("icon_heart.svg"),
            parent = self,
            app_parent = self.ui.central_widget,
            tooltip_text = "Start/Stop",
            width = 40,
            height = 40,
            radius = 20,
            dark_one = self.themes["app_color"]["dark_one"],
            icon_color = self.themes["app_color"]["icon_color"],
            icon_color_hover = self.themes["app_color"]["dark_four"],
            icon_color_pressed = self.themes["app_color"]["icon_active"],
            icon_color_active = self.themes["app_color"]["icon_active"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["green"]
        )

        # TABLE WIDGETS
        #* Đọc data frame có sẵn
        file_path = "./Attendance.csv"

        # Đọc dữ liệu từ file CSV vào một DataFrame
        df = pd.read_csv(file_path)

        # Đặt tất cả giá trị của cột "Attendance" thành "False"
        df['Attendance'] = 'Processing'
        df['Check-in'] = None
        df['Check-out'] = None
 

        # Ghi lại dữ liệu đã cập nhật vào file CSV
        df.to_csv(file_path, index=False)
         
        self.table_widget = PyTableWidget(
            radius = 8,
            color = self.themes["app_color"]["text_foreground"],
            selection_color = self.themes["app_color"]["context_color"],
            bg_color = self.themes["app_color"]["bg_two"],
            header_horizontal_color = "#6b90da",
            # header_vertical_color = self.themes["app_color"]["bg_three"],
            header_vertical_color = "#f26f21",
            bottom_line_color = self.themes["app_color"]["bg_three"],
            grid_line_color = self.themes["app_color"]["bg_one"], 
            scroll_bar_bg_color = self.themes["app_color"]["bg_one"],
            scroll_bar_btn_color = self.themes["app_color"]["dark_four"],
            context_color = self.themes["app_color"]["context_color"]
        )

        self.table_widget.setColumnCount(30)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Columns / Header
        self.column_1 = QTableWidgetItem()
        self.column_1.setTextAlignment(Qt.AlignCenter)
        self.column_1.setText("Staff ID")

        self.column_2 = QTableWidgetItem()
        self.column_2.setTextAlignment(Qt.AlignCenter)
        self.column_2.setText("Avatar")

        self.column_3 = QTableWidgetItem()
        self.column_3.setTextAlignment(Qt.AlignCenter)
        self.column_3.setText("Last Name")

        self.column_4 = QTableWidgetItem()
        self.column_4.setTextAlignment(Qt.AlignCenter)
        self.column_4.setText("Surname")

        self.column_5 = QTableWidgetItem()
        self.column_5.setTextAlignment(Qt.AlignCenter)
        self.column_5.setText("Name")
        
        self.column_6 = QTableWidgetItem()
        self.column_6.setTextAlignment(Qt.AlignCenter)
        self.column_6.setText("Check-in")
        
        self.column_7 = QTableWidgetItem()
        self.column_7.setTextAlignment(Qt.AlignCenter)
        self.column_7.setText("Check-out")
        
        self.column_8 = QTableWidgetItem()
        self.column_8.setTextAlignment(Qt.AlignCenter)
        self.column_8.setText("Time-in")
        
        self.column_9 = QTableWidgetItem()
        self.column_9.setTextAlignment(Qt.AlignCenter)
        self.column_9.setText("Time-out")
        
        self.column_10 = QTableWidgetItem()
        self.column_10.setTextAlignment(Qt.AlignCenter)
        self.column_10.setText("Working Duration")
        
        self.column_11 = QTableWidgetItem()
        self.column_11.setTextAlignment(Qt.AlignCenter)
        self.column_11.setText("Attendance")

        # Set column
        self.table_widget.setHorizontalHeaderItem(0, self.column_1)
        self.table_widget.setHorizontalHeaderItem(1, self.column_2)                                           
        self.table_widget.setHorizontalHeaderItem(2, self.column_3)
        self.table_widget.setHorizontalHeaderItem(3, self.column_4)                                           
        self.table_widget.setHorizontalHeaderItem(4, self.column_5)
        self.table_widget.setHorizontalHeaderItem(5, self.column_6)
        self.table_widget.setHorizontalHeaderItem(6, self.column_7)        
        self.table_widget.setHorizontalHeaderItem(7, self.column_8)
        self.table_widget.setHorizontalHeaderItem(8, self.column_9)
        self.table_widget.setHorizontalHeaderItem(9, self.column_10)
        self.table_widget.setHorizontalHeaderItem(10, self.column_11)

        #! page 1 (show data frame)
        self.ui.load_pages.row_1_2layout.addWidget(self.table_widget)

        #! page 2 (chỉ  cần show camera)
        #* Gọi model
        self.Detector = FPTvision.app.FaceAnalysis()
        self.Detector.prepare(ctx_id=0, det_size=(640, 640))

        self.Recognition = FPTvision.model_zoo.arcface_onnx.ArcFaceONNX(model_file='./gui/models/Recognition/model.onnx')
        self.Recognition.prepare(ctx_id=0)
        
        self.Function1 = ModelFunction(self.Detector, self.Recognition)
        
        self.ui.load_pages.row_1_3layout.addWidget(self.Function1.video_label)
        
        self.ui.load_pages.row_2_3layout.addWidget(self.btn_start)
        
        self.btn_start.clicked.connect(self.Function1.turn_on_off_model)

    def resize_grips(self):
        if self.settings["custom_title_bar"]:
            self.left_grip.setGeometry(5, 10, 10, self.height())
            self.right_grip.setGeometry(self.width() - 15, 10, 10, self.height())
            self.top_grip.setGeometry(5, 5, self.width() - 10, 10)
            self.bottom_grip.setGeometry(5, self.height() - 15, self.width() - 10, 10)
            self.top_right_grip.setGeometry(self.width() - 20, 5, 15, 15)
            self.bottom_left_grip.setGeometry(5, self.height() - 20, 15, 15)
            self.bottom_right_grip.setGeometry(self.width() - 20, self.height() - 20, 15, 15)