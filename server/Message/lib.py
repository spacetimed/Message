import asyncio
import websockets
import json

from colorama import Fore, Back, Style
from time import time as getTimestamp
from hashlib import sha256

from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Any
from typing import Union

"""
    To Do:
    - Show login prompt
    - Make database tables (`users`, `messages[?]`)
    Bugs:
    - [FIXED] If only 2 clients in room, and client 0 refreshes, it does not display any information to client 1 
                              []
            0 -> Join  	      [0]
            1 -> Join	      [0,1]
            0 -> Disconnect	  [1]
            1 -> Join	      [1,1]
"""

class Server:
    
    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.start: websockets.WebSocketServer = websockets.serve(self.handleNewClient, self.host, self.port)
        self.clients: List[Type[Client]] = []
        self.clientIdIndex: int = 0
        self.log: Type[Logger] = Logger(f'{__name__}/{__class__.__name__}')
        if self.start is not None:
            self.log('Started! Listening...')

    async def handleNewClient(self, websocket: Any, path: Any) -> None:
        clientId: int = self.clientIdIndex
        self.clientIdIndex += 1
        self.clients.append(Client(clientId, websocket, path, self))
        await self.clients[-1].serve()

    async def handleDisconnect(self, clientObject: Any, clientId: int) -> None:
        if clientObject in self.clients:
            self.clients.remove(clientObject)
        else:
            self.log(f'Disconnect error (Client #{str(clientId)})')
        return None


class Client:

    def __init__(self, clientId: int, websocket: Any, path: Any, MasterServer: Type[Server]) -> None:
        self.clientId: int = clientId
        self.websocket: Any = websocket
        self.path: Any = path
        self.MasterServer: Type[Server] = MasterServer
        self.clientHash: str = self.makeClientHash()
        self.log: Type[Logger] = Logger(f'{__name__}/{__class__.__name__}::{self.clientId}')
        self.log('New connection!')
        self.commands = {
            'users' : self.handleUsersCommand,
        }

    def BroadcastHandler(commandFunc) -> None:
        async def BroadcastWrapper(self, *args, **kwargs) -> None:
            if(len(self.MasterServer.clients) > 1):
                for client in self.MasterServer.clients:
                    if client.clientId != self.clientId:
                        messageObject: Dict = await commandFunc(self, *args)
                        await client.send('message', messageObject)
            return None
        return BroadcastWrapper

    def CommandHandler(commandFunc) -> None:
        async def CommandWrapper(self) -> None:
            return await self.send('message', {'author' : 'Server', 'message' : await commandFunc(self)})
        return CommandWrapper

    async def serve(self) -> None:
        handshake: Dict = await self.makeHandshake()
        await self.send('handshake', handshake)
        await self.handleWelcome()
        try:
            while True:
                message: str = await self.websocket.recv()
                await self.recv(message)
        except websockets.ConnectionClosed:
            self.log('Disconnect')
            await self.handleGoodbye()
            await self.MasterServer.handleDisconnect(self, self.clientId)

    async def makeHandshake(self) -> str:
        handshake: Union[Dict, str] = {'clientId' : self.clientId, 'clientHash': self.clientHash}
        handshake = json.dumps(handshake)
        return handshake

    @CommandHandler
    async def handleUsersCommand(self) -> str:
        return f'Number of active users: {str(len(self.MasterServer.clients))}'

    @BroadcastHandler
    async def handleWelcome(self) -> str:
        message: Union[Dict, str] = self.clientHash + ' has entered the chat.'
        message = {'author' : 'Server', 'message' : message}
        return(message)

    @BroadcastHandler
    async def handleGoodbye(self) -> str:
        message: Union[Dict, str] = self.clientHash + ' has left the chat.'
        message = {'author' : 'Server', 'message' : message}
        return(message)

    @BroadcastHandler
    async def handleSendMessage(self, message) -> None:
        message: Dict = {'author' : self.clientHash, 'message' : message}
        return(message)

    async def send(self, type: str, data: dict) -> None:
        local: Union[Dict, str] = {'type' : type, 'data' : data}
        local = json.dumps(local)
        self.log(f'SEND => {local}')
        await self.websocket.send(local)

    async def recv(self, message: str) -> None:
        self.log(f'RECV <= {message}')
        if(message[0] == '/' and message[1:] in self.commands):
            await self.commands[message[1:]]()
        else:
            await self.handleSendMessage(message)

    def makeClientHash(self) -> str:
        toEncode: bytes = (str(getTimestamp()) + str(self.clientId)).encode('utf-8')
        return sha256(toEncode).hexdigest()[:8]


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
        print(f'{Fore.RED}{self.name.ljust(26)}{Style.RESET_ALL}{message}')