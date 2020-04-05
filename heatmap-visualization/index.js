import 'ol/ol.css';
import { Map, View } from 'ol';
import OSM from 'ol/source/OSM';
import { Heatmap as HeatmapLayer, Tile as TileLayer } from 'ol/layer';
import Stamen from 'ol/source/Stamen';
import VectorSource from 'ol/source/Vector';
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import { transform } from 'ol/proj';
import { fromLonLat } from 'ol/proj'



var dryCoughData = [{'lng': 48.373606, 'lat': 21.83895}, {'lng': 48.398794, 'lat': 21.923079}, {'lng': 48.426951, 'lat': 16.994058}, {'lng': 48.606273, 'lat': 21.373201}, {'lng': 47.616161, 'lat': 18.674631}, {'lng': 49.031002, 'lat': 21.648734}, {'lng': 48.093997, 'lat': 17.864693}, {'lng': 48.744916, 'lat': 22.251724}, {'lng': 48.470146, 'lat': 20.219833}, {'lng': 48.755612, 'lat': 17.451699}, {'lng': 48.288746, 'lat': 17.741896}, {'lng': 48.45672, 'lat': 17.719505}, {'lng': 48.680575, 'lat': 17.652725}, {'lng': 48.463313, 'lat': 19.138178}, {'lng': 48.610223, 'lat': 21.595733}, {'lng': 48.418822, 'lat': 19.01365}, {'lng': 48.641014, 'lat': 20.389604}, {'lng': 48.867398, 'lat': 18.52686}, {'lng': 49.061428, 'lat': 18.607926}, {'lng': 48.534829, 'lat': 18.636501}, {'lng': 48.410753, 'lat': 18.757327}]
var feverData = [{'lng': 47.946966, 'lat': 18.784978}, {'lng': 49.31292, 'lat': 21.378606}, {'lng': 48.426951, 'lat': 16.994058}, {'lng': 47.616161, 'lat': 18.674631}, {'lng': 48.439394, 'lat': 21.862996}, {'lng': 49.031002, 'lat': 21.648734}, {'lng': 48.586983, 'lat': 21.490395}, {'lng': 48.744916, 'lat': 22.251724}, {'lng': 48.740539, 'lat': 17.629498}, {'lng': 47.915683, 'lat': 17.014693}, {'lng': 48.470146, 'lat': 20.219833}, {'lng': 48.45672, 'lat': 17.719505}, {'lng': 48.680575, 'lat': 17.652725}, {'lng': 48.418822, 'lat': 19.01365}, {'lng': 48.641014, 'lat': 20.389604}, {'lng': 48.867398, 'lat': 18.52686}, {'lng': 49.061428, 'lat': 18.607926}, {'lng': 48.534829, 'lat': 18.636501}, {'lng': 48.410753, 'lat': 18.757327}]


function makeVectorSource(data) {
  var vectorSource = new VectorSource();
  for (var i = 0; i < data.length; i++) {
    var d = data[i];
    // TODO: might be messing the order of lat and lng
    var coord = fromLonLat([d['lat'], d['lng']]);
    var lonLat = new Point(coord);
    var pointFeature = new Feature({
      geometry: lonLat,
      weight: 6
    });
    vectorSource.addFeature(pointFeature);
  }
  return vectorSource;
}

var heatmapDryCough = new HeatmapLayer({
  source: makeVectorSource(dryCoughData),
  blur: 20,
  radius: 20,
  weight: () => 10,
});


var heatmapFever = new HeatmapLayer({
  source: makeVectorSource(feverData),
  blur: 20,
  radius: 20,
  weight: () => 5,
});

var view = new View({
  center: transform([19.2, 48.6], 'EPSG:4326', 'EPSG:3857'),
  zoom: 7
});

var raster = new TileLayer({
  source: new OSM()
  // source: new Stamen({
  //   layer: 'toner'
  // })
});

const map = new Map({
  target: 'map-cough',
  layers: [
    raster, heatmapDryCough,
  ],
  view: view
});

var raster2 = new TileLayer({
  source: new OSM()
});
const mapFever = new Map({
  target: 'map-fever',
  layers: [
    raster2, heatmapFever
  ],
  view: view
});