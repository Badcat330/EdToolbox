from PyQt5.QtWidgets import *
from PyQt5 import QtCore

import Model.EnvironmentVariables as Variables


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)

        self.setWindowTitle('Settings')
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMinimumSize(100, 150)

        self.settings_line_edit_login = QLineEdit()
        self.number_of_subgroups = QSpinBox()
        self.sync_cb = QComboBox()

        self.settings_line_edit_login.setText(Variables.owner_login)
        self.number_of_subgroups.setMinimum(1)
        self.number_of_subgroups.setMaximum(20)
        self.number_of_subgroups.setValue(Variables.number_of_subgroups)

        if self.sync_cb.model().rowCount() == 0:
            for el in Variables.syncs:
                self.sync_cb.addItem(el)
        self.sync_cb.setCurrentIndex(Variables.selected_sync_ind)

        layout = QVBoxLayout()

        login_hbox = QHBoxLayout()
        label_login = QLabel('<font size="4"> Логин владельца новых групп </font>')
        login_hbox.addWidget(label_login)
        login_hbox.addWidget(self.settings_line_edit_login)
        layout.addLayout(login_hbox)

        subgroups_hbox = QHBoxLayout()
        label_subgroups = QLabel('<font size="4"> Количество подгрупп при создании группы </font>')
        subgroups_hbox.addWidget(label_subgroups)
        subgroups_hbox.addWidget(self.number_of_subgroups)
        layout.addLayout(subgroups_hbox)

        sync_hbox = QHBoxLayout()
        label_sync = QLabel('<font size="4"> Режим синхронизации </font>')
        sync_hbox.addWidget(label_sync)
        sync_hbox.addWidget(self.sync_cb)
        layout.addLayout(sync_hbox)

        apply_btn = QPushButton('Применить')
        apply_btn.clicked.connect(self.on_apply_btn_clicked)
        apply_btn.setMinimumHeight(30)
        layout.addWidget(apply_btn)

        self.setLayout(layout)

    @QtCore.pyqtSlot()
    def on_apply_btn_clicked(self):
        if self.settings_line_edit_login.text() != '':
            Variables.owner_login = self.settings_line_edit_login.text()
            Variables.number_of_subgroups = self.number_of_subgroups.value()
            Variables.selected_sync_ind = self.sync_cb.currentIndex()

            self.close()
        else:
            QMessageBox.critical(self, 'Ошибка', 'Логин владельца не может быть пустым.')
