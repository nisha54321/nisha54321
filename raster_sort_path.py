# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets, QtGui
from qgis.core import Qgis
import subprocess
from datetime import datetime, timedelta

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .raster_path_dialog import RasterPathDialog
import os.path
from qgis import processing
from qgis.core import (
    QgsRasterLayer,
    QgsProject,
    QgsPointXY,
    QgsRaster,
    QgsRasterShader,
    QgsColorRampShader,
    QgsSingleBandPseudoColorRenderer,QgsVectorLayerTemporalProperties,QgsCoordinateReferenceSystem,QgsSvgMarkerSymbolLayer,
    QgsSingleBandColorDataRenderer,
    QgsSingleBandGrayRenderer,QgsVectorLayer, QgsPoint, QgsVectorLayer, QgsFeature, QgsGeometry, QgsVectorFileWriter, QgsField, QgsPalLayerSettings, QgsVectorLayerSimpleLabeling
)
from qgis.gui import QgsMapToolIdentifyFeature, QgsMapToolEmitPoint
from PyQt5 import QtWidgets 
from PyQt5 import QtGui
from qgis.PyQt.QtWidgets import QAction
import re, os.path
from qgis.PyQt.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QWidget, QVBoxLayout, QAction, QLabel, QLineEdit, QMessageBox, QFileDialog, QFrame, QDockWidget, QProgressBar, QProgressDialog, QToolTip
from datetime import timedelta, datetime
from time import strftime
from time import gmtime

