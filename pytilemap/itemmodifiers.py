from typing import Optional
import numpy as np

from qtpy.QtWidgets import QGraphicsItem

from mapitems import MapGraphicsPoint
from mapitems import MapGraphicsPolyline

class RouteManager(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._routes = dict()

    def add_route(self, route_id: str):
        self._routes[route_id]

    def add_point_to_route(self, route_id: str, point: MapGraphicsPoint):
        if route_id not in self._routes:
            raise ValueError(f"Route {route_id} does not exist")
        self._routes[route_id].append(point)


class PolylineMover():
    def __init__(self, polyline: MapGraphicsPolyline) -> None:
        self.poly_under_change = polyline
        self.lats, self.lons = polyline.get_lat_lon()