function loopr_init(){

	// fullscreen polyfill stuff
    
	var btn = document.getElementById("fullscreen");
	var loop = document.getElementById("loopr"); 

	btn.addEventListener("click", function() {
		loop.requestFullscreen();
	}, false);

	loopr_load();
}

function loopr_load(){

	var onsuccess = function(rsp){
		loopr_show(rsp['loops']);
	};

	$.ajax({'url': loopr_url, 'success': onsuccess, 'dataType': 'json' });
}

function loopr_show(loops){

	var img = loops.pop()

	$("#offstage").attr("src", img);

	$("#offstage").load(function(){
		$("#loopr").attr("src", img);
		$("#offstage").attr("src", "");

		var m = img.match(/\/loopr-(\d+)\.gif$/);
		var ts = m[1];

		var dt = new Date(ts * 1000);
		var h = dt.getHours();
		var m = dt.getMinutes();

		if (h < 10){ h = "0" + h; }
		if (m < 10){ m = "0" + m; }

		$("#when").html(h + "H" + m);
	});

	setTimeout(function(){
		(loops.length) ? loopr_show(loops) : loopr_load();
	}, 10000);
}
