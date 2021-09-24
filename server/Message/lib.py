import asyncio
import websockets
from colorama import Fore, Back, Style

class Server:
    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.start: websockets.WebSocketServer = websockets.serve(self.handleNewClient, self.host, self.port)
        self.clients = []
        self.log = Logger(__name__ + '/' + __class__.__name__)
        if self.start is not None:
            self.log('Started! Listening...')

    async def handleNewClient(self, websocket, path):
        print('New Client=>', websocket, path)
        try:
            while True:
                message = await websocket.recv()
                print('Recv=>', message)
        except websockets.ConnectionClosed:
            print('DC')


class Client:
    def __init__(self, websocket, path):
        print('New Client!')


class Logger:
    def __init__(self, name: str):
        self.name: str = name
        if 'Server' in name:
            logo = """
      `:+oo+/-`     
   `odMMMMMMMMNy:   
  -mMMMMMMMMMMMMMs          Welcome to Message!
  hMMMMMMMMMMMMMMM-           a simple chat server using websockets
  sMMMMMMMMMMMMMMN`           https://github.com/FFFFFF-base16/Message
  `sNMMMMMMMMMMMd-            2021, MIT License (c)
    -NMMMNMNmhs:`   
   -dMmy:...`       
 `oM:"""                   
            print(logo, end='\n\n')
    def __call__(self, message: str):
        print(f'{Fore.RED}{self.name.ljust(20)}{Style.RESET_ALL}{message}')