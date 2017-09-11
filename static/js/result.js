$('#choose_pic').click(function(){
	$('#choose_pic_pop').fadeIn("fast");
});

$('body').click(function(evt){
	if(evt.target.id != "choose_pic_pop" &&  evt.target.id != "choose_pic" && evt.target.id != "choose_mode" && $('#choose_pic_pop').css("display")=="block") {
		$('#choose_pic_pop').fadeOut("fast");
		$('#random_pic').css({"margin-left": "20px"});
	}
});


$('#pic_pop_btn').on('click',function(){
	$('#form_top_input').click();
});

$('#form_top_input').change(function () {
	if ($('#form_top_input').val()=="") {
		alert("请选择一张图片");
	} else {
		$("#form_top_submit").click();
		$("#pic_pop_words").css({"visibility":"hidden"});
		$("#pic_pop_loading").fadeIn("fast");
	}
});
