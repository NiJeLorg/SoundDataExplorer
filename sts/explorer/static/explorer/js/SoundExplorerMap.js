/* 
* Functions to create the main Sound Data Explorer Map
*/

// initialize map
function SoundExplorerMap() {
	// set zoom and center for this map	
    this.center = [40.735551, -72.932739];
    this.zoom = 9;

    this.map = new L.Map('map', {
		minZoom:5,
		maxZoom:17,
    	center: this.center,
   	 	zoom: this.zoom,
   	 	zoomControl: false,
	});
	
	// add CartoDB tiles
	this.CartoDBLayer = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',{
	  attribution: 'Created By <a href="http://nijel.org/">NiJeL</a> | &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
	});
	this.map.addLayer(this.CartoDBLayer);

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


	var pctPass = ((feature.properties.TotalPassSamples / feature.properties.NumberOfSamples) * 100).toFixed(1);

	var pctDryPass = ((feature.properties.DryWeatherPassSamples / feature.properties.TotalDryWeatherSamples) * 100).toFixed(1);

	var pctWetPass = ((feature.properties.WetWeatherPassSamples / feature.properties.TotalWetWeatherSamples) * 100).toFixed(1);

	layer.bindLabel("<span class='text-capitalize'>" + feature.properties.BeachName + "<br />" + feature.properties.County + "</span> County, " + feature.properties.State + "<br />" + pctPass + "% of total samples pass<br />" + pctDryPass + "% of dry weather samples pass<br />" + pctWetPass + "% of wet weather samples pass<br />" + feature.properties.NumberOfSamples + " total samples", { direction:'auto' });
	
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
		}

	});

	// we'll now add an ID to each layer so we can fire the mouseover and click outside of the map
    layer._leaflet_id = 'layerID' + count;
    count++;

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
		});

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

		bcEnter.append('circle');
		bcEnter.append('text');
		bcEnter.append('g');
		bcEnter.call(update);


		// exiting old stuff
		beaconCircles.exit().remove();


	});

	thismap.BEACON_D3_POINTS.addTo(thismap.map);

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
	// moment parses unix offsets and javascript date objects in the same way
	var startDate = moment(value[0]).startOf('month').format("YYYY-MM-DD");
	var endDate = moment(value[1]).endOf('month').format("YYYY-MM-DD");

	d3.json('/beaconapi/?startDate=' + startDate + '&endDate=' + endDate, function(data) {
		geojsonData = data;

		$.each(geojsonData.features, function(i, d){
			d.properties.leafletId = 'layerID' + i;
		});
		// clear layer
		MY_MAP.BEACON_POINTS.clearLayers();
		// add new data
		MY_MAP.BEACON_POINTS.addData(geojsonData);
	});

}



