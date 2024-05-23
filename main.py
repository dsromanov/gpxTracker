import math
import math
import os
import sys
import time
from datetime import datetime
import gpxpy
import matplotlib
from PIL import Image, ImageDraw
from PyQt5.QtGui import QPixmap, QImage, QPainter
from matplotlib import pyplot as plt
import pyautogui

from StatsWidget import StatsWidget

matplotlib.use('Agg')
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog, QAction, QSizePolicy, QLabel, \
    QMainWindow, QMessageBox, QInputDialog, QListWidget, QAbstractItemView, QPushButton, QDialog, QLineEdit, qApp
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5.QtCore import QFile, QTextStream, Qt, QTimer
from GraphWidget import GraphWindow


def calculate_distance(lat1, lon1, lat2, lon2):
    # переводим координаты из градусов в радианы
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # средний радиус Земли в метрах
    r = 6371302

    # Расчет расстояния между двумя точками по формуле Хаверсина
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = r * c

    return distance / 1000


class MapWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scale = 10
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
        self.loaded_tracks = {}  # список загруженных треков

    def init_menu_bar(self):
        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")

        open_gpx_action = QAction("Открыть GPX", self)
        open_gpx_action.triggered.connect(self.open_gpx_dialog)
        file_menu.addAction(open_gpx_action)

        clear_tracks_action = QAction("Очистить треки", self)
        clear_tracks_action.triggered.connect(self.clear_tracks)
        file_menu.addAction(clear_tracks_action)

        # Меню "Статистика"
        stats_menu = menubar.addMenu("Статистика")

        calculate_stats_action = QAction("Рассчитать статистику", self)
        calculate_stats_action.triggered.connect(self.calculate_statistics)
        stats_menu.addAction(calculate_stats_action)

        # Меню "Скриншот"
        screenshot_menu = menubar.addMenu("Скриншот")

        save_screenshot_action = QAction("Сохранить скриншот", self)
        save_screenshot_action.triggered.connect(self.save_screenshot)
        screenshot_menu.addAction(save_screenshot_action)

        build_elevation_graph_action = QAction("Построить график высот", self)
        build_elevation_graph_action.triggered.connect(self.build_elevation_graph)
        stats_menu.addAction(build_elevation_graph_action)

    def load_map(self):
        file = QFile("map.html")
        if not file.open(QFile.ReadOnly | QFile.Text):
            QMessageBox.warning(self, "Ошибка", f"Невозможно открыть файл: {file.errorString()}")
            return

        stream = QTextStream(file)
        html_content = stream.readAll()
        file.close()

        self.webview.setHtml(html_content)

    def open_gpx_dialog(self):
        # Здесь показываем диалог выбора файла GPX и запрашиваем цвет и толщину линии
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть GPX", "", "GPX Files (*.gpx)")
        if file_name:
            color_dialog = QtWidgets.QColorDialog(self)
            color_dialog.setCurrentColor(Qt.red)
            color = color_dialog.getColor()
            if color.isValid():
                thickness, ok = QInputDialog.getInt(self, "Толщина линии", "Введите толщину линии:", 5, 1, 10, 1)
                if ok:
                    self.load_gpx(file_name, color, thickness)

    def load_gpx(self, file_name, color, thickness):
        if file_name:
            with open(file_name, 'r') as gpx_file:
                gpx = gpxpy.parse(gpx_file)
                track_points = []  # Список точек текущего трека
                for track in gpx.tracks:
                    for segment in track.segments:
                        for point in segment.points:
                            track_points.append(
                                [point.latitude, point.longitude, point.time.timestamp(), point.elevation])
                self.loaded_tracks[
                    file_name] = track_points  # Добавляем список точек текущего трека в словарь загруженных треков, с ключом - именем файла GPX
                color_rgb = color.name()
                self.webview.page().runJavaScript(
                    f"drawTrack({track_points}, '{color_rgb}', {thickness}, '{file_name}')")

    def calculate_statistics(self):
        filename = ""
        if not self.loaded_tracks:
            QMessageBox.warning(self, "Предупреждение", "Не загружено ни одного трека GPX.")
            return

        if len(self.loaded_tracks) == 1:
            selected_track = next(iter(self.loaded_tracks.values()))  # Если загружен только один трек, выбираем его
            filename = list(self.loaded_tracks.keys())[0]
        else:
            track_names = list(self.loaded_tracks.keys())
            filename, ok_pressed = QInputDialog.getItem(self, "Выбор трека",
                                                        "Выберите трек для расчета статистики:",
                                                        track_names, 0, False)
            if not ok_pressed:
                return  # Пользователь отменил выбор
            selected_track = self.loaded_tracks[filename]

        self.webview.page().runJavaScript(f"focusOnTrack('{filename}')")
        statsWidget = StatsWidget(selected_track)
        statsWidget.exec_()

    def save_screenshot(self):
        if not self.loaded_tracks:
            QMessageBox.warning(self, "Предупреждение", "Не загружено ни одного трека GPX.")
            return

        dialog = QDialog()
        dialog.setWindowTitle("Выбор треков и масштаба")
        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        list_widget.addItems(list(self.loaded_tracks.keys()))
        layout.addWidget(list_widget)

        scale_input = QLineEdit()
        scale_input.setPlaceholderText("Введите масштаб для скриншота(от 1 до 20)")
        layout.addWidget(scale_input)

        ok_button = QPushButton("OK")
        layout.addWidget(ok_button)

        ok_button.clicked.connect(lambda: self.take_screenshots(list_widget.selectedItems(), scale_input.text()))
        ok_button.clicked.connect(dialog.accept)
        dialog.exec_()

    def take_screenshots(self, selected_items, scale_str):
        try:
            self.scale = float(scale_str)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректное числовое значение масштаба.")
            return
        if self.scale < 1 or self.scale > 20:
            QMessageBox.warning(self, "Ошибка", "Масштаб должен быть в диапазоне от 1 до 20.")
            return

        self.selected_items = [item.text() for item in selected_items]  # Сохраняем имена треков для обработки
        self.screenshots = []  # Список для хранении путей к созданным скриншотам

        # Запускаем рекурсивную функцию для фокусировки на каждом выбранном треке
        self.focus_on_next_track()

    def focus_on_next_track(self):
        if not self.selected_items:
            # Когда все треки обработаны, объединяем скриншоты
            self.combine_screenshots()
            return

        # Фокусируемся на следующем треке
        track_name = self.selected_items.pop(0)
        self.webview.page().runJavaScript(f"focusOnTrack('{track_name}')")

        # Создаем скриншот после задержки
        QTimer.singleShot(1000, lambda: self.take_screenshot_for_track(track_name))

    def take_screenshot_for_track(self, track_name):
        screenshot_path = f"{track_name}_screenshot.png"
        pixmap = self.webview.grab()
        pixmap.save(screenshot_path)
        self.screenshots.append(screenshot_path)

        # Переходим к следующему треку
        QTimer.singleShot(0, self.focus_on_next_track)

    def combine_screenshots(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "", "PNG Files (*.png)")

        if save_path:
            screen_width, screen_height = pyautogui.size()
            combined_image = Image.new('RGB', (screen_width, screen_height * len(self.screenshots)))
            y_offset = 0

            for img_path in self.screenshots:
                img = Image.open(img_path)
                combined_image.paste(img, (0, y_offset))
                y_offset += screen_height

            combined_image.save(save_path)

            # Удаление временных скриншотов
            for img_path in self.screenshots:
                os.remove(img_path)

            QMessageBox.information(self, "Информация",
                                    f"Скриншоты всех треков успешно объединены и сохранены по пути: {save_path}.")

    def build_elevation_graph(self):
        if not self.loaded_tracks:
            QMessageBox.warning(self, "Предупреждение", "Не загружено ни одного трека GPX.")
            return

        filename = ""
        if len(self.loaded_tracks) == 1:
            selected_track = next(iter(self.loaded_tracks.values()))  # Если загружен только один трек, выбираем его
            filename = list(self.loaded_tracks.keys())[0]
        else:
            track_names = list(self.loaded_tracks.keys())
            filename, ok_pressed = QInputDialog.getItem(self, "Выбор трека",
                                                        "Выберите трек для построения графика высот:",
                                                        track_names, 0, False)
            if not ok_pressed:
                return  # Пользователь отменил выбор
            selected_track = self.loaded_tracks[filename]

        graph_window = GraphWindow(selected_track)
        graph_window.exec_()

    def clear_tracks(self):
        self.webview.page().runJavaScript("clearTracks();")
        self.stats_label.clear()
        self.stats_label.hide()
        self.loaded_tracks.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWidget()
    window.show()
    sys.exit(app.exec_())
