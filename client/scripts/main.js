var ws;
var clientId;
var clientHash;
var authPopup;

const handleHandshake = (data) => {
    data = JSON.parse(data);
    clientId = data.clientId;
    clientHash = data.clientHash;
    __clientHash = (clientHash[0] == '_') ? clientHash.substr(1) : clientHash;
    document.getElementsByClassName('loading')[0].style.display = 'none';
    addMessage('Welcome, ' + __clientHash + '!', true);
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
    if('authRequired' in data) {
        authPopup.style.display = 'block';
    }
};

const userColors = {
    '_' : '#000000',
    'a' : '#ff9a9a',
    'b' : '#ff9a9a',
    'c' : '#ff9a9a',
    'd' : '#ff9a9a',
    'e' : '#9affe8',
    'f' : '#9affe8',
    '0' : '#9affe8',
    '1' : '#9affe8',
    '2' : '#f99aff',
    '3' : '#f99aff',
    '4' : '#f99aff',
    '5' : '#f99aff',
    '6' : '#7fd06b',
    '7' : '#7fd06b',
    '8' : '#7fd06b',
    '9' : '#7fd06b',
}

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
        if(author[0] == '_') {
            console.log('Dope');
            author = author.substr(1) + '✓';
        }
        miscA.innerText = author + ': ';
        miscB.innerText = message;
        if(author == 'Server')
            miscA.style.color = '#7d7dfd';
        if(author[0] in userColors && author[0] != '_')
            miscA.style.color = userColors[author[0]]
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
    const authInput = document.getElementById('auth_input');
    const button = document.getElementById('auth_button');
    authPopup = document.getElementsByClassName('contentAuth')[0];
    input.addEventListener('keydown', function(e) {
        if(ws.readyState != 1)
            return;
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
    button.addEventListener('click', function(e) {
        authPopup.style.display = 'none';
    });
    authInput.addEventListener('keydown', function(e) {
        if(e.code != 'Enter')
            return;
        authPopup.style.display = 'none';
        authObj = {'auth' : this.value};
        authObj = JSON.stringify(authObj);
        this.value = '';
        ws.send(authObj);
    });
});