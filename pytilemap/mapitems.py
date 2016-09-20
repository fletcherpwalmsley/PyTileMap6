from __future__ import print_function, absolute_import

import numpy as np

from PyQt4.Qt import Qt
from PyQt4.QtCore import QLineF, QPointF, QRectF
from PyQt4.QtGui import QGraphicsEllipseItem, QGraphicsLineItem, \
    QGraphicsPathItem, QPainterPath, QGraphicsPixmapItem, \
    QGraphicsSimpleTextItem, QGraphicsItem, QGraphicsRectItem, \
    QGraphicsLineItem, QGraphicsItemGroup, QPen, QBrush, QColor

from .functions import getQVariantValue, iterRange, makePen, izip

SolidLine = Qt.SolidLine


class MapItem(object):
    """Base class for each item in the MapGraphicScene

    The default implementation connects the MapGraphicScene.sigZoomChanged() signal
    to the MapItem.setZoom() slot. This slot call the MapItem.updatePosition() method
    for updating the position of the item in reaction to a change in the zoom level.
    """

    QtParentClass = None

    def __init__(self):
        if not isinstance(self, QGraphicsItem):
            raise RuntimeError('MapItem must be an instance of QGraphicsItem')

    def itemChange(self, change, value):
        if change == self.ItemSceneChange:
            # Disconnect the old scene, if any
            oldScene = self.scene()
            if oldScene is not None:
                oldScene.sigZoomChanged.disconnect(self.setZoom)
            # Connect the new scene, if any
            if value is not None:
                newScene = getQVariantValue(value)
                newScene.sigZoomChanged.connect(self.setZoom)
                # Setup the new position of the item
                self.updatePosition(newScene)
        return self.QtParentClass.itemChange(self, change, value)

    def setZoom(self, zoom):
        '''Set a new zoom level.

        Args:
            zoom (int): The new zoom level.
        '''
        scene = self.scene()
        self.updatePosition(scene)

    def updatePosition(self, scene):
        raise NotImplementedError()


class MapGraphicsCircleItem(QGraphicsEllipseItem, MapItem):
    """Circle item for the MapGraphicsScene
    """

    QtParentClass = QGraphicsEllipseItem

    def __init__(self, longitude, latitude, radius, parent=None):
        """Constructor.

        Args:
            longitude(float): Longitude of the center of the circle.
            latitude(float): Latitude of the center of the circle.
            radius(float): Radius of the circle in pixels.
            scene(MapGraphicsScene): Scene to which the circle belongs.
            parent(QGraphicsItem): Parent item, default None.

        Note:
            The management of the parent item is work in progress.
        """
        QGraphicsEllipseItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._lon = longitude
        self._lat = latitude
        self._radius = radius

        d = self._radius * 2
        self.setRect(0, 0, d, d)

    def updatePosition(self, scene):
        """Update the position of the circle.

        Args:
            scene(MapGraphicsScene): Scene to which the circle belongs.
        """
        pos = scene.posFromLonLat(self._lon, self._lat)
        r = self._radius
        self.prepareGeometryChange()
        self.setPos(pos[0] - r, pos[1] - r)

    def setLonLat(self, longitude, latitude):
        """Set the center coordinates of the circle.

        Args:
            longitude(float): Longitude of the center of the circle.
            latitude(float): Latitude of the center of the circle.
        """
        self._lon = longitude
        self._lat = latitude
        scene = self.scene()
        if scene is not None:
            self.updatePosition(scene)


class MapGraphicsRectItem(QGraphicsRectItem, MapItem):
    """Circle item for the MapGraphicsScene
    """

    QtParentClass = QGraphicsRectItem

    def __init__(self, lon0, lat0, lon1, lat1, parent=None):
        """Constructor.

        Args:
            lon0(float): Longitude of the top left point.
            lat0(float): Latitude of the top left point.
            lon1(float): Longitude of the bottom right point.
            lat1(float): Latitude of the bottom right point.
            parent(QGraphicsItem): Parent item, default None.

        Note:
            The management of the parent item is work in progress.
        """
        QGraphicsRectItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1

    def updatePosition(self, scene):
        """Update the position of the circle.

        Args:
            scene(MapGraphicsScene): Scene to which the circle belongs.
        """
        pos0 = scene.posFromLonLat(self._lon0, self._lat0)
        pos1 = scene.posFromLonLat(self._lon1, self._lat1)

        self.prepareGeometryChange()
        rect = QRectF(pos0, pos1).normalized()
        self.setRect(rect)
        self.setPos(QPointF(0.0, 0.0))

    def setLonLat(self, lon0, lat0, lon1, lat1):
        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1
        scene = self.scene()
        if scene is not None:
            self.updatePosition(self.scene())


class MapGraphicsLineItem(QGraphicsLineItem, MapItem):

    QtParentClass = QGraphicsLineItem

    def __init__(self, lon0, lat0, lon1, lat1, parent=None):
        QGraphicsLineItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1

    def updatePosition(self, scene):
        pos0 = scene.posFromLonLat(self._lon0, self._lat0)
        pos1 = scene.posFromLonLat(self._lon1, self._lat1)
        deltaPos = QPointF(pos1[0] - pos0[0], pos1[1] - pos0[1])

        self.prepareGeometryChange()
        self.setLine(QLineF(QPointF(0.0, 0.0), deltaPos))
        self.setPos(pos0[0], pos0[1])

    def setLonLat(self, lon0, lat0, lon1, lat1):
        self._lon0 = lon0
        self._lat0 = lat0
        self._lon1 = lon1
        self._lat1 = lat1
        scene = self.scene()
        if scene is not None:
            self.updatePosition(self.scene())


