from PyQt5.QtWidgets import *
from PyQt5 import QtCore

import Model.EnvironmentVariables as Variables
import UI.MainView as StudentsRegistration
import Model.GraphAPI as API


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)

        self.setWindowTitle('Login')
        self.setFixedSize(350, 150)

        layout = QGridLayout()

        label_name = QLabel('<font size="4"> Username </font>')
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('Please enter your username')
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 1)

        label_password = QLabel('<font size="4"> Password </font>')
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setEchoMode(QLineEdit.Password)  # hiding password
        self.lineEdit_password.setPlaceholderText('Please enter your password')
        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 1)

        button_login = QPushButton('Login')
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
                API.get_token('aglushko@ithse.ru', 'Defoze330')

            if Variables.user_token is None:
                self.status.setText("<font color = 'red'>Invalid name or password.</font>")
            else:
                # TODO check user license and give access only to admin accounts
                self.accept()
        else:
            self.status.setText("<font color = 'red'>Name and password can`t be empty.</font>")
            # QtWidgets.QMessageBox.warning(self, 'Error', 'Bad user or password')


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    login = LoginWindow()

    if login.exec_() == QDialog.Accepted:
        window = StudentsRegistration.MainWindow()
        window.show()

        sys.exit(app.exec_())
