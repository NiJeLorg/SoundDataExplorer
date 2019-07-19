/* 
* Functions to create the main Sound Health Explorer Map
*/



// initialize map
function SoundExplorerModalMap(lat, lon) {
	// set zoom and center for this map	
    this.center = [lat, lon];
    this.zoom = 16;

    this.map = new L.Map('modalMap', {
		minZoom:14,
		maxZoom:17,
    	center: this.center,
   	 	zoom: this.zoom,
   	 	zoomControl: false,
	});
	
	// add CartoDB tiles
	/*
	this.CartoDBLayer = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',{
	  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
	});
	this.map.addLayer(this.CartoDBLayer);
	*/

	this.OSMHOTLayer = L.tileLayer('http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',{
	  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="http://hotosm.org/">OSM HOT</a>'
	});
	this.map.addLayer(this.OSMHOTLayer);

	// load zoom control in top right
	this.map.addControl(L.control.zoom({ position: 'topright' }));

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


}


SoundExplorerModalMap.onEachFeature_BEACON_POINTS = function(feature,layer){	

	layer.bindLabel("<span class='text-capitalize'>" + feature.properties.BeachName + "<br />" + feature.properties.County + "</span> County, " + feature.properties.State, { direction:'auto' });

	layer.on('mouseover', function(ev) {		
    });
		
    layer.on('mouseout', function(ev) {
    });	


	// we'll now add an ID to each layer so we can fire the mouseover and click outside of the map
    layer._leaflet_id = feature.properties.leafletId;

}


SoundExplorerModalMap.prototype.loadPointLayers = function (){
	// load points layers
	var thismap = this;

	// create date for today and for 5 years ago
	var startDate = moment($( ".annualFilter.active" ).val(), "YYYY").startOf('year').format("YYYY-MM-DD");
	var endDate = moment($( ".annualFilter.active" ).val(), "YYYY").endOf('year').format("YYYY-MM-DD");

	d3.json('/beaconapi/?startDate=' + startDate + '&endDate=' + endDate, function(data) {
		geojsonData = data;

		geojsonData = SoundExplorerModalMap.processData(geojsonData);

		thismap.BEACON_POINTS = L.geoJson(geojsonData, {
		    pointToLayer: SoundExplorerModalMap.getStyleFor_BEACON_POINTS,
			onEachFeature: SoundExplorerModalMap.onEachFeature_BEACON_POINTS
		});

		if ($('#beacon').prop('checked')) {
			thismap.BEACON_POINTS.addTo(thismap.map);
		}

		// create the D3 layer for Beacon data, but don't add to map until we hit a specfic zoom level
		SoundExplorerModalMap.createBEACON_D3_POINTS(geojsonData.features, thismap);

	});

}


SoundExplorerModalMap.getStyleFor_BEACON_POINTS = function (feature, latlng){
	if (feature.properties.NumberOfSamples < 9) {
		var marker = L.circleMarker(latlng, {
			radius: 0,
			color: '#636363',
			weight: 1,
			opacity: 1,
			fillColor: "#ccc",
			fillOpacity: 1
		});		
	} else {
		var marker = L.circleMarker(latlng, {
			radius: 0,
			color: '#636363',
			weight: 1,
			opacity: 1,
			fillColor: SoundExplorerModalMap.SDEPctPassColor(feature.properties.pctPassNotRounded),
			fillOpacity: 1
		});		
	}

	
	return marker;
	
}


SoundExplorerModalMap.onEachFeature_BOATLAUNCH = function(feature,layer){

	layer.bindLabel(feature.properties.Name, { direction:'auto' });

}

SoundExplorerModalMap.onEachFeature_CSOS = function(feature,layer){

	layer.bindLabel(feature.properties.facility + "<br />Permit Number: " + feature.properties.spdes_num, { direction:'auto' });

}

SoundExplorerModalMap.onEachFeature_CSOS_CT = function(feature,layer){

	layer.bindLabel(feature.properties.Location + "<br />" + feature.properties.TownName, { direction:'auto' });

}

