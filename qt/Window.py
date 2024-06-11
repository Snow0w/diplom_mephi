from PyQt6.QtWidgets import (
    QMessageBox,
    QFileDialog,
    QComboBox,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
)
from Classifier import Classifier
from WrongDataException import WrongDataException
from ClassificationReportException import ClassificationReportException


class Window(QWidget):
    def __init__(self):
        self.__WORK_WITH_SERVER_STATE = 1
        super().__init__()
        self.fileName = ""
        self.setWindowTitle("Классификация частиц")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.pageCombo = QComboBox()
        self.pageCombo.addItems(["Локальный файл", "Сервер"])
        self.pageCombo.activated.connect(self.switchPage)
        self.stackedLayout = QStackedLayout()
        self.page1 = QWidget()
        self.page1Layout = QVBoxLayout()
        self.page1Button = QPushButton("Выбрать файл")
        self.page1Button.clicked.connect(self.page1button_was_clicked)
        self.page1Label = QLabel("Выбранный файл: ")
        self.page1Layout.addWidget(self.page1Button)
        self.page1Layout.addWidget(self.page1Label)
        self.page1.setLayout(self.page1Layout)
        self.stackedLayout.addWidget(self.page1)
        self.page2 = QWidget()
        self.page2Layout = QVBoxLayout()
        self.page2Button = QPushButton("Подключиться к серверу")
        self.page2Button.clicked.connect(self.page2button_was_clicked)
        self.page2Label = QLabel("Статус: не подключено")
        self.page2Layout.addWidget(self.page2Button)
        self.page2Layout.addWidget(self.page2Label)
        self.page2.setLayout(self.page2Layout)
        self.stackedLayout.addWidget(self.page2)
        mainLabel = QLabel("Источник:")
        layout.addWidget(mainLabel)
        layout.addWidget(self.pageCombo)
        layout.addLayout(self.stackedLayout)
        self.classifierButton = QPushButton("Классифицировать")
        self.classifierButton.clicked.connect(self.classifierButton_was_clicked)
        layout.addWidget(self.classifierButton)
        self.classifierReportButton = QPushButton("Классифицировать с отчетом")
        self.classifierReportButton.clicked.connect(self.classifierReportButton_was_clicked)
        layout.addWidget(self.classifierReportButton)
        
    def classifierButton_was_clicked(self):
        if self.pageCombo.currentIndex() == self.__WORK_WITH_SERVER_STATE:
            self.errorDialog("Ошибка", "Данный функционал не поддерживается")
            return
        if self.fileName == "":
            self.errorDialog("Ошибка", "Не выбран файл")
            return
        try:
            classifier = Classifier(self.fileName)
            classifier.classification()
            self.errorDialog("Готово", "Классификация успешно выполнена")
        except WrongDataException as ex:
            self.errorDialog("Ошибка", str(ex))
        except OSError as ex:
            self.errorDialog("Ошибка", str(ex))
        except Exception as ex:
            self.errorDialog("Ошибка", str(ex))

    def classifierReportButton_was_clicked(self):
        if self.pageCombo.currentIndex() == self.__WORK_WITH_SERVER_STATE:
            self.errorDialog("Ошибка", "Данный функционал не поддерживается")
            return
        if self.fileName == "":
            self.errorDialog("Ошибка", "Не выбран файл")
            return
        try:
            classifier = Classifier(self.fileName)
            classifier.classification_with_report()
            self.errorDialog("Готово", "Классификация успешно выполнена")
        except WrongDataException as ex:
            self.errorDialog("Ошибка", str(ex))
        except OSError as ex:
            self.errorDialog("Ошибка", str(ex))
        except ClassificationReportException as ex:
            self.errorDialog("Ошибка", str(ex))
        except Exception as ex:
            self.errorDialog("Ошибка", str(ex))


    def page1button_was_clicked(self):
        try:
            self.fileName = QFileDialog.getOpenFileName(self)[0]
            self.page1Label.setText("Выбранный файл: " + self.fileName)
        except Exception as ex:
            self.fileName = ""
            self.errorDialog("Ошибка", str(ex))

    def page2button_was_clicked(self):
        self.errorDialog("Ошибка", "Данный функционал не поддерживается")

    def errorDialog(self, name, text):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(name)
        dlg.setText(text)
        dlg.exec()

    def switchPage(self):
        self.stackedLayout.setCurrentIndex(self.pageCombo.currentIndex())

