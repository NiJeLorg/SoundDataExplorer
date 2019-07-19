/* 
* Functions to create the main Sound Health Explorer Map
*/

// initialize map
function SoundExplorerMap() {
	// set zoom and center for this map	
    this.center = [41.008338, -72.887421];

    // set body width
    bodyWidth = $('body').width();

    // set zoom 9 on desktop and 8 on mobile
    if (bodyWidth <= 768) {
    	this.zoom = 8;
    } else {
    	this.zoom = 9;
    }

    this.map = new L.Map('map', {
		minZoom:8,
		maxZoom:17,
    	center: this.center,
   	 	zoom: this.zoom,
   	 	zoomControl: false,
   	 	zoomAnimation: true,
   	 	touchZoom: true,
	});

	// locate visitor on map
	this.map.locate();

	var that = this;
	this.map.on('locationfound', function(e) {
		var southWest = L.latLng(40.759074, -73.860741),
    		northEast = L.latLng(41.380351, -71.832733),
    		bounds = L.latLngBounds(southWest, northEast);
    	if (bounds.contains(e.latlng)) {
			that.map.setView(e.latlng, 15);
    	} 
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
	var geocoder = this.map.addControl(L.Control.geocoder({collapsed: true, placeholder:'Search...', geocoder:new L.Control.Geocoder.Nominatim()}));
	
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
	this.SUBWATERSHEDS = null; // just impervious layer with different styling
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
		autoPanPaddingTopLeft: L.point(10, 35)
	});

	// subscribe to zoomend event to show
	this.map.on('zoomend', function(e) {
	    SoundExplorerMap.checkZoomSwitchLayers();
	});

}


SoundExplorerMap.onEachFeature_BEACON_POINTS = function(feature,layer){	
	// we'll now add an ID to each layer so we can fire the mouseover and click outside of the map
    layer._leaflet_id = feature.properties.leafletId;

	var highlight = {
	    weight: 2,
	    color: '#fff'
	};
	var noHighlight = {
        weight: 1,
        color: '#636363'
	};


	layer.bindLabel("<span class='text-capitalize'>" + feature.properties.BeachName + "<br />" + feature.properties.County + "</span> County, " + feature.properties.State, { direction:'auto' });
	
    // onclick set content in bottom bar and open doc if not open already 
	layer.on("click",function(ev){
		console.log(feature.properties.TotalPoints);

		var year_selected = $(".annualFilter.active").val();
		
		if (feature.properties.BeachStory) {
			var beachStory = "<br /><a href='"+ feature.properties.BeachStory +"' target='_blank'>Read this Beach Story</a>";			
		} else {
			var beachStory = "";
		}

		
		MY_MAP.popup.setLatLng(ev.target._latlng);
		if (feature.properties.NumberOfSamples < 9) {
			MY_MAP.popup.setContent(feature.properties.BeachName + "<br /><small>"+ feature.properties.NumberOfSamples + " samples tested in "+ year_selected + ".</small><br />Too few samples to provide a grade. Beaches should be sampled at least once a week during swimming season. Typical swimming season is 16 weeks.<br /><a href='#' data-toggle='modal' data-target='#siteView' data-beachid='"+ feature.properties.BeachID +"' data-beachname='"+ feature.properties.BeachName +"' data-lat='"+ feature.geometry.coordinates[1] +"' data-lon='"+ feature.geometry.coordinates[0] +"'>Enter Site View for more information.</a>");
		} else {
			MY_MAP.popup.setContent(feature.properties.BeachName + "<br /><div class='clearfix'></div><div class='pull-left'><div id='gradeSvgPopup'></div></div><div class='textPopup textDropPopup'><h4 class='text-center'>"+ feature.properties.NumberOfSamples + " samples tested in "+ year_selected + ".</h4></div></div><div class='clearfix'></div><a href='#' data-toggle='modal' data-target='#siteView' data-beachid='"+ feature.properties.BeachID +"' data-beachname='"+ feature.properties.BeachName +"' data-lat='"+ feature.geometry.coordinates[1] +"' data-lon='"+ feature.geometry.coordinates[0] +"'>Enter Site View for more information.</a>"+ beachStory +"<br /><h5>DRY WEATHER</h5><div class='pull-left'><div id='dryFrequency'></div></div><div class='textPopup textDropPopup'><div id='dryFrequencyText'>Hello</div></div><div class='clearfix'></div><div class='pull-left'><div id='dryMagnitude'></div></div><div class='textPopup textDropPopup'><div id='dryMagnitudeText'>Hello</div></div><div class='clearfix'></div><h5>WET WEATHER</h5><div class='pull-left'><div id='wetFrequency'></div></div><div class='textPopup textDropPopup'><div id='wetFrequencyText'>Hello</div></div><div class='clearfix'></div><div class='pull-left'><div id='wetMagnitude'></div></div><div class='textPopup textDropPopup'><div id='wetMagnitudeText'>Hello</div></div><div class='clearfix'></div>");
		}

		MY_MAP.map.openPopup(MY_MAP.popup);

		// draw grade seal after popup is open
		SoundExplorerMap.createGrade(feature);

		if (feature.properties.TotalDryWeatherSamples > 0) {
			SoundExplorerMap.createFrequency(feature.properties.frequencyDryPoints, "#dryFrequency", "#dryFrequencyText");

			SoundExplorerMap.createMagnitude(feature.properties.magnitudeDryPoints, "#dryMagnitude", "#dryMagnitudeText");
		} else {
			SoundExplorerMap.createFrequency(0, "#dryFrequency", "#dryFrequencyText");
			SoundExplorerMap.createMagnitude(0, "#dryMagnitude", "#dryMagnitudeText");
		}

		if (feature.properties.TotalWetWeatherSamples > 0) {
			SoundExplorerMap.createFrequency(feature.properties.frequencyWetPoints, "#wetFrequency", "#wetFrequencyText");

			SoundExplorerMap.createMagnitude(feature.properties.magnitudeWetPoints, "#wetMagnitude", "#wetMagnitudeText");
		} else {
			SoundExplorerMap.createFrequency(0, "#wetFrequency", "#wetFrequencyText");
			SoundExplorerMap.createMagnitude(0, "#wetMagnitude", "#wetMagnitudeText");
		}


	});

    layer.on('mouseover', function(ev) {		

		layer.setStyle(highlight);

		if (!L.Browser.ie && !L.Browser.opera) {
	        //layer.bringToFront();
	    }

    });
		
    layer.on('mouseout', function(ev) {
		layer.setStyle(noHighlight);		
    });	


}

