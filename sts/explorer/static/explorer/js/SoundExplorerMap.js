/* 
* Functions to create the main Sound Data Explorer Map
*/

// initialize map
function SoundExplorerMap() {
	// set zoom and center for this map	
    this.center = [40.735551, -72.932739];
    this.zoom = 9;

    this.map = new L.Map('map', {
		minZoom:8,
		maxZoom:17,
    	center: this.center,
   	 	zoom: this.zoom,
   	 	zoomControl: false,
	});

	// add CartoDB tiles
	/*
	this.CartoDBLayer = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',{
	  attribution: 'Created By <a href="http://nijel.org/">NiJeL</a> | &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
	});
	this.map.addLayer(this.CartoDBLayer);
	*/
	this.OSMHOTLayer = L.tileLayer('http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',{
	  attribution: 'Created By <a href="http://nijel.org/">NiJeL</a> | &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="http://hotosm.org/">OSM HOT</a>'
	});
	this.map.addLayer(this.OSMHOTLayer);

	// load zoom control in top right
	this.map.addControl(L.control.zoom({ position: 'topright' }));
	
	//load geocoder control
	var geocoder = this.map.addControl(L.Control.geocoder({collapsed: true, placeholder:'Address Search', geocoder:new L.Control.Geocoder.Google()}));
	
	//load scale bars
	this.map.addControl(L.control.scale());
	
    // enable events
    this.map.doubleClickZoom.enable();
    this.map.scrollWheelZoom.enable();
	
	// empty containers for layers 
	this.BEACON_POINTS = null;
	this.BEACON_D3_POINTS = null;
	this.BOATLAUNCH = null;
	this.CSOS = null;
	this.CSOS_CT = null;
	this.IMPERVIOUS = null;
	this.WATERSHEDS = null;
	this.SHELLFISH = null;
	this.WASTEWATER_CT = null;
	this.WASTEWATER_NY = null;
	this.LANDUSE = null;

	// popup container to catch popups
	this.popup = new L.Popup({ 
		maxWidth: 300,
		minWidth: 100, 
		minHeight: 30, 
		closeButton:true,
		autoPanPaddingTopLeft: L.point(0, 50)
	});

	// subscribe to zoomend event to show
	this.map.on('zoomend', function(e) {
	    SoundExplorerMap.checkZoomSwitchLayers();
	});

}


SoundExplorerMap.onEachFeature_BEACON_POINTS = function(feature,layer){	
	var highlight = {
	    weight: 2,
	    color: '#000'
	};
	var noHighlight = {
        weight: 1,
        color: '#f1f1f1'
	};

	var start_date = moment($( "#start_date option:selected" ).val()).format('MMMM YYYY');
	var end_date = moment($( "#end_date option:selected" ).val()).format('MMMM YYYY');

	var sample_start_date = moment(feature.properties.StartDate).format('MMMM YYYY');
	var sample_end_date = moment(feature.properties.EndDate).format('MMMM YYYY');

	var pctFail = 100 - ((feature.properties.TotalPassSamples / feature.properties.NumberOfSamples) * 100).toFixed(0);

	var pctDryFail = 100 - ((feature.properties.DryWeatherPassSamples / feature.properties.TotalDryWeatherSamples) * 100).toFixed(0);

	var pctWetFail = 100 - ((feature.properties.WetWeatherPassSamples / feature.properties.TotalWetWeatherSamples) * 100).toFixed(0);

	layer.bindLabel("<span class='text-capitalize'>" + feature.properties.BeachName + "<br />" + feature.properties.County + "</span> County, " + feature.properties.State, { direction:'auto' });
	
    layer.on('mouseover', function(ev) {		

		layer.setStyle(highlight);

		if (!L.Browser.ie && !L.Browser.opera) {
	        layer.bringToFront();
	    }

    });
		
    layer.on('mouseout', function(ev) {
		layer.setStyle(noHighlight);		
    });	

    // onclick set content in bottom bar and open doc if not open already 
	layer.on("click",function(ev){	
		if ($( ".popup-wrapper" ).hasClass( "popup-wrapper-open" )) {
			// don't toggle classes
		} else {
			$( ".popup-wrapper" ).toggleClass("popup-wrapper-open");
			$( ".map" ).toggleClass("map-popup-wrapper-open");
			$( ".legend" ).toggleClass("legend-popup-wrapper-open");
		}

		var dropSvg = SoundExplorerMap.createDrop(pctWetFail);
		var sunSvg = SoundExplorerMap.createSun(pctDryFail);

		MY_MAP.popup.setLatLng(ev.target._latlng)
		MY_MAP.popup.setContent(feature.properties.BeachName + "<br />For the selected time period, samples failed: <br /><div class='dropMargin pull-left'><div id='ringSvgPopup'></div></div><div class='textPopup textDropPopup'>"+pctFail+"% of the time.</div></div><div class='clearfix'></div><div class='dropMargin pull-left'>" + dropSvg + "</div><div class='textPopup textDropPopup'>"+pctWetFail+"% of the time after wet weather.</div></div><div class='clearfix'></div><div class='pull-left'>" + sunSvg + "</div><div class='textPopup textSunPopup'>"+pctDryFail+"% of the time after dry weather.</div></div><div class='clearfix'></div>" + feature.properties.TotalPassSamples + " samples taken from " + start_date + " to " + end_date + ". Site sampled from " + sample_start_date + " through " + sample_end_date + ".<br /><a href='#' data-toggle='modal' data-target='#siteView' data-backdrop='false' data-beachid='"+ feature.properties.BeachID +"' data-lat='"+ feature.geometry.coordinates[1] +"' data-lon='"+ feature.geometry.coordinates[0] +"'>Enter Site View to see detailed data.</a>")
		MY_MAP.map.openPopup(MY_MAP.popup);

		// draw ring after popup is open
		SoundExplorerMap.createRing(feature.properties.pctPassFail);


	});

	// we'll now add an ID to each layer so we can fire the mouseover and click outside of the map
    layer._leaflet_id = 'layerID' + count;
    count++;

}

