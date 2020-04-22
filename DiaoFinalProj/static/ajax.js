var timeoutID;
var timeout = 1000;

function setup() {
	document.getElementById("btn").addEventListener("click", makePost, true);
	timeoutID = window.setTimeout(makePoll(), timeout)
}

function makePost() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up - cannot create XMLHttp instance');
		return false;
	}

	httpRequest.onreadystatechange = function() { alertResult(httpRequest) };

	httpRequest.open("POST", "/add_message");
	httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

	var data;
	data = "author=" + document.getElementById('author').value + "&chat_name=" + document.getElementById('chat_name').value + "&text=" + document.getElementById('text').value;
	console.log(data);
	httpRequest.send(data);
}

function alertResult(httpRequest) {
	console.log(httpRequest.readyState);
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			var msg = JSON.parse(httpRequest.response);
			console.log(msg.pub_date);
			var msgDiv = document.getElementById('msgs');
			temp = document.createElement('div');
			temp.innerHTML = '<li><p><strong>' + msg.author + ': </strong><small> - ' + msg.pub_date + ' </small></p><p style="margin-top: 8px">' + msg.text + '</p></lig>';
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