SoundExplorerMap.createGrade = function (feature){
	var w = 70;
	var h = 70;
	var circleRadius = 31;
	var circleStroke = 2;
	var innerRadius = 31;
	var outerRadius = 34;

	var arc = d3.svg.arc()
	    .outerRadius(outerRadius)
	    .innerRadius(innerRadius);

	var pie = d3.layout.pie()
		.sort(null)
		.value(function(d) { return Math.round(d.pct); });

	var gradeSvg = d3.select('#gradeSvgPopup').append('svg')
		.attr('width', w)
		.attr('height', h)
		.append('g')
		.attr("class", "grades")
		.attr("transform", "translate("+w/2+","+h/2+")")
		.selectAll(".arc")
		.data(function(d) { return pie(feature.properties.pctPassFail); });

	gradeSvg.enter().append('circle')
		.attr('r', circleRadius)
		.attr('fill', function(d){
			console.log(feature);
			if (feature.properties.NumberOfSamples < 9) {
				return "#ccc";
			} else {
				return SoundExplorerMap.SDEPctPassColor(feature.properties.TotalPoints);
			}
		})
		.attr('stroke', '#252525')
		.attr('stroke-width', circleStroke);

	gradeSvg.enter().append('text')
		.attr("text-anchor", "middle")
		.attr("transform", "translate(2,13)")
		.attr('style', function(d) { 			
			return "font-size: 42px; font-family:'print_boldregular';"
		})
		.text(function(d) { 
			if (feature.properties.NumberOfSamples < 9) {
				return 'N/A';
			} else {
				return SoundExplorerMap.SDEPctPassGrade(feature.properties.TotalPoints);	
			}
		});


	var rings = gradeSvg.enter()
		.append("path")
		.attr("class", "arc")
		.attr("d", arc)
		.style("fill", function(d) {
			return '#252525';
			// if (d.data.name == "pass") {
			// 	return "#009444";
			// } else {
			// 	return "#be1e2d";
			// }
		});
}