SoundExplorerMap.createRing = function (pctPassFail){
	var w = 55;
	var h = 60;
	var innerRadius = 20;
	var outerRadius = 25;

	var arc = d3.svg.arc()
	    .outerRadius(outerRadius)
	    .innerRadius(innerRadius);

	var pie = d3.layout.pie()
		.sort(null)
		.value(function(d) { return d.pct; });

	var ringSvg = d3.select('#ringSvgPopup').append('svg')
		.attr('width', w)
		.attr('height', h)
		.append('g')
		.attr("class", "rings")
		.attr("transform", "translate("+w/2+","+h/2+")")
		.selectAll(".arc")
		.data(function(d) { return pie(pctPassFail); });

	ringSvg.enter().append('text')
		.attr("text-anchor", "middle")
		.attr("transform", "translate(0,6)")
		.attr('style', function(d) { 
			if (d.data.name == "fail") {
				var pctNum = +d.data.pct;
				if (pctNum == 100) {
					var fontSize = 16;
				} else {
					var fontSize = 20;
				}				
				return "font-size: "+ fontSize +"; stroke: #be1e2d; }"
			} 
		})
		.text(function(d) { 
			if (d.data.name == "fail") {
				return d.data.pct.toFixed(0) + "%";
			}
		});


	var rings = ringSvg.enter()
		.append("path")
		.attr("class", "arc")
		.attr("d", arc)
		.style("fill", function(d) {
			if (d.data.name == "pass") {
				return "#009444";
			} else {
				return "#be1e2d";
			}
		});

}

SoundExplorerMap.createDrop = function (pctWetFail){
	var dropSvg = '<svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" version="1.1" width="53.771" height="59.867249" id="svg2" xml:space="preserve"><g transform="matrix(1.25,0,0,-1.25,0,59.86725)" id="g10"><g transform="translate(9.4551,8.6643)"id="g20"><path d="m 0,0 c 6.529,-6.529 17.116,-6.53 23.643,-0.002 6.528,6.528 6.527,17.114 -0.002,23.643 L 11.82,35.462 0,23.642 C -6.528,17.114 -6.528,6.528 0,0" id="path22" style="fill:#c1e5e6;fill-opacity:1;fill-rule:nonzero;stroke:none" /></g><g transform="translate(9.4551,8.6643)" id="g24"><path d="m 0,0 c 6.529,-6.529 17.116,-6.53 23.643,-0.002 6.528,6.528 6.527,17.114 -0.002,23.643 L 11.82,35.462 0,23.642 C -6.528,17.114 -6.528,6.528 0,0 z" id="path26" style="fill:none;stroke:#0a8ba7;stroke-width:3;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:10;stroke-opacity:1;stroke-dasharray:none" /></g></g>';

	// change translation if 100%, between 99 and 10 percent and less than 10 percent.
	if (pctWetFail == 100) {
		var fontSize = 16;
		var translateRight = 9;
	} else if (pctWetFail > 9.99) {
		var fontSize = 20;
		var translateRight = 10;		
	} else {
		var fontSize = 20;
		var translateRight = 15;				
	}

	var dropSvgText = '<g transform="translate('+ translateRight +',40)" id="g26"><text style="font-family:\'Print Clearly\'; font-size: '+ fontSize +'; stroke:#0a8ba7;">'+pctWetFail+'%</text></g>';

	var dropSvgClose = '</svg>';

	dropSvg = dropSvg + dropSvgText + dropSvgClose;

	return dropSvg;

} 