class RasterPath:
    """QGIS Plugin Implementation."""
    xy = []
    iii = 0
    vl = ''
    def __init__(self, iface):
        
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RasterPath_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Raster Path')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RasterPath', message)


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
        

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        plugin_dir = os.path.dirname(__file__)
        icon_path = plugin_dir+'/'+'army2.png'
        #icon_path = ':/plugins/raster_path/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Raster shortest path'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Raster Path'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        if self.first_start == True:
            self.first_start = False
            self.dlg = RasterPathDialog()
        
        plugin_dir = os.path.dirname(__file__)

        if(self.iii == 0):
            self.vl = QgsVectorLayer("Point?crs=EPSG:4326", "markpoint", "memory")
            rlayer = QgsRasterLayer(plugin_dir+'/os1_4326.tif', "OS1")
            QgsProject.instance().addMapLayer(rlayer)
            self.iii = 1
        
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))
        #buffer 
        def buffer():
            out_buffer_path = '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/buffer.shp'
            processing.run("native:buffer", {'INPUT':'/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/linestring.shp',
                        'DISTANCE':0.0027027027,
                        'SEGMENTS':5,
                        'END_CAP_STYLE':0,
                        'JOIN_STYLE':0,
                        'MITER_LIMIT':2,
                        'DISSOLVE':False,
                        'OUTPUT':out_buffer_path})
            vlayer = QgsVectorLayer(out_buffer_path, "Buffer", "ogr")
            if not vlayer.isValid():
                print("Layer failed to load!")
            else:
                QgsProject.instance().addMapLayer(vlayer)


        #slope (OS1.tif, os1_4326)
        def slope1():
            processing.run("native:slope", {'INPUT':plugin_dir+'/os1_4326.tif',
                                    'Z_FACTOR':1,
                                    'OUTPUT':plugin_dir+'/OS1_Slope.tif'})
            rlayer = QgsRasterLayer(plugin_dir+'/OS1_Slope.tif', "Slope")
            QgsProject.instance().addMapLayer(rlayer)

            self.dlg.label_reclassify.show()
            self.dlg.pushButton_reclassify.show()

        #reclassify by table
        #89.9997,67.5923
        def reclassifytable():
            processing.run("native:reclassifybytable", {'INPUT_RASTER':plugin_dir+'/OS1_Slope.tif',
                                            'RASTER_BAND':1,
                                            'TABLE':[0,30,1,30,89.9997,2],
                                            'NO_DATA':-9999,
                                            'RANGE_BOUNDARIES':0,
                                            'NODATA_FOR_MISSING':False,
                                            'DATA_TYPE':5,
                                            'OUTPUT':plugin_dir+'/OS1_Reclassify.tif'})

            
            rlayer = QgsRasterLayer(plugin_dir+'/OS1_Reclassify.tif', "Reclassifybytable")
            QgsProject.instance().addMapLayer(rlayer)
            self.iface.messageBar().pushMessage("Please wait ...............", level=Qgis.Info)

            ##background process
            roadrail = []

            name = ["AOI_Rail_","AOI_Road_","AOI_Settlement15000_Buffer500m"]
            s1 = iter(name)

            for file in os.listdir(plugin_dir+"/data/"):
                if file.endswith(".shp"):
                    fpath = os.path.join(plugin_dir+"/data/", file)
                    roadrail.append(fpath)
            #print(roadrail)

            dir = plugin_dir+"/data"
            for input in roadrail:
                yy = next(s1)
                ##addfieldtoattributestable
                processing.run("native:addfieldtoattributestable", 
                                {'INPUT':input,
                                'FIELD_NAME':'value',
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':10,
                                'FIELD_PRECISION':0,
                                'OUTPUT':dir+'/output/%saddfieldtoatttable.shp'%(yy)})
                                
                ##reproject layer
                processing.run("native:reprojectlayer", 
                                {'INPUT':dir+'/output/%saddfieldtoatttable.shp'%(yy),
                                'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:3857'),
                                'OUTPUT':dir+'/output/%sreproject.shp'%(yy)})
                #pointsalonglines
                processing.run("native:pointsalonglines", 
                                {'INPUT':dir+'/output/%sreproject.shp'%(yy),
                                'DISTANCE':500,
                                'START_OFFSET':0,
                                'END_OFFSET':0,
                                'OUTPUT':dir+'/output/%spointAlongGem.shp'%(yy)})

                ##buffervectors 20 meter
                processing.run("gdal:buffervectors", 
                            {'INPUT':dir+'/output/%spointAlongGem.shp'%(yy),
                            'GEOMETRY':'geometry',
                            'DISTANCE':20,
                            'FIELD':'',
                            'DISSOLVE':False,
                            'EXPLODE_COLLECTIONS':True,
                            'OPTIONS':'',
                            'OUTPUT':dir+'/output/%sbuffer20.shp'%(yy)})
                ##clip
                processing.run("native:clip",
                            {'INPUT':dir+'/output/%sreproject.shp'%(yy),
                            'OVERLAY':dir+'/output/%sbuffer20.shp'%(yy),
                            'OUTPUT':dir+'/output/%sclip.shp'%(yy)})

                #fieldcalculator 2
                processing.run("native:fieldcalculator",
                                {'INPUT':dir+'/output/%sclip.shp'%(yy),
                                'FIELD_NAME':'value',
                                'FIELD_TYPE':1,
                                'FIELD_LENGTH':0,
                                'FIELD_PRECISION':0,
                                'FORMULA':'2',
                                'OUTPUT':dir+'/output/%sfieldCalu2.shp'%(yy)})
                #difference
                processing.run("native:difference",
                                {'INPUT':dir+'/output/%sreproject.shp'%(yy),
                                'OVERLAY':dir+'/output/%sbuffer20.shp'%(yy),
                                'OUTPUT':dir+'/output/%sdiffrence.shp'%(yy)})
                
                #fieldcalculator 0   
                processing.run("native:fieldcalculator",
                                {'INPUT':dir+'/output/%sdiffrence.shp'%(yy),
                                'FIELD_NAME':'value',
                                'FIELD_TYPE':1,
                                'FIELD_LENGTH':0,
                                'FIELD_PRECISION':0,
                                'FORMULA':'0',
                                'OUTPUT':dir+'/output/%sfieldcal0.shp'%(yy)})
                                
                #merge
                processing.run("native:mergevectorlayers",
                                {'LAYERS':[dir+'/output/%sfieldcal0.shp'%(yy),dir+'/output/%sfieldCalu2.shp'%(yy)],
                                'CRS':QgsCoordinateReferenceSystem('EPSG:3857'),
                                'OUTPUT':dir+'/output/%smerge.shp'%(yy)})
                
                        
                #buffer 40 meter
                processing.run("native:buffer",
                            {'INPUT':dir+'/output/%smerge.shp'%(yy),
                            'DISTANCE':40,
                            'SEGMENTS':5,
                            'END_CAP_STYLE':1,
                            'JOIN_STYLE':0,
                            'MITER_LIMIT':2,
                            'DISSOLVE':False,
                            'OUTPUT':dir+'/merge/%sFinal_merge.shp'%(yy)})

            ###for settlement and waterbody

            settelementBufferdir = plugin_dir+"/data/waterSattlemnt"

            name = ["waterbody","settlement"]
            s1 = iter(name)

            roadrail1 = []
            for file in os.listdir(settelementBufferdir):
                if file.endswith(".shp"):
                    fpath = os.path.join(settelementBufferdir, file)
                    roadrail1.append(fpath)
            #print(roadrail1)

            dir = plugin_dir+"/data/waterSattlemnt"
            for input in roadrail1:
                yy = next(s1)
                #reprojection
                processing.run("native:addfieldtoattributestable", 
                                    {'INPUT':input,
                                    'FIELD_NAME':'value',
                                    'FIELD_TYPE':0,
                                    'FIELD_LENGTH':10,
                                    'FIELD_PRECISION':0,
                                    'OUTPUT':dir+'/out/%saddfieldtoatttable.shp'%(yy)})

                processing.run("native:reprojectlayer", 
                                {'INPUT':dir+'/out/%saddfieldtoatttable.shp'%(yy),
                                'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:3857'),
                                'OUTPUT':dir+'/out/%s_reprojection.shp'%(yy)})

                processing.run("native:fieldcalculator",
                                {'INPUT':dir+'/out/%s_reprojection.shp'%(yy),
                                'FIELD_NAME':'value',
                                'FIELD_TYPE':1,
                                'FIELD_LENGTH':0,
                                'FIELD_PRECISION':0,
                                'FORMULA':'0',
                                'OUTPUT':dir+'/out/%s_fieldCalu2.shp'%(yy)})
                

                #buffer
                processing.run("native:buffer",
                                {'INPUT':dir+'/out/%s_fieldCalu2.shp'%(yy),
                                'DISTANCE':500,
                                'SEGMENTS':5,
                                'END_CAP_STYLE':0,
                                'JOIN_STYLE':0,
                                'MITER_LIMIT':2,
                                'DISSOLVE':False,
                                'OUTPUT':plugin_dir+"/data/merge/%s_merge.shp"%(yy)})
                            
            ##final merge all files 
            dir1 = plugin_dir+"/data/merge"
            merge = []
            for file in os.listdir(dir1):
                if file.endswith(".shp"):
                    fpath = os.path.join(dir1, file)
                    merge.append(fpath)
            #print(merge)
            processing.run("native:mergevectorlayers",
                            {'LAYERS':merge,
                            'CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                            'OUTPUT':plugin_dir+'/Final_merge_railRoadSettlement.shp'
                            })

            #####finally rasterize data
            processing.run("gdal:rasterize_over",
                {'INPUT':plugin_dir+'/Final_merge_railRoadSettlement.shp',
                'INPUT_RASTER':plugin_dir+'/OS1_Reclassify.tif',
                'FIELD':'value',
                'ADD':False,
                'EXTRA':''})

            print("success background algorithm")

            self.dlg.label_path.show()
            self.dlg.pushButton_path.show()
            
            self.dlg.label_info.show()
            self.iface.messageBar().pushMessage("Please Select Two Points for Shortest Path", level=Qgis.Info)


        point_label = iter(["source", "destination","source", "destination","source", "destination","source", "destination","source", "destination","source", "destination","source", "destination","source", "destination","source", "destination"])

        ##get coordinates of click event
        def display_point( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            print(coorx, coory)
            self.xy.append(coorx)
            self.xy.append(coory)

            #marked points

            #vl = QgsVectorLayer("Point?crs=EPSG:4326", "Point", "memory")
            self.vl.renderer().symbol().setColor(QColor("red"))
            self.vl.renderer().symbol().setSize(4)

            self.vl.triggerRepaint()

            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx, coory)))
            pr = self.vl.dataProvider()

            #Add Attribute
            self.vl.startEditing()
            pr.addAttributes([QgsField("point_label", QVariant.String)])

            x = next(point_label)
            attvalAdd = [x]
            f.setAttributes(attvalAdd)
            self.vl.triggerRepaint()

            pr.addFeature(f)
            self.vl.updateExtents() 
            self.vl.updateFields() 
            QgsProject.instance().addMapLayers([self.vl])

            #set label
            layer_settings  = QgsPalLayerSettings()
            layer_settings.fieldName = "point_label"
            layer_settings.placement = 2
            layer_settings.enabled = True

            layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
            self.vl.setLabelsEnabled(True)
            self.vl.setLabeling(layer_settings)
            self.vl.triggerRepaint()
            self.vl.startEditing()
            self.vl.triggerRepaint()
       
        
        canvas = self.iface.mapCanvas()   
        pointTool = QgsMapToolEmitPoint(canvas)
        pointTool.canvasClicked.connect( display_point )
        canvas.setMapTool( pointTool )
 

        def line1():
            start_point = QgsPoint(self.xy[-4], self.xy[-3])
            end_point = QgsPoint(self.xy[-2], self.xy[-1])
            print("line====  ",self.xy)
            import os

            os.system(f"python3 /home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/shortest_path.py {self.xy[-4]} {self.xy[-3]} {self.xy[-2]} {self.xy[-1]}")
            

            vl = QgsVectorLayer("MultiLineString?crs=EPSG:4326", "Shortest path", "memory")
            vl.renderer().symbol().setColor(QColor("green"))
            vl.renderer().symbol().setWidth(1.06)

            vl.triggerRepaint()
            pr = vl.dataProvider()
            wktdata = ''

            with open("/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/path.txt", 'r') as file_obj:
                wkt1 = file_obj.read().strip()
                multiwkt = wkt1.split(os.linesep)
                
                for wkt in  multiwkt:
                    vl.startEditing()

                    pr = vl.dataProvider()
                    pr.addAttributes([QgsField("length", QVariant.String)])
                    vl.updateFields()

                    feature_obj = QgsFeature()
                    
                    feature_obj.setGeometry(QgsGeometry.fromWkt(wkt))
                    pr.addFeature(feature_obj)
                    
                    x = feature_obj.geometry().length()*100
                    len1 = "%.2f" % x +" km"

            #        print(len1)
                    feature_obj.setAttributes([len1])
                    pr.addFeatures([feature_obj])
                    
                    vl.triggerRepaint()
                    vl.updateExtents() 
                    
                    layer_settings  = QgsPalLayerSettings()
                    layer_settings.fieldName = "length"
                    layer_settings.placement = 2
                    layer_settings.enabled = True

                    layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
                    vl.setLabelsEnabled(True)
                    vl.setLabeling(layer_settings)
                    vl.triggerRepaint()
                    vl.startEditing()
                    vl.commitChanges()
                    QgsProject.instance().addMapLayer(vl)
        
        
                    ###animationAt
                    for feature in vl.getFeatures():
                        geom = feature.geometry()
                        wktdata1 = geom.asWkt()
                        wktdata += wktdata1
            ##find min value of field
            fieldname='length'
            #layer=iface.activeLayer()
            idx=vl.fields().indexFromName(fieldname)
            print("min distance")

            slen = vl.minimumValue(idx)
            print(vl.minimumValue(idx))

            ###selection feature of layer according to short length
            vl.selectByExpression('"length"= '+"'"+slen+"'", QgsVectorLayer.SetSelection)
            self.iface.mapCanvas().setSelectionColor( QColor("blue") )
   

            #add maptips(mouse hover)
            expression = """[%  @layer_name  %]"""
            vl.setMapTipTemplate(expression)

            vl.updateExtents() 
            vl.updateFields() 
            
            #add animation csv file
