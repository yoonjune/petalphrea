console.log('Loaded script.js');

function Hello(){
	alert("hello");
}

function VoteUp(greetingKey) {
				$.ajax({
					type: "POST",
					url : "/vote/",
					dataType: 'json',
					data : JSON.stringify({ "greetingKey" : greetingKey}),
					success : function(data){
						$('.voteCount'+data['storyid']).text(data['storyvote']);
					},
					error : function() {
						alert('hehe');
					}
				})
			};
$(document).ready(function(){

});