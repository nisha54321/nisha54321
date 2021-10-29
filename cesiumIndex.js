// TODO: Change EventListener to ending motion of camera, NOT just moving
//Increase frame distance of camera proportionally to the rect box vertices distance from cameras position
'use strict';

//Gets JSON objects from the SQL query
const Cesium = require('cesium/Cesium');
require('cesium/Widgets/widgets.css');
let expressProxyBaseUrl = 'http://localhost:8585/';
let geoserverBaseUrl = 'http://localhost:8080/';

let viewer = new Cesium.Viewer('cesiumContainer', {
    requestRenderMode : true,
    maximumRenderTimeChange : Infinity,
    shouldAnimate: true,
});



(function() {
    setTimeout(()=>{
	
        let rectangle = Cesium.Rectangle.fromDegrees(87.1766451354, 5.96553477623, 90.4025614766, 29.4940095078);


     	 viewer.camera.flyTo({
            destination: rectangle
       });
    }, 1000);

    viewer.imageryLayers.remove(viewer.imageryLayers.get(0));
    let prov = new Cesium.WebMapServiceImageryProvider({
            url : geoserverBaseUrl+'geoserver/bisag/wms',
            layers: 'node',
            parameters: {
                service: 'WMS',
                version: '1.1.1',
                request: 'GetMap',
                format: 'image/png',
                tiled: true
            }
    });

    let prov1 = new Cesium.WebMapServiceImageryProvider({
        url : geoserverBaseUrl+'geoserver/bisag/wms',
        layers: 'network',
        parameters: {
            service: 'WMS',
            version: '1.1.1',
            request: 'GetMap',
            format: 'image/png',
            transparent: 'true',
            tiled: true
        }
});
viewer.imageryLayers.addImageryProvider(prov);
viewer.imageryLayers.addImageryProvider(prov1);

let tp = new Cesium.CesiumTerrainProvider({
       //url : 'http://192.168.1.245:9000/tilesets/test',
	//url : 'http://192.168.1.244:8585/tilesets/test',
	url : 'http://localhost:8585/tilesets/test',
     requestVertexNormals : true
    });
viewer.terrainProvider = tp;

viewer.entities.add({
    id: 'mou',
    label: {
        // position : Cesium.Cartesian2.ZERO, 
        show: true   // Removed semicolon here
    }
});

viewer.scene.canvas.addEventListener('mousemove', function(e) {
    var entity = viewer.entities.getById('mou');
    var ellipsoid = viewer.scene.globe.ellipsoid;
    // Mouse over the globe to see the cartographic position 

    var cartesian = viewer.camera.pickEllipsoid(new Cesium.Cartesian3(e.clientX, e.clientY), ellipsoid);
    if (cartesian) {
        var cartographic = ellipsoid.cartesianToCartographic(cartesian);
        var longitudeString = Cesium.Math.toDegrees(cartographic.longitude).toFixed(10);
        var latitudeString = Cesium.Math.toDegrees(cartographic.latitude).toFixed(10);
        entity.position = cartesian;
        entity.label.show = true;
        entity.label.font_style = 84;
        //entity.position= Cesium.Cartesian2.ZERO; 
        entity.label.text = '(' + longitudeString + ', ' + latitudeString + ')';
        var result = entity.label.text;  // We can reuse this
        document.getElementById("demo").innerHTML = result;
    } else {
        entity.label.show = false;
    }
});

var parameters = new URLSearchParams(window.location.search);

viewer.camera.setView({
        destination : Cesium.Cartesian3.fromDegrees(
            parameters.get('x'), //1
            parameters.get('y'), //2
            Cesium.Ellipsoid.WGS84.cartesianToCartographic(viewer.camera.position).height
        )
});
//http://localhost:8585/?x=74.314&y=26.278
})();

var dataSourcePromise = viewer.dataSources.add(
    Cesium.CzmlDataSource.load("test.czml")
  );

  dataSourcePromise
    .then(function (dataSource) {
      viewer.trackedEntity = dataSource.entities.getById(
        "aircraft model"
      );
    })
    .otherwise(function (error) {
      window.alert(error);
    });

if (typeof Cesium !== "undefined") {
  window.startupCalled = true;
  startup(Cesium);
}


    