SoundExplorerMap.createSun = function (pctDryFail){
	var sunSvg = '<svg width="78.911" height="78.212"><g transform="matrix(1.25 0 0 -1.25 0 78.21)"><path d="M46.63 30.497c0-8.034-6.512-14.546-14.545-14.546-8.034 0-14.546 6.513-14.546 14.547s6.51 14.546 14.545 14.546c8.033 0 14.546-6.512 14.546-14.546" fill="#ee4137"/><path d="M46.63 30.497c0-8.034-6.512-14.546-14.545-14.546-8.034 0-14.546 6.513-14.546 14.547s6.51 14.546 14.545 14.546c8.033 0 14.546-6.512 14.546-14.546z" fill="none" stroke="#f79420" stroke-width="3" stroke-miterlimit="10"/><path d="M52.164 30.497h6.84M46.283 44.695l4.836 4.836M32.085 50.576v6.84M17.886 44.695L13.05 49.53M17.886 16.298l-3.842-3.842M32.123 10.726v-6.84M46.283 16.298l4.836-4.836M4.207 30.497h6.84" fill="none" stroke="#faaf41" stroke-width="5" stroke-linecap="round" stroke-miterlimit="10"/></g>';

	// change translation if 100%, between 99 and 10 percent and less than 10 percent.
	if (pctDryFail == 100) {
		var fontSize = 14;
		var translateRight = 24;
	} else if (pctDryFail > 9.99) {
		var fontSize = 18;
		var translateRight = 25;		
	} else {
		var fontSize = 20;
		var translateRight = 28;				
	}


	var sunSvgText = '<g transform="translate('+ translateRight +',45)" id="g26"><text style="font-family:\'Print Clearly\'; font-size: '+ fontSize +'; stroke:#fff;">'+pctDryFail+'%</text></g>';

	var sunSvgClose = '</svg>';

	sunSvg = sunSvg + sunSvgText + sunSvgClose;

	return sunSvg;

} 


SoundExplorerMap.prototype.loadPointLayers = function (){
	// load points layers
	var thismap = this;

	// create date for today and for 5 years ago
	var endDate = moment().endOf('month').add(1, 'days').format("YYYY-MM-DD");
	var startDate = moment().subtract(5, 'years').startOf('month').format("YYYY-MM-DD");

	d3.json('/beaconapi/?startDate=' + startDate + '&endDate=' + endDate, function(data) {
		geojsonData = data;

		$.each(geojsonData.features, function(i, d){
			d.properties.leafletId = 'layerID' + i;
			// create coordiantes with latLon instead of lonLat for use with D3 later
			d.properties.latLonCoordinates = [d.geometry.coordinates[1], d.geometry.coordinates[0]];
			d.properties.pctPass = (d.properties.TotalPassSamples / d.properties.NumberOfSamples) * 100;
			var pctFail = 100 - ((d.properties.TotalPassSamples / d.properties.NumberOfSamples) * 100);
			d.properties.pctPassFail = [{name: "fail", pct: pctFail},{name: "pass", pct: d.properties.pctPass}];
		});

		thismap.BEACON_POINTS = L.geoJson(geojsonData, {
		    pointToLayer: SoundExplorerMap.getStyleFor_BEACON_POINTS,
			onEachFeature: SoundExplorerMap.onEachFeature_BEACON_POINTS
		}).addTo(thismap.map);

		// create the D3 layer for Beacon data, but don't add to map until we hit a specfic zoom level
		SoundExplorerMap.createBEACON_D3_POINTS(geojsonData.features, thismap);

		// draw time slider with these data
		SoundExplorerMap.drawTimeSlider(geojsonData.features);

	});

}


