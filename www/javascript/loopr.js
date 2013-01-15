function loopr_init(){
	loopr_load();
}

function loopr_load(){
	$.ajax({'url': loopr_url, 'success': loopr_show, 'dataType': 'json' });
}

function loopr_show(rsp){

	var loops = rsp['loops']
	var count = loops.length;

	var i = 0;

    /* BROKEN ... */

	var load = function(){

		var current = loops[i];

		if (! current){
			loopr_load();
			return;
		}

		i++;
		loopr_load(current);
		setTimeout(load, 10000);
	};

	load();
}

function loopr_load(img){

	$("#offstage").attr("src", img);

	$("#offstage").load(function(){
		$("#loopr").attr("src", img);
	});
}
