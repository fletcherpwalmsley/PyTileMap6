from __future__ import print_function, absolute_import

from qtpy.QtCore import Qt, Signal, Slot, QObject, QByteArray
from qtpy.QtGui import QPixmap

from .maptilesource import MapTileSource
import grequests
import os
import threading
import copy

class MapTileHTTPLoader(QObject):

    tileLoaded = Signal(int, int, int, QByteArray)
    fetchBundleDone = Signal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self._tileInDownload = dict()
        self._grs = list()
        self._grs_keys = list()
        self._grs_bundles = list()
        self._threadlock = threading.Lock()

    # @Slot(int, int, int, str)
    def asyncLoadTile(self, x, y, zoom, url):
        url = f"https://basemaps.linz.govt.nz/v1/tiles/aerial/WebMercatorQuad/{zoom}/{x}/{y}.jpeg?api=c01hj0qr6shwmem3jazjgqvrzsc"
        key = (x, y, zoom)
        if key in self._tileInDownload:
            print(f"In memory {key[0]}/{key[1]}/{key[2]}.jpeg")
            self.tileLoaded.emit(key[0], key[1], key[2], self._tileInDownload[key])
        elif os.path.isfile(f"tiles/{key[0]}/{key[1]}/{key[2]}.jpeg"):
            print(f"On disk: {key[0]}/{key[1]}/{key[2]}.jpeg")
            with open(f"tiles/{key[0]}/{key[1]}/{key[2]}.jpeg", 'rb') as f:
                self._tileInDownload[key] = f.read()
                self.tileLoaded.emit(key[0], key[1], key[2], self._tileInDownload[key])
        else:
            print(f"Requesting: {key[0]}/{key[1]}/{key[2]}.jpeg")
            self._grs.append(grequests.get(url))
            self._grs_keys.append(key)

    def fetch_tile(self):
        # Return the requested images from remote server
        while len(self._grs_bundles) > 0:
            keys, grs = self._grs_bundles.pop(0)
            responses = grequests.map(grs)
            for key, response in zip(keys, responses):
                self._tileInDownload[key] = response.content
                write_path = f"tiles/{key[0]}/{key[1]}/"
                os.makedirs(write_path, exist_ok=True)
                with open(f"{write_path}{key[2]}.jpeg", 'wb') as f:
                    f.write(response.content)
                self.tileLoaded.emit(key[0], key[1], key[2], self._tileInDownload[key])
            self.fetchBundleDone.emit()

    def bundle_requests(self):
        assert len(self._grs_keys) == len(self._grs)
        self._grs_bundles.append(
                (
                    copy.deepcopy(self._grs_keys), copy.deepcopy(self._grs)
                )
            )
        self._grs.clear()
        self._grs_keys.clear()

    @Slot()
    def asyncFetchTile(self):
        self.bundle_requests()
        if self._threadlock.locked():
            return
        else:
            with self._threadlock:
                if len(self._grs_bundles) > 0:
                    thread = threading.Thread(target=self.fetch_tile)
                    thread.start()

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
        self._loader.fetchBundleDone.connect(self.requestRedraw)

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
        self.tileReceived.emit(x, y, zoom, pix)

    @Slot()
    def requestRedraw(self):
        self.redrawNeeded.emit()

    def abortAllRequests(self):
        self._loader.abortAllRequests()

    def imageFormat(self):
        return 'jpg'
