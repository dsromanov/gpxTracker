import os
import unittest
from unittest.mock import patch
import math
import gpxpy
from PyQt5.QtGui import QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from main import calculate_distance, MapWidget  # Предположим, что ваш основной файл называется main.py


class TestCalculateDistance(unittest.TestCase):
    def test_calculate_distance(self):
        lat1, lon1 = 55.7558, 37.6173  # Москва
        lat2, lon2 = 59.9343, 30.3351  # Санкт-Петербург

        distance = calculate_distance(lat1, lon1, lat2, lon2)
        self.assertAlmostEqual(distance, 634, delta=1)


class TestGPXLoading(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.window = MapWidget()

    def test_valid_gpx_file(self):
        gpx_file = 'sample.gpx'
        self.window.load_gpx(gpx_file, QColor(255, 0, 0), 5)
        self.assertIn(gpx_file, self.window.loaded_tracks)
        self.assertTrue(len(self.window.loaded_tracks[gpx_file]) > 0)

    def test_invalid_gpx_file(self):
        gpx_file = 'invalid_track.gpx'
        with self.assertRaises(Exception):
            self.window.load_gpx(gpx_file, QColor(255, 0, 0), 5)

    def test_empty_gpx_file(self):
        gpx_file = 'empty_track.gpx'
        self.window.load_gpx(gpx_file, QColor(255, 0, 0), 5)
        self.assertIn(gpx_file, self.window.loaded_tracks)
        self.assertEqual(len(self.window.loaded_tracks[gpx_file]), 0)


class TestUserInterface(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.window = MapWidget()

    def test_open_gpx_dialog(self):
        with unittest.mock.patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=('sample.gpx', '')):
            self.window.open_gpx_dialog()
            self.assertTrue(self.window.loaded_tracks)

    def test_line_thickness_input(self):
        with unittest.mock.patch('PyQt5.QtWidgets.QInputDialog.getInt', return_value=(5, True)):
            thickness, ok = QInputDialog.getInt(self.window, "Толщина линии", "Введите толщину линии:", 5, 1, 10, 1)
            self.assertEqual(thickness, 5)
            self.assertTrue(ok)



class TestMapFunctionality(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.window = MapWidget()

    def test_initial_map_load(self):
        self.assertIsInstance(self.window.webview, QWebEngineView)
        self.assertTrue(self.window.webview.loadFinished)

    def test_map_zoom(self):
        initial_zoom = self.window.scale
        self.window.scale += 1
        self.assertEqual(self.window.scale, initial_zoom + 1)


class TestScreenshotFunctionality(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.window = MapWidget()

    def test_single_track_screenshot(self):
        gpx_file = 'sample.gpx'
        self.window.load_gpx(gpx_file, QColor(255, 0, 0), 5)
        save_path = 'single_screenshot.png'
        with unittest.mock.patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName', return_value=(save_path, '')):
            self.window.save_screenshot()
            self.assertTrue(os.path.exists(save_path))
            os.remove(save_path)

    def test_multiple_tracks_screenshot(self):
        gpx_file1 = 'Усмань.gpx'
        gpx_file2 = 'sample.gpx'
        self.window.load_gpx(gpx_file1, QColor(255, 0, 0), 5)
        self.window.load_gpx(gpx_file2, QColor(0, 255, 0), 5)
        save_path = 'multiple_screenshot.png'
        with unittest.mock.patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName', return_value=(save_path, '')):
            self.window.save_screenshot()
            self.assertTrue(os.path.exists(save_path))
            os.remove(save_path)

    class TestElevationGraph(unittest.TestCase):

        @classmethod
        def setUpClass(cls):
            cls.app = QApplication([])

        def setUp(self):
            self.window = MapWidget()

        def test_single_track_elevation_graph(self):
            gpx_file = 'sample.gpx'
            self.window.load_gpx(gpx_file, QColor(255, 0, 0), 5)
            with unittest.mock.patch('PyQt5.QtWidgets.QInputDialog.getItem', return_value=(gpx_file, True)):
                self.window.build_elevation_graph()
                self.assertTrue(self.window.graph_window.isVisible())

        def test_multiple_tracks_elevation_graph(self):
            gpx_file1 = 'Усмань.gpx'
            gpx_file2 = 'sample.gpx'
            self.window.load_gpx(gpx_file1, QColor(255, 0, 0), 5)
            self.window.load_gpx(gpx_file2, QColor(0, 255, 0), 5)
            with unittest.mock.patch('PyQt5.QtWidgets.QInputDialog.getItem', return_value=(gpx_file1, True)):
                self.window.build_elevation_graph()
                self.assertTrue(self.window.graph_window.isVisible())


if __name__ == '__main__':
    unittest.main()
