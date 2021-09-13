import cv2
import matplotlib.pyplot as plt
import rasterio
import pyastar2d
import numpy as np
import sys
from shapely.geometry import LineString
import os

raster_one = rasterio.open("/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/OS1_Reclassify.tif")

print(sys.argv)
grid = raster_one.read(1).astype(np.float32)

print(grid[0])
grid[grid < 1] = np.inf

start = raster_one.index(float(sys.argv[1]), float(sys.argv[2]))
end = raster_one.index(float(sys.argv[3]), float(sys.argv[4]))

print(start, end)

print(grid[start[0], start[1]])
print(grid[end[0], end[1]])

# start = raster_one.index(self.xy[-4], self.xy[-3])
# end = raster_one.index(self.xy[-2], self.xy[-1])

if grid[start[0], start[1]] == np.inf or grid[end[0], end[1]] == np.inf:
    raise Exception("start and end points must not be obstacle")


def update_grid(grid, path, margin=20):
    if path is None:
        return
    prev_point = path[1]
    for point in path[2:]:
        change_x = abs(point[1] - prev_point[1])
        change_y = abs(point[0] - prev_point[0])
        if change_y == 1:
            grid[prev_point[0], prev_point[1]: prev_point[1] + margin] = np.inf
            grid[prev_point[0], prev_point[1] - margin:prev_point[1]] = np.inf
        elif change_x == 1:
            grid[prev_point[0]: prev_point[0] + margin, prev_point[1]] = np.inf
            grid[prev_point[0] - margin: prev_point[0], prev_point[1]] = np.inf
        prev_point = point
    return grid


def compute_bounds(start, end):
    return [min(start[0], end[0]), min(start[1], end[1])], [max(start[0], end[0]), max(start[1], end[1])]


def save_image(fn, grid):
    grid[grid == np.inf] = 255
    cv2.imwrite(fn, grid.astype(np.uint8))


def compute_paths(grid, nb_paths=5):
    paths = [None] * nb_paths
    save_image("/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/1.jpg", grid)
    paths[0] = pyastar2d.astar_path(grid, start, end, allow_diagonal=False)
    for i in range(nb_paths - 1):
        grid = update_grid(grid, paths[i])
        save_image("/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/"+f"{i + 2}.jpg", grid)
        paths[i+1] = pyastar2d.astar_path(grid, start, end, allow_diagonal=False)
    return paths


paths = compute_paths(grid)

points = []

czml_list = []

with open("/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/path.txt", "w") as f:
    for path in paths:
        points = []
        if path is None:
            continue
        for location in path:
            points.append(raster_one.xy(location[0], location[1]))
        path_ls = LineString(points)
        f.write(path_ls.wkt + os.linesep)
print(points)
# with open("/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/path.txt", "w") as f:
#     for location in path:
#         points.append(raster_one.xy(location[0], location[1]))
#     path_ls = LineString(points)
#     f.write(path_ls.wkt)

with open("/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/path_points.txt", 'w') as f:
    for point in points:
        f.write(str(point)+ os.linesep)


index_file = open("/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/index.html", "w")
index_file.truncate()
index_file.close()

with open("/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/index.html", 'w') as f:
    mycarto_cords= ""
    for point in points:
        mycarto_cords += str(point).replace("(","").replace(")",", 0,")
    str1 = '''
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <!-- Make the application on mobile take up the full browser screen and disable user scaling. -->
    <meta
    name="viewport"
    content="width=device-width, initial-scale=1, maximum-scale=1, minimum-scale=1, user-scalable=no"
    />
    <title>Index</title>
    <script src="/Build/Cesium/Cesium.js"></script>
    <link href="/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
    <style>
        html,
        body,
        #cesiumContainer {
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
        overflow: hidden;
        }
    </style>
    <style>
        .cesium-viewer-animationContainer{
        display: none;
        }
        .cesium-viewer-bottom{
        display: none;
        }
    </style>

    </head>
    <body>
        <div id="cesiumContainer"></div>
    <script>

Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJmOTQ1OWNhZS00NDY3LTQ3ZGItYTY5Ni03OTliOTgxMWVjYzIiLCJpZCI6NDAzMjIsImlhdCI6MTYwODYyNzkxNX0.yVW1tez7XbulKavYnEIswlgREug_3JxTj1ZXOuwKm2A";


var viewer = new Cesium.Viewer("cesiumContainer", {
  infoBox: false,
  selectionIndicator: false,
  shadows: true,
  shouldAnimate: true,
});


    
    var czml = [
    {
        id: "document",
        name: "CZML Geometries: Polyline",
        version: "1.0",
    },
    {
        id: "redLine",
        name: "Red line clamped to terain",
        polyline: {
        positions: {
            cartographicDegrees: ['''+mycarto_cords[:-1]+'''],
        },
        material: {
            solidColor: {
            color: {
                rgba: [255, 0, 0, 255],
            },
            },
        },
        width: 5,
        clampToGround: true,
        show: true,
        zIndex: 0

        },
    },
    ];


    var dataSourcePromise = Cesium.CzmlDataSource.load(czml);
    viewer.dataSources.add(dataSourcePromise);
    viewer.zoomTo(dataSourcePromise);                        
    </script>
    </body>
    </html>

    '''

    f.write(str1)
