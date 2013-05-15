$(document).ready(function(){
	//вертикальная граница (sidebar_border) высотой с контейнер (container)
	$("body").load($("#sidebar_border").height($("#container").height()+75));
	//количество нажатий на кнопку "добавить статью" 
	var i = 1;
	$("#main_add_btn").click(function() {
		if(i%2==0){
			$("#popup_window").css("display", "none");
		}
		else{
		$("#popup_window").css("display", "");
		}
		i++;
	});
	

	//закрываем всплывающее окно по нажатию на кнопку "закрыть"
	// $("#close_popup_window").click(function() {
		// $("#popup_window").css("display", "none")
	// });
	
	// $("#close_popup_window").click(function() {
		// if(!$("#popup_window_err_mes").hasClass("hidden_error")){
			// $("#popup_window_err_mes").addClass("hidden_error");
		// }
	// });
	
	// $("#main_add_btn").click(function() {
		// $("#popup_window_err_mes").addClass("hidden_error");
	// });
});