class MapGraphicsPolylineItem(QGraphicsPathItem, MapItem):

    QtParentClass = QGraphicsPathItem

    def __init__(self, longitudes, latitudes, parent=None):
        QGraphicsPathItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        assert len(longitudes) == len(latitudes)

        self._longitudes = np.array(longitudes, dtype=np.float32)
        self._latitudes = np.array(latitudes, dtype=np.float32)

    def updatePosition(self, scene):
        path = QPainterPath()

        self.prepareGeometryChange()

        count = len(self._longitudes)
        if count > 0:
            x, y = scene.posFromLonLat(self._longitudes, self._latitudes)
            dx = x - x[0]
            dy = y - y[0]
            for i in iterRange(1, count):
                path.lineTo(dx[i], dy[i])
            self.setPos(x[0], y[0])

        self.setPath(path)

    def setLonLat(self, longitudes, latitudes):
        assert len(longitudes) == len(latitudes)

        self._longitudes = np.array(longitudes, dtype=np.float32)
        self._latitudes = np.array(latitudes, dtype=np.float32)
        scene = self.scene()
        if scene is not None:
            self.updatePosition(scene)


class MapGraphicsPixmapItem(QGraphicsPixmapItem, MapItem):
    """Item for showing a pixmap in a MapGraphicsScene.
    """

    QtParentClass = QGraphicsPixmapItem

    def __init__(self, longitude, latitude, pixmap, parent=None):
        """Constructor.

        Args:
            longitude(float): Longitude of the origin of the pixmap.
            latitude(float): Latitude of the center of the pixmap.
            pixmap(QPixmap): Pixmap.
            scene(MapGraphicsScene): Scene the item belongs to.
            parent(QGraphicsItem): Parent item.
        """
        QGraphicsPixmapItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        self._lon = longitude
        self._lat = latitude
        self.setPixmap(pixmap)

    def updatePosition(self, scene):
        """Update the origin position of the item.

        Origin coordinates are unchanged.

        Args:
            scene(MapGraphicsScene): Scene the item belongs to.
        """
        pos = scene.posFromLonLat(self._lon, self._lat)
        self.prepareGeometryChange()
        self.setPos(pos[0], pos[1])

    def setLonLat(self, longitude, latitude):
        """Update the origin coordinates of the item.

        Origin position will be updated.

        Args:
            longitude(float): Longitude of the origin of the pixmap.
            latitude(float): Latitude of the center of the pixmap.
        """
        self._lon = longitude
        self._lat = latitude
        scene = self.scene()
        if scene is not None:
            self.updatePosition(scene)


class MapGraphicsTextItem(QGraphicsSimpleTextItem, MapItem):
    """Text item for the MapGraphicsScene
    """

    QtParentClass = QGraphicsSimpleTextItem

    def __init__(self, longitude, latitude, text, parent=None, min_zoom_visibility=None):
        QGraphicsSimpleTextItem.__init__(self, text, parent=parent)
        MapItem.__init__(self)
        self._min_zoom = min_zoom_visibility
        self._lon, self._lat = longitude, latitude

    def resetMinZoomVisibility(self):
        """Delete level of zoom under which the text disappears. """
        self._min_zoom = None

    def setMinZoomVisibility(self, zoom_level):
        """Update level of zoom under which the text disappears. """
        self._min_zoom = zoom_level

    def updatePosition(self, scene):
        """Update the origin position of the item."""

        pos = scene.posFromLonLat(self._lon, self._lat)
        self.setPos(pos)
        if self._min_zoom is not None:
            self.setVisible(scene._zoom >= self._min_zoom)


class MapGraphicsLinesGroupItem(QGraphicsItem, MapItem):

    QtParentClass = QGraphicsItem

    def __init__(self, longitudes, latitudes, parent=None):
        QGraphicsItem.__init__(self, parent=parent)
        MapItem.__init__(self)

        assert len(longitudes) == len(latitudes)
        assert len(longitudes) >= 2

        self._longitudes = np.array(longitudes, dtype=np.float32)
        self._latitudes = np.array(latitudes, dtype=np.float32)

        # Setup internal lines
        linesGroup = QGraphicsItemGroup(parent=self)
        self._linesGroup = linesGroup
        self._lines = [QGraphicsLineItem(parent=linesGroup) for i in iterRange(len(longitudes)-1)]

    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return self._linesGroup.boundingRect()

    def setLineStyle(self, colors, width=1., style=SolidLine):
        pen = makePen(colors, width=width, style=style)

        if isinstance(pen, list):
            if len(pen) != len(self._lines):
                raise ValueError('The number of colors must be equal to the number of lines')
            for line, p in izip(self._lines, pen):
                line.setPen(p)
        else:
            for line in self._lines:
                line.setPen(pen)

    def updatePosition(self, scene):
        self.prepareGeometryChange()

        x, y = scene.posFromLonLat(self._longitudes, self._latitudes)
        lines = self._lines
        for i in iterRange(0, len(lines)-1):
            lines[i].setLine(x[i], y[i], x[i+1], y[i+1])

    def setLonLat(self, longitudes, latitudes):
        assert len(longitudes) == len(latitudes)
        assert len(longitudes) >= 2

        self._longitudes = np.array(longitudes, dtype=np.float32)
        self._latitudes = np.array(latitudes, dtype=np.float32)

        old_lines = self._lines
        for line in old_lines:
            line.setParentItem(None)

        scene = self.scene()
        if scene is not None:
            for line in old_lines:
                scene.removeItem(line)

        linesGroup = self._linesGroup
        self._lines = [QGraphicsLineItem(parent=linesGroup) for i in iterRange(len(longitudes)-1)]

        if scene is not None:
            self.updatePosition(scene)

    def __getitem__(self, index):
        return self._lines[index]