SoundExplorerModalMap.onEachFeature_IMPERVIOUS = function(feature,layer){
	var pctIS10 = (feature.properties.pctIS10).toFixed(1);

	layer.bindLabel(feature.properties.Name + "<br />" + pctIS10 + "% impervious surfaces", { direction:'auto' });

}

SoundExplorerModalMap.onEachFeature_SUBWATERSHEDS = function(feature,layer){

	layer.bindLabel(feature.properties.Name, { direction:'auto' });

}

SoundExplorerModalMap.onEachFeature_WATERSHEDS = function(feature,layer){

	layer.bindLabel(feature.properties.Name, { direction:'auto' });

}

SoundExplorerModalMap.onEachFeature_SHELLFISH = function(feature,layer){

	layer.bindLabel(feature.properties.CLASS, { direction:'auto' });

}

SoundExplorerModalMap.onEachFeature_WASTEWATER_CT = function(feature,layer){

	layer.bindLabel(feature.properties.FAC_NAME + "<br />Permit Number: " + feature.properties.NPDES_PRMT, { direction:'auto' });

}

SoundExplorerModalMap.onEachFeature_WASTEWATER_NY = function(feature,layer){

	layer.bindLabel(feature.properties.Facility_N + "<br />Permit Number: " + feature.properties.SPDES_ID, { direction:'auto' });

}


