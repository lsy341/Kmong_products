import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QSettings

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("이전 데이터 불러오기 예제")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.text_input = QLineEdit(self)
        layout.addWidget(self.text_input)

        load_button = QPushButton("불러오기", self)
        load_button.clicked.connect(self.load_data)
        layout.addWidget(load_button)

        save_button = QPushButton("저장하기", self)
        save_button.clicked.connect(self.save_data)
        layout.addWidget(save_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_data(self):
        settings = QSettings("myapp", "mysettings")
        saved_text = settings.value("text", "")
        self.text_input.setText(saved_text)

    def save_data(self):
        settings = QSettings("myapp", "mysettings")
        text_to_save = self.text_input.text()
        settings.setValue("text", text_to_save)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
