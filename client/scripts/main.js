var ws;
var clientId;
var clientHash;

const handleHandshake = (data) => {
    data = JSON.parse(data);
    clientId = data.clientId;
    clientHash = data.clientHash;
    document.getElementsByClassName('loading')[0].style.display = 'none';
    addMessage('Welcome, ' + clientHash + '!', true);
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

const handleMessageRecv = (data) => {
    addMessage(data.message, false, data.author);
};

const addMessage = (message, misc = false, author = false) => {
    let element = document.createElement('li');
    let contentText = document.getElementsByClassName('contentText')[0];
    element.classname = 'message';
    if(misc) {
        let miscA = document.createElement('a');
        miscA.innerText = message;
        miscA.className = 'contentMisc';
        element.append(miscA);
    } else if(author) {
        let miscA = document.createElement('span');
        let miscB = document.createElement('span');
        miscA.className = 'contentAuthor';
        miscB.className = 'contentMessage';
        miscA.innerText = author + ':';
        miscB.innerText = message;
        if(author == 'Server')
            miscA.style.color = '#7d7dfd';
        element.append(miscA);
        element.append(miscB);
    } else {
        element.innerText = message;
    }
    document.getElementsByClassName('contentMessages')[0].append(element);
    contentText.scrollTop = contentText.scrollHeight;
}

window.addEventListener('DOMContentLoaded', () => {
    const handlers = {
        'handshake' : handleHandshake,
        'message' : handleMessageRecv,
    }
    addDate();
    addMessage('Connecting...', true);
    ws = new WebSocket("ws://127.0.0.1:6943/");
    const input = document.getElementById('chatbar_input');
    input.addEventListener('keydown', function(e) {
        if(e.code != 'Enter')
            return;
        const message = this.value;
        if(message.length <= 0)
            return;
        this.value = '';
        ws.send(message);
        addMessage(message, false, clientHash);
    });
    ws.addEventListener('message', (event) => { 
        dataBlock = JSON.parse(event.data);
        if(dataBlock.type in handlers) {
            handlers[dataBlock.type](dataBlock.data);
        }
    });
});