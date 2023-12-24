import time, sys
from PyQt5.QtWidgets import QDialogButtonBox, QDialog, QMainWindow, QGridLayout, QTextEdit, QLineEdit, QWidget, \
    QMessageBox, QApplication, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal, QBasicTimer
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
import json
from Astar import point
from Astar import A_Search
from  config import config


class GameBoard(QMainWindow):  # 可视化类，pyqt5进行编写。
    def __init__(self):
        print('初始化地图...')
        self.Map = []
        for i in range(config.HEIGHT):
            col = []
            for j in range(config.WIDTH):
                col.append(0)
            self.Map.append(col)
        self.startPoint = None
        self.endPoint = None
        self.search = None
        self.centerTimer = None
        self.yi = None
        self.special = None
        self.displayFlush = False
        #标记地图是否更新
        self.changed = [[False for _ in range(config.WIDTH)] for _ in range(config.HEIGHT)]
        super().__init__()
        print('初始化UI...')
        self.initUI()

    def initUI(self):
        # 开始初始化UI部分
        # 创建UI控件
        self.label_tips = QLabel(
            "<p style='color:green'>使用说明：</p>右键单击格子选定起始点,左键格子选定格子为墙壁或删除墙壁。\n<p style='color:green'>颜色说明：</p>\n黄色代表起点，绿色代表终点，黑色代表墙壁，红色代表待搜索的open列表，灰色代表已搜索过的close列表，蓝色代表当前搜索到的路径",
            self)
        self.label_display = QLabel("", self)
        self.button_start = QPushButton("开始搜索", self)
        self.button_clearSE = QPushButton("重选起始点", self)
        self.button_clearWall = QPushButton("清空地图墙壁", self)
        self.button_saveMap = QPushButton("保存地图", self)
        self.button_loadMap = QPushButton("加载地图", self)

        # 设置控件属性
        self.label_tips.setWordWrap(True)
        self.label_display.setWordWrap(True)
        # 设置控件样式
        self.label_display.setStyleSheet("border:1px solid black")
        self.label_display.setAlignment(Qt.AlignLeft)
        self.label_display.setAlignment(Qt.AlignTop)
        # 设置控件的尺寸和位置
        #上方描述
        self.label_tips.resize(200, 150)
        self.button_saveMap.resize(80, 30)
        self.button_loadMap.resize(80, 30)
        #下方描述
        self.label_display.resize(200, 300)

        self.label_tips.move(100 + (config.WIDTH - 1) * config.blockLength, 0)
        self.label_display.move(100 + (config.WIDTH - 1) * config.blockLength, 400)
        self.button_start.move(100 + (config.WIDTH - 1) * config.blockLength, 200)
        self.button_clearSE.move(100 + (config.WIDTH - 1) * config.blockLength, 250)
        self.button_clearWall.move(100 + (config.WIDTH - 1) * config.blockLength, 300)
        self.button_saveMap.move(100 + (config.WIDTH - 1) * config.blockLength, 350)
        self.button_loadMap.move(200 + (config.WIDTH - 1) * config.blockLength, 350)
        # 给控件绑定事件
        self.button_start.clicked.connect(self.button_StartEvent)
        self.button_clearSE.clicked.connect(self.button_Clear)
        self.button_clearWall.clicked.connect(self.button_Clear)
        self.button_saveMap.clicked.connect(self.button_SaveMap)
        self.button_loadMap.clicked.connect(self.button_LoadMap)
        # UI初始化完成
        self.setGeometry(0, 0, 150 + (config.WIDTH * config.blockLength - config.blockLength) + 200,
                         150 + (config.HEIGHT * config.blockLength - config.blockLength))
        self.setMinimumSize(150 + (config.WIDTH * config.blockLength - config.blockLength) + 200,
                            150 + (config.HEIGHT * config.blockLength - config.blockLength))
        self.setMaximumSize(150 + (config.WIDTH * config.blockLength - config.blockLength) + 200,
                            150 + (config.HEIGHT * config.blockLength - config.blockLength))
        self.setWindowTitle('地图')
        self.show()

    def addDisplayText(self, text):
        if self.displayFlush:
            self.label_display.setText(text + '\n')
            self.displayFlush = False
        else:
            self.label_display.setText(self.label_display.text() + text + '\n')

    def mousePressEvent(self, event):
        x, y = event.x() - 50, event.y() - 50
        x = x // config.blockLength
        y = y // config.blockLength
        if x >= 0 and x < config.WIDTH and y >= 0 and y < config.HEIGHT:
            #左键
            if event.button() == Qt.LeftButton:
                if (x, y) != self.startPoint and (x, y) != self.endPoint:
                    self.Map[y][x] = (1 if self.Map[y][x] == 0 else 0)
            #鼠标右键
            if event.button() == Qt.RightButton:
                if self.Map[y][x] == 0:
                    if self.startPoint == None:
                        self.startPoint = (x, y)
                        self.addDisplayText('添加了一个起点:(%d,%d)' % (x, y))
                    elif self.endPoint == None and self.startPoint != (x, y):
                        self.endPoint = (x, y)
                        self.addDisplayText('添加了一个终点:(%d,%d)' % (x, y))
            self.repaint()

    def button_StartEvent(self):
        sender = self.sender()
        print(sender)
        if self.startPoint != None and self.endPoint != None:
            if self.centerTimer == None:
                self.centerTimer = QBasicTimer()
            self.button_start.setEnabled(False)
            self.button_clearSE.setEnabled(False)
            self.button_clearWall.setEnabled(False)
            self.centerTimer.start(10, self)

            #启动函数
            #传入起始点，目标点，地图
            self.search = A_Search(point(self.startPoint[1], self.startPoint[0]),
                                   point(self.endPoint[1], self.endPoint[0]), self.Map)
            #启动搜索
            self.yi = self.search.process()
            self.addDisplayText('开始进行搜索')

    def button_SaveMap(self):
        with open('map.txt', 'w') as f:
            f.write(json.dumps(self.Map))
            self.addDisplayText('地图保存成功-->map.txt')

    # else:
    # self.addDisplayText('地图保存失败')
    def button_LoadMap(self):
        try:
            with open('map.txt', 'r') as f:
                self.Map = json.loads(f.read())
                config.HEIGHT = len(self.Map)
                config.WIDTH = len(self.Map[0])
                self.addDisplayText('地图加载成功')
                #重绘
                self.repaint()
        except Exception as e:
            print('失败', e, type(e))
            if type(e) == FileNotFoundError:
                self.addDisplayText('地图加载失败:地图文件不存在')
            elif type(e) == json.decoder.JSONDecodeError:
                self.addDisplayText('地图加载失败:错误的地图文件')

    def button_Clear(self):
        sender = self.sender()
        print(self.button_clearSE, type(self.button_clearSE))
        if sender == self.button_clearSE:
            self.startPoint = None
            self.endPoint = None
            self.repaint()
            self.addDisplayText('清空起始点')
        elif sender == self.button_clearWall:
            for i in range(len(self.Map)):
                for j in range(len(self.Map[i])):
                    self.Map[i][j] = 0
            self.repaint()
            self.addDisplayText('清空所有墙壁')

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawBoard(event, qp)
        qp.end()

    def drawBoard(self, event, qp):
        self.drawMap(qp)

    def drawMap(self, qp):  # 画面绘制方法，每次地图有所改动都将重绘
        time1 = time.time()
        if self.search != None:
            if self.special != None:
                e = self.special[0]
                path = [e]
                while True:
                    e = e.father
                    if e != None:
                        path.append(e)
                    else:
                        break
            else:
                path = None
            pen = QPen(QColor(0, 0, 0), 1, Qt.SolidLine)
            qp.setPen(pen)
            for i in range(len(self.Map)):
                for j in range(len(self.Map[i])):
                    wordTag = False
                    #起点颜色
                    if i == self.search.start.x and j == self.search.start.y:
                        qp.setBrush(QColor(255, 255, 0))
                    #终点颜色
                    elif i == self.search.end.x and j == self.search.end.y:
                        qp.setBrush(QColor(100, 200, 50))
                    else:
                        if self.Map[i][j] == 0:
                            tagx = True
                            if path:
                                for k in path:
                                    #路径颜色
                                    if k.x == i and k.y == j:
                                        tagx = False
                                        qp.setBrush(QColor(0, 100, 255))
                            if tagx:
                                if self.special != None:
                                    if i == self.special[0].x and j == self.special[0].y:
                                        qp.setBrush(QColor(0, 255, 0))
                                    else:
                                        tag = True
                                        for k in self.special[1]:
                                            if k.x == i and k.y == j:
                                                tag = False
                                                wordTag = True
                                                #记录F值
                                                word = str(k.F)

                                                qp.setBrush(QColor(150, 0, 0))
                                                break
                                            else:
                                                qp.setBrush(QColor(220, 220, 220))
                                        if tag:
                                            for k in self.special[2]:
                                                if k.x == i and k.y == j:
                                                    qp.setBrush(QColor(150, 150, 150))
                                                    break
                                                else:
                                                    qp.setBrush(QColor(220, 220, 220))
                                else:
                                    qp.setBrush(QColor(220, 220, 220))
                        elif self.Map[i][j] == 1:
                            qp.setBrush(QColor(0, 0, 0))
                        else:
                            qp.setBrush(QColor(255, 0, 0))
                    qp.drawRect(50 + j * config.blockLength, 50 + i * config.blockLength, config.blockLength,
                                config.blockLength)
                    if wordTag:
                        qp.setFont(QFont('楷体', 5, QFont.Light))
                        #绘制F值
                        qp.drawText(50 + 10 + j * config.blockLength, 50 + 10 + i * config.blockLength, word)
                        wordTag = False
        # time.sleep(20)
        else:
            for i in range(len(self.Map)):
                for j in range(len(self.Map[i])):
                    if (j, i) == self.startPoint:
                        qp.setBrush(QColor(255, 255, 0))
                    elif (j, i) == self.endPoint:
                        qp.setBrush(QColor(100, 200, 50))
                    else:
                        if self.Map[i][j] == 0:
                            qp.setBrush(QColor(220, 220, 220))
                        elif self.Map[i][j] == 1:
                            qp.setBrush(QColor(0, 0, 0))
                        else:
                            qp.setBrush(QColor(255, 0, 0))

                    qp.drawRect(50 + j * config.blockLength, 50 + i * config.blockLength, config.blockLength,
                                config.blockLength)
        time2 = time.time()

    # time.sleep(20)
    # print('绘制时间：',time2-time1)
    def timerEvent(self, e):
        try:
            start_time = time.time()
            data = next(self.yi)
            end_time = time.time()
            elapsed_time = end_time - start_time
            # 转换为毫秒
            elapsed_time_ms = elapsed_time * 1000
            print("本次消耗",elapsed_time, "毫秒")
        except Exception as e:
            self.addDisplayText('搜索结束:')
            print('搜索结束！')
            if self.search.result == None:
                self.addDisplayText('未找到可行路径')
                print('搜索结束！')
            else:
                self.addDisplayText('总计搜索节点数：%d' % self.search.count)
                #self.addDisplayText(self.search.result)
                self.addDisplayText('最终路径长度：%d' % len(self.search.result))
            self.centerTimer.stop()
            self.search = None
            self.yi = None
            self.special = None
            point.clear()
            self.button_start.setEnabled(True)
            self.button_clearSE.setEnabled(True)
            self.button_clearWall.setEnabled(True)
            self.displayFlush = True
        else:
            self.special = data
            self.repaint()