SoundExplorerModalMap.prototype.loadExtraLayers = function (){
	// load all other layers -- don't show yet
	var thismap = this;

	d3.json(boatlaunch, function(data) {
		var boatlaunchTopojson = topojson.feature(data, data.objects.boatlaunch_ny_ct).features;
		drawBoatlaunch(boatlaunchTopojson);
	});

	function drawBoatlaunch(boatlaunchTopojson) {
		thismap.BOATLAUNCH = L.geoJson(boatlaunchTopojson, {
		    pointToLayer: SoundExplorerModalMap.getStyleFor_BOATLAUNCH,
			onEachFeature: SoundExplorerModalMap.onEachFeature_BOATLAUNCH
		});

		if ($('#boatlaunch').prop('checked')) {
			thismap.BOATLAUNCH.addTo(thismap.map);
		}
	}

	d3.json(csos, function(data) {
		var csosTopojson = topojson.feature(data, data.objects.CSOs_LISound_NY).features;
		drawCsos(csosTopojson);
	});

	function drawCsos(csosTopojson) {
		thismap.CSOS = L.geoJson(csosTopojson, {
		    pointToLayer: SoundExplorerModalMap.getStyleFor_CSOS,
			onEachFeature: SoundExplorerModalMap.onEachFeature_CSOS
		});

		if ($('#csos').prop('checked')) {
			thismap.CSOS.addTo(thismap.map);
		}

	}

	d3.json(csos_CT, function(data) {
		var csos_CTTopojson = topojson.feature(data, data.objects.CT_Municipal_CSO_Locations_4326).features;
		drawcsos_CT(csos_CTTopojson);
	});

	function drawcsos_CT(csos_CTTopojson) {
		thismap.CSOS_CT = L.geoJson(csos_CTTopojson, {
		    pointToLayer: SoundExplorerModalMap.getStyleFor_CSOS,
			onEachFeature: SoundExplorerModalMap.onEachFeature_CSOS_CT
		});

		if ($('#csos').prop('checked')) {
			thismap.CSOS_CT.addTo(thismap.map);
		}

	}

	d3.json(impervious, function(data) {
		var imperviousTopojson = topojson.feature(data, data.objects.IS_estimates_ALL_4326).features;
		drawImpervious(imperviousTopojson);
	});

	function drawImpervious(imperviousTopojson) {
		thismap.IMPERVIOUS = L.geoJson(imperviousTopojson, {
		    style: SoundExplorerModalMap.getStyleFor_IMPERVIOUS,
			onEachFeature: SoundExplorerModalMap.onEachFeature_IMPERVIOUS
		});

		if ($('#impervious').prop('checked')) {
			thismap.IMPERVIOUS.addTo(thismap.map).bringToBack();
		}

		thismap.SUBWATERSHEDS = L.geoJson(imperviousTopojson, {
		    style: SoundExplorerModalMap.getStyleFor_SUBWATERSHEDS,
			onEachFeature: SoundExplorerModalMap.onEachFeature_SUBWATERSHEDS
		});

		if ($('#subwatersheds').prop('checked')) {
			thismap.SUBWATERSHEDS.addTo(thismap.map).bringToBack();
		}
	}

	d3.json(watersheds, function(data) {
		var watershedsTopojson = topojson.feature(data, data.objects.NY_CT_LIS_watersheds2).features;
		drawWatersheds(watershedsTopojson);
	});

	function drawWatersheds(watershedsTopojson) {
		thismap.WATERSHEDS = L.geoJson(watershedsTopojson, {
		    style: SoundExplorerModalMap.getStyleFor_WATERSHEDS,
			onEachFeature: SoundExplorerModalMap.onEachFeature_WATERSHEDS
		});	

		if ($('#watersheds').prop('checked')) {
			thismap.WATERSHEDS.addTo(thismap.map).bringToBack();
		}
	
	}

	d3.json(shellfish, function(data) {
		var shellfishTopojson = topojson.feature(data, data.objects.SHELLFISH_AREA_CLASS_POLY_4326).features;
		drawShellfish(shellfishTopojson);

	});

	function drawShellfish(shellfishTopojson) {
		thismap.SHELLFISH = L.geoJson(shellfishTopojson, {
		    style: SoundExplorerModalMap.getStyleFor_SHELLFISH,
			onEachFeature: SoundExplorerModalMap.onEachFeature_SHELLFISH
		});

		if ($('#shellfish').prop('checked')) {
			thismap.SHELLFISH.addTo(thismap.map).bringToBack();
		}
	}

	// two wastewater layers -- one for CT and one for NY
	d3.json(wastewater_CT, function(data) {
		var wastewater_CTTopojson = topojson.feature(data, data.objects.stp_2013_4326).features;
		drawWastewater_CT(wastewater_CTTopojson);

	});

	function drawWastewater_CT(wastewater_CTTopojson) {
		thismap.WASTEWATER_CT = L.geoJson(wastewater_CTTopojson, {
		    pointToLayer: SoundExplorerModalMap.getStyleFor_WASTEWATER,
			onEachFeature: SoundExplorerModalMap.onEachFeature_WASTEWATER_CT
		});

		if ($('#wastewater').prop('checked')) {
			thismap.WASTEWATER_CT.addTo(thismap.map);
		}

	}

	/*
	d3.json(wastewater_NY, function(data) {
		var wastewater_NYTopojson = topojson.feature(data, data.objects.wastewater_NY).features;
		drawWastewater_NY(wastewater_NYTopojson);

	});

	function drawWastewater_NY(wastewater_NYTopojson) {
		thismap.WASTEWATER_NY = L.geoJson(wastewater_NYTopojson, {
		    pointToLayer: SoundExplorerModalMap.getStyleFor_WASTEWATER,
			onEachFeature: SoundExplorerModalMap.onEachFeature_WASTEWATER_NY
		});
	}
	*/

	thismap.WASTEWATER_NY = L.esri.featureLayer({
		url: "http://services.arcgis.com/jDGuO8tYggdCCnUJ/ArcGIS/rest/services/Municipal_wastewater_discharge_facilities_in_NYS/FeatureServer/0",
		pointToLayer: SoundExplorerMap.getStyleFor_WASTEWATER,
		onEachFeature: SoundExplorerMap.onEachFeature_WASTEWATER_NY
	});

	if ($('#wastewater').prop('checked')) {
		thismap.WASTEWATER_NY.addTo(thismap.map);
	}

	thismap.LANDUSE = L.esri.dynamicMapLayer({
	    url: 'http://gis1.usgs.gov/arcgis/rest/services/gap/GAP_Land_Cover_NVC_Class_Landuse/MapServer',
	    opacity: 0.5,
	    useCors: false
	});

	thismap.LANDUSE.on('load', function(e){
	  $("body").removeClass("loading");
	});

	if ($('#landuse').prop('checked')) {
		thismap.LANDUSE.addTo(thismap.map).bringToBack();
	}



}

