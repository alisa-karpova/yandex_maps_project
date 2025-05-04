import sys
import requests

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QApplication

from size import get_toponym_size


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('map.ui', self)
        self.search_btn.clicked.connect(self.search)
        self.theme_btn.clicked.connect(self.change_theme)
        self.reset_btn.clicked.connect(self.reset)
        self.pc_rb.toggled.connect(self.postal_code)

        # basic setup
        self.ll = '37.587998,55.733723'
        self.pt = '37.587998,55.733723'
        self.toponym = self.find_toponym(self.ll)
        self.current_theme = "light"
        self.spn = get_toponym_size(self.toponym)
        self.delta_spn = 0.005
        self.delta_ll = 0.00015

        # show
        self.show_map()

    def keyPressEvent(self, event):
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        if event.key() == Qt.Key.Key_PageUp:
            ln_spn, lt_spn = self.spn.split(',')
            spn = [str(float(ln_spn) + self.delta_spn), str(float(lt_spn) + self.delta_spn)]
            self.spn = ','.join(spn)
            self.show_map()

        if event.key() == Qt.Key.Key_PageDown:
            ln_spn, lt_spn = self.spn.split(',')
            new_ln_spn, new_lt_spn = float(ln_spn) - self.delta_spn, float(lt_spn) - self.delta_spn
            min_ln_spn, min_lt_spn = get_toponym_size(self.toponym).split(',')

            if not (new_ln_spn < float(min_ln_spn) or new_lt_spn < float(min_lt_spn)):
                self.spn = ','.join([str(new_ln_spn), str(new_lt_spn)])

            self.show_map()

        if event.key() == Qt.Key.Key_Down:
            ln_ll, lt_ll = self.ll.split(',')
            lt_ll = float(lt_ll) - self.delta_ll
            self.ll = f"{ln_ll},{lt_ll}"
            self.show_map()

        if event.key() == Qt.Key.Key_Up:
            ln_ll, lt_ll = self.ll.split(',')
            lt_ll = float(lt_ll) + self.delta_ll
            self.ll = f"{ln_ll},{lt_ll}"
            self.show_map()

        if event.key() == Qt.Key.Key_Left:
            ln_ll, lt_ll = self.ll.split(',')
            ln_ll = float(ln_ll) - self.delta_ll
            self.ll = f"{ln_ll},{lt_ll}"
            self.show_map()

        if event.key() == Qt.Key.Key_Right:
            ln_ll, lt_ll = self.ll.split(',')
            ln_ll = (float(ln_ll) + self.delta_ll)
            self.ll = f"{ln_ll},{lt_ll}"
            self.show_map()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toponym = self.find_toponym(self.ll)
            self.pt = self.ll
            self.spn = get_toponym_size(self.toponym)
            self.show_map()

    def change_theme(self):
        if self.current_theme == "light":
            self.theme_btn.setText("light")
            self.current_theme = "dark"
        else:
            self.theme_btn.setText("dark")
            self.current_theme = "light"
        self.show_map()

    def search(self):
        self.toponym = self.find_toponym(self.request.text())
        self.ll = ','.join(self.toponym["Point"]["pos"].split())
        self.pt = self.ll
        self.spn = get_toponym_size(self.toponym)
        self.show_map()

    def reset(self):
        self.pt = None
        self.show_map()
        self.address.clear()

    def postal_code(self):
        address = self.toponym['metaDataProperty']['GeocoderMetaData']['text']
        if self.toponym['metaDataProperty']['GeocoderMetaData']['kind'] == 'house':
            postal_code = self.toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
        else:
            postal_code = None

        if self.pc_rb.isChecked():
            self.address.setText(f"address: {address}; postal code: {postal_code}")
        else:
            self.address.setText(f"address: {address}")

    def find_toponym(self, toponym_to_find):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
            "geocode": toponym_to_find,
            "format": "json",
        }

        response = requests.get(geocoder_api_server, params=geocoder_params)

        if not response:
            print('geocoder: wrong request')

        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

        return toponym

    def show_map(self):
        apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
        map_api_server = "https://static-maps.yandex.ru/v1"

        map_params = {
            "ll": self.ll,
            "spn": self.spn,
            "apikey": apikey,
            "theme": self.current_theme
        }

        if self.pt is not None:
            map_params["pt"] = f"{self.pt},round"
            self.postal_code()

        response = requests.get(map_api_server, params=map_params)

        if not response:
            print('static: wrong request')

        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(map_file)
        self.map.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    map = Map()
    map.show()
    sys.exit(app.exec())