SoundExplorerMap.getStyleFor_BEACON_POINTS = function (feature, latlng){
	var marker = L.circleMarker(latlng, {
		radius: 5,
		color: '#bdbdbd',
		weight: 1,
		opacity: 1,
		fillColor: SoundExplorerMap.SDEPctPassColor(feature.properties.pctPass),
		fillOpacity: 1
	});
	
	return marker;
	
}


SoundExplorerMap.onEachFeature_BOATLAUNCH = function(feature,layer){

	layer.bindLabel(feature.properties.Name, { direction:'auto' });

}

SoundExplorerMap.onEachFeature_CSOS = function(feature,layer){

	layer.bindLabel(feature.properties.facility + "<br />Permit Number: " + feature.properties.spdes_num, { direction:'auto' });

}

SoundExplorerMap.onEachFeature_CSOS_CT = function(feature,layer){

	layer.bindLabel(feature.properties.Location + "<br />" + feature.properties.TownName, { direction:'auto' });

}

SoundExplorerMap.onEachFeature_IMPERVIOUS = function(feature,layer){
	var pctIS10 = (feature.properties.pctIS10).toFixed(1);

	layer.bindLabel(feature.properties.Name + "<br />" + pctIS10 + "% impervious surfaces", { direction:'auto' });

}

SoundExplorerMap.onEachFeature_WATERSHEDS = function(feature,layer){

	layer.bindLabel(feature.properties.Name, { direction:'auto' });

}

SoundExplorerMap.onEachFeature_SHELLFISH = function(feature,layer){

	layer.bindLabel(feature.properties.CLASS, { direction:'auto' });

}

SoundExplorerMap.onEachFeature_WASTEWATER_CT = function(feature,layer){

	layer.bindLabel(feature.properties.FAC_NAME + "<br />Permit Number: " + feature.properties.NPDES_PRMT, { direction:'auto' });

}

SoundExplorerMap.onEachFeature_WASTEWATER_NY = function(feature,layer){

	layer.bindLabel(feature.properties.Facility_N + "<br />Permit Number: " + feature.properties.SPDES_ID, { direction:'auto' });

}