SoundExplorerMap.createFrequency = function (points, div1, div2) {
	var w = 50;
	var h = 25;
	var gradeSvg = d3.select(div1).append('svg')
		.attr('width', w)
		.attr('height', h);

	gradeSvg.append('rect')
		.attr('x', 1)
		.attr('y', 1)
		.attr('width', w-2)
		.attr('height', h-2)
		.attr('fill', function(d){
			return SoundExplorerMap.SDEFreqMagColor(points);
		})
		.attr('stroke', 'black')
		.attr('stroke-width', 1);

	gradeSvg.append('text')
		.attr("text-anchor", "middle")
		.attr("transform", "translate(25,17)")
		.attr('style', function(d) { 			
			return "font-size: 14px; font-family:'print_boldregular'; }"
		})
		.text("FRQ");

	$(div2).text(SoundExplorerMap.frequencyText(points));

}

SoundExplorerMap.createMagnitude = function (points, div1, div2) {
	var w = 50;
	var h = 25;
	var gradeSvg = d3.select(div1).append('svg')
		.attr('width', w)
		.attr('height', h);

	gradeSvg.append('rect')
		.attr('x', 1)
		.attr('y', 1)
		.attr('width', w-2)
		.attr('height', h-2)
		.attr('fill', function(d){
			return SoundExplorerMap.SDEFreqMagColor(points);
		})
		.attr('stroke', 'black')
		.attr('stroke-width', 1);

	gradeSvg.append('text')
		.attr("text-anchor", "middle")
		.attr("transform", "translate(25,17)")
		.attr('style', function(d) { 			
			return "font-size: 14px; font-family:'print_boldregular'; }"
		})
		.text("MAG");

	$(div2).text(SoundExplorerMap.magnitudeText(points));

}


SoundExplorerMap.prototype.loadPointLayers = function (){
	// load points layers
	var thismap = this;

	startDate = moment(startDate).format("YYYY-MM-DD");
	endDate = moment(endDate).format("YYYY-MM-DD");

	d3.json('/beaconapi/?startDate=' + startDate + '&endDate=' + endDate, function(data) {
		geojsonData = data;

		geojsonData = SoundExplorerMap.processData(geojsonData);

		thismap.BEACON_POINTS = L.geoJson(geojsonData, {
		    pointToLayer: SoundExplorerMap.getStyleFor_BEACON_POINTS,
			onEachFeature: SoundExplorerMap.onEachFeature_BEACON_POINTS
		}).addTo(thismap.map);

		// create the D3 layer for Beacon data, but don't add to map until we hit a specfic zoom level
		SoundExplorerMap.createBEACON_D3_POINTS(geojsonData.features, thismap);

	});

}


