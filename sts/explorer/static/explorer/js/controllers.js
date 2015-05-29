/**
 * controller.js: listeners and controllers for DNAinfo crime map
 * Author: NiJeL
 */


$( document ).ready(function() {

	// open the bottom area on page load
	$( ".popup-wrapper" ).toggleClass("popup-wrapper-open");
	$( ".map" ).toggleClass("map-popup-wrapper-open");

	// close popup tray
	$('#popup-close').click(function() {
		$( ".popup-wrapper" ).toggleClass("popup-wrapper-open");
		$( ".map" ).toggleClass("map-popup-wrapper-open");
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
	  var minDate = new Date(2004,0,1);
	  var maxDate = moment().toDate();
	  var start_date = moment($( "#start_date option:selected" ).val()).toDate();
	  var end_date = moment($( "#end_date option:selected" ).val()).toDate();
	  updateSlider(minDate, maxDate, start_date, end_date);

	});

	$( "#end_date" ).change(function() {
	  var minDate = new Date(2004,0,1);
	  var maxDate = moment().toDate();
	  var start_date = moment($( "#start_date option:selected" ).val()).toDate();
	  var end_date = moment($( "#end_date option:selected" ).val()).toDate();
	  updateSlider(minDate, maxDate, start_date, end_date);

	});

	function updateSlider (minDate, maxDate, start_date, end_date) {
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
					// run a function to update map layers with new dates
					SoundExplorerMap.updateMapFromSlider(value);
				});

		d3.select('#timeSlider').call(mapSlider);

		// update the map data as well
		var value = [ start_date, end_date ];
		SoundExplorerMap.updateMapFromSlider(value);
		
	}



});
