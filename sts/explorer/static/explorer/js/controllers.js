/**
 * controller.js: listeners and controllers for DNAinfo crime map
 * Author: NiJeL
 */


$( document ).ready(function() {
	// remove loading class
	$("body").removeClass("loading");

	if (!$.cookie('noIntro') && !beachId && !beachLat && !beachLon) {
		$('#introduction').modal('show');
		$("body").removeClass("loading");
		// close if button clicked
		$('#closeIntroModal').click(function() {
			$('#introduction').modal('hide');
		});
		$('#siteTutorialModal').click(function() {
			$('#introduction').modal('hide');
			$('.carousel').carousel();
		});          
		// set cookie if don't show this message is checked
		$('#toggleIntroCookie').change(function() {
			if($(this).is(":checked")) {
				$.cookie('noIntro', 'noIntro', { expires: 365, path: '/' });
			} else {
				$.removeCookie('noIntro', { path: '/' });
			}
		});
	}

	// open and close the legend
	$('#legendClose').click(function() {
		$( ".legend" ).addClass("hidden");
		$( "#legendOpen" ).removeClass("hidden");		
	});

	$('#legendOpen').click(function() {
		$( ".legend" ).removeClass("hidden");
		$( "#legendOpen" ).addClass("hidden");		
	});

	// open modal on page load if url passed with beach id
	if (beachId && beachLat && beachLon) {
		// loading
		$("body").addClass("loading");
		// open the modal
		$('#siteView').modal('show');
		// load the data
		var modalMap = new SoundExplorerModalMap(parseFloat(beachLat), parseFloat(beachLon));
		modalMap.loadPointLayers();
		modalMap.loadExtraLayers();
		setTimeout(function() {
			modalMap.map.invalidateSize();		
		}, 10);
		MY_MAP_MODAL = modalMap;
		// ajax call to WQ samples api 
		var startDate = moment($( "#start_date option:selected" ).val()).format("YYYY-MM-DD");
		var endDate = moment($( "#end_date option:selected" ).val()).format("YYYY-MM-DD");

	    $.ajax({
	        type: 'GET',
	        url:  'modalapi/?startDate=' + startDate + '&endDate=' + endDate + '&beachId=' + beachId,
	        success: function(data){
	        	$("#modalData").html(data);
	        	$("body").removeClass("loading");
			    //zoom main map on modal open
			    SoundExplorerMap.modalZoom(parseFloat(beachLat), parseFloat(beachLon));
	        }
	    });


	}

	// listen for modal click
	$('#siteView').on('show.bs.modal', function (event) {
		$("body").addClass("loading");
		var link = $(event.relatedTarget);
		var beachid = link.data('beachid');
		var lat = link.data('lat');
		var lon = link.data('lon');
		var modalMap = new SoundExplorerModalMap(lat, lon);
		modalMap.loadPointLayers();
		modalMap.loadExtraLayers();
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
	        	$("body").removeClass("loading");
			    //zoom main map on modal open
			    SoundExplorerMap.modalZoom(lat, lon);
	        }
	    });

	   	// create url parameters 
		window.history.pushState( {} , '', '?beach=' + beachid );


	});

	$('#siteView').on('hidden.bs.modal', function (event) {
		// destroy old map container and create a new one
		$('#modalMap').remove();
		$( "#modalMapWrapper" ).append( '<div id="modalMap"></div>' );
		// clear modal data areas
		$("#modalData").html('');

	   	// create url parameters 
		window.history.pushState( {} , '', '/' );
		
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

	$( "#subwatersheds" ).change(function() {
		if ($( "#subwatersheds" ).prop('checked')) {
			SoundExplorerMap.addLayers('subwatersheds');
		} else {
			SoundExplorerMap.removeLayers('subwatersheds');
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

	// ensure that popovers are ready to go
	$('[data-toggle="tooltip"]').tooltip();


});
