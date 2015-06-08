/**
 * Application.js: Sets global JS variables and initializes Sound Data Explorer
 * Author: NiJeL
 */

/*
  On DOM load handlers
 */
var open_tooltips = [];
var BEACON_POINTS = null;
var BEACON_D3_POINTS = null;
var BOATLAUNCH = null;
var CSOS = null;
var CSOS_CT = null;
var IMPERVIOUS = null;
var WATERSHEDS = null;
var SHELLFISH = null;
var WASTEWATER_CT = null;
var WASTEWATER_NY = null;
var LANDUSE = null;
var MY_MAP = null;
var MY_MAP_MODAL = null;
var count = 0;
var mapSlider = null;

$().ready(new function(){
    var myMap = new SoundExplorerMap();
    myMap.loadPointLayers();
    myMap.loadExtraLayers();
    MY_MAP = myMap;	
});