#
            for feature in vl.getFeatures():
               geom = feature.geometry()
               wkt = geom.asWkt()
               
            wkt = wktdata
            wkt = wkt.replace("LineString (","")

            wkt = wkt.replace(")LineString (",",")
            wkt = wkt.replace(")","")

            longlat = wkt.split(", ")
            pair = list(zip(longlat, longlat[1:] + longlat[:1]))
            animationfile = open(plugin_dir+"/animationcsv/Animation_path.csv","w")
            animationfile.write("field_1,field_2,field_3,field_4\n")

            min1 = 0
            ct = str(datetime.now())
            timelist = []
            timelist.append(ct)

            for i in pair:
                x = (i[0])
                coord = x.replace(" ",",")
                
                min1 +=2
                add = str(datetime.now() +timedelta( minutes=min1 ))
                timelist.append(add)

                csv = timelist[0] +","+ coord +","+ timelist[1]
                timelist.pop(0)
                
                animationfile.write(csv+"\n")
   
            animationfile.close()
            # wkt = wkt.replace("MultiLineString ((","")
            # wkt = wkt.replace("))","")
            # wkt = wkt.replace("LineString (","")
            # wkt = wkt.replace(")","")
            
            # longlat = wkt.split(", ")
            # pair = list(zip(longlat, longlat[1:] + longlat[:1]))
            # animationfile = open(plugin_dir+"/animationcsv/Animation_path.csv","w")
            # animationfile.write("field_1,field_2,field_3,field_4\n")
            
            # min1 = 0
            # ct = str(datetime.now())
            # timelist = []
            # timelist.append(ct)
            
            # for i in pair:
            #    x = (i[0])
            #    coord = x.replace(" ",",")
               
            #    min1 +=2
            #    add = str(datetime.now() +timedelta( minutes=min1 ))
            #    timelist.append(add)
            
            #    csv = timelist[0] +","+ coord +","+ timelist[1]
            #    timelist.pop(0)
               
            #    animationfile.write(csv+"\n")
               
            # animationfile.close()

            #######################

            save_options = QgsVectorFileWriter.SaveVectorOptions()
            save_options.driverName = "ESRI Shapefile"
            save_options.fileEncoding = "UTF-8"
            transform_context = QgsProject.instance().transformContext()
            error = QgsVectorFileWriter.writeAsVectorFormatV2(vl,
                                                  "/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/linestring.shp",
                                                  transform_context,
                                                  save_options)
            if error[0] == QgsVectorFileWriter.NoError:
                print("success again!")
            else:
                print(error)

            buffer()
            
            #QgsProject.instance().addMapLayers([vl])
            os.system(f"python3 /home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/elevation_profile.py")
            self.dlg.pushButton_cesium.show()
            self.dlg.pushButton_path_2.show()
            self.dlg.pushButton_animation.show()

            # os.system(f"eog /home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/elevation_profile.png")

            ###find length of path

            # selectedfeats = vl.getFeatures()

            # total = 0
            # for feature in selectedfeats :
            #     geom = feature.geometry()
            #     total += geom.length()
                
            # len = total*100#(km) if meter then multiply 1000
            # len1 = "%.2f" % len

            # self.dlg.label_len1.show()
            # self.dlg.label_len.show()

            # self.dlg.label_len1.setStyleSheet("color: brown; ")
            # self.dlg.label_len.setStyleSheet("color: blue; ")  

            # self.dlg.label_len.setText(str(len1))

            # print(len)

        
        def elevation_profile():
            os.system(f"eog /home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/elevation_profile.png")

        def cesium():
            run_server = 'gnome-terminal --title="cesium_server" --command="bash -c \'cd /home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/; python3 -m http.server 3000; $SHELL\'"'
            os.system(run_server)
            os.system("/opt/google/chrome/chrome http://127.0.0.1:3000/index.html")

        def animation():
            directory = plugin_dir+"/animationcsv"

            def load_and_configure(filename):
                path = os.path.join(directory, filename)
                uri = 'file:///' + path + "?type=csv&escape=&useHeader=No&detectTypes=yes"
                uri = uri + "&crs=EPSG:4326&xField=field_2&yField=field_3"
                vlayer = QgsVectorLayer(uri, filename, "delimitedtext")

                try:
                    symbol = QgsSvgMarkerSymbolLayer('/usr/share/qgis/svg/transport/transport_train_station2.svg')
                    symbol.setSize(9)
                    symbol.setFillColor(QColor('#3333cc'))

                    vlayer.renderer().symbol().changeSymbolLayer(0, symbol )
                    #layer.loadNamedStyle('/home/bisag/Documents/aniCsvStyle.qml')
                    vlayer.triggerRepaint()
                    vlayer.startEditing()
                    
                except Exception as e4:
                    print('Error: ' + str(e4))
                #title label decorations add
                QgsProject.instance().addMapLayer(vlayer)
                mode = QgsVectorLayerTemporalProperties.ModeFeatureDateTimeStartAndEndFromFields

                tprops = vlayer.temporalProperties()

                tprops.setStartField("field_1")
                tprops.setEndField("field_4")
                tprops.setMode(mode)
                tprops.setIsActive(True)

            for filename in os.listdir(directory):
                if filename.endswith(".csv"):
                    load_and_configure(filename)

            for i in self.iface.mainWindow().findChildren(QtWidgets.QDockWidget):
                if i.objectName() == 'Temporal Controller':
                    #self.iface.mainWindow().findChild(QDockWidget,'PythonConsole').setVisible(False)
                    i.setVisible(True) 

        self.dlg.pushButton_animation.clicked.connect(animation)  
        self.dlg.pushButton_animation.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_animation.setToolTip('click')

        self.dlg.pushButton_cesium.clicked.connect(cesium)  
        self.dlg.pushButton_cesium.setStyleSheet("color: blue;font-size: 12pt; ") 
        self.dlg.pushButton_cesium.setToolTip('click')

        self.dlg.pushButton_slope.clicked.connect(slope1)  
        self.dlg.pushButton_reclassify.clicked.connect(reclassifytable) 
        self.dlg.pushButton_path.clicked.connect(line1) 
        self.dlg.pushButton_path_2.clicked.connect(elevation_profile)  
        self.dlg.pushButton_path_2.setStyleSheet("color: Maroon;font-size: 12pt; ") 
        self.dlg.pushButton_slope.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_slope.setToolTip('click')

        self.dlg.pushButton_reclassify.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_reclassify.setToolTip('click')

        self.dlg.pushButton_path.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_path.setToolTip('click')
        self.dlg.label_title.setStyleSheet("color: Indigo; font-size: 13pt;") 
        self.dlg.label_slope.setStyleSheet("color: brown; ") 
        self.dlg.label_reclassify.setStyleSheet("color: brown; ") 
        self.dlg.label_path.setStyleSheet("color: brown; ") 
        self.dlg.label_info.setStyleSheet("color: Navy; ") 

        self.dlg.label_reclassify.hide()
        self.dlg.pushButton_reclassify.hide()

        self.dlg.label_path.hide()
        self.dlg.pushButton_path.hide()
        self.dlg.pushButton_path_2.hide()
        self.dlg.label_info.hide()
        
        self.dlg.pushButton_cesium.hide()
        # self.dlg.label_len1.hide()
        # self.dlg.label_len.hide()
        self.dlg.pushButton_animation.hide()
        # self.dlg.pushButton_rasterize_over.hide()
        # self.dlg.label_rasterize_over.hide()


        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass
