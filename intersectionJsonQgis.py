import os
from getpass import getuser
from json import dumps
import sys
import shapefile
new_path = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '.', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder/extlibs', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis2web', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms', '/home/bisag/Documents/qgisCode']
for i in new_path:
    sys.path.append(i)
import qgis
from qgis.core import *    

from PyQt5.QtWidgets import QApplication, QWidget
from qgis.core import QgsVectorLayer,QgsProject,QgsApplication, QgsGeometry, QgsFeature, QgsSymbol,QgsLayerTreeLayer, QgsSingleSymbolRenderer, QgsDataSourceUri,QgsCoordinateReferenceSystem



from flask import Flask,request,jsonify

app = Flask(__name__)

cwd = os.getcwd()


# import processing
# from processing.core.Processing import Processing
from qgis import processing
from qgis.analysis import QgsNativeAlgorithms
import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())


output_folder = cwd+'/static/intersectionLayer/'

output_shapefile= output_folder+'intersectionLine.shp'

@app.route("/", methods=['GET', 'POST'])
def rail_road_api():


    # path1 = request.args.get("path1")
    # path2 = request.args.get("path2")

    # json1 = {
    #     "path1": path1,
    #     "path2": path2
    # }

    # resp = jsonify(json1)
    # print(json1)
    #Processing.initialize()
    # Processing.updateAlgsList()

    processing.run("native:lineintersections",

        {'INPUT':output_folder+'Canal_updated_F.shp',
        'INTERSECT':output_folder+'road_clear.shp',
        'INPUT_FIELDS':[],
        'INTERSECT_FIELDS':[],
        'INTERSECT_FIELDS_PREFIX':'',
        'OUTPUT':output_shapefile})
    #convert geojson using python

    reader = shapefile.Reader(output_shapefile)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []

    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        buffer.append(dict(type="Feature", \
        geometry=geom, properties=atr)) 

    # write the GeoJSON file
    geojson = open(output_folder+"intersection.geojson", "w")
    geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
    geojson.close()

    # geojson = dumps('''{"type": "FeatureCollection", "features": '''+buffer+'''}''')
    # print(str(geojson))

    # print("success::")

    #data = json.loads(strinjJson)

    #return "<h4>"+str(geojson)+"</h4>"
    return str(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")


if __name__ == "__main__":
    app.run(debug=True)
