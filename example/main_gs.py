import sys

from qtpy.QtCore import Qt
from qtpy.QtGui import QPainter, QColor, QPen, QBrush, QPixmap
from qtpy.QtWidgets import QMainWindow, QGraphicsView, QGraphicsItem, \
    QGraphicsSimpleTextItem, QApplication

from pytilemap import MapGraphicsView, MapTileSourceHere, MapTileSourceOSM


POINTS = [(172.61, -43.501),
          (172.62, -43.502),
          (172.64, -43.504),
          (172.603, -43.503),
          (172.605, -43.505),
          (172.606, -43.506),
          (172.607, -43.507),
          (172.608, -43.508),
          (172.609, -43.509),
          (172.610, -43.510),
          (172.611, -43.511),
          (172.612, -43.512),
          (172.613, -43.513),
          (172.614, -43.514),
          (172.615, -43.515)]

POINTS_2 = [(172.6, -43.5), (172.5, -43.4), (172.4, -43.3),
            (172.3, -43.2), (172.2, -43.1), (172.1, -43.0)]
POINTS_2_SIZES = [1, 2, 3, 4, 5]
POINTS_2_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 0, 0)]


class MapZoom(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        view = MapGraphicsView(tileSource=MapTileSourceOSM())

        self.setCentralWidget(view)

        view.scene().setCenter(172.6, -43.5)
        view.setOptimizationFlag(QGraphicsView.DontSavePainterState, True)
        view.setRenderHint(QPainter.Antialiasing, True)
        view.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        pointItem = view.scene().addCircle(172.6, -43.5, 3)
        pointItem.setBrush(Qt.red)
        pointItem.setToolTip('172.6, -43.5')
        pointItem.setFlag(QGraphicsItem.ItemIsSelectable, True)
        pointItem.setZValue(1)
        pointItem.setVisible(True)

        lats = list()
        lons = list()
        for p in POINTS:
            pointItem = view.scene().addCircle(p[0], p[1], 5)
            pointItem.setBrush(Qt.green)
            pointItem.setPen(QPen(Qt.NoPen))
            pointItem.setToolTip('%f, %f' % (p[0], p[1]))
            pointItem.setFlag(QGraphicsItem.ItemIsSelectable, True)
            pointItem.setZValue(1)
            pointItem.setVisible(True)
            lons.append(p[0])
            lats.append(p[1])

        # lineItem = view.scene().addLine(172.6, -43.5, 172.7, -43.6)
        # lineItem.setPen(QPen(QBrush(Qt.blue), 3.0))

        polylineItem = view.scene().addPolyline(lons, lats)
        polylineItem.setPen(QPen(QBrush(Qt.red), 3.0))
        polylineItem.setFlag(QGraphicsItem.ItemIsSelectable, True)

        pix = QPixmap(24, 24)
        pix.fill(Qt.red)
        pixmapItem = view.scene().addPixmap(172.64, -43.54, pix)
        pixmapItem.setOffset(-12, -12)
        pointItemPixmapOrigin = view.scene().addCircle(172.62, -43.52, 3.0)
        pointItemPixmapOrigin.setBrush(Qt.black)

        pointItemWithChild = view.scene().addCircle(172.65, -43.55, 3.0)
        pointItemWithChild.setBrush(Qt.blue)
        pointItemWithChild.setPen(QPen(Qt.NoPen))

        textItem = QGraphicsSimpleTextItem('Annotation\nfor blue point', parent=pointItemWithChild)
        textItem.setBrush(QBrush(QColor(Qt.blue)))
        textItem.setPos(-5, 3)

        lats_2 = list()
        lons_2 = list()
        for p in POINTS_2:
            lons_2.append(p[0])
            lats_2.append(p[1])
        linesGroupItem = view.scene().addLinesGroup(lons_2, lats_2)
        linesGroupItem.setLineStyle(POINTS_2_COLORS, width=POINTS_2_SIZES)

        legendItem = view.scene().addLegend()
        legendItem.addPoint('Point 1', '#FF0000', border=None)
        legendItem.addRect('Rect 2', '#00FF00', border=None)
        legendItem.addPoint('Circle 3', '#0000FF', border=None)
        legendItem.addRect('Sphere 4', '#00FFFF', border=None)
        legendItem.addPoint('Polygon 5', '#FF00FF', border=None)

        scaleItem = view.scene().addScale(anchor=Qt.BottomRightCorner)


def main():
    w = MapZoom()
    w.setWindowTitle("OpenStreetMap")

    w.resize(800, 600)
    w.show()

    return app.exec_()


if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName("TileMap")

    sys.exit(main())
