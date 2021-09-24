import asyncio
import Message.lib
import websockets

HOST = '127.0.0.1'
PORT = 6943

if __name__ == '__main__':
    MessageServer = Message.lib.Server(HOST, PORT)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(MessageServer.start)
        loop.run_forever()
    except KeyboardInterrupt:
        print('Exit')