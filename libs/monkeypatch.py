import contextlib

from routingpy import utils
import kivy_garden.mapview.view


def __decode_polyline5__(polyline, is3d=False, order="latlng"):
    """Decodes an encoded polyline string which was encoded with a precision of 6.

    :param polyline: An encoded polyline, only the geometry.
    :type polyline: str

    :param is3d: Specifies if geometry contains Z component. Currently only GraphHopper and OpenRouteService
        support this. Default False.
    :type is3d: bool

    :param order: Specifies the order in which the coordinates are returned.
                  Options: latlng, lnglat. Defaults to 'lnglat'.
    :type order: str

    :returns: List of decoded coordinates with precision 6.
    :rtype: list
    """

    return utils._decode(polyline, precision=5, is3d=is3d, order=order)


# Monkey patch routingpy.utils.decode_polyline5
utils.decode_polyline5 = __decode_polyline5__


def set_source(self, cache_fn):
    with contextlib.suppress(Exception):
        self.source = cache_fn
        self.state = "need-animation"


# Monkey patch Tile.set_source
kivy_garden.mapview.view.Tile.set_source = set_source