SoundExplorerMap.prototype.loadExtraLayers = function (){
	// load all other layers -- don't show yet
	var thismap = this;

	d3.json(boatlaunch, function(data) {
		var boatlaunchTopojson = topojson.feature(data, data.objects.boatlaunch_ny_ct).features;
		drawBoatlaunch(boatlaunchTopojson);
	});

	function drawBoatlaunch(boatlaunchTopojson) {
		thismap.BOATLAUNCH = L.geoJson(boatlaunchTopojson, {
		    pointToLayer: SoundExplorerMap.getStyleFor_BOATLAUNCH,
			onEachFeature: SoundExplorerMap.onEachFeature_BOATLAUNCH
		});
	}

	d3.json(csos, function(data) {
		var csosTopojson = topojson.feature(data, data.objects.CSOs_LISound_NY).features;
		drawCsos(csosTopojson);
	});

	function drawCsos(csosTopojson) {
		thismap.CSOS = L.geoJson(csosTopojson, {
		    pointToLayer: SoundExplorerMap.getStyleFor_CSOS,
			onEachFeature: SoundExplorerMap.onEachFeature_CSOS
		});
	}

	d3.json(csos_CT, function(data) {
		var csos_CTTopojson = topojson.feature(data, data.objects.CT_Municipal_CSO_Locations_4326).features;
		drawcsos_CT(csos_CTTopojson);
	});

	function drawcsos_CT(csos_CTTopojson) {
		thismap.CSOS_CT = L.geoJson(csos_CTTopojson, {
		    pointToLayer: SoundExplorerMap.getStyleFor_CSOS,
			onEachFeature: SoundExplorerMap.onEachFeature_CSOS_CT
		});
	}

	d3.json(impervious, function(data) {
		var imperviousTopojson = topojson.feature(data, data.objects.IS_estimates_ALL_4326).features;
		drawImpervious(imperviousTopojson);
	});

	function drawImpervious(imperviousTopojson) {
		thismap.IMPERVIOUS = L.geoJson(imperviousTopojson, {
		    style: SoundExplorerMap.getStyleFor_IMPERVIOUS,
			onEachFeature: SoundExplorerMap.onEachFeature_IMPERVIOUS
		});
	}

	d3.json(watersheds, function(data) {
		var watershedsTopojson = topojson.feature(data, data.objects.NY_CT_LIS_watersheds2).features;
		drawWatersheds(watershedsTopojson);
	});

	function drawWatersheds(watershedsTopojson) {
		thismap.WATERSHEDS = L.geoJson(watershedsTopojson, {
		    style: SoundExplorerMap.getStyleFor_WATERSHEDS,
			onEachFeature: SoundExplorerMap.onEachFeature_WATERSHEDS
		});
	}

	d3.json(shellfish, function(data) {
		var shellfishTopojson = topojson.feature(data, data.objects.SHELLFISH_AREA_CLASS_POLY_4326).features;
		drawShellfish(shellfishTopojson);

	});

	function drawShellfish(shellfishTopojson) {
		thismap.SHELLFISH = L.geoJson(shellfishTopojson, {
		    style: SoundExplorerMap.getStyleFor_SHELLFISH,
			onEachFeature: SoundExplorerMap.onEachFeature_SHELLFISH
		});
	}

	// two wastewater layers -- one for CT and one for NY
	d3.json(wastewater_CT, function(data) {
		var wastewater_CTTopojson = topojson.feature(data, data.objects.stp_2013_4326).features;
		drawWastewater_CT(wastewater_CTTopojson);

	});

	function drawWastewater_CT(wastewater_CTTopojson) {
		thismap.WASTEWATER_CT = L.geoJson(wastewater_CTTopojson, {
		    pointToLayer: SoundExplorerMap.getStyleFor_WASTEWATER,
			onEachFeature: SoundExplorerMap.onEachFeature_WASTEWATER_CT
		});
	}

	/*
	d3.json(wastewater_NY, function(data) {
		var wastewater_NYTopojson = topojson.feature(data, data.objects.wastewater_NY).features;
		drawWastewater_NY(wastewater_NYTopojson);

	});

	function drawWastewater_NY(wastewater_NYTopojson) {
		thismap.WASTEWATER_NY = L.geoJson(wastewater_NYTopojson, {
		    pointToLayer: SoundExplorerMap.getStyleFor_WASTEWATER,
			onEachFeature: SoundExplorerMap.onEachFeature_WASTEWATER_NY
		});
	}
	*/

	thismap.WASTEWATER_NY = L.esri.featureLayer("http://services.arcgis.com/jDGuO8tYggdCCnUJ/ArcGIS/rest/services/Municipal_wastewater_discharge_facilities_in_NYS/FeatureServer/0", {
			pointToLayer: SoundExplorerMap.getStyleFor_WASTEWATER,
			onEachFeature: SoundExplorerMap.onEachFeature_WASTEWATER_NY
	});

	thismap.LANDUSE = L.esri.dynamicMapLayer("http://gis1.usgs.gov/arcgis/rest/services/gap/GAP_Land_Cover_NVC_Class_Landuse/MapServer", {
		  opacity : 0.5
		});

	thismap.LANDUSE.on('load', function(e){
	  $("body").removeClass("loading");
	});



}

SoundExplorerMap.getStyleFor_BOATLAUNCH = function (feature, latlng){

	var pointMarker = L.circleMarker(latlng, {
		radius: 3,
		color: '#bdbdbd',
		weight: 1,
		opacity: 1,
		fillColor: '#545454',
		fillOpacity: 1
	});
	
	return pointMarker;
	
}


SoundExplorerMap.getStyleFor_CSOS = function (feature, latlng){

	var pointMarker = L.circleMarker(latlng, {
		radius: 3,
		color: '#bdbdbd',
		weight: 1,
		opacity: 1,
		fillColor: '#543005',
		fillOpacity: 1
	});
	
	return pointMarker;
	
}

SoundExplorerMap.getStyleFor_IMPERVIOUS = function (feature){
	var pctIS10 = (feature.properties.pctIS10).toFixed(1);
	
    return {
        weight: 1,
        opacity: 0.75,
        color: '#f1f1f1',
        fillOpacity: 0.75,
        fillColor: SoundExplorerMap.fillColor_IMPERVIOUS(pctIS10)
    }
}

SoundExplorerMap.getStyleFor_WATERSHEDS = function (feature){
	
    return {
        weight: 1,
        opacity: 0.75,
        color: '#545454',
        fillOpacity: 0.00001,
        fillColor: '#fff'
    }
}

