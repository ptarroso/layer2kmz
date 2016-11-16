# -*- coding: utf-8 -*-
"""
/***************************************************************************
 layer2kmz
                                 A QGIS plugin
 A quick & dirty plugin to build a kmz from a layer of spatial points
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
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import QAction, QIcon, QColor
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from layer2kmz_dialog import layer2kmzDialog
import os.path
import tempfile
import zipfile
from kml import kml


def createSymbol(imgname, symbol):
    # Exports a QGIS symbol to png, using a QGIS canvas
    # imgname - string for a image file name with path
    # symbol - a symbol of class QgsMarkerSymbolV2
    # Only works to point symbols!

    ## adds 'png' extension to 'imgname' if missing
    if imgname[-4:].lower() != ".png":
        imgname += ".png"

    ## Create a in memory vector layer with a point at (1,1)
    vl = QgsVectorLayer("Point?crs=epsg:4326", "symbols", "memory")
    pr = vl.dataProvider()
    vl.startEditing()
    fet = QgsFeature()
    geo = QgsGeometry.fromPoint(QgsPoint(1,1))
    fet.setGeometry(geo)
    pr.addFeatures([fet])
    vl.commitChanges()
    vl.updateExtents()

    ## Adds the "symbol" to the layer
    rnd = vl.rendererV2()
    rnd.setSymbol(symbol)

    ## Register the layer without showing
    newlyr= QgsMapLayerRegistry.instance().addMapLayer(vl, False)

    ## Starts a new canvas, centers to vl and exports to png
    canvas = QgsMapCanvas()
    ## Transparent background
    color = QColor(255, 255, 255, 0)
    canvas.setCanvasColor(color)
    canvas.enableAntiAliasing(True)
    canvas.setExtent(QgsRectangle(0.5,0.5,1.5,1.5))
    canvas.setLayerSet([QgsMapCanvasLayer(vl)])
    settings = canvas.mapSettings()
    settings.setOutputSize(QSize(30,30)) ## output png size 30x30
    job = QgsMapRendererSequentialJob(settings)
    job.start()
    job.waitForFinished()
    img = job.renderedImage()
    img.save(imgname,"png")

    ## Unregister the layer
    #QgsMapLayerRegistry.instance().removeMapLayer(newlyr.id())

class layer2kmz:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'layer2kmz_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = layer2kmzDialog(iface)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&layer2kmz')
        # TODO: We are going to let the user set this up in a future iteration
        if self.iface.pluginToolBar():
            self.toolbar = self.iface.pluginToolBar()
        else:
            self.toolbar = self.iface.addToolBar(u'layer2kmz')
        self.toolbar.setObjectName(u'layer2kmz')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('layer2kmz', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/layer2kmz/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Layer to KMZ'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&layer2kmz'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""

        # Update combos
        layers = self.iface.legendInterface().layers()
        pntLayers = [lyr for lyr in layers if lyr.type() == 0 and lyr.geometryType() == 0]
        self.dlg.updateLayerCombo([lyr.name() for lyr in pntLayers])

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            layerName = self.dlg.getVectorLayer()
            labelFld = self.dlg.getLabel()
            folderFld = self.dlg.getFolder()
            exportFld = self.dlg.getExports()
            outFile = self.dlg.getOutFile()

            # Get the layer object from active layers
            canvas = self.iface.mapCanvas()
            shownLayers = [x.name() for x in canvas.layers()]
            layer = canvas.layer(shownLayers.index(layerName))

            if layerName not in shownLayers:
                self.dlg.warnMsg("Species table not found or active!", layerName)
            elif outFile == "":
                self.dlg.errorMsg("Choose an output kmz file!", "")

            elif exportFld== []:
                self.dlg.errorMsg("At least one field to export must be selected.", "")
            else:
                self.dlg.setProgressBar("Processing", "", 100)

                kmlproc = kmlprocess(layer, labelFld, folderFld, exportFld,
                                  outFile, self.dlg.ProgressBar)
                kmlproc.process()


class kmlprocess():
    def __init__(self, layer, label, folder, exports, outFile, prg):
        self.layer = layer
        self.label = label
        self.folder = folder
        self.exports = exports
        self.styleField = None
        self.outFile = outFile
        self.tmpDir = tempfile.gettempdir()
        self.progress = prg

    def processLayer(self):
        lyr = self.layer
        self.counter = lyr.featureCount() + 1
        lyrFields = [f.name() for f in lyr.pendingFields()]
        expFieldInd = [lyrFields.index(f) for f in self.exports]
        iter = lyr.getFeatures()
        fldInd = lyrFields.index(self.folder)
        lblInd = lyrFields.index(self.label)

        ## If there is a style field, save a list of style for each feature
        if self.styleField is not None:
            styles = []
            styInd = lyrFields.index(self.styleField)

        ## Process all features
        data = []
        featFolder = []
        coords = []
        labels = []
        pg = 0
        for feature in iter:
            self.updateProgress(pg)
            # note: converting everything to string!
            data.append([str(feature.attributes()[i]) for i in expFieldInd])
            featFolder.append(str(feature.attributes()[fldInd]))
            labels.append(str(feature.attributes()[lblInd]))
            coords.append(feature.geometry().asPoint())
            if self.styleField is not None:
                styles.append(str(feature.attributes()[styInd]))
            pg += 1

        self.coords = coords
        self.data = data
        self.featFolder = featFolder
        self.labels = labels
        if self.styleField is not None:
            self.featStyles = styles

    def getStyles(self):
        lyr = self.layer
        rnd = lyr.rendererV2()
        styles = []
        if rnd.type() == u'categorizedSymbol':
            styleField = rnd.classAttribute()
            self.styleField = styleField
            for cat in rnd.categories():
                name = str(cat.value())
                symb = cat.symbol()
                imgname = "color_%s.png" % name
                createSymbol(os.path.join(self.tmpDir, imgname), symb)
                styles.append([name, imgname])
        elif rnd.type() == u'singleSymbol':
            symb = rnd.symbol()
            imgname = "color_style.png"
            createSymbol(os.path.join(self.tmpDir, imgname), symb)
            styles.append(["style", imgname])
        else:
            self.error.emit("Symbology must be single or categorized.")
            self.finished.emit(False)

        self.styles = styles

    def updateProgress(self, i):
        progress = int(i / float(self.counter) * 100)
        self.progress(progress)

    def process(self):
        self.getStyles()
        self.processLayer()
        Kml = kml(self.layer.name())
        types = ["string" for x in self.exports]
        Kml.addSchema(self.layer.name(), self.exports, types)

        for item in self.styles:
            Kml.addStyle(item[0], item[1])

        style = self.styles[0][0]
        for i in range(len(self.data)):
            folder = self.featFolder[i]
            name = self.labels[i]
            coords = tuple(self.coords[i])
            if self.styleField is not None:
                style = self.featStyles[i]
            fields = {}
            fields[self.layer.name()] = zip(self.exports, self.data[i])
            Kml.addPoint(folder, name, style, coords, fields)

        tmpKml = os.path.join(self.tmpDir, "doc.kml")
        fstream = open(tmpKml, "w")
        fstream.writelines(Kml.generatekml())
        fstream.close()

        z = zipfile.ZipFile(self.outFile, "w")
        z.write(tmpKml, arcname="doc.kml")
        for filename in [x[1] for x in self.styles]:
            filename = os.path.join(self.tmpDir, filename)
            z.write(filename, arcname=os.path.basename(filename))
        z.close()

        self.updateProgress(self.counter)