# -*- coding: utf-8 -*-
"""
/***************************************************************************
 layer2kmz
                                 A QGIS plugin
 A quick & dirty plugin to build a kmz from a layer of spatial points
                             -------------------
        begin                : 2016-11-08
        copyright            : (C) 2016 by Pedro Tarroso
        email                : ptarroso@cibio.up.pt
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load layer2kmz class from file layer2kmz.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .layer2kmz import layer2kmz
    return layer2kmz(iface)