SoundExplorerMap.getStyleFor_SHELLFISH = function (feature){
	
    return {
        weight: 1,
        opacity: 0.75,
        color: '#f1f1f1',
        fillOpacity: 0.75,
        fillColor: SoundExplorerMap.fillColor_SHELLFISH(feature.properties.AV_LEGEND)
    }
}

SoundExplorerMap.getStyleFor_WASTEWATER = function (feature, latlng){

	var pointMarker = L.circleMarker(latlng, {
		radius: 3,
		color: '#bdbdbd',
		weight: 1,
		opacity: 1,
		fillColor: '#35978f',
		fillOpacity: 1
	});
	
	return pointMarker;
	
}



SoundExplorerMap.addLayers = function (layer){
	if (layer == "beacon") {
		MY_MAP.BEACON_POINTS.addTo(MY_MAP.map);
		if (MY_MAP.map.getZoom() >= 14) {
			MY_MAP.BEACON_D3_POINTS.addTo(MY_MAP.map);
		}
	}
	if (layer == "boatlaunch") {
		MY_MAP.BOATLAUNCH.addTo(MY_MAP.map);
	}
	if (layer == "csos") {
		MY_MAP.CSOS.addTo(MY_MAP.map);
		MY_MAP.CSOS_CT.addTo(MY_MAP.map);
	}
	if (layer == "impervious") {
		MY_MAP.IMPERVIOUS.addTo(MY_MAP.map);
	}
	if (layer == "watersheds") {
		MY_MAP.WATERSHEDS.addTo(MY_MAP.map);
	}
	if (layer == "shellfish") {
		MY_MAP.SHELLFISH.addTo(MY_MAP.map);
	}
	if (layer == "wastewater") {
		MY_MAP.WASTEWATER_CT.addTo(MY_MAP.map);
		MY_MAP.WASTEWATER_NY.addTo(MY_MAP.map);
	}
	if (layer == "landuse") {
		MY_MAP.LANDUSE.addTo(MY_MAP.map).bringToBack();
	}

	if (MY_MAP.map.hasLayer(MY_MAP.BEACON_POINTS)) {
		MY_MAP.BEACON_POINTS.bringToFront();
	}
	if (MY_MAP.map.hasLayer(MY_MAP.BEACON_D3_POINTS)) {
		MY_MAP.BEACON_D3_POINTS.bringToFront();
	}

}

SoundExplorerMap.removeLayers = function (layer){
	if (layer == "beacon") {
		MY_MAP.map.removeLayer(MY_MAP.BEACON_POINTS);
		MY_MAP.map.removeLayer(MY_MAP.BEACON_D3_POINTS);
	}
	if (layer == "boatlaunch") {
		MY_MAP.map.removeLayer(MY_MAP.BOATLAUNCH);
	}
	if (layer == "csos") {
		MY_MAP.map.removeLayer(MY_MAP.CSOS);
		MY_MAP.map.removeLayer(MY_MAP.CSOS_CT);
	}
	if (layer == "impervious") {
		MY_MAP.map.removeLayer(MY_MAP.IMPERVIOUS);
	}
	if (layer == "watersheds") {
		MY_MAP.map.removeLayer(MY_MAP.WATERSHEDS);
	}
	if (layer == "shellfish") {
		MY_MAP.map.removeLayer(MY_MAP.SHELLFISH);
	}
	if (layer == "wastewater") {
		MY_MAP.map.removeLayer(MY_MAP.WASTEWATER_CT);
		MY_MAP.map.removeLayer(MY_MAP.WASTEWATER_NY);
	}
	if (layer == "landuse") {
		MY_MAP.map.removeLayer(MY_MAP.LANDUSE);
	}

}


SoundExplorerMap.fillColor_SHELLFISH = function (d){
    return d == 'A' ? '#a6cee3' :
           d == 'CA' ? '#1f78b4' :
           d == 'R-R/DP' ? '#b2df8a' :
           d == 'CR-R/DP' ? '#33a02c' :
           d == 'R-R' ? '#fb9a99' :
           d == 'CR-R' ? '#e31a1c' :
           d == 'P' ? '#fdbf6f' :
                   	'#fff' ;	

}

SoundExplorerMap.fillColor_IMPERVIOUS = function (d){
    return d > 25 ? '#252525' :
           d > 20 ? '#636363' :
           d > 15 ? '#969696' :
           d > 10 ? '#bdbdbd' :
           d > 5  ? '#d9d9d9' :
                   	'#f7f7f7' ;	

}

