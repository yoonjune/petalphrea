function toggleOffCanvasMenu(){
	var overlay = $("#offcanvas");
	var container = $("#container");
	
	if(overlay.is(":visible")){
		closeOffCanvasMenu()
	}
	else {
		showOffCanvasMenu()
	}
}

function showOffCanvasMenu(){
	var overlay = $("#offcanvas");
	var container = $("#container");	
	
	overlay.show();
	container.css({ paddingLeft : overlay.width() });
}
function closeOffCanvasMenu(){
	var overlay = $("#offcanvas");
	var container = $("#container");
	
	overlay.hide();
	container.css({ paddingLeft: 0});
}