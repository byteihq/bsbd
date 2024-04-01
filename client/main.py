import sys
import os
import logging
import datetime
from pyui.auth_window import AuthWindow
from PyQt5.QtWidgets import QApplication
from client.net.server_api import ServerApi


def init_logger():
    today_date = datetime.datetime.now().strftime('%d-%m-%Y')
    file_handler = logging.FileHandler(f'client_{today_date}.log')

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])


def login(server_api):
    app = QApplication(sys.argv)
    win = AuthWindow(server_api)
    win.show()
    app.exec()


def main():
    init_logger()

    server_api = ServerApi('https://localhost', os.path.abspath('secrets/cert.pem'))
    login(server_api)


if __name__ == "__main__":
    main()