SoundExplorerMap.SDEPctPassColor = function (d){
    return d > 95 ? '#39b54a' :
           d > 90 ? '#f7e34f' :
           d > 85 ? '#f9ae08' :
           d > 78 ? '#f47f45' :
           d >= 0 ? '#ef4136' :
                   	'#545454' ;	
}

SoundExplorerMap.SDEPctPassGrade = function (d){
    return d > 95 ? 'A' :
           d > 90 ? 'B' :
           d > 85 ? 'C' :
           d > 78 ? 'D' :
           d >= 0 ? 'F' :
                   	'' ;	
}


SoundExplorerMap.createBEACON_D3_POINTS = function (features, thismap) {
	var circleRadius = 20;
	var circleStroke = 4;
	var innerRadius = 20;
	var outerRadius = 24;

	thismap.BEACON_D3_POINTS = L.d3SvgOverlay( function(sel,proj){

		// create dots with the same color as the leaflet overlay dots and create on hover and click interactions

		function update() {
			//updating
			beaconCircles.select('circle')
				.attr('r', circleRadius/scale)
				.attr('cx',function(d){ return proj.latLngToLayerPoint(d.properties.latLonCoordinates).x;})
				.attr('cy',function(d){return proj.latLngToLayerPoint(d.properties.latLonCoordinates).y;})
				.attr('fill', function(d){ 
					return SoundExplorerMap.SDEPctPassColor(d.properties.pctPass);
				})
				.attr('stroke', 'white')
				.attr('stroke-width', circleStroke/scale);

			var beaconRings = beaconCircles.select("g")
				.attr("class", "rings")
				.attr("transform", function(d, i) { return "translate(" + proj.latLngToLayerPoint(d.properties.latLonCoordinates).x + "," + proj.latLngToLayerPoint(d.properties.latLonCoordinates).y + ")"; });

			var beaconArcs = beaconRings.selectAll(".arc")
				.data(function(d) { return pie(d.properties.pctPassFail); });

			beaconArcs.enter()
				.append("path")
				.attr("class", "arc")
				.attr("d", arc)
				.style("fill", function(d) {
					if (d.data.name == "pass") {
						return "#009444";
					} else {
						return "#be1e2d";
					}
				});

			beaconCircles.select("text")
				.attr("text-anchor", "middle")
				.attr("dx", function(d){ return proj.latLngToLayerPoint(d.properties.latLonCoordinates).x;})
				.attr("dy", function(d){return (proj.latLngToLayerPoint(d.properties.latLonCoordinates).y) + 8/scale; })
				.attr('style', "font-size: "+ 24/scale +";")
				.text(function(d) { return SoundExplorerMap.SDEPctPassGrade(d.properties.pctPass); });

		}

		// set up vars
		var scale = this._scale;

		var arc = d3.svg.arc()
		    .outerRadius(outerRadius/scale)
		    .innerRadius(innerRadius/scale);

		var pie = d3.layout.pie()
			.sort(null)
			.value(function(d) { return d.pct; });


		// binding data
		var beaconCircles = sel.selectAll('.beaconCircles')
			.data(features)

		//update elements as needed
		beaconCircles.selectAll("circle")
			.attr('r', innerRadius/scale);
		beaconCircles.selectAll("text")
			.attr('style', "font-size: "+ 24/scale +";")
			.attr("dy", function(d){return (proj.latLngToLayerPoint(d.properties.latLonCoordinates).y) + 8/scale; });
		beaconCircles.selectAll("path")
			.attr("d", arc);		

		// entering new stuff
		var bcEnter = beaconCircles.enter().append("g")
			.attr("class", "beaconCircles")
			.on('click', function(d){
				// lat lon for click
				thismap.map._layers[d.properties.leafletId].fire('click');
			})
			.on('mouseover', function(d){ 
				beaconCircles.sort(function (a, b) { 
					if (a.id != d.id) return -1;
					else return 1;
				});
				thismap.map._layers[d.properties.leafletId].fire('mouseover');
			})
			.on('mouseout', function(d){ 
				thismap.map._layers[d.properties.leafletId].fire('mouseout');
			});


		bcEnter.append('circle');
		bcEnter.append('text');
		bcEnter.append('g');
		bcEnter.call(update);


		// exiting old stuff
		beaconCircles.exit().remove();


	});


}


