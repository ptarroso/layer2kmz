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
import xml.etree.ElementTree as ET
from xml.dom import minidom

class kml():
    """ creates a kml doc from geographic content """

    def __init__(self, name, version=1.0, encoding="utf-8",
                 namespace="http://www.opengis.net/kml/2.2"):

        self.docname = str(name)
        self.xmlver = version
        self.encoding = encoding
        self.namespace = namespace
        self.schemas = []
        self.styles = []
        self.folders = []

    def addSchema(self, idSchema, fieldnames, types):
        # idSchema - id ref for the schema
        # fieldnames - a list of names to add to schema
        # types - a list of type for each name

        if len(fieldnames) != len(types):
            raise Exception("'fieldnames' and 'types' must have same length!")

        if idSchema in self.listSchemas():
            raise Exception("Schemas must be unique. " \
                            "Schema with ID %s already present." % idSchema)

        schema = ET.Element("Schema")
        schema.set("name", "")
        schema.set("id", idSchema)
        #self.schemas.append(idSchema)

        for i in range(len(fieldnames)):
            if types[i].lower() not in ["string", "float"]:
                raise Exception("types must be string or float!")
            field = ET.Element("SimpleField")
            field.set("name", fieldnames[i])
            field.set("type", types[i])
            schema.append(field)

        self.schemas.append(schema)

    def addStyle(self, idStyle, **kwargs):
        ## Add a new style, trying to guess from kwargs if it is
        ## an icon, line or polygon
        ## icon - needs "iconfile = str"
        ## line - needs either "color = HEX" or "width = int"
        ## polygon - needs either "fill = HEX" or "outline = Bool"

        if idStyle in self.listStyles():
            raise Exception("Styles must be unique. " \
                            "Style with ID %s already present." % idStyle)
        if kwargs.keys() == []:
            raise Exception("The function need more arguments to create a " \
                            "style. Available args are 'iconfile' for icon " \
                            "style, 'color' and 'width' for line style, and " \
                            "'fill' and 'outline' for poygon style")

        style = ET.Element("Style")
        style.set("id", idStyle)

        linetest = ["color", "width"]
        polytest = ["fill", "outline"]

        if "iconfile" in kwargs.keys():
            style.append(self._addIconSty(kwargs["iconfile"]))
        if any(i in kwargs.keys() for i in linetest):
            try:
                line = self._addLineSty(kwargs["color"], kwargs["width"])
            except KeyError, e:
                e = linetest.pop(linetest.index(e.args[0]))
                line = self._addLineSty(kwargs[linetest[0]])
            style.append(line)
        if any(i in kwargs.keys() for i in polytest):
            try:
                poly = self._addPolySty(kwargs["fill"], kwargs["outline"])
            except KeyError, e:
                e = polytest.pop(polytest.index(e.args[0]))
                poly = self._addPolySty(kwargs[polytest[0]])
            style.append(poly)

        self.styles.append(style)

    def _addIconSty(self, iconfile):
        icon = ET.Element("Icon")
        href = ET.Element("href")
        href.text = iconfile
        icon.append(href)
        return(icon)

    def _addLineSty(self, color, width = 1):
        ## color is hexadecimal string
        line = ET.Element("LineStyle")
        colorl = ET.Element("color")
        colorl.text = color
        widthl = ET.Element("width")
        widthl.text = str(width)
        line.append(colorl)
        line.append(widthl)
        return(line)

    def _addPolySty(self, fill = None, outline = False):
        ## color is hexadecimal string
        poly = ET.Element("PolyStyle")
        if fill is not None:
            colorp = ET.Element("color")
            colorp.text = fill
            poly.append(colorp)
            fillp = ET.Element("fill")
            fillp.text = "1"
            poly.append(fillp)
        outlp = ET.Element("outline")
        if outline is True:
            outlp.text = "1"
        else:
            outlp.text = "0"
        poly.append(outlp)
        return(poly)

    def addFolder(self, foldername):
        if foldername in self.listFolders():
            raise Exception("Folder %s already created." % folder)

        folder = ET.Element("Folder")
        folder.set("id", str(foldername))
        name = ET.Element("name")
        name.text = foldername
        folder.append(name)
        self.folders.append(folder)

    def addPlacemark(self, folder, name, style, coords, fieldData):
        # folder - Name of the folder to organise the placemarks
        # name - Name of the placemark to be displayed with symbol
        # style - Style for the placemark (Must be added before)
        # coords - It can be either a tuple specifying a point, a list of
        #          coordinate tuples specifying a line or a list of lists of
        #          coordinate tuples, where the first element is the outer
        #          polygon and subsequent elements define inner polygons (i.e.
        #          holes). The coordinate tuple for any shape must have two
        #          elements, a Longitude and a Latitude value in that order. If
        #          a third element if given in the coordinates tuple it is
        #          interpreted as altitude.
        #          Examples
        #           Point:
        #            (Lon1,Lat1)
        #           Line:
        #            [(lon1,lat1), (lon2, lat2), ...]
        #           Polygon:
        #            [[(lon1,lat1, (lon2,lat2), ...], [(lon1, lat1), ...], ...]
        # fieldData - A dictionary with schemas filled with tuples
        #             example: {"schema1": [("id", 1), ("altitude", 300)]}

        if style not in self.listStyles():
            raise Exception("Style %s must be added before a " \
                            "placemark using it." % (style))

        for schema in fieldData.keys():
            if schema not in self.listSchemas():
                raise Exception("Schema %s must be added before a " \
                                "placemark using it." % (schema))
            for field in [x[0] for x in fieldData[schema]]:
                if field not in self.listFields(schema):
                    raise Exception("Field %s must be added to schema %s " \
                                    "before a placemark using it." \
                                    % (field, schema))

        folder = str(folder)
        name = str(name)

        if folder not in self.listFolders():
            self.addFolder(folder)

        fInd = self.listFolders().index(folder)
        folder = self.folders[fInd]

        placemark = ET.Element("Placemark")
        pname = ET.Element("name")
        pname.text = name
        styleUrl = ET.Element("styleUrl")
        styleUrl.text = "#%s" % style
        extData = ET.Element("ExtendedData")
        for schema in fieldData.keys():
            schemaUrl = ET.Element("SchemaData")
            schemaUrl.set("schemaUrl", schema)
            for fdata in fieldData[schema]:
                sData = ET.Element("SimpleData")
                sData.set("name", fdata[0])
                sData.text = fdata[1]
                schemaUrl.append(sData)
            extData.append(schemaUrl)

        if isinstance(coords, tuple):
            crd = self._addPoint(coords)
        elif isinstance(coords, list):
            if isinstance(coords[0], tuple):
                crd = self._addLine(coords)
            elif isinstance(coords[0], list):
                crd = self._addPolygon(coords)
        else:
            raise Exception("'coords' must be a tuple or a list.")

        placemark.append(pname)
        placemark.append(styleUrl)
        placemark.append(extData)
        placemark.append(crd)

        folder.append(placemark)
        self.folders[fInd] = folder

    def _addPoint(self, coordinates):
        fmt = ",".join(["%s" for x in coordinates])
        pnt = ET.Element("Point")
        crd = ET.Element("coordinates")
        crd.text = fmt % coordinates
        pnt.append(crd)
        return(pnt)

    def _addLine(self, coordinates, tessellate = True):
        fmt = ",".join(["%s" for x in coordinates[0]])
        line = ET.Element("LineString")
        tess = ET.Element("tessellate")
        tess.text = str(int(tessellate))
        crd = ET.Element("coordinates")
        crd.text = " ".join([fmt % tuple(x) for x in coordinates])
        line.append(tess)
        line.append(crd)
        return(line)

    def _addPolygon(self, coordinates, tessellate = True):
        fmt = ",".join(["%s" for x in coordinates[0][0]])
        poly = ET.Element("Polygon")
        tess = ET.Element("tessellate")
        tess.text = str(int(tessellate))
        poly.append(tess)
        outBound = ET.Element("outerBoundaryIs")
        lRing = ET.Element("LinearRing")
        crd = ET.Element("coordinates")
        crd.text = " ".join([fmt % tuple(x) for x in coordinates[0]])
        lRing.append(crd)
        outBound.append(lRing)
        poly.append(outBound)

        if len(coordinates) > 1:
            for iPoly in coordinates[1:]:
                inBound = ET.Element("innerBoundaryIs")
                lRing = ET.Element("LinearRing")
                crd = ET.Element("coordinates")
                crd.text = " ".join([fmt % tuple(x) for x in iPoly])
                lRing.append(crd)
                inBound.append(lRing)
                poly.append(inBound)
        return(poly)

    def listStyles(self):
        #returns a list of available styles IDs
        sty = self.styles
        return([y[1] for x in sty for y in x.items() for z in y if z == "id"])

    def listSchemas(self):
        #returns a list of available schemas IDs
        sch = self.schemas
        return([y[1] for x in sch for y in x.items() for z in y if z == "id"])

    def listFields(self, schema):
        #returns a list of available fields in schemas
        sch = list(self.schemas[self.listSchemas().index(schema)])
        res = [y[1] for x in sch for y in x.items() for z in y if z == "name"]
        return(res)

    def listFolders(self):
        #returns a list of available folders names
        fld = self.folders
        return([y[1] for x in fld for y in x.items() for z in y if z == "id"])

    def generatekml(self):
        root = ET.Element("kml")
        root.set("xmlns", self.namespace)
        doc = ET.Element("Document")
        name = ET.Element("name")
        name.text = self.docname
        doc.append(name)
        for schema in self.schemas:
            doc.append(schema)
        for style in self.styles:
            doc.append(style)
        for folder in self.folders:
            doc.append(folder)
        root.append(doc)
        kmlstr = minidom.parseString(ET.tostring(root))
        return kmlstr.toprettyxml(indent="    ")
