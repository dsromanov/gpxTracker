import math
import time

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QHBoxLayout


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


class StatsWidget(QDialog):
    def __init__(self, selected_track, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Статистика трека")

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Вычисление статистики
        total_distance = 0
        total_time = 0
        max_speed = 0
        total_elevation_gain = 0
        max_elevation = -float('inf')
        min_elevation = float('inf')

        previous_point = None
        previous_time = None

        for point in selected_track:
            lat, lon, timestamp, elevation = point

            if previous_point:
                prev_lat, prev_lon, prev_timestamp, prev_elevation = previous_point

                # Расчет дистанции
                distance = calculate_distance(prev_lat, prev_lon, lat, lon)
                total_distance += distance

                # Расчет времени
                time_diff = timestamp - prev_timestamp
                total_time += time_diff

                # Расчет скорости
                if time_diff > 0:
                    speed = distance / (time_diff / 3600)  # скорость в км/ч
                    if speed > max_speed:
                        max_speed = speed

                # Расчет набора высоты
                elevation_gain = elevation - prev_elevation
                if elevation_gain > 0:
                    total_elevation_gain += elevation_gain

            # Максимальная высота
            if elevation > max_elevation:
                max_elevation = elevation

            # Минимальная высота
            if elevation < min_elevation:
                min_elevation = elevation

            previous_point = point

        # Средняя скорость
        average_speed = (total_distance / (total_time / 3600)) if total_time > 0 else 0

        # Преобразование общего времени из секунд в формат чч:мм:сс
        total_time_human_readable = time.strftime("%H:%M:%S", time.gmtime(total_time))

        # Отображение статистики
        stats_text = f"Общая дистанция: {total_distance:.2f} км\n" \
                     f"Общее время: {total_time_human_readable}\n" \
                     f"Максимальная скорость: {max_speed:.2f} км/ч\n" \
                     f"Средняя скорость: {average_speed:.2f} км/ч\n" \
                     f"Набор высоты: {total_elevation_gain:.2f} м\n" \
                     f"Максимальная высота: {max_elevation:.2f} м"

        stats_label = QLabel(stats_text)
        layout.addWidget(stats_label)

        button_layout = QHBoxLayout()

        # Кнопки закрытия
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)

        # Добавляем кнопку в горизонтальный макет
        button_layout.addWidget(buttons)

        # Добавляем горизонтальный макет в вертикальный макет
        layout.addLayout(button_layout)