SoundExplorerMap.drawTimeSlider = function (){
	var minDate = new Date(2004,0,1);
	var maxDate = moment().toDate();
	var fiveYearAgo = moment().subtract(5, 'years').toDate();

	mapSlider = d3.slider()
					.axis(
						d3.svg.axis()
							.orient("top")
							.scale(
								d3.time.scale()
									.domain([minDate, maxDate])
							)
							.ticks(d3.time.years)
							.tickSize(24, 0)
							.tickFormat(d3.time.format("%Y"))
					)
					.scale(
						d3.time.scale()
							.domain([minDate, maxDate])
					)
					.value( [ fiveYearAgo, maxDate ] )
					.on("slideend", function(evt, value) {
						$("body").addClass("loading");
						// run a function to update map layers with new dates
						SoundExplorerMap.updateMapFromSlider(value);
						// update combo boxes
						var start_date = moment(value[0]).format('YYYY-MM');
						start_date = start_date + '-01';
						console.log(start_date);
						$( "#start_date" ).val(start_date);
						var end_date = moment(value[1]).format('YYYY-MM');
						end_date = end_date + '-01';
						$( "#end_date" ).val(end_date);
					});

	d3.select('#timeSlider').call(mapSlider);

}

SoundExplorerMap.updateMapFromSlider = function (value){
	// close popups
	MY_MAP.map.closePopup();
	// moment parses unix offsets and javascript date objects in the same way
	var startDate = moment(value[0]).startOf('month').format("YYYY-MM-DD");
	var endDate = moment(value[1]).endOf('month').format("YYYY-MM-DD");

	d3.json('/beaconapi/?startDate=' + startDate + '&endDate=' + endDate, function(data) {
		geojsonData = data;

		$.each(geojsonData.features, function(i, d){
			d.properties.leafletId = 'layerID' + i;
			// create coordiantes with latLon instead of lonLat for use with D3 later
			d.properties.latLonCoordinates = [d.geometry.coordinates[1], d.geometry.coordinates[0]];
			d.properties.pctPass = (d.properties.TotalPassSamples / d.properties.NumberOfSamples) * 100;
			var pctFail = 100 - ((d.properties.TotalPassSamples / d.properties.NumberOfSamples) * 100);
			d.properties.pctPassFail = [{name: "fail", pct: pctFail},{name: "pass", pct: d.properties.pctPass}];
		});

		// clear layer
		MY_MAP.BEACON_POINTS.clearLayers();
		// add new data
		MY_MAP.BEACON_POINTS.addData(geojsonData);

		// remove D3 layer
		MY_MAP.map.removeLayer(MY_MAP.BEACON_D3_POINTS);
		// recreate new D3 layer
		SoundExplorerMap.createBEACON_D3_POINTS(geojsonData.features, MY_MAP);

		// depending on zoom level, add correct one to the map
		if (MY_MAP.map.getZoom() < 10) {
			//check for existance of layers, then add or remove
			if (MY_MAP.map.hasLayer(MY_MAP.BEACON_D3_POINTS)) {
				MY_MAP.map.removeLayer(MY_MAP.BEACON_D3_POINTS);
			}
		} else {
			//check for existance of layers, then add or remove
			if (!MY_MAP.map.hasLayer(MY_MAP.BEACON_D3_POINTS)) {
				MY_MAP.BEACON_D3_POINTS.addTo(MY_MAP.map);
			}
		}

		$("body").removeClass("loading");

	});

}

SoundExplorerMap.checkZoomSwitchLayers = function (){
	// if zoom level is small, show the small dots on the map, otherwise show the big dots with scores
	if (MY_MAP.map.getZoom() < 14) {
		//check for existance of layers, then add or remove
		if (MY_MAP.map.hasLayer(MY_MAP.BEACON_D3_POINTS)) {
			MY_MAP.map.removeLayer(MY_MAP.BEACON_D3_POINTS);
		}
	} else {
		//check for existance of layers, then add or remove
		if (!MY_MAP.map.hasLayer(MY_MAP.BEACON_D3_POINTS)) {
			MY_MAP.BEACON_D3_POINTS.addTo(MY_MAP.map);
		}
	}

}

SoundExplorerMap.modalZoom = function (lat, lon){
	MY_MAP.map.closePopup();
	// when a user opens a modal, have the main map zoom to the dot
	MY_MAP.map.panTo([lat,lon]);
	MY_MAP.map.setZoom(16);
	MY_MAP.map.panBy([400, 200]);

}



