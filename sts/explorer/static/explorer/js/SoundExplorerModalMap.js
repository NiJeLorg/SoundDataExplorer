/* 
* Functions to create the main Sound Data Explorer Map
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
	var startDate = moment($( "#start_date option:selected" ).val()).startOf('month').format("YYYY-MM-DD");
	var endDate = moment($( "#end_date option:selected" ).val()).endOf('month').format("YYYY-MM-DD");

	d3.json('/beaconapi/?startDate=' + startDate + '&endDate=' + endDate, function(data) {
		geojsonData = data;

		$.each(geojsonData.features, function(i, d){
			d.properties.leafletId = 'layerModalID' + i;
			// create coordiantes with latLon instead of lonLat for use with D3 later
			d.properties.latLonCoordinates = [d.geometry.coordinates[1], d.geometry.coordinates[0]];
			d.properties.pctPass = (d.properties.TotalPassSamples / d.properties.NumberOfSamples) * 100;
			var pctFail = 100 - ((d.properties.TotalPassSamples / d.properties.NumberOfSamples) * 100);
			d.properties.pctPassFail = [{name: "fail", pct: pctFail},{name: "pass", pct: d.properties.pctPass}];
		});

		thismap.BEACON_POINTS = L.geoJson(geojsonData, {
		    pointToLayer: SoundExplorerModalMap.getStyleFor_BEACON_POINTS,
			onEachFeature: SoundExplorerModalMap.onEachFeature_BEACON_POINTS
		}).addTo(thismap.map);

		// create the D3 layer for Beacon data, but don't add to map until we hit a specfic zoom level
		SoundExplorerModalMap.createBEACON_D3_POINTS(geojsonData.features, thismap);

	});

}


SoundExplorerModalMap.getStyleFor_BEACON_POINTS = function (feature, latlng){
	var marker = L.circleMarker(latlng, {
		radius: 5,
		color: '#bdbdbd',
		weight: 1,
		opacity: 1,
		fillColor: SoundExplorerModalMap.SDEPctPassColor(feature.properties.pctPass),
		fillOpacity: 1
	});
	
	return marker;
	
}


SoundExplorerModalMap.SDEPctPassColor = function (d){
    return d > 95 ? '#39b54a' :
           d > 90 ? '#f7e34f' :
           d > 85 ? '#f9ae08' :
           d > 78 ? '#f47f45' :
           d >= 0 ? '#ef4136' :
                   	'#545454' ;	
}

SoundExplorerModalMap.SDEPctPassGrade = function (d){
    return d > 95 ? 'A' :
           d > 90 ? 'B' :
           d > 85 ? 'C' :
           d > 78 ? 'D' :
           d >= 0 ? 'F' :
                   	'' ;	
}


SoundExplorerModalMap.createBEACON_D3_POINTS = function (features, thismap) {
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
					return SoundExplorerModalMap.SDEPctPassColor(d.properties.pctPass);
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
				.text(function(d) { return SoundExplorerModalMap.SDEPctPassGrade(d.properties.pctPass); });

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

	thismap.BEACON_D3_POINTS.addTo(thismap.map);


}

SoundExplorerModalMap.updateMapFromSlider = function (value){
	// close popups
	MY_MAP_MODAL.map.closePopup();
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
		MY_MAP_MODAL.BEACON_POINTS.clearLayers();
		// add new data
		MY_MAP_MODAL.BEACON_POINTS.addData(geojsonData);

		// remove D3 layer
		MY_MAP_MODAL.map.removeLayer(MY_MAP_MODAL.BEACON_D3_POINTS);
		// recreate new D3 layer
		SoundExplorerModalMap.createBEACON_D3_POINTS(geojsonData.features, MY_MAP_MODAL);
		MY_MAP_MODAL.BEACON_D3_POINTS.addTo(MY_MAP_MODAL.map);
		
	});

}




