var timeoutID;
var timeout = 1000;

function setup() {
	document.getElementById("sendbtn").addEventListener("click", makePostMsg, true);
	document.getElementById("sendimgebtn").addEventListener("click", makePostImage, true);
	//timeoutID = window.setTimeout(makePoll(), timeout)
}

function makePostImage() {
	var httpRequest = new XMLHttpRequest();
	if (!httpRequest) {
		alert('Giving up - cannot create XMLHttp instance');
		return false;
	}
	httpRequest.onreadystatechange = function() { alertResultMsg(httpRequest) };
	httpRequest.open("POST", "/add_image_two_user");
	var formData = new FormData(document.getElementById('img-form'));
	httpRequest.send(formData);
}

function makePostMsg() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up - cannot create XMLHttp instance');
		return false;
	}

	httpRequest.onreadystatechange = function() { alertResultMsg(httpRequest) };

	httpRequest.open("POST", "/add_message_two_user");
	httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

	var data;
	data = "fromuser=" + document.getElementById('fromuser').value + "&touser=" + document.getElementById('touser').value + "&text=" + document.getElementById('text').value;
	console.log(data);
	httpRequest.send(data);
}

function alertResultMsg(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			var msg = JSON.parse(httpRequest.response);
			console.log(msg);
			var msgDiv = document.getElementById('msgs');
			temp = document.createElement('li');
			if (msg.image){
				temp.innerHTML = '<p><strong>' + msg.fromuser + ' said to ' +msg.touser + '</strong> <small> - ' + msg.pub_date + ' </small></p><p style="margin-top: 8px;"><img src="data:;base64,' + msg.image + '" />';
			}else {
				temp.innerHTML = '<p><strong>' + msg.fromuser + ' said to ' +msg.touser + '</strong> <small> - ' + msg.pub_date + ' </small></p><p style="margin-top: 8px">' + msg.text + '</p>';
			}
			msgDiv.appendChild(temp);
			msgDiv.scrollTop = msgDiv.scrollHeight;
		}
		else {
			console.log("didn't work");
		}
	}
}

function makePoll() {
	var httpRequest = new XMLHttpRequest();
	
	if (!httpRequest) {
		alert('Giving up - cannot create XMLHttp instance');
		return false;
	}

	httpRequest.onreadystatechange = function() { handlePoll(httpRequest) };

	httpRequest.open("POST", "/get_new_messages");
	httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

	var data;
	var d = new Date();
	var t = d.getTime();

	data = "chat_name=" + document.getElementById('chat_name').value + "&timestamp=" + (t-timeout);
	httpRequest.send(data);
}

function handlePoll(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200 && httpRequest.response != "null") {
			console.log(httpRequest.response);
			var msg = JSON.parse(httpRequest.response);
			var ul = document.getElementById("msgs");
				var li = document.createElement("li");
				li.innerHTML = "<strong>"+ msg.author + ": </a></strong>" + msg.text + "<small> - " + msg.pub_date + " </small>";
				ul.appendChild(li);
			timeoutID = window.setTimeout(makePoll, timeout);
		}
		else {
			console.log("nothing new");
			timeoutID = window.setTimeout(makePoll, timeout);
		}
	}
}

window.addEventListener("load", setup, true);
