from __future__ import print_function, absolute_import

from qtpy.QtCore import Qt, Signal, Slot, QObject, QByteArray, QUrl, QThread
from qtpy.QtGui import QPixmap

from .maptilesource import MapTileSource
import grequests


class MapTileHTTPLoader(QObject):

    tileLoaded = Signal(int, int, int, QByteArray)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self._tileInDownload = dict()
        self._grs = list()
        self._gps_keys = list()
        self._local_keys = list()

    @Slot(int, int, int, str)
    def asyncLoadTile(self, x, y, zoom, url):
        url = f"https://basemaps.linz.govt.nz/v1/tiles/aerial/WebMercatorQuad/{zoom}/{x}/{y}.jpeg?api=c01hj0qr6shwmem3jazjgqvrzsc"
        key = (x, y, zoom)
        if key not in self._tileInDownload:
            self._grs.append(grequests.get(url))
            self._gps_keys.append(key)
        else:
            self.tileLoaded.emit(key[0], key[1], key[2], self._tileInDownload[key])



    @Slot()
    def asyncFetchTile(self):
        # Return the requested images from remote server
        if len(self._grs) > 0:
            responses = grequests.map(self._grs)
            for key, response in zip(self._gps_keys, responses):
                self._tileInDownload[key] = response.content
                self.tileLoaded.emit(key[0], key[1], key[2], self._tileInDownload[key])
            self._grs.clear()
            self._gps_keys.clear()


    @Slot()
    def abortRequest(self, x, y, zoom):
        # p = (x, y, zoom)
        # if p in self._tileInDownload:
            # reply = self._tileInDownload[p]
            # del self._tileInDownload[p]
        #     reply.close()
        #     reply.deleteLater()
        print("Aborting requests")
        # self._grs.clear()
        # self._gps_keys.clear()

    @Slot()
    def abortAllRequests(self):
        # for x, y, zoom in list(self._tileInDownload.keys()):
        #     self.abortRequest(x, y, zoom)
        pass


class MapTileSourceHTTP(MapTileSource):

    def __init__(self, tileSize=256, minZoom=2, maxZoom=21, mapHttpLoader=None, parent=None):
        MapTileSource.__init__(self, tileSize=tileSize, minZoom=minZoom, maxZoom=maxZoom, parent=parent)

        if mapHttpLoader is not None:
            self._loader = mapHttpLoader
        else:
            self._loader = MapTileHTTPLoader()

        self._loader.tileLoaded.connect(self.handleTileDataLoaded)

    @Slot()
    def close(self):
        self._loader.abortAllRequests()

    def url(self, x, y, zoom):
        raise NotImplementedError()

    def requestTile(self, x, y, zoom):
        url = self.url(x, y, zoom)
        self._loader.loadTile(x, y, zoom, url)

    def asyncLoadTiles(self, x, y, zoom):
        url = self.url(x, y, zoom)
        self._loader.asyncLoadTile(x, y, zoom, url)

    def asyncRequestTiles(self):
        self._loader.asyncFetchTile()

    @Slot(int, int, int, QByteArray)
    def handleTileDataLoaded(self, x, y, zoom, data):
        pix = QPixmap()
        pix.loadFromData(data)
        print(f"Got {x}/{y}/{zoom}")
        self.tileReceived.emit(x, y, zoom, pix)

    def abortAllRequests(self):
        self._loader.abortAllRequests()

    def imageFormat(self):
        return 'PNG'
