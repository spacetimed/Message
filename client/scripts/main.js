var ws;

window.addEventListener('DOMContentLoaded', () => {
    ws = new WebSocket("ws://127.0.0.1:6943/");

    document.getElementById('chatbar_input').addEventListener('input', function(e) {
        console.log(this.value);
        ws.send(this.value);
    });
});