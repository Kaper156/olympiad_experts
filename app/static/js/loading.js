$(document).ready(function () {
	$('span.btn-toggle').click(function(){
		$(' ~ *', this).toggle();
	});
});