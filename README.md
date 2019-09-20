# Layer2KMZ

Layer2KMZ is a plug-in for QGIS (version >= 3.0; http://www.qgis.org). It allows
the conversion between spatial layers (points, lines or polygons) to a KMZ file.
It exports the symbology as shown in QGIS but, at the moment, it only works with
simple or categorized styles.

The purpose of this plug-in was to facilitate the creation of a KMZ file for a
fast visualization of organized data in Google Earth and to export to other devices
like tablets using a KMZ compatible software. Other QGIS plug-ins allow more
advanced interaction with Google Earth (check GEarthView, for instance).

## Features

The Layer2KMZ plug-in allows to:

* Export data to KMZ
* Use the QGIS symbology (single or categorized)
* Choose an attribute field to group data in folders
* Choose an attribute field to display labels associated with each feature.

## Installation

### QGIS plugin manager

The Layer2KMZ is in the QGIS plugin repository. Using the plugin manager inside
QGIS, search layer2kmz and install.

### Manual install

Download the files to your computer into a folder layer2kmz. Copy this folder to
the plug-in folder of your QGIS user profile. You can find your user profile 
folder in QGIS menu "Settings -> User Profiles" ([check also QGIS manuals](https://docs.qgis.org/testing/en/docs/user_manual/plugins/plugins.html#core-and-external-plugins) for more details).
In QGIS, activate the layer2kmz in the plug-in manager.
