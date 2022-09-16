from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial

import io
import sharepy
import pandas as pd

import Model.EnvironmentVariables as Variables
import Model.TeamsSynchronization as TeamsSync
import UI.AssignmentView as AssignmentView
import UI.SettingsView as SettingsView

from Model.Exceptions import *

import Model.GraphAPI as API


def on_mouse_double_clicked(QModelIndex):
    if QModelIndex is not None:
        group_name = QModelIndex.data()
        group_id = QModelIndex.data(QtCore.Qt.UserRole)
        member_list = API.get_group_members(Variables.user_token, group_id)


def on_mouse_double_clicked_file(QModelIndex):
    if QModelIndex is not None:
        group_name = QModelIndex.data()
        group_id = QModelIndex.data(QtCore.Qt.UserRole)
        member_list = API.get_group_members(Variables.user_token, group_id)


class MyListModelContingent(QtCore.QAbstractListModel):
    def __init__(self, *args, data=None, **kwargs):
        super(MyListModelContingent, self).__init__(*args, **kwargs)
        self.data_list = data or []

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self.data_list[index.row()]['displayName']
        elif role == QtCore.Qt.UserRole:
            return self.data_list[index.row()]['id']

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.data_list)


class MyListModelFiles(QtCore.QAbstractListModel):
    def __init__(self, *args, data=None, **kwargs):
        super(MyListModelFiles, self).__init__(*args, **kwargs)
        self.data_list = data or []

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self.data_list[index.row()][0]
        elif role == QtCore.Qt.UserRole:
            return self.data_list[index.row()][1]

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.data_list)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, share_point_con, parent=None):
        super(MainWindow, self).__init__(parent)

        self.share_point = share_point_con
        # setting the minimum size
        self.setMinimumHeight(400)
        self.setMinimumWidth(600)

        self.filter = QLineEdit()
        self.push_button_filter = QPushButton()
        self.push_button_select_class = QPushButton()
        self.push_button_select_file = QPushButton()

        self.classes_model = MyListModelContingent()
        self.students_model = MyListModelContingent()
        self.files_model = MyListModelFiles()
        self.sites_model = MyListModelFiles()

        self.list_view_contingent = QListView()
        self.list_view_files = QListView()

        self.stacked_widget = QtWidgets.QStackedWidget(self)
        self.first_page = self.csv_selecting_page()
        self.second_page = self.classes_selecting_page()

        self.stacked_widget.addWidget(self.first_page)
        self.stacked_widget.addWidget(self.second_page)
        self.stacked_widget.setCurrentIndex(0)

        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.tool_bar())
        self.setCentralWidget(self.stacked_widget)

    def csv_selecting_page(self):
        widget = QWidget(self)

        self.list_view_files = QListView(widget)
        self.list_view_files.setModel(self.files_model)
        self.list_view_files.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_view_files.doubleClicked.connect(on_mouse_double_clicked_file)

        self.push_button_select_file.setMaximumHeight(40)
        self.push_button_select_file.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout_vertical = QVBoxLayout(widget)
        layout_vertical.addWidget(self.list_view_files)
        layout_vertical.addWidget(self.push_button_select_file)

        self.populate_sites_table()

        return widget

    def classes_selecting_page(self):
        widget = QWidget(self)

        self.filter.setPlaceholderText("Поиск...")
        self.push_button_filter.setText("Поиск")
        self.push_button_filter.clicked.connect(partial(self.on_search_btn_clicked,
                                                        page_model=self.classes_model))

        filter_box = QHBoxLayout()
        filter_box.addWidget(self.filter)
        filter_box.addWidget(self.push_button_filter)

        self.list_view_contingent = QListView(widget)
        self.list_view_contingent.setModel(self.classes_model)
        self.list_view_contingent.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_view_contingent.doubleClicked.connect(on_mouse_double_clicked)

        self.push_button_select_class.setMaximumHeight(40)
        self.push_button_select_class.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.push_button_select_class.setText("Выбрать класс")
        self.push_button_select_class.clicked.connect(self.on_select_class_btn_clicked)

        layout_vertical = QVBoxLayout(widget)
        layout_vertical.addLayout(filter_box)
        layout_vertical.addWidget(self.list_view_contingent)
        layout_vertical.addWidget(self.push_button_select_class)

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
        pages_tool_bar.addActions([first_page_act, second_page_act])
        pages_tool_bar.addWidget(spacer2)
        pages_tool_bar.addAction(settings_page_act)
        pages_tool_bar.addWidget(spacer3)

        return pages_tool_bar

    def populate_sites_table(self):
        self.list_view_files.setModel(self.sites_model)
        self.push_button_select_file.setText("Выбрать сайт")
        self.push_button_select_file.clicked.connect(self.on_select_site_btn_clicked)

        resp = self.share_point.get(
            "https://ithse.sharepoint.com/_api/search/query?"
            "querytext='contentclass:STS_Site Path:\"https://ithse.sharepoint.com/*\"'")
        results = resp.json()['d']['query']['PrimaryQueryResult']['RelevantResults']['Table']['Rows']['results']
        res = []

        for i in results:
            for j in i['Cells']['results']:
                if j['Key'] == 'SiteName':
                    res.append([j['Value']])

        self.sites_model.data_list = res

    def populate_files_table(self, results):
        self.list_view_files.setModel(self.files_model)
        self.push_button_select_file.setText("Выбрать файл")
        self.push_button_select_file.clicked.connect(self.on_select_file_btn_clicked)

        res = []
        for i in results:
            res.append([i['ServerRelativeUrl'].rpartition('/')[-1], i['ServerRelativeUrl']])

        self.files_model.data_list = res


    @QtCore.pyqtSlot()
    def on_first_page_btn_clicked(self):
        self.populate_sites_table()

        self.stacked_widget.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def on_second_page_btn_clicked(self):
        self.classes_model.data_list = API.get_classes_in_organization()

        self.stacked_widget.setCurrentIndex(1)

    @QtCore.pyqtSlot()
    def on_settings_page_btn_clicked(self):
        setting_window = SettingsView.SettingsWindow(self)
        setting_window.exec_()

    @QtCore.pyqtSlot()
    def on_select_class_btn_clicked(self):
        ids = [i.data(QtCore.Qt.UserRole) for i in self.list_view_contingent.selectedIndexes()]

        if ids:
            students = API.get_class_members(ids[0])
            self.students_model.data_list = students

            self.list_view_contingent.setModel(self.students_model)
            self.list_view_contingent.setSelectionMode(QAbstractItemView.MultiSelection)
            self.push_button_filter.clicked.connect(
                partial(self.on_search_btn_clicked, page_model=self.students_model))

            self.push_button_select_class.clicked.disconnect()
            self.push_button_select_class.setText("Создать задание")
            self.push_button_select_class.clicked.connect(
                partial(self.on_create_assignment_btn_clicked, class_id=ids[0]))
        else:
            QMessageBox.critical(self, "Ошибка", "Выберите класс для продолжения.")

    @QtCore.pyqtSlot()
    def on_create_assignment_btn_clicked(self, class_id):
        students_ids = [i.data(QtCore.Qt.UserRole) for i in
                        self.list_view_contingent.selectedIndexes()]

        if students_ids:
            assignment_window = AssignmentView.AssignmentWindow(students_ids, class_id)
            assignment_window.exec_()

            self.classes_model.data_list = API.get_classes_in_organization()

            self.list_view_contingent.setModel(self.classes_model)
            self.list_view_contingent.setSelectionMode(QAbstractItemView.SingleSelection)
            self.list_view_contingent.doubleClicked.connect(on_mouse_double_clicked)

            self.push_button_filter.clicked.connect(partial(self.on_search_btn_clicked,
                                                            page_model=self.classes_model))

            self.push_button_select_class.clicked.disconnect()
            self.push_button_select_class.setText("Выбрать класс")
            self.push_button_select_class.clicked.connect(
                self.on_select_class_btn_clicked)

        else:
            team_tags = dict([(x, y) for (x, y) in
                              API.get_tags_in_class(class_id).items() if 'Подгруппа' in x])

            if len(team_tags) != 0:
                assignment_window = AssignmentView.AssignmentWindow(students_ids, class_id, team_tags)
                assignment_window.exec_()
            else:
                QMessageBox.critical(self, "Ошибка",
                                     "В вашей группе нет ни одной подгруппы! Выберите студентов из списка.")

    @QtCore.pyqtSlot()
    def on_select_site_btn_clicked(self):
        site_paths = [i.data() for i in
                      self.list_view_files.selectedIndexes()]

        if site_paths:
            folder_url = 'Shared Documents'
            url = site_paths[0] + f"/_api/Web/GetFolderByServerRelativeUrl('{ folder_url }')?$expand=Folders,Files"
            resp = self.share_point.get(url)

            self.push_button_select_file.clicked.disconnect()
            self.populate_files_table(resp.json()['d']['Files']['results'])
        else:
            QMessageBox.critical(self, "Ошибка", "Выберите хотя бы один сайт.")

    @QtCore.pyqtSlot()
    def on_select_file_btn_clicked(self):
        paths = [i.data(QtCore.Qt.UserRole) for i in
                 self.list_view_files.selectedIndexes()]

        if paths:
            resp = self.share_point.get('https://ithse.sharepoint.com/' + paths[0])
            file = io.BytesIO(resp.content)
            data = pd.read_excel(file, 'Sheet1', index_col=0)

            sync_dialog = QMessageBox()
            sync_dialog.setIcon(QMessageBox.Question)
            sync_dialog.setText('Выбор режима')
            table_with_classes_btn = sync_dialog.addButton("таблица с MS Teams", QMessageBox.YesRole)
            classes_with_table_btn = sync_dialog.addButton("MS Teams с таблицей", QMessageBox.NoRole)
            sync_dialog.exec_()

            if sync_dialog.clickedButton() == table_with_classes_btn:
                only_table_members, data = TeamsSync.sync_table_with_classes(data)

                file = io.BytesIO()
                data.to_excel(file)
                content = file.getvalue()
                headers = {"accept": "application/json;odata=verbose",
                           "Authorization": f"Bearer {self.share_point.auth.digest}",
                           "Content-Type": "application/octet-stream;",
                           "Content-Transfer-Encoding": "binary",
                           "content-length": f"{len(content)}"}

                find_index = -1
                while paths[0][find_index] != '/':
                    find_index -= 1

                folder_path = paths[0][0:find_index]
                resp = self.share_point.post(
                    f"https://ithse.sharepoint.com/sites/TestSharePointAndPowerApps/_api/web/"
                    f"GetFolderByServerRelativeUrl('{folder_path}')/Files/add(url='Book.xlsx',overwrite=true)",
                    data=file.getvalue(), headers=headers)
            else:
                data = data.loc[data['Статус'] == 1]
                TeamsSync.sync_classes_with_table(data.to_numpy())

            QMessageBox.information(self, 'Операция завершена', 'Операция завершена успешно!')
        else:
            QMessageBox.critical(self, "Ошибка", "Выберите файл для продолжение.")

    @QtCore.pyqtSlot()
    def on_search_btn_clicked(self, page_model):
        filter_text = str(self.filter.text()).lower()

        for row in range(page_model.rowCount()):
            if filter_text in page_model.data_list[row]['displayName'].lower():
                self.list_view_contingent.setRowHidden(row, False)
            else:
                self.list_view_contingent.setRowHidden(row, True)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('ProjectS')

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
