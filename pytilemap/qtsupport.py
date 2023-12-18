
import sys
# import sip

import qtpy


__all__ = [
    'getQVariantValue',
    'wheelAngleDelta',
]


try:
    if qtpy.PYQT5 or qtpy.PYSIDE6:
        QVARIANT_API = 2
    else:
        QVARIANT_API = 1
except ValueError:
    QVARIANT_API = 1


if QVARIANT_API == 1:
    def getQVariantValue(variant):
        return variant.toPyObject()
else:
    def getQVariantValue(variant):
        return variant

if qtpy.PYQT5 or qtpy.PYSIDE6:
    def wheelAngleDelta(wheelEvent):
        return wheelEvent.angleDelta().y()
else:
    def wheelAngleDelta(wheelEvent):
        return wheelEvent.delta()


if qtpy.PYQT5 or qtpy.PYSIDE6:
    from qtpy.QtCore import QStandardPaths

    def getCacheFolder():
        return QStandardPaths.writableLocation(QStandardPaths.CacheLocation)

else:
    from qtpy.QtGui import QDesktopServices

    def getCacheFolder():
        return QDesktopServices.storageLocation(QDesktopServices.CacheLocation)
