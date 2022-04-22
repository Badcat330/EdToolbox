from PyQt5.QtWidgets import *
from PyQt5 import QtCore

from functools import partial
from multiprocessing.dummy import Pool as ThreadPool

import Model.AssignmentsCreation as AssignmentsCreation
import Model.GraphAPI as API

task_types = ['Unit validation task', 'Unit conversion task']
task_formats = ['binary_choice', 'choice', 'options', 'number']


class AssignmentWindow(QDialog):
    def __init__(self, students_ids, class_id, tags=None, parent=None):
        super(AssignmentWindow, self).__init__(parent)

        self.setWindowTitle('Параметры задания')
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMinimumSize(350, 200)

        self.students_ids = students_ids
        self.class_id = class_id
        self.tags = tags

        self.name = QLineEdit()
        self.type = QComboBox()
        self.format = QComboBox()
        self.number = QSpinBox()
        self.date = QDateTimeEdit(calendarPopup=True)
        self.tag = QComboBox()

        self.number.setMinimum(1)
        self.number.setMaximum(20)
        self.date.setDateTime(QtCore.QDateTime.currentDateTime())
        self.date.setDisplayFormat("yyyy-MM-dd'T'hh:mm:ssZ")

        self.type.addItems(task_types)
        self.format.addItems(task_formats)

        layout = QVBoxLayout()

        name_hbox = QHBoxLayout()
        label_name = QLabel('<font size="4"> Название </font>')
        name_hbox.addWidget(label_name)
        name_hbox.addWidget(self.name)
        layout.addLayout(name_hbox)

        type_hbox = QHBoxLayout()
        label_type = QLabel('<font size="4"> Тип </font>')
        type_hbox.addWidget(label_type)
        type_hbox.addWidget(self.type)
        layout.addLayout(type_hbox)

        format_hbox = QHBoxLayout()
        label_format = QLabel('<font size="4"> Формат </font>')
        format_hbox.addWidget(label_format)
        format_hbox.addWidget(self.format)
        layout.addLayout(format_hbox)

        number_hbox = QHBoxLayout()
        label_number = QLabel('<font size="4"> Количество номеров </font>')
        number_hbox.addWidget(label_number)
        number_hbox.addWidget(self.number)
        layout.addLayout(number_hbox)

        date_hbox = QHBoxLayout()
        label_date = QLabel('<font size="4"> Дата закрытия задания </font>')
        date_hbox.addWidget(label_date)
        date_hbox.addWidget(self.date)
        layout.addLayout(date_hbox)

        if tags:
            self.tag.addItems(tags.keys())

            tag_hbox = QHBoxLayout()
            label_tag = QLabel('<font size="4"> Подгруппа </font>')
            tag_hbox.addWidget(label_tag)
            tag_hbox.addWidget(self.tag)
            layout.addLayout(tag_hbox)

        create_btn = QPushButton('Создать')
        create_btn.clicked.connect(self.on_create_btn_clicked)
        create_btn.setMinimumHeight(30)
        layout.addWidget(create_btn)

        self.setLayout(layout)

    @QtCore.pyqtSlot()
    def on_create_btn_clicked(self):
        if self.name.text() != '':
            if self.tags:
                self.students_ids = \
                    API.get_tag_members(self.class_id, self.tags[self.tag.currentText()])

            date_time = self.date.dateTime().toUTC()
            pool = ThreadPool()
            pool.map(partial(AssignmentsCreation.create_assignments,
                             self.class_id,
                             self.type.currentText(),
                             self.format.currentText(),
                             self.number.value(),
                             date_time.toString(self.date.displayFormat()),
                             self.name.text()), self.students_ids)
            pool.close()
            pool.join()

            self.close()
        else:
            QMessageBox.critical(self, 'Ошибка', 'Название задачи не может быть пустым.')
