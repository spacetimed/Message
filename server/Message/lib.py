import asyncio
import websockets
from colorama import Fore, Back, Style

from typing import List
from typing import Type
from typing import Any

class Server:
    
    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.start: websockets.WebSocketServer = websockets.serve(self.handleNewClient, self.host, self.port)
        self.clients: List[Type[Client]] = []
        self.log: Type[Logger] = Logger(__name__ + '/' + __class__.__name__)
        if self.start is not None:
            self.log('Started! Listening...')

    async def handleNewClient(self, websocket: Any, path: Any) -> None:
        clientId: int = len(self.clients)
        self.clients.append(Client(clientId, websocket, path, self))
        await self.clients[clientId].serve()

    def handleDisconnect(self, clientId: int) -> None:
        if clientId <= len(self.clients):
            self.clients.pop(clientId)
        else:
            self.log(f'Disconnect error (Client #{str(clientId)})')
        return None


class Client():

    def __init__(self, clientId: int, websocket: Any, path: Any, MasterServer: Type[Server]) -> None:
        self.clientId: int = clientId
        self.websocket: Any = websocket
        self.path: Any = path
        self.MasterServer: Type[Server] = MasterServer
        print('New Client! #', clientId)

    async def serve(self) -> None:
        try:
            while True:
                message = await self.websocket.recv()
                print('Recv=>', message)
        except websockets.ConnectionClosed:
            self.MasterServer.handleDisconnect(self.clientId)
            print('Dc')


class Logger:

    def __init__(self, name: str) -> None:
        self.name: str = name
        if 'Server' in name:
            logo: str = """
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

    def __call__(self, message: str) -> None:
        print(f'{Fore.RED}{self.name.ljust(20)}{Style.RESET_ALL}{message}')