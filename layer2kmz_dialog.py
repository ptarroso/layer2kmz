# -*- coding: utf-8 -*-
"""
/***************************************************************************
 layer2kmz
                                 A QGIS plugin
 Build a kmz from a layer of spatial points, lines or polygons
                              -------------------
        begin                : 2016-02-02
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Pedro Tarroso
        email                : ptarroso@cibio.up.pt
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; version 2 of the License.               *
 *                                                                         *
 ***************************************************************************/
"""
import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5 import QtCore

from qgis.core import QgsProject, Qgis

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'layer2kmz_dialog_base.ui'))


class layer2kmzDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(layer2kmzDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.outputButton.clicked.connect(self.outFile)
        self.layerCombo.currentIndexChanged.connect(self.updateFields)

    def outFile(self):
        # Show the file dialog for output
        self.outputLine.clear()
        fileDialog = QtWidgets.QFileDialog()
        outFileName = fileDialog.getSaveFileName(self, "Save as", ".",
                                                 "kmz (*.kmz)")[0]
        if outFileName:
            if outFileName[-4:].lower() != ".kmz":
                outFileName += ".kmz"
            self.outputLine.clear()
            self.outputLine.insert(outFileName)

    def getVectorLayer(self):
        return(str(self.layerCombo.currentText()))

    def getLabel(self):
        return(str(self.labelCombo.currentText()))

    def getFolder(self):
        return(str(self.folderCombo.currentText()))

    def getExports(self):
        selected = self.exportList.selectedItems()
        exports = [item.text() for item in selected]
        return(exports)

    def getOutFile(self):
        return(self.outputLine.text())

    def updateLayerCombo(self, items):
        if len(items) > 0:
            self.layerCombo.clear()
            for item in items:
                self.layerCombo.addItem(item)

    def updateFields(self):
        layer = self.getVectorLayer()
        if layer != "":
            layerTree = QgsProject.instance().layerTreeRoot().findLayers()
            allLayers = [lyr.layer() for lyr in layerTree]
            allLyrNames = [lyr.name() for lyr in allLayers]
            if layer in allLyrNames:
                lyr = allLayers[allLyrNames.index(layer)]
                fields = lyr.fields()
                self.labelCombo.clear()
                self.folderCombo.clear()
                self.exportList.clear()
                for f in fields:
                    self.labelCombo.addItem(f.name())
                    self.folderCombo.addItem(f.name())
                    self.exportList.addItem(f.name())

    def setProgressBar(self, main, text, maxVal=100):
        self.widget = self.iface.messageBar().createMessage(main, text)
        self.prgBar = QtWidgets.QProgressBar()
        self.prgBar.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.prgBar.setValue(0)
        self.prgBar.setMaximum(maxVal)
        self.widget.layout().addWidget(self.prgBar)
        self.iface.messageBar().pushWidget(self.widget, Qgis.Info)

    def showMessage(self, main, txt):
        self.widget.setTitle(main)
        self.widget.setText(txt)

    def ProgressBar(self, value):
        self.prgBar.setValue(value)
        if (value == self.prgBar.maximum()):
            self.iface.messageBar().clearWidgets()
            self.iface.mapCanvas().refresh()

    def warnMsg(self, main, text):
        self.warn = self.iface.messageBar().createMessage(main, text)
        self.iface.messageBar().pushWidget(self.warn, Qgis.Warning)
        
    def errorMsg(self, main, text):
        self.warn = self.iface.messageBar().createMessage(main, text)
        self.iface.messageBar().pushWidget(self.warn, Qgis.Critical)
