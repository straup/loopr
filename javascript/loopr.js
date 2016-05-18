// var loopr_url = 'https://info.aaronland.loopr.s3.amazonaws.com/info.aaronland.loopr.json';
var loopr_url = 'https://s3.amazonaws.com/info.aaronland.loopr/info.aaronland.loopr.json';

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

	$("#offstage").attr("src", img);

	$("#offstage").load(function(){
		$("#loopr").attr("src", img);
		$("#offstage").attr("src", "");
	});

	setTimeout(function(){
		(loops.length) ? loopr_show(loops) : loopr_load();
	}, 7000);

}
