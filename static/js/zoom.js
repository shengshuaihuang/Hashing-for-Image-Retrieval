var carrousel=$(".zoom_carrousel");
var blur = $("#result_container, #query_container, #random_list, .footer");
// var blur = $('*').not(".zoom_carrousel *")
var thumb_index = 0;
var width = $(window).width();
var height = $(window).height();

function zoom_function(thumb) {
	var number =thumb.length;
	var zoomclose = $("#fullback,#zoom_close");

	thumb.click(function () {
		thumb_index = $(this).index();
		var src = $(this).find("img").attr("src");
		$(".zoom_icon").fadeIn("fast");
		carrousel.fadeIn("fast");
		$("#fullback").fadeIn("fast");
		var scrollTop = $(document).scrollTop();
		$("#fullback").css({"top": scrollTop+80});
		zoom_position(src, width, height);
		blur.css({"-webkit-filter": "blur(10px)","-ms-filter": "blur(10px)","-moz-filter": "blur(10px)","filter": "blur(10px)"});
		$("body").css({"overflow-y":"hidden"});
		var msg = $(".zoom_msg");
		document.getElementById('zoom_next').onclick = function () {
			if (thumb_index < (number - 1)) {
				thumb_index++;
			}else {
				msg.html("已经是最后一张").fadeIn();
				setTimeout(msg.fadeOut(), 10000);
			}
			src = getsrc(thumb_index);
			zoom_position(src, width, height);
		};
		document.getElementById('zoom_before').onclick = function () {
			if (thumb_index != 0) {
				thumb_index--;
			} else {
				msg.html("已经是第一张").fadeIn();
				setTimeout(msg.fadeOut(), 10000);
			}
			src = getsrc(thumb_index);
			zoom_position(src, width, height);
		};
	});

	
	zoomclose.click(function(){
		carrousel.find(".zoom_img").attr("src",'');
		carrousel.fadeOut(200);
		$("#fullback").fadeOut(200);
		$(".zoom_icon").fadeOut(200);
		blur.css({"-webkit-filter": "","-ms-filter": "","-moz-filter": "","filter": ""});
		$("body").css({"overflow-y":"scroll"});
	});
}

function zoom_position(src, window_w, window_h) {
	carrousel.find(".zoom_img").attr("src", src);
	$(".zoom_img").css({"max-width":window_w-200, "max-height":window_h-200});
	var w = carrousel.find(".zoom_img").width();
	var h = carrousel.find(".zoom_img").height();
	var msg = $(".zoom_msg");
	var w_msg = msg.width();
	var scrollTop = $(document).scrollTop();
	carrousel.css({
		"left": (window_w-w)/2,
		"top": (window_h-h)/2+scrollTop+40,
		"width": w,
		"height": h
	});
	msg.css({"top":h/2-50,"left":(w-w_msg)/2});
	$("#zoom_next").css({"top":window_h/2+scrollTop+40});
	$("#zoom_before").css({"top":window_h/2+scrollTop+40});
	$("#zoom_close").css({"top":scrollTop+100});
}

function getsrc(index){
	return $(".thumb:eq("+index+")").find("img").attr("src")
}