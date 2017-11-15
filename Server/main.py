from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt)
from PyQt5.QtGui import (QBrush, QColor, QPainter)
from PyQt5.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene,
    QGraphicsItem, QGridLayout, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton
)
import sys

class Main(QGraphicsItem):
    def __init__(self):
        super(Main, self).__init__()

    def boundingRect(self):
        return QRectF(0, 0, 800, 600)

    def paint(self, painter, option, widget):
        return

    def mousePressEvent(self, event):
        pos = event.pos()
        self.update()
        super(Main, self).mousePressEvent(event)

class MainWindow(QGraphicsView):
    def __init__(self):
        super(MainWindow, self).__init__()
        scene = QGraphicsScene(self)
        self.main = Main()
        scene.addItem(self.main)
        scene.setSceneRect(0, 0, 800, 600)
        self.setScene(scene)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setWindowTitle("Siulator server")

    def keyPressEvent(self, event):
        key = event.key()
        super(MainWindow, self).keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    mainWindow.show()
    sys.exit(app.exec_())
