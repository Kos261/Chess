import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QDialog

class Widget1(QDialog):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.label = QLabel("Wprowadź parametr:")
        self.edit = QLineEdit()
        self.button = QPushButton("Otwórz Widget2")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.openWidget2)

    def openWidget2(self):
        param_value = self.edit.text()

        # Zamknij bieżące okno
        self.accept()

        # Otwórz Widget2 z przekazanymi parametrami
        widget2 = Widget2(param_value)
        widget2.exec_()

class Widget2(QDialog):
    def __init__(self, param_value):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.label = QLabel(f"Parametr z Widget1: {param_value}")
        self.button = QPushButton("Zamknij")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.accept)

def main():
    app = QApplication(sys.argv)

    widget1 = Widget1()
    widget1.exec_()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
