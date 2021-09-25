var ws;
var clientId;
var clientHash;

const handleHandshake = (data) => {
    data = JSON.parse(data);
    clientId = data.clientId;
    clientHash = data.clientHash;
    document.getElementsByClassName('loading')[0].style.display = 'none';
    addMessage('Welcome, ' + clientHash + '!');
}

const addDate = () => {
    let d = new Date();
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    m = months[d.getMonth()];
    d = d.getDate();
    let dateElement = document.createElement('a');
    dateElement.className = 'contentDate';
    dateElement.innerText = 'Message session - ' + m + ', ' + d;
    let element = document.createElement('li');
    element.classname = 'message';
    element.append(dateElement);
    document.getElementsByClassName('contentMessages')[0].append(element);
}

const addMessage = (message, misc = false) => {
    let element = document.createElement('li');
    element.classname = 'message';
    if(misc) {
        let miscA = document.createElement('a');
        miscA.innerText = message;
        miscA.className = 'contentMisc';
        element.append(miscA);
    } else {
        element.innerText = message;
    }
    document.getElementsByClassName('contentMessages')[0].append(element);
}

window.addEventListener('DOMContentLoaded', () => {
    const handlers = {
        'handshake' : handleHandshake,
    }
    addDate();
    addMessage('Connecting...', true);
    ws = new WebSocket("ws://127.0.0.1:6943/");
    document.getElementById('chatbar_input').addEventListener('input', function(e) {
        console.log(this.value);
        ws.send(this.value);
    });
    ws.addEventListener('message', (event) => { 
        dataBlock = JSON.parse(event.data);
        if(dataBlock.type in handlers) {
            handlers[dataBlock.type](dataBlock.data);
        }
    });
});