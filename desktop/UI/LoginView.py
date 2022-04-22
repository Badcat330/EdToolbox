from PyQt5.QtWidgets import *
from PyQt5 import QtCore

import sharepy

import Model.EnvironmentVariables as Variables
import UI.MainView as StudentsRegistration
import Model.GraphAPI as API


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)

        self.share_point = None
        self.setWindowTitle('Login')
        self.setFixedSize(450, 150)

        layout = QGridLayout()

        label_name = QLabel('<font size="4"> Имя пользователя </font>')
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('Пожалуйста, введите имя пользователя')
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 1)

        label_password = QLabel('<font size="4"> Пароль </font>')
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setEchoMode(QLineEdit.Password)  # hiding password
        self.lineEdit_password.setPlaceholderText('Пожалуйста, введите пароль')
        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 1)

        button_login = QPushButton('Авторизоваться')
        button_login.clicked.connect(self.handle_login)
        button_login.setMinimumHeight(30)
        layout.addWidget(button_login, 2, 0, 2, 2)
        layout.setRowMinimumHeight(2, 50)

        self.status = QLabel('', self)
        self.status.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.status, 4, 0, 1, 2)

        self.setLayout(layout)

    def handle_login(self):
        if self.lineEdit_username.text() and self.lineEdit_password.text():
            Variables.user_token, Variables.refresh_token = \
                API.get_token(self.lineEdit_username.text(), self.lineEdit_password.text())

            Variables.owner_login = self.lineEdit_username.text()

            if Variables.user_token is None:
                self.status.setText("<font color = 'red'>Неверное имя пользователя и/или пароль.</font>")
            else:
                self.share_point = sharepy.connect('https://ithse.sharepoint.com',
                                                   username=self.lineEdit_username.text(),
                                                   password=self.lineEdit_password.text())
                self.accept()
        else:
            self.status.setText("<font color = 'red'>Имя пользователя и пароль не могут быть пустыми.</font>")
            # QtWidgets.QMessageBox.warning(self, 'Error', 'Bad user or password')


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    login = LoginWindow()

    if login.exec_() == QDialog.Accepted:
        window = StudentsRegistration.MainWindow(login.share_point)
        window.show()

        sys.exit(app.exec_())
