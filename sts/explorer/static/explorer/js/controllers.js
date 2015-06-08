/**
 * controller.js: listeners and controllers for DNAinfo crime map
 * Author: NiJeL
 */


$( document ).ready(function() {

	// open the bottom area on page load
	$( ".popup-wrapper" ).toggleClass("popup-wrapper-open");
	$( ".map" ).toggleClass("map-popup-wrapper-open");
	$( ".legend" ).toggleClass("legend-popup-wrapper-open");

	// close popup tray
	$('#popup-close').click(function() {
		$( ".popup-wrapper" ).toggleClass("popup-wrapper-open");
		$( ".map" ).toggleClass("map-popup-wrapper-open");
		$( ".legend" ).toggleClass("legend-popup-wrapper-open");
	});

	// create start and end date combo boxes
	var start_date_options = '';
	var end_date_options = '';

	var minDate = moment(new Date(2004,0,1));
	var checkDate = moment().startOf('month');
	var fiveYearAgo = moment().subtract(5, 'years').startOf('month');

	while (checkDate.isAfter(minDate)) {
		var value = checkDate.format('YYYY-MM-DD');
		var printValue = checkDate.format('MMM YYYY');
		var selected = '';
		if (checkDate.isSame(fiveYearAgo)) {
			var selected = 'selected';
		}
		start_date_options += '<option ' + selected + ' value="' + value + '">' + printValue + '</option>'; 

		end_date_options += '<option value="' + value + '">' + printValue + '</option>'; 

		checkDate.subtract(1, 'months');
	}

	$('#start_date').html(start_date_options);
	$('#end_date').html(end_date_options);


	// set up combo box selction to update map and slider
	$( "#start_date" ).change(function() {
	  updateSlider();
	});

	$( "#end_date" ).change(function() {
	  updateSlider();
	});

	function updateSlider (minDate, maxDate, start_date, end_date) {
		$("body").addClass("loading");

		var minDate = new Date(2004,0,1);
		var maxDate = moment().toDate();
		var start_date = moment($( "#start_date option:selected" ).val()).toDate();
		var end_date = moment($( "#end_date option:selected" ).val()).toDate();

	  	// destroy the old slider
	  	d3.select('#timeSlider').selectAll("*").remove();

	  	// recreate slider
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
				.value( [ start_date, end_date ] )
				.on("slideend", function(evt, value) {
					$("body").addClass("loading");
					// run a function to update map layers with new dates
					SoundExplorerMap.updateMapFromSlider(value);
					// update combo boxes
					var start_date = moment(value[0]).format('YYYY-MM');
					start_date = start_date + '-01';
					$( "#start_date" ).val(start_date);
					var end_date = moment(value[1]).format('YYYY-MM');
					end_date = end_date + '-01';
					$( "#end_date" ).val(end_date);					
				});

		d3.select('#timeSlider').call(mapSlider);

		// update the map data as well
		var value = [ start_date, end_date ];
		SoundExplorerMap.updateMapFromSlider(value);

	}

	// listen for modal click
	$('#siteView').on('show.bs.modal', function (event) {
		var link = $(event.relatedTarget);
		var beachid = link.data('beachid');
		var lat = link.data('lat');
		var lon = link.data('lon');
		var modalMap = new SoundExplorerModalMap(lat, lon);
		modalMap.loadPointLayers();
		setTimeout(function() {
			modalMap.map.invalidateSize();		
		}, 10);
		MY_MAP_MODAL = modalMap;
		// ajax call to WQ samples api 
		var startDate = moment($( "#start_date option:selected" ).val()).format("YYYY-MM-DD");
		var endDate = moment($( "#end_date option:selected" ).val()).format("YYYY-MM-DD");

	    $.ajax({
	        type: 'GET',
	        url:  'modalapi/?startDate=' + startDate + '&endDate=' + endDate + '&beachId=' + beachid,
	        success: function(data){
	        	$("#modalData").html(data);
	        }
	    });

	    //zoom main map on modal open
	    SoundExplorerMap.modalZoom(lat, lon);

	});

	$('#siteView').on('hidden.bs.modal', function (event) {
		// destroy old map container and create a new one
		modalMap.remove();
		$( "#modalMapWrapper" ).append( '<div id="modalMap"></div>' );
		// clear modal data areas
		$("#modalData").html('');

		
	});

	// toggle map layer listeners
	$( "#beacon" ).change(function() {
		if ($( "#beacon" ).prop('checked')) {
			SoundExplorerMap.addLayers('beacon');
		} else {
			SoundExplorerMap.removeLayers('beacon');
		}
	});

	$( "#boatlaunch" ).change(function() {
		if ($( "#boatlaunch" ).prop('checked')) {
			SoundExplorerMap.addLayers('boatlaunch');
		} else {
			SoundExplorerMap.removeLayers('boatlaunch');
		}
	});

	$( "#csos" ).change(function() {
		if ($( "#csos" ).prop('checked')) {
			SoundExplorerMap.addLayers('csos');
		} else {
			SoundExplorerMap.removeLayers('csos');
		}
	});

	$( "#impervious" ).change(function() {
		if ($( "#impervious" ).prop('checked')) {
			$('#impervious-legend').removeClass('hidden').addClass('show');
			SoundExplorerMap.addLayers('impervious');
		} else {
			$('#impervious-legend').removeClass('show').addClass('hidden');
			SoundExplorerMap.removeLayers('impervious');
		}
	});

	$( "#watersheds" ).change(function() {
		if ($( "#watersheds" ).prop('checked')) {
			SoundExplorerMap.addLayers('watersheds');
		} else {
			SoundExplorerMap.removeLayers('watersheds');
		}
	});

	$( "#shellfish" ).change(function() {
		if ($( "#shellfish" ).prop('checked')) {
			$('#shellfish-legend').removeClass('hidden').addClass('show');
			SoundExplorerMap.addLayers('shellfish');
		} else {
			$('#shellfish-legend').removeClass('show').addClass('hidden');
			SoundExplorerMap.removeLayers('shellfish');
		}
	});

	$( "#wastewater" ).change(function() {
		if ($( "#wastewater" ).prop('checked')) {
			SoundExplorerMap.addLayers('wastewater');
		} else {
			SoundExplorerMap.removeLayers('wastewater');
		}
	});

	$( "#landuse" ).change(function() {
		if ($( "#landuse" ).prop('checked')) {
			$("body").addClass("loading");
			$('#lulc-legend').removeClass('hidden').addClass('show');
			SoundExplorerMap.addLayers('landuse');
		} else {
			$('#lulc-legend').removeClass('show').addClass('hidden');
			SoundExplorerMap.removeLayers('landuse');
		}
	});


});
