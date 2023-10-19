from PySide6.QtWidgets import QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap, QIcon

import pandas as pd
from . style import *
class PyTableWidget(QTableWidget):
    def __init__(
        self, 
        radius = 8,
        color = "#FFF",
        bg_color = "#444",
        selection_color = "#FFF",
        header_horizontal_color = "#333",
        header_vertical_color = "#444",
        bottom_line_color = "#555",
        grid_line_color = "#555",
        scroll_bar_bg_color = "#FFF",
        scroll_bar_btn_color = "#3333",
        context_color = "#00ABE8"
    ):
        super().__init__()
        self.set_stylesheet(
            radius,
            color,
            bg_color,
            header_horizontal_color,
            header_vertical_color,
            selection_color,
            bottom_line_color,
            grid_line_color,
            scroll_bar_bg_color,
            scroll_bar_btn_color,
            context_color
        )
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_from_csv)
        self.timer.start(16)
        
    def update_from_csv(self):
        # Load dataframe
        df = pd.read_csv('./Attendance.csv')

        # Set row and column counts
        self.setRowCount(df.shape[0])
        self.setColumnCount(df.shape[1])

        # Set data
        for row in df.iterrows():
            for col, val in enumerate(row[1]):
                column_name = df.columns[col]

                # Columns with Image Paths (Avatar, Check-in, Check-out)
                if column_name in ['Avatar', 'Check-in', 'Check-out'] and pd.notnull(val):
                    pixmap = QPixmap(val)
                    item = QTableWidgetItem()
                    item.setData(Qt.DecorationRole, pixmap)
                    self.setItem(row[0], col, item)

                    # # Adjust row height based on image height
                    if column_name in ['Avatar']:
                        self.setRowHeight(row[0], pixmap.height())

                # Other Columns
                else:
                    self.setItem(row[0], col, QTableWidgetItem(str(val)))

        # Optionally resize columns
        self.resizeColumnsToContents()

        
    def set_stylesheet(
        self,
        radius,
        color,
        bg_color,
        header_horizontal_color,
        header_vertical_color,
        selection_color,
        bottom_line_color,
        grid_line_color,
        scroll_bar_bg_color,
        scroll_bar_btn_color,
        context_color
    ):
        style_format = style.format(
            _radius = radius,          
            _color = color,
            _bg_color = bg_color,
            _header_horizontal_color = header_horizontal_color,
            _header_vertical_color = header_vertical_color,
            _selection_color = selection_color,
            _bottom_line_color = bottom_line_color,
            _grid_line_color = grid_line_color,
            _scroll_bar_bg_color = scroll_bar_bg_color,
            _scroll_bar_btn_color = scroll_bar_btn_color,
            _context_color = context_color
        )
        self.setStyleSheet(style_format)