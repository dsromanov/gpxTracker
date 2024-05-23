import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtGui import QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class GraphWindow(QDialog):
    def __init__(self, selected_track):
        super().__init__()
        self.setWindowTitle("Elevation Graph")
        self.selected_track = selected_track
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        fig, ax = plt.subplots()
        ax.set_title("Elevation Graph")
        ax.set_xlabel("Time (hours)")
        ax.set_ylabel("Elevation (meters)")

        times_hours = [(point[2] - self.selected_track[0][2]) / 3600 for point in self.selected_track]
        elevations = [point[3] for point in self.selected_track]

        ax.plot(times_hours, elevations)
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
