# -*- coding: utf-8 -*-
"""
/***************************************************************************
 layer2kmz
                                 A QGIS plugin
 Build a kmz from a layer of spatial points, lines or polygons
                              -------------------
        begin                : 2016-11-08
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
from PyQt4 import QtGui, uic, QtCore

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'layer2kmz_dialog_base.ui'))


class layer2kmzDialog(QtGui.QDialog, FORM_CLASS):
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
        fileDialog = QtGui.QFileDialog()
        outFileName = fileDialog.getSaveFileName(self, "Save as", ".",
                                                 "kmz (*.kmz)")
        if outFileName:
            if outFileName[-4:].lower() != ".kmz":
                outFileName += ".kmz"
            self.outputLine.clear()
            self.outputLine.insert(outFileName)

    def getVectorLayer(self):
        return(unicode(self.layerCombo.currentText()))

    def getLabel(self):
        return(unicode(self.labelCombo.currentText()))

    def getFolder(self):
        return(unicode(self.folderCombo.currentText()))

    def getExports(self):
        exports = []
        count = self.exportList.count()
        for i in range(0, count):
            item = self.exportList.item(i)
            if self.exportList.isItemSelected(item):
                exports.append(item.text())
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
            allLayers = self.iface.legendInterface().layers()
            allLyrNames = [lyr.name() for lyr in allLayers]
            if layer in allLyrNames:
                lyr = allLayers[allLyrNames.index(layer)]
                fields = lyr.pendingFields()
                self.labelCombo.clear()
                self.folderCombo.clear()
                self.exportList.clear()
                for f in fields:
                    self.labelCombo.addItem(f.name())
                    self.folderCombo.addItem(f.name())
                    self.exportList.addItem(f.name())

    def setProgressBar(self, main, text, maxVal=100):
        self.widget = self.iface.messageBar().createMessage(main, text)
        self.prgBar = QtGui.QProgressBar()
        self.prgBar.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.prgBar.setValue(0)
        self.prgBar.setMaximum(maxVal)
        self.widget.layout().addWidget(self.prgBar)
        self.iface.messageBar().pushWidget(self.widget,
                                           self.iface.messageBar().INFO)

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
        self.iface.messageBar().pushWidget(self.warn,
                                           self.iface.messageBar().WARNING)
    def errorMsg(self, main, text):
        self.warn = self.iface.messageBar().createMessage(main, text)
        self.iface.messageBar().pushWidget(self.warn,
                                           self.iface.messageBar().CRITICAL)
