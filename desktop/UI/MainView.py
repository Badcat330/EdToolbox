from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets

import csv
import os
import threading

# import Src.Model.CreatingMailAddresses as CreatingMailAddresses
# import Src.Model.CreatingAccounts as CreatingAccounts
# import Src.Model.CreatingOfficeGroups as CreatingGroups
import Model.EnvironmentVariables as Variables
import Model.TeamsSynchronization as TeamsSync
import Model.AssignmentsCreation as AssignmentsCreation
# import Src.UI.MessageView as MessageView
# import Src.UI.SettingsView as SettingsView
# import Src.UI.GroupInfoView as GroupInfoView

from Model.Exceptions import *

import Model.GraphAPI as API


def on_mouse_double_clicked(QModelIndex):
    if QModelIndex is not None:
        group_name = QModelIndex.data()
        group_id = QModelIndex.data(QtCore.Qt.UserRole)
        member_list = API.get_group_members(Variables.user_token, group_id)

        # gv = GroupInfoView.GroupInfoWindow(group_name, member_list)
        # gv.exec_()


class MyListModel(QtCore.QAbstractListModel):
    def __init__(self, *args, data=None, **kwargs):
        super(MyListModel, self).__init__(*args, **kwargs)
        self.data_list = data or []

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self.data_list[index.row()]['displayName']
        elif role == QtCore.Qt.UserRole:
            return self.data_list[index.row()]['id']

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.data_list)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # setting the minimum size
        self.setMinimumHeight(400)
        self.setMinimumWidth(600)

        self.file_path = ""

        self.filter = QLineEdit()
        self.groups_model = MyListModel()
        self.list_view = QListView()

        self.stacked_widget = QtWidgets.QStackedWidget(self)
        self.model = QtGui.QStandardItemModel(self)
        self.first_page = self.accounts_creation_page(self.model)
        self.second_page = self.groups_creation_page(self.model)
        self.third_page = self.messaging_page()

        self.stacked_widget.addWidget(self.first_page)
        self.stacked_widget.addWidget(self.second_page)
        self.stacked_widget.addWidget(self.third_page)
        self.stacked_widget.setCurrentIndex(0)

        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.tool_bar())
        self.setCentralWidget(self.stacked_widget)

    def accounts_creation_page(self, model):
        widget = QtWidgets.QWidget(self)

        table_view = QtWidgets.QTableView(widget)
        table_view.setModel(model)
        table_view.horizontalHeader().setStretchLastSection(True)
        table_view.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        push_button_load = QtWidgets.QPushButton(widget)
        push_button_load.setText("Load Csv File!")
        push_button_load.clicked.connect(self.on_pushButtonLoad_clicked)

        push_button_write = QtWidgets.QPushButton(widget)
        push_button_write.setText("Create Corp. Logins")
        push_button_write.clicked.connect(self.on_pushButtonCreateLogins_clicked)

        layout_vertical = QtWidgets.QVBoxLayout(widget)
        layout_vertical.addWidget(table_view)
        layout_vertical.addWidget(push_button_load)
        layout_vertical.addWidget(push_button_write)

        return widget

    def groups_creation_page(self, model):
        widget = QWidget(self)

        table_view = QTableView(widget)
        table_view.setModel(model)
        table_view.horizontalHeader().setStretchLastSection(True)

        self.lineEdit_groupName = QLineEdit()
        self.lineEdit_groupName.setPlaceholderText('Please enter group name')

        push_button_create = QPushButton(widget)
        push_button_create.setText("Create Outlook Group")
        push_button_create.clicked.connect(self.on_pushButtonCreateGroup_clicked)

        layout_vertical = QVBoxLayout(widget)
        layout_vertical.addWidget(table_view)
        layout_vertical.addWidget(self.lineEdit_groupName)
        layout_vertical.addWidget(push_button_create)

        return widget

    def messaging_page(self):
        widget = QWidget(self)

        self.filter.setPlaceholderText("Search...")
        push_button_filter = QPushButton(widget)
        push_button_filter.setText("Search")
        push_button_filter.clicked.connect(self.on_search_btn_clicked)

        filter_box = QHBoxLayout()
        filter_box.addWidget(self.filter)
        filter_box.addWidget(push_button_filter)

        self.list_view = QListView(widget)
        self.list_view.setModel(self.groups_model)
        self.list_view.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_view.doubleClicked.connect(on_mouse_double_clicked)

        push_button_massage = QPushButton(widget)
        push_button_massage.setMaximumHeight(40)
        push_button_massage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        push_button_massage.setText("Select Groups")
        push_button_massage.clicked.connect(self.on_message_btn_clicked)

        layout_vertical = QVBoxLayout(widget)
        layout_vertical.addLayout(filter_box)
        layout_vertical.addWidget(self.list_view)
        layout_vertical.addWidget(push_button_massage)

        return widget

    def tool_bar(self):
        first_page_act = QAction("FP", self)
        first_page_act.setShortcut('Ctrl+1')
        first_page_act.setStatusTip('Jump to first page')
        first_page_act.triggered.connect(self.on_first_page_btn_clicked)

        second_page_act = QAction("SP", self)
        second_page_act.setShortcut('Ctrl+2')
        second_page_act.setStatusTip('Jump to second page')
        second_page_act.triggered.connect(self.on_second_page_btn_clicked)

        third_page_act = QAction("TP", self)
        third_page_act.setShortcut('Ctrl+3')
        third_page_act.setStatusTip('Jump to third page')
        third_page_act.triggered.connect(self.on_third_page_btn_clicked)

        settings_page_act = QAction(QtGui.QIcon('/Users/rinokus/Downloads/icons8-настройки-150.png'), "ST", self)
        settings_page_act.setShortcut('Ctrl+4')
        settings_page_act.setStatusTip('Jump to settings page')
        settings_page_act.triggered.connect(self.on_settings_page_btn_clicked)

        spacer1 = QtWidgets.QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer2 = QtWidgets.QWidget()
        spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer3 = QtWidgets.QWidget()
        spacer3.setMaximumSize(10, 10)
        spacer3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        pages_tool_bar = QToolBar('Pages')
        pages_tool_bar.addWidget(spacer1)
        pages_tool_bar.addActions([first_page_act, second_page_act, third_page_act])
        pages_tool_bar.addWidget(spacer2)
        pages_tool_bar.addAction(settings_page_act)
        pages_tool_bar.addWidget(spacer3)

        return pages_tool_bar

    def load_csv(self, container):
        self.model.clear()
        # CreatingMailAddresses.new_csv_rows.clear()
        # CreatingMailAddresses.first_csv_parse_rows.clear()
        self.file_path = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]

        if self.file_path == '':  # Чтобы не вылезала ошибка, если пользователь отменит выбор файла
            QMessageBox.warning(self, "Error", "You have to choose file.")
        else:
            file_name, file_extension = os.path.splitext(self.file_path)
            if file_extension == '.csv':
                with open(self.file_path, "r") as fileInput:
                    for row in csv.reader(fileInput):
                        if len(row) != 1:
                            container.append(row)
                            items = [
                                QtGui.QStandardItem(field)
                                for field in row
                            ]
                        else:  # Костыль для успешного считывания файла обоих диалектов (',' и ';')
                            new_row = row[0].split(';')
                            container.append(new_row)
                            items = [
                                QtGui.QStandardItem(field)
                                for field in new_row
                            ]
                        self.model.appendRow(items)
            else:
                QMessageBox.warning(self, "Error", "Your file have to be .csv!")

    def create_logins(self):
        # if len(CreatingMailAddresses.first_csv_parse_rows) == 0:
        #     QMessageBox.warning(self, "Error", "You had not parse csv yet!")
        # elif len(CreatingMailAddresses.first_csv_parse_rows[0]) != 4:
        #     QMessageBox.warning(self, "Error", "Users should have 4 data fields!")
        # else:
        #     CreatingMailAddresses.create_csv_with_logins()
        #     self.model.clear()  # убираем устаревшую таблицу из программы
        #     CreatingAccounts.registration()
        #
        #     for row in CreatingMailAddresses.new_csv_rows:  # генерируем новую таблицу
        #         items = [
        #             QtGui.QStandardItem(field)
        #             for field in row
        #         ]
        #         self.model.appendRow(items)

            save_dialog = QMessageBox()
            save_dialog.setIcon(QMessageBox.Question)
            save_dialog.setText("Do yo want to save new csv?")
            save_dialog.setWindowTitle("Saving..")
            save_dialog.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            retval = save_dialog.exec_()

            exc_checker = True

            if retval == QMessageBox.Yes:
                while exc_checker:
                    path = QFileDialog.getSaveFileName(self, "Choose path", '')[0]

                    try:
                        # CreatingMailAddresses.save_new_csv(path)
                        exc_checker = False
                    except OSError:
                        print("Handled an permissions exception.")

    @QtCore.pyqtSlot()
    def on_pushButtonCreateLogins_clicked(self):
        try:
            #self.create_logins()
            AssignmentsCreation.create_assignments(["student1_id", "student2_id"],
                                                   "class_id", "type", "format",
                                                   10, "2022-09-07T00:00:00Z", "LinkTask")
        except TokenException as ex:
            QMessageBox.critical(self, "Error", str(ex))

    @QtCore.pyqtSlot()
    def on_pushButtonLoad_clicked(self):
        ...
        TeamsSync.sync_teams_with_table(TeamsSync.table_r)
        #self.load_csv(CreatingMailAddresses.first_csv_parse_rows)

    @QtCore.pyqtSlot()
    def on_first_page_btn_clicked(self):
        self.stacked_widget.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def on_second_page_btn_clicked(self):
        self.stacked_widget.setCurrentIndex(1)

    @QtCore.pyqtSlot()
    def on_third_page_btn_clicked(self):
        groups = API.get_groups(Variables.user_token)
        self.groups_model.data_list = groups

        self.stacked_widget.setCurrentIndex(2)

    @QtCore.pyqtSlot()
    def on_settings_page_btn_clicked(self):
        ...
        # setting_window = SettingsView.SettingsWindow(self)
        # setting_window.exec_()

    @QtCore.pyqtSlot()
    def on_pushButtonCreateGroup_clicked(self):
        try:
            if self.lineEdit_groupName.text() != "":
                ...
                # if len(CreatingMailAddresses.new_csv_rows) > 1:
                #     save_dialog = QMessageBox()
                #     save_dialog.setIcon(QMessageBox.Question)
                #     save_dialog.setText("Create teams channel?")
                #     save_dialog.setWindowTitle("Teams..")
                #     save_dialog.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
                #     retval = save_dialog.exec_()
                #
                #     group_creator = threading.Thread(target=CreatingGroups.start_creating,
                #                                      args=(retval, self.lineEdit_groupName.text(),))
                #     group_creator.start()
                #     QMessageBox.information(None, "Complete", "Group is successfully created!")
                # else:
                #     QMessageBox.critical(self, "Error", 'Group csv is empty!')
            else:
                QMessageBox.critical(self, "Error", "Group name can't be empty!")
        except TokenException as ex:
            QMessageBox.critical(self, "Error", str(ex))

    @QtCore.pyqtSlot()
    def on_message_btn_clicked(self):
        ids = [i.data(QtCore.Qt.UserRole) for i in self.list_view.selectedIndexes()]

        if ids:
            mails = API.get_users_of_groups(Variables.user_token, ids)

            # message_window = MessageView.MessageWindow(mails, ids)
            # message_window.exec_()
        else:
            QMessageBox.critical(self, "Error", "Choose at least one group for messaging.")

    @QtCore.pyqtSlot()
    def on_search_btn_clicked(self):
        filter_text = str(self.filter.text()).lower()

        for row in range(self.groups_model.rowCount()):
            if filter_text in self.groups_model.data_list[row]['displayName'].lower():
                self.list_view.setRowHidden(row, False)
            else:
                self.list_view.setRowHidden(row, True)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('ProjectS')

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