SoundExplorerModalMap.getStyleFor_BOATLAUNCH = function (feature, latlng){

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


SoundExplorerModalMap.getStyleFor_CSOS = function (feature, latlng){

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

SoundExplorerModalMap.getStyleFor_IMPERVIOUS = function (feature){
	var pctIS10 = (feature.properties.pctIS10).toFixed(1);
	
    return {
        weight: 1,
        opacity: 0.75,
        color: '#f1f1f1',
        fillOpacity: 0.75,
        fillColor: SoundExplorerModalMap.fillColor_IMPERVIOUS(pctIS10)
    }
}

SoundExplorerModalMap.getStyleFor_SUBWATERSHEDS = function (feature){	
    return {
        weight: 1,
        opacity: 0.75,
        color: '#000',
        fillOpacity: 0.75,
        fillColor: '#9ecae1'
    }
}

SoundExplorerModalMap.getStyleFor_WATERSHEDS = function (feature){
	
    return {
        weight: 1,
        opacity: 0.75,
        color: '#000',
        fillOpacity: 0.5,
        fillColor: '#08519c'
    }
}

SoundExplorerModalMap.getStyleFor_SHELLFISH = function (feature){
	
    return {
        weight: 1,
        opacity: 0.75,
        color: '#f1f1f1',
        fillOpacity: 0.75,
        fillColor: SoundExplorerModalMap.fillColor_SHELLFISH(feature.properties.AV_LEGEND)
    }
}

SoundExplorerModalMap.getStyleFor_WASTEWATER = function (feature, latlng){

	var pointMarker = L.circleMarker(latlng, {
		radius: 5,
		color: '#bdbdbd',
		weight: 1,
		opacity: 1,
		fillColor: '#35978f',
		fillOpacity: 1
	});
	
	return pointMarker;
	
}


SoundExplorerModalMap.addLayers = function (layer){
	if (layer == "beacon") {
		MY_MAP_MODAL.BEACON_POINTS.addTo(MY_MAP_MODAL.map).bringToFront();
		MY_MAP_MODAL.BEACON_D3_POINTS.addTo(MY_MAP_MODAL.map).bringToFront();
	}
	if (layer == "boatlaunch") {
		MY_MAP_MODAL.BOATLAUNCH.addTo(MY_MAP_MODAL.map);
	}
	if (layer == "csos") {
		MY_MAP_MODAL.CSOS.addTo(MY_MAP_MODAL.map);
		MY_MAP_MODAL.CSOS_CT.addTo(MY_MAP_MODAL.map);
	}
	if (layer == "impervious") {
		MY_MAP_MODAL.IMPERVIOUS.addTo(MY_MAP_MODAL.map).bringToBack();
	}
	if (layer == "watersheds") {
		MY_MAP_MODAL.WATERSHEDS.addTo(MY_MAP_MODAL.map).bringToBack();
	}
	if (layer == "subwatersheds") {
		MY_MAP_MODAL.SUBWATERSHEDS.addTo(MY_MAP_MODAL.map).bringToBack();
	}
	if (layer == "shellfish") {
		MY_MAP_MODAL.SHELLFISH.addTo(MY_MAP_MODAL.map).bringToBack();
	}
	if (layer == "wastewater") {
		MY_MAP_MODAL.WASTEWATER_CT.addTo(MY_MAP_MODAL.map);
		MY_MAP_MODAL.WASTEWATER_NY.addTo(MY_MAP_MODAL.map);
	}
	if (layer == "landuse") {
		MY_MAP_MODAL.LANDUSE.addTo(MY_MAP_MODAL.map).bringToBack();
	}

	if (MY_MAP_MODAL.map.hasLayer(MY_MAP_MODAL.BEACON_POINTS)) {
		MY_MAP_MODAL.BEACON_POINTS.bringToFront();
	}

}

SoundExplorerModalMap.removeLayers = function (layer){
	if (layer == "beacon") {
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.BEACON_POINTS);
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.BEACON_D3_POINTS);
	}
	if (layer == "boatlaunch") {
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.BOATLAUNCH);
	}
	if (layer == "csos") {
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.CSOS);
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.CSOS_CT);
	}
	if (layer == "impervious") {
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.IMPERVIOUS);
	}
	if (layer == "watersheds") {
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.WATERSHEDS);
	}
	if (layer == "subwatersheds") {
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.SUBWATERSHEDS);
	}
	if (layer == "shellfish") {
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.SHELLFISH);
	}
	if (layer == "wastewater") {
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.WASTEWATER_CT);
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.WASTEWATER_NY);
	}
	if (layer == "landuse") {
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.LANDUSE);
	}

}


