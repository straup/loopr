function loopr_init(){
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
	console.log(img);

	$("#offstage").attr("src", img);

	$("#offstage").load(function(){
		$("#loopr").attr("src", img);
		$("#offstage").attr("src", "");
	});

	setTimeout(function(){
		(loops.length) ? loopr_show(loops) : loopr_load();
	}, 10000);
}