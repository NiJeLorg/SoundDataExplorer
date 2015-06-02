/**
 * Application.js: Sets global JS variables and initializes Sound Data Explorer
 * Author: NiJeL
 */

/*
  On DOM load handlers
 */
var BEACON_POINTS = null;
var BEACON_D3_POINTS = null;
var MY_MAP = null;
var count = 0;
var mapSlider = null;

$().ready(new function(){
    var myMap = new SoundExplorerMap();
    myMap.loadPointLayers();
    MY_MAP = myMap;	
});