SoundExplorerModalMap.fillColor_SHELLFISH = function (d){
    return d == 'A' ? '#a6cee3' :
           d == 'CA' ? '#1f78b4' :
           d == 'R-R/DP' ? '#b2df8a' :
           d == 'CR-R/DP' ? '#33a02c' :
           d == 'R-R' ? '#fb9a99' :
           d == 'CR-R' ? '#e31a1c' :
           d == 'P' ? '#fdbf6f' :
                   	'#fff' ;	

}

SoundExplorerModalMap.fillColor_IMPERVIOUS = function (d){
    return d > 25 ? '#252525' :
           d > 20 ? '#636363' :
           d > 15 ? '#969696' :
           d > 10 ? '#bdbdbd' :
           d > 5  ? '#d9d9d9' :
                   	'#f7f7f7' ;	

}


SoundExplorerModalMap.SDEFreqMagColor = function (d){
    return d >= 7 ? '#2bb673' :
           d >= 5 ? '#fff200' :
           d >= 3 ? '#f7941d' :
           d >= 1 ? '#ef4136' :
                   	'#545454' ;	
}

SoundExplorerModalMap.frequencyText = function (d){
    return d >= 7 ? 'Consistently Passes' :
           d >= 5 ? 'Rarely Fails' :
           d >= 3 ? 'Sometimes Fails' :
           d >= 1 ? 'Consistently Fails' :
                   	'' ;	
}

SoundExplorerModalMap.magnitudeText = function (d){
    return d >= 7 ? 'No Sample Failure' :
           d >= 5 ? 'Low Intensity Failure' :
           d >= 3 ? 'Medium Intensity Failure' :
           d >= 1 ? 'High Intensity Fails' :
                   	'' ;	
}

SoundExplorerModalMap.SDEPctPassColor = function (d){
    return d >= 23 ? '#2bb673' :
           d >= 17 ? '#c3db67' :
           d >= 11 ? '#fff200' :
           d >= 5  ? '#f7941d' :
           d >= 0  ? '#ef4136' :
                   	 '#545454' ;	
}

SoundExplorerModalMap.SDEPctPassGrade = function (d){
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

SoundExplorerModalMap.MagnitudePoints = function (d){
    return d > 1040 ? 1:
           d > 521  ? 3:
           d > 105  ? 5:
                   	  7;	
}

SoundExplorerModalMap.FrequencyPoints = function (d){
    return d > 23 ? 1:
           d > 10 ? 3:
           d > 5  ? 5:
                   	7;	
}



SoundExplorerModalMap.createBEACON_D3_POINTS = function (features, thismap) {
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
						return SoundExplorerModalMap.SDEPctPassColor(d.properties.TotalPoints);
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
						return SoundExplorerModalMap.SDEPctPassGrade(d.properties.TotalPoints);	
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
			.attr("class", "beaconCircles")
			.on('mouseover', function(d){ 
				beaconCircles.sort(function (a, b) { 
					if (a.id != d.id) return -1;
					else return 1;
				});
			});


		bcEnter.append('circle');
		bcEnter.append('text');
		bcEnter.append('g');
		bcEnter.call(update);


		// exiting old stuff
		beaconCircles.exit().remove();


	});

	if ($('#beacon').prop('checked')) {
		thismap.BEACON_D3_POINTS.addTo(thismap.map);
	}



}

