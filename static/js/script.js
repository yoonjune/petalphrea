console.log('Loaded script.js');

function Hello() {
	alert("hello");
}

function VoteUp(greetingKey) {
	$.ajax({
		type : "POST",
		url : "/vote/",
		dataType : 'json',
		data : JSON.stringify({
			"greetingKey" : greetingKey
		}),
		success : function(data) {
			$('.voteCount' + data['storyid']).text(data['storyvote']);
		},
		error : function() {
			alert('hehe');
		}
	})
};
function commentSave(data) {
	if(data.result == true) {
		$("#comment").val("");
		commentList(data);
		alert("댓글이 입력 되었습니다.");
	} else {
		if(data.msg) {
			alert(data.msg);
		} else {
			alert("댓글입력에 실패 하였습니다.");
		}
	}
}

function commentView(page) {
	$.ajax({
		type : "GET",
		cache : false,
		url : "/comment_list/" + $("#idx").val() + "/" + page,
		dataType : "json",
		success : commentList
	});
}


function commentList(data) {
	if(data.redirect){
		window.location.href = data.redirect;
	}else{
		$("#opinion_list").html(data.html);
	}
}


$(document).ready(function() {
	$(document).on("click", "#comment_save", function() {
		if ($("#comment").val() == "") {
			alert('댓글을 입력해 주세요.');
			$("#comment").focus();
			return false;
		}
		var queryString = {
			"comment" : $("#comment").val(),
			"guestbook_name" : $("#guestbook_name").val()
		};

		$.ajax({
			type : "POST",
			url : "/comment/",
			data : JSON.stringify(queryString),
			dataType : "json",
			success : commentSave
		});
	});
	
});