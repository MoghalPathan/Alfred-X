import sys
import subprocess
from PyQt5.QtWidgets import *

class AlfredLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alfred X Launcher")
        self.setGeometry(300, 200, 400, 200)

        btn = QPushButton("🚀 Start Alfred X", self)
        btn.setGeometry(100, 60, 200, 60)
        btn.clicked.connect(self.start_alfred)

    def start_alfred(self):
        subprocess.Popen(["python", "main.py"])

app = QApplication(sys.argv)
win = AlfredLauncher()
win.show()
sys.exit(app.exec_())