SoundExplorerModalMap.updateMapFromSlider = function (value){
	// close popups
	MY_MAP_MODAL.map.closePopup();
	// moment parses unix offsets and javascript date objects in the same way
	var startDate = moment(value[0]).startOf('month');
	var endDate = moment(value[1]).endOf('month').format("YYYY-MM-DD");

	var earliestDate = moment(new Date(2004,0,1));
	if (startDate.isBefore(earliestDate)) {
		startDate = earliestDate;
	}

	startDate = startDate.format("YYYY-MM-DD");


	d3.json('/beaconapi/?startDate=' + startDate + '&endDate=' + endDate, function(data) {
		geojsonData = data;

		geojsonData = SoundExplorerModalMap.processData(geojsonData);

		// clear layer
		MY_MAP_MODAL.BEACON_POINTS.clearLayers();
		// add new data
		MY_MAP_MODAL.BEACON_POINTS.addData(geojsonData);

		// remove D3 layer
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.BEACON_D3_POINTS);
		// recreate new D3 layer
		SoundExplorerModalMap.createBEACON_D3_POINTS(geojsonData.features, MY_MAP_MODAL);
		
	});

}

SoundExplorerModalMap.processData = function (geojsonData){
	$.each(geojsonData.features, function(i, d){
		d.properties.leafletId = 'layerModalID' + i;
		// create coordiantes with latLon instead of lonLat for use with D3 later
		d.properties.latLonCoordinates = [d.geometry.coordinates[1], d.geometry.coordinates[0]];
		if (d.properties.NumberOfSamples > 0) {
			// calculate scoring
			// Magnitude Dry
			if (d.properties.TotalDryWeatherSamples > 0) {
				d.properties.magnitudeDryPoints = SoundExplorerModalMap.MagnitudePoints(d.properties.MaxValueDry);
			} else {
				d.properties.magnitudeDryPoints = SoundExplorerModalMap.MagnitudePoints(d.properties.MaxValueWet);
			}
			
			// Magnitude Wet
			if (d.properties.TotalWetWeatherSamples > 0) {
				d.properties.magnitudeWetPoints = SoundExplorerModalMap.MagnitudePoints(d.properties.MaxValueWet);	
			} else {
				d.properties.magnitudeWetPoints = SoundExplorerModalMap.MagnitudePoints(d.properties.MaxValueDry);
			}		

			d.properties.pctPass = Math.round((d.properties.TotalPassSamples / d.properties.NumberOfSamples) * 100);
			d.properties.pctPassNotRounded = (d.properties.TotalPassSamples / d.properties.NumberOfSamples) * 100;
			d.properties.pctFail = Math.round(100 - ((d.properties.TotalPassSamples / d.properties.NumberOfSamples) * 100));
			d.properties.pctPassFail = [{name: "fail", pct: d.properties.pctFail}, {name: "pass", pct: d.properties.pctPass}];

			// Frequency Dry
			if (d.properties.TotalDryWeatherSamples > 0) {
				d.properties.frequencyDryPoints = SoundExplorerModalMap.FrequencyPoints(100 - ((d.properties.DryWeatherPassSamples / d.properties.TotalDryWeatherSamples) * 100));
			} else {
				d.properties.frequencyDryPoints = SoundExplorerModalMap.FrequencyPoints(100 - ((d.properties.WetWeatherPassSamples / d.properties.TotalWetWeatherSamples) * 100));
			} 

			// Frequency Wet
			if (d.properties.TotalWetWeatherSamples > 0) {
				d.properties.frequencyWetPoints = SoundExplorerModalMap.FrequencyPoints(100 - ((d.properties.WetWeatherPassSamples / d.properties.TotalWetWeatherSamples) * 100));
			} else {
				d.properties.frequencyWetPoints = SoundExplorerModalMap.FrequencyPoints(100 - ((d.properties.DryWeatherPassSamples / d.properties.TotalDryWeatherSamples) * 100));
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




