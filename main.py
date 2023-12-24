from gameboard import GameBoard
from Astar import point
from Astar import A_Search
import time, sys
from PyQt5.QtWidgets import QDialogButtonBox, QDialog, QMainWindow, QGridLayout, QTextEdit, QLineEdit, QWidget, \
    QMessageBox, QApplication, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal, QBasicTimer
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
import json
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GameBoard()
    sys.exit(app.exec_())
