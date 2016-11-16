import xml.etree.ElementTree as ET
from xml.dom import minidom

class kml():

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

    def addStyle(self, idStyle, iconfile):
        if idStyle in self.listStyles():
            raise Exception("Styles must be unique. " \
                            "Style with ID %s already present." % idStyle)

        style = ET.Element("Style")
        style.set("id", idStyle)
        icon = ET.Element("Icon")
        href = ET.Element("href")
        href.text = iconfile
        icon.append(href)
        style.append(icon)
        self.styles.append(style)

    def addFolder(self, foldername):
        if foldername in self.listFolders():
            raise Exception("Folder %s already created." % folder)

        folder = ET.Element("Folder")
        folder.set("id", str(foldername))
        name = ET.Element("name")
        name.text = foldername
        folder.append(name)
        self.folders.append(folder)

    def addPoint(self, folder, name, style, coords, fieldData):
        # folder - Name of the folder to organise the placemarks
        # name - Name of the placemark to be displayed with symbol
        # style - Style for the placemark (Must be added before)
        # coords - Tuple with (Longitude,Latitude)
        # fieldData - a dictionary with schemas filled with tuples
        #             e.g. {"schema1": [("id", 1), ("altitude", 300)]}

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
        pnt = ET.Element("Point")
        crd = ET.Element("coordinates")
        crd.text = "%s,%s" % coords
        pnt.append(crd)

        placemark.append(pname)
        placemark.append(styleUrl)
        placemark.append(extData)
        placemark.append(pnt)

        folder.append(placemark)
        self.folders[fInd] = folder

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
