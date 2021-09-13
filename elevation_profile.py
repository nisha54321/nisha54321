import gdal,ogr
import struct
import matplotlib.pyplot as plt
import numpy as np
        
src_filename = r"/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/os1_4326.tif"
src_ds=gdal.Open(src_filename) 
gt=src_ds.GetGeoTransform()
rb=src_ds.GetRasterBand(1)


results = []
labels = []
with open('/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/path_points.txt') as f:
    cnt = 0
    for line in f.readlines():
        values = line.replace("(", "").replace(")", "").split(", ")
        mx, my = float(values[0].strip()), float(values[1].strip())


        px = int((mx - gt[0]) / gt[1]) #x pixel
        py = int((my - gt[3]) / gt[5]) #y pixel


        structval=rb.ReadRaster(px,py,1,1,buf_type=gdal.GDT_UInt16) #Assumes 16 bit int aka 'short'
        intval = struct.unpack('h' , structval) #use the 'short' format code (2 bytes) not int (4 bytes)
        
        elevation = intval[0] #intval is a tuple, length=1 as we only asked for 1 pixel value
        results.append(elevation)
        labels.append("{:.4f}, {:.4f}".format(mx, my))
        cnt += 1

xs = np.arange(len(results))
plt.figure(figsize=(20,13))
plt.plot(xs, results)
plt.xlabel('Location')
plt.ylabel('Height (meter)')
plt.title('Mobility Corridor')
for i in range(len(labels)):
    if i % 10 != 0:
        labels[i] = ""
plt.xticks(xs, labels, rotation='vertical')
plt.savefig("/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/elevation_profile.png")
