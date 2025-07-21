import sys
import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

class ClassB(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.button = QPushButton('Click me', self)
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.button.clicked.connect(self.onButtonClicked)

    def onButtonClicked(self):
        # 이 버튼 클릭 핸들러는 ClassB의 GUI 위젯에서 실행됨
        print('Button clicked in ClassB')

class WorkerThread(QThread):
    finished = pyqtSignal()

    def run(self):
        # ClassA에서 이 스레드를 사용하여 ClassB의 GUI 위젯에 접근
        time.sleep(2)  # 시뮬레이션을 위한 대기 시간
        self.finished.emit()

class ClassA(QWidget):
    def __init__(self, class_b_instance):
        super().__init__()
        self.classB = class_b_instance
        self.initUI()

    def initUI(self):
        self.button = QPushButton('Start Worker Thread', self)
        self.button.clicked.connect(self.startWorkerThread)
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)

    def startWorkerThread(self):
        worker = WorkerThread()
        worker.finished.connect(self.workerFinished)
        worker.start()

    def workerFinished(self):
        # ClassB의 GUI 위젯에 접근하지 않고 작업을 완료하는 신호 처리
        print('Worker thread finished')
        self.classB.button.setText('Work Finished')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    classB = ClassB()
    classA = ClassA(classB)

    classB.show()
    classA.show()

    sys.exit(app.exec_())
