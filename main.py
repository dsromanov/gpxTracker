import sys
import tempfile
from datetime import datetime

import gpxpy
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QAction, QSizePolicy, QLabel, \
    QMainWindow, QMessageBox, QInputDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QFile, QTextStream


class MapWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenStreetMap with GPX")
        self.setGeometry(100, 100, 1500, 900)

        layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        self.webview = QWebEngineView()
        self.webview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.webview)

        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)
        self.stats_label.hide()

        self.init_menu_bar()

        self.load_map()
        self.track_points = []

    def init_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")

        open_gpx_action = QAction("Открыть GPX", self)
        open_gpx_action.triggered.connect(self.load_gpx)
        file_menu.addAction(open_gpx_action)

        show_stats_action = QAction("Показать статистику", self)
        show_stats_action.triggered.connect(self.show_stats)
        file_menu.addAction(show_stats_action)

        save_screenshot_action = QAction("Сохранить как скриншот", self)
        save_screenshot_action.triggered.connect(self.save_screenshot)
        file_menu.addAction(save_screenshot_action)

        clear_tracks_action = QAction("Очистить треки", self)
        clear_tracks_action.triggered.connect(self.clear_tracks)
        file_menu.addAction(clear_tracks_action)

    def load_map(self):
        file = QFile("map.html")
        if not file.open(QFile.ReadOnly | QFile.Text):
            QMessageBox.warning(self, "Ошибка", f"Невозможно открыть файл: {file.errorString()}")
            return

        stream = QTextStream(file)
        html_content = stream.readAll()
        file.close()

        self.webview.setHtml(html_content)

    def load_gpx(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть GPX", "", "GPX Files (*.gpx)")
        if file_name:
            with open(file_name, 'r') as gpx_file:
                gpx = gpxpy.parse(gpx_file)
                for track in gpx.tracks:
                    for segment in track.segments:
                        for point in segment.points:
                            self.track_points.append([point.latitude, point.longitude])
                self.webview.page().runJavaScript(f"drawTrack({self.track_points})")

    def show_stats(self):
        self.webview.page().runJavaScript("calculateStats()", self.display_stats_callback)

    def display_stats_callback(self, result):
        if "error" in result:
            QMessageBox.warning(self, "Ошибка", result["error"])
        else:
            stats_str = f"""
            Общее время движения: {result["total_time"]} сек
            Время движения: {result["moving_time"]} сек
            Время отдыха: {result["resting_time"]} сек
            Максимальная скорость: {result["max_speed"]} м/с
            Средняя скорость: {result["avg_speed"]} м/с
            """
            QMessageBox.information(self, "Статистика", stats_str)

    def save_screenshot(self):
        scale_factor, _ = QInputDialog.getDouble(self, "Масштаб", "Введите масштаб (от 0.1 до 10):", 1, 0.1, 10, 1)
        if scale_factor:
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"map_screenshot_{date_time}.png"

            pixmap = self.webview.grab()
            pixmap.save(file_name)

            QMessageBox.information(self, "Успех", f"Скриншот сохранен как {file_name}")

    def clear_tracks(self):
        self.webview.page().runJavaScript("clearTracks();")
        self.track_points.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWidget()
    window.show()
    sys.exit(app.exec_())
