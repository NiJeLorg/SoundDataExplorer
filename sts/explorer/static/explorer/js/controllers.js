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

	// swap out mobile images and desktop images when tutorial modal is loaded if mobile screen size
	$('#tutorial').on('show.bs.modal', function (e) {
		if ($("body").width() < 768) {
			$('.slide_image').addClass('hidden');
			$('.slide_image_mobile').removeClass('hidden');			
		}
	});

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
	if (beachId && beachName && beachLat && beachLon) {
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
		var startDate = moment($( ".annualFilter.active" ).val()).startOf('year').format("YYYY-MM-DD");
		var endDate = moment($( ".annualFilter.active" ).val()).endOf('year').format("YYYY-MM-DD");

	    $.ajax({
	        type: 'GET',
	        url:  'modalapi/?startDate=' + startDate + '&endDate=' + endDate + '&beachId=' + beachId,
	        success: function(data){
	        	$("#modalData").html(data);
	        	$("body").removeClass("loading");
			    //zoom main map on modal open
	    		setTimeout(function() {
					SoundExplorerMap.modalZoom(parseFloat(beachLat), parseFloat(beachLon));		
				}, 2000);
			    
			}
	    });

	    // update facebook and twitter share urls
		updateSocialButtons(beachId, beachName);


	}

	// listen for modal click
	$('#siteView').on('show.bs.modal', function (event) {
		$("body").addClass("loading");
		var link = $(event.relatedTarget);
		var beachid = link.data('beachid');
		var beachname = link.data('beachname');
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
		var startDate = moment($( ".annualFilter.active" ).val()).startOf('year').format("YYYY-MM-DD");
		var endDate = moment($( ".annualFilter.active" ).val()).endOf('year').format("YYYY-MM-DD");

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

		// update facebook and twitter share urls
		updateSocialButtons(beachid, beachname);


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


	// update share buttons
    // set up twitter and facebook URLs for main map
    var app_id = '1737867593200968';
    var fbdescription = "Interested in seeing how your Long Island Sound beach stacks up against neighboring beaches? Come check out our grades on the Sound Health Explorer!";
    var fblink = "http://soundhealthexplorer.org/";
    var fbpicture = "http://soundhealthexplorer.org/static/explorer/css/images/fbshare.png";
    var fbname = "Sound Health Explorer, a project of Save the Sound";
    var fbcaption = "Save The Sound";
    var fbUrl = 'https://www.facebook.com/dialog/feed?app_id=' + app_id + '&display=popup&description=' + encodeURIComponent(fbdescription) + '&link=' + encodeURIComponent(fblink) + '&redirect_uri=' + encodeURIComponent(fblink) + '&name=' + encodeURIComponent(fbname) + '&caption=' + encodeURIComponent(fbcaption) + '&picture=' + encodeURIComponent(fbpicture);
    var fbOnclick = 'window.open("' + fbUrl + '","facebook-share-dialog","width=626,height=436");return false;';
    $('#showShareFB').attr("onclick", fbOnclick);


    var twitterlink = "http://soundhealthexplorer.org/";
    var via = 'SavetheSound';
    var twittercaption = "How does your #LongIslandSound beach stack up against other beaches? Check out our grades here:";
    var twitterUrl = 'https://twitter.com/intent/tweet?url=' + encodeURIComponent(twitterlink) + '&via=' + encodeURIComponent(via) + '&text=' + encodeURIComponent(twittercaption);
    var twitterOnclick = 'window.open("' + twitterUrl + '","twitter-share-dialog","width=626,height=436");return false;';
    $('#showShareTwitter').attr("onclick", twitterOnclick);

    function updateSocialButtons(beach_id, beach_name) {
		// update share buttons
	    // set up twitter and facebook URLs for main map
	    var app_id = '1737867593200968';
	    var fbdescription = "Here's the how my Long Island Sound beach, " + beach_name + ", is doing. Check out and compare your beach here!";
	    var fblink = "http://soundhealthexplorer.org/beach=" + beach_id;
	    var fbpicture = "http://soundhealthexplorer.org/static/explorer/css/images/fbshare.png";
	    var fbname = "Sound Health Explorer, a project of Save the Sound";
	    var fbcaption = "Save The Sound";
	    var fbUrl = 'https://www.facebook.com/dialog/feed?app_id=' + app_id + '&display=popup&description=' + encodeURIComponent(fbdescription) + '&link=' + encodeURIComponent(fblink) + '&redirect_uri=' + encodeURIComponent(fblink) + '&name=' + encodeURIComponent(fbname) + '&caption=' + encodeURIComponent(fbcaption) + '&picture=' + encodeURIComponent(fbpicture);
	    var fbOnclick = 'window.open("' + fbUrl + '","facebook-share-dialog","width=626,height=436");return false;';
	    $('#showShareFBModal').attr("onclick", fbOnclick);


	    var twitterlink = "http://soundhealthexplorer.org/beach=" + beach_id;
	    var via = 'SavetheSound';
	    var twittercaption = "Here's the how my #LongIslandSound beach, " + beach_name + ", is doing. Check out yours here!";
	    var twitterUrl = 'https://twitter.com/intent/tweet?url=' + encodeURIComponent(twitterlink) + '&via=' + encodeURIComponent(via) + '&text=' + encodeURIComponent(twittercaption);
	    var twitterOnclick = 'window.open("' + twitterUrl + '","twitter-share-dialog","width=626,height=436");return false;';
	    $('#showShareTwitterModal').attr("onclick", twitterOnclick);    	

    }


});
