import sys
from PyQt4 import Qt, QtCore, QtGui

from mapview import MapGraphicsView


POINTS = [(44.837632, 10.201736),
          (44.837621, 10.201474),
          (44.837594, 10.201205),
          (44.837558, 10.200954),
          (44.837528, 10.200715),
          (44.837501, 10.200464),
          (44.837473, 10.200212),
          (44.837437, 10.199949),
          (44.837390, 10.199687),
          (44.837340, 10.199453),
          (44.837297, 10.199205),
          (44.837244, 10.198961),
          (44.837186, 10.198719),
          (44.837130, 10.198492),
          (44.837076, 10.198255),
          (44.837012, 10.198013),
          (44.836951, 10.197785),
          (44.836875, 10.197554),
          (44.836797, 10.197321),
          (44.836720, 10.197089),
          (44.836641, 10.196857),
          (44.836554, 10.196610),
          (44.836468, 10.196377),
          (44.836382, 10.196144),
          (44.836257, 10.195911),
          (44.836167, 10.195688),
          (44.836072, 10.195474),
          (44.835972, 10.195254),
          (44.835867, 10.195032),
          (44.835764, 10.194817),
          (44.835679, 10.194624),
          (44.835570, 10.194426),
          (44.835457, 10.194223),
          (44.835341, 10.194014),
          (44.835196, 10.193864),
          (44.835078, 10.193683),
          (44.834959, 10.193495),
          (44.834845, 10.193302),
          (44.834724, 10.193118),
          (44.834596, 10.192943),
          (44.834460, 10.192766),
          (44.834327, 10.192593),
          (44.834200, 10.192429),
          (44.834065, 10.192293),
          (44.833928, 10.192140),
          (44.833793, 10.191997),
          (44.833653, 10.191842),
          (44.833520, 10.191694),
          (44.833388, 10.191560),
          (44.833248, 10.191425),
          (44.833100, 10.191291),
          (44.832954, 10.191164),
          (44.832810, 10.191037)]


class MapZoom(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        view = MapGraphicsView()

        self.setCentralWidget(view)

        nightModeAction = QtGui.QAction("&Night Mode", self)
        nightModeAction.setCheckable(True)
        nightModeAction.setChecked(False)
        osmAction = QtGui.QAction("&About OpenStreetMap", self)
        #nightModeAction.triggered.connect(self.map.toggleNightMode)
        osmAction.triggered.connect(self.aboutOsm)

        menu = self.menuBar().addMenu("&Options")
        menu.addSeparator()
        menu.addAction(nightModeAction)
        menu.addAction(osmAction)

        view.scene().setCenter(44.861041, 10.065990)
        pointItem = view.scene().addEllipse(10.068640, 44.860767, 5.0)
        pointItem.setBrush(Qt.Qt.black)

        for p in POINTS:
            pointItem = view.scene().addEllipse(p[1], p[0], 5.0)
            pointItem.setBrush(Qt.Qt.black)

        lineItem = view.scene().addLine(10.191037, 44.832810, 10.201736, 44.837632)
        lineItem.setPen(Qt.Qt.blue)

        #self.map.addLines(POINTS, width=4, color=Qt.Qt.red)

    def aboutOsm(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://www.openstreetmap.org"))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("TileMap")

    w = MapZoom()
    w.setWindowTitle("OpenStreetMap")

    if False:
        w.showMaximized()
    else:
        w.resize(800, 600)
        w.show()

    sys.exit(app.exec_())