SoundExplorerMap.getStyleFor_BEACON_POINTS = function (feature, latlng){
	if (feature.properties.NumberOfSamples < 9) {
		var marker = L.circleMarker(latlng, {
			radius: 6,
			color: '#636363',
			weight: 1,
			opacity: 1,
			fillColor: "#ccc",
			fillOpacity: 1
		});		
	} else {
		var marker = L.circleMarker(latlng, {
			radius: 6,
			color: '#636363',
			weight: 1,
			opacity: 1,
			fillColor: SoundExplorerMap.SDEPctPassColor(feature.properties.TotalPoints),
			fillOpacity: 1
		});		
	}

	
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

SoundExplorerMap.onEachFeature_SUBWATERSHEDS = function(feature,layer){

	layer.bindLabel(feature.properties.Name, { direction:'auto' });

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
		thismap.SUBWATERSHEDS = L.geoJson(imperviousTopojson, {
		    style: SoundExplorerMap.getStyleFor_SUBWATERSHEDS,
			onEachFeature: SoundExplorerMap.onEachFeature_SUBWATERSHEDS
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

	thismap.WASTEWATER_NY = L.esri.featureLayer({
		url: "http://services.arcgis.com/jDGuO8tYggdCCnUJ/ArcGIS/rest/services/Municipal_wastewater_discharge_facilities_in_NYS/FeatureServer/0",
		pointToLayer: SoundExplorerMap.getStyleFor_WASTEWATER,
		onEachFeature: SoundExplorerMap.onEachFeature_WASTEWATER_NY
	});

	thismap.LANDUSE = L.esri.dynamicMapLayer({
	    url: 'http://gis1.usgs.gov/arcgis/rest/services/gap/GAP_Land_Cover_NVC_Class_Landuse/MapServer',
	    opacity: 0.5,
	    useCors: false
	});

	

	thismap.LANDUSE.on('load', function(e){
	  $("body").removeClass("loading");
	});



}

SoundExplorerMap.getStyleFor_BOATLAUNCH = function (feature, latlng){

	var pointMarker = L.circleMarker(latlng, {
		radius: 5,
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
		radius: 5,
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

SoundExplorerMap.getStyleFor_SUBWATERSHEDS = function (feature){	
    return {
        weight: 1,
        opacity: 0.75,
        color: '#000',
        fillOpacity: 0.25,
        fillColor: '#9ecae1'
    }
}

SoundExplorerMap.getStyleFor_WATERSHEDS = function (feature){
	
    return {
        weight: 1,
        opacity: 0.75,
        color: '#000',
        fillOpacity: 0.25,
        fillColor: '#08519c'
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
		radius: 5,
		color: '#bdbdbd',
		weight: 1,
		opacity: 1,
		fillColor: '#8856a7',
		fillOpacity: 1
	});
	
	return pointMarker;
	
}



SoundExplorerMap.addLayers = function (layer){
	if (layer == "beacon") {
		MY_MAP.BEACON_POINTS.addTo(MY_MAP.map);
		if (MY_MAP.map.getZoom() >= 12) {
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
		MY_MAP.IMPERVIOUS.addTo(MY_MAP.map).bringToBack();
	}
	if (layer == "watersheds") {
		MY_MAP.WATERSHEDS.addTo(MY_MAP.map).bringToBack();;
	}
	if (layer == "subwatersheds") {
		MY_MAP.SUBWATERSHEDS.addTo(MY_MAP.map).bringToBack();
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
	if (layer == "subwatersheds") {
		MY_MAP.map.removeLayer(MY_MAP.SUBWATERSHEDS);
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

SoundExplorerMap.SDEFreqMagColor = function (d){
    return d >= 7 ? '#2bb673' :
           d >= 5 ? '#fff200' :
           d >= 3 ? '#f7941d' :
           d >= 1 ? '#ef4136' :
                   	'#bcbec0' ;	
}

SoundExplorerMap.frequencyText = function (d){
    return d >= 7 ? 'Consistently Passes' :
           d >= 5 ? 'Rarely Fails' :
           d >= 3 ? 'Sometimes Fails' :
           d >= 1 ? 'Consistently Fails' :
                   	'Not Enough Data' ;	
}

SoundExplorerMap.magnitudeText = function (d){
    return d >= 7 ? 'No Sample Failure' :
           d >= 5 ? 'Low Intensity Failure' :
           d >= 3 ? 'Medium Intensity Failure' :
           d >= 1 ? 'High Intensity Failure' :
                   	'Not Enough Data' ;	
}

SoundExplorerMap.SDEPctPassColor = function (d){
    return d >= 23 ? '#2bb673' :
           d >= 17 ? '#c3db67' :
           d >= 11 ? '#fff200' :
           d >= 5  ? '#f7941d' :
           d >= 0  ? '#ef4136' :
                   	 '#bcbec0' ;	
}

SoundExplorerMap.SDEPctPassGrade = function (d){
    return d >= 27 ? 'A+' :
           d >= 25 ? 'A' :
           d >= 23 ? 'A-' :
           d >= 21 ? 'B+' :
           d >= 19 ? 'B' :
           d >= 17 ? 'B-' :
           d >= 15 ? 'C+' :
           d >= 13 ? 'C' :
           d >= 11 ? 'C-' :
           d >= 9  ? 'D+' :
           d >= 7  ? 'D' :
           d >= 5  ? 'D-' :
           d >= 0  ? 'F' :
                   	 '' ;	
}

SoundExplorerMap.MagnitudePoints = function (d){
    return d > 1040 ? 1:
           d > 521  ? 3:
           d > 105  ? 5:
                   	  7;	
}

SoundExplorerMap.FrequencyPoints = function (d){
    return d > 23 ? 1:
           d > 10 ? 3:
           d > 5  ? 5:
                   	7;	
}


SoundExplorerMap.createBEACON_D3_POINTS = function (features, thismap) {
	var circleRadius = 21;
	var circleStroke = 2;
	var innerRadius = 21;
	var outerRadius = 24;

	thismap.BEACON_D3_POINTS = L.d3SvgOverlay( function(sel,proj){

		// create dots with the same color as the leaflet overlay dots and create on hover and click interactions

		function update() {
			//updating
			beaconCircles.select('circle')
				.attr('r', circleRadius/scale)
				.attr('cx',function(d){ return proj.latLngToLayerPoint(d.properties.latLonCoordinates).x;})
				.attr('cy',function(d){ return proj.latLngToLayerPoint(d.properties.latLonCoordinates).y;})
				.attr('fill', function(d){
					if (d.properties.NumberOfSamples < 9) {
						return "#ccc";
					} else {
						return SoundExplorerMap.SDEPctPassColor(d.properties.TotalPoints);
					}
				})
				.attr('stroke', '#252525')
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
					return '#252525';
					// if (d.data.name == "pass") {
					// 	return "#009444";
					// } else {
					// 	return "#be1e2d";
					// }
				});

			beaconCircles.select("text")
				.attr("text-anchor", "middle")
				.attr("dx", function(d){ return proj.latLngToLayerPoint(d.properties.latLonCoordinates).x;})
				.attr("dy", function(d){return (proj.latLngToLayerPoint(d.properties.latLonCoordinates).y) + 8/scale; })
				.attr('style', "font-size: "+ 24/scale +"px;")
				.text(function(d) { 
					if (d.properties.NumberOfSamples < 9) {
						return 'N/A';
					} else {
						return SoundExplorerMap.SDEPctPassGrade(d.properties.TotalPoints);	
					}
				});

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
			.attr('style', "font-size: "+ 24/scale +"px;")
			.attr("dy", function(d){return (proj.latLngToLayerPoint(d.properties.latLonCoordinates).y) + 8/scale; });
		beaconCircles.selectAll("path")
			.attr("d", arc);		

		// entering new stuff
		var bcEnter = beaconCircles.enter().append("g")
			.attr("class", "beaconCircles");

		bcEnter.append('circle');
		bcEnter.append('text');
		bcEnter.append('g');
		bcEnter.call(update);

		// exiting old stuff
		beaconCircles.exit().remove();


	}, {zoomAnimate: true, zoomHide: false});


}


SoundExplorerMap.updateMapFromSlider = function (value, main){
	// close popups
	MY_MAP.map.closePopup();
	// moment parses unix offsets and javascript date objects in the same way
	var startDate = moment(value[0]).startOf('month');
	var endDate = moment(value[1]).endOf('month').format("YYYY-MM-DD");

	var earliestDate = moment(new Date(2004,0,1));
	if (startDate.isBefore(earliestDate)) {
		startDate = earliestDate;
	}

	startDate = startDate.format("YYYY-MM-DD");

	// update map
	d3.json('/beaconapi/?startDate=' + startDate + '&endDate=' + endDate, function(data) {
		geojsonData = data;

		geojsonData = SoundExplorerMap.processData(geojsonData);

		// clear layer
		MY_MAP.BEACON_POINTS.clearLayers();
		// add new data
		MY_MAP.BEACON_POINTS.addData(geojsonData);

		// remove D3 layer
		MY_MAP.map.removeLayer(MY_MAP.BEACON_D3_POINTS);
		// recreate new D3 layer
		SoundExplorerMap.createBEACON_D3_POINTS(geojsonData.features, MY_MAP);

		// if zoom level is small, show the small dots on the map, otherwise show the big dots with scores
		if (MY_MAP.map.getZoom() < 12) {
			//check for existance of layers, then add or remove
			if (MY_MAP.map.hasLayer(MY_MAP.BEACON_D3_POINTS)) {
				MY_MAP.map.removeLayer(MY_MAP.BEACON_D3_POINTS);
			}
			MY_MAP.BEACON_POINTS.setStyle({radius: 6});
		} else {
			//check for existance of layers, then add or remove
			if (!MY_MAP.map.hasLayer(MY_MAP.BEACON_D3_POINTS)) {
				MY_MAP.BEACON_D3_POINTS.addTo(MY_MAP.map);
			}
			MY_MAP.BEACON_POINTS.setStyle({radius: 24});
		}

		if (main == true) {
			$("body").removeClass("loading");
		}
		

	});

}

SoundExplorerMap.processData = function (geojsonData){
	$.each(geojsonData.features, function(i, d){
		d.properties.leafletId = 'layerID' + i;
		// create coordiantes with latLon instead of lonLat for use with D3 later
		d.properties.latLonCoordinates = [d.geometry.coordinates[1], d.geometry.coordinates[0]];
		if (d.properties.NumberOfSamples > 0) {
			// calculate scoring
			// Magnitude Dry
			if (d.properties.TotalDryWeatherSamples > 0) {
				d.properties.magnitudeDryPoints = SoundExplorerMap.MagnitudePoints(d.properties.MaxValueDry);
			} else {
				d.properties.magnitudeDryPoints = SoundExplorerMap.MagnitudePoints(d.properties.MaxValueWet);
			}
			
			// Magnitude Wet
			if (d.properties.TotalWetWeatherSamples > 0) {
				d.properties.magnitudeWetPoints = SoundExplorerMap.MagnitudePoints(d.properties.MaxValueWet);	
			} else {
				d.properties.magnitudeWetPoints = SoundExplorerMap.MagnitudePoints(d.properties.MaxValueDry);
			}		

			d.properties.pctPass = Math.round((d.properties.TotalPassSamples / d.properties.NumberOfSamples) * 100);
			d.properties.pctPassNotRounded = (d.properties.TotalPassSamples / d.properties.NumberOfSamples) * 100;
			d.properties.pctFail = Math.round(100 - ((d.properties.TotalPassSamples / d.properties.NumberOfSamples) * 100));
			d.properties.pctPassFail = [{name: "fail", pct: d.properties.pctFail}, {name: "pass", pct: d.properties.pctPass}];

			// Frequency Dry
			if (d.properties.TotalDryWeatherSamples > 0) {
				d.properties.frequencyDryPoints = SoundExplorerMap.FrequencyPoints(100 - ((d.properties.DryWeatherPassSamples / d.properties.TotalDryWeatherSamples) * 100));
			} else {
				d.properties.frequencyDryPoints = SoundExplorerMap.FrequencyPoints(100 - ((d.properties.WetWeatherPassSamples / d.properties.TotalWetWeatherSamples) * 100));
			} 

			// Frequency Wet
			if (d.properties.TotalWetWeatherSamples > 0) {
				d.properties.frequencyWetPoints = SoundExplorerMap.FrequencyPoints(100 - ((d.properties.WetWeatherPassSamples / d.properties.TotalWetWeatherSamples) * 100));
			} else {
				d.properties.frequencyWetPoints = SoundExplorerMap.FrequencyPoints(100 - ((d.properties.DryWeatherPassSamples / d.properties.TotalDryWeatherSamples) * 100));
			}
			
			// Total points
			d.properties.TotalPoints = d.properties.magnitudeDryPoints + d.properties.magnitudeWetPoints + d.properties.frequencyDryPoints + d.properties.frequencyWetPoints;

		} else {
			d.properties.pctPass = 100;
			d.properties.pctPassNotRounded = 100;
			d.properties.pctFail = 0;
			d.properties.pctPassFail = [{name: "fail", pct: d.properties.pctFail}, {name: "pass", pct: d.properties.pctPass}];
			d.properties.magnitudeDryPoints = 7;
			d.properties.magnitudeWetPoints = 7;
			d.properties.frequencyDryPoints = 7;
			d.properties.frequencyWetPoints = 7;
			d.properties.TotalPoints = d.properties.magnitudeDryPoints + d.properties.magnitudeWetPoints + d.properties.frequencyDryPoints + d.properties.frequencyWetPoints;

		}
	});
	return geojsonData;
}

SoundExplorerMap.checkZoomSwitchLayers = function (){
	// if zoom level is small, show the small dots on the map, otherwise show the big dots with scores
	// only if checked 
	if ($( "#beacon" ).prop('checked')) {
		if (MY_MAP.map.getZoom() < 12) {
			//check for existance of layers, then add or remove
			if (MY_MAP.map.hasLayer(MY_MAP.BEACON_D3_POINTS)) {
				MY_MAP.map.removeLayer(MY_MAP.BEACON_D3_POINTS);
			}
			MY_MAP.BEACON_POINTS.setStyle({radius: 6});
		} else {
			//check for existance of layers, then add or remove
			if (!MY_MAP.map.hasLayer(MY_MAP.BEACON_D3_POINTS)) {
				MY_MAP.BEACON_D3_POINTS.addTo(MY_MAP.map);
			}
			MY_MAP.BEACON_POINTS.setStyle({radius: 24});
		}		
	}

}

SoundExplorerMap.modalZoom = function (lat, lon){
	MY_MAP.map.closePopup();
	// when a user opens a modal, have the main map zoom to the dot
	MY_MAP.map.panTo([lat,lon]);
	MY_MAP.map.setZoom(15);
	MY_MAP.map.panBy([50, 100]);

}



