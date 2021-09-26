import asyncio
import websockets
import json
import aiosqlite

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
        - /identify command (e.g. /identify man)
        - if account exists, asks for passkey (new prompt for this)
        - authenticates and updates username/color "man </(checkmark!)"
        - Make database tables (`users` -> `username`, `password`)
        - databases / sqlite?
"""

class Server:
    
    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.start: websockets.WebSocketServer = websockets.serve(self.handleNewClient, self.host, self.port)
        self.clients: List[Type[Client]] = []
        self.clientIdIndex: int = 0
        self.log: Type[Logger] = Logger(f'{__name__}/{__class__.__name__}')
        self.database = None
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
        self.tempUsername = None
        self.commands = {
            'users'    : self.handleUsersCommand,
            'id'       : self.handleIdCommand,
            'identify' : self.handleIdentify,
        }

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
        async def CommandWrapper(self, data) -> None:
            messageObject: Union[Dict, None] = await commandFunc(self, data)
            if messageObject is not None:
                return await self.send('message', messageObject)
        return CommandWrapper

    @CommandHandler
    async def handleUsersCommand(self, data) -> str:
        message: Union[Dict, str] = f'Number of active users: {str(len(self.MasterServer.clients))}'
        message = {'author' : 'Server', 'message' : message}
        return(message)

    @CommandHandler
    async def handleIdCommand(self, data) -> str:
        message: Union[Dict, str] = f'Your ID is: {str(self.clientId)}'
        message = {'author' : 'Server', 'message' : message}
        return(message)

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

    @CommandHandler
    async def handleIdentify(self, data) -> Union[None, Dict]:
        if(len(data) != 1):
            message: Dict = {'author' : 'Server', 'message' : 'Incorrect syntax. (e.g. /identify username)'}
            return(message)
        username = data[0]
        if username is not None:
            async with aiosqlite.connect('Message.db') as db:
                async with db.execute('SELECT * FROM accounts WHERE `username` = :username', {'username' : username}) as cursor:
                    result = await cursor.fetchall()
                    if len(result) > 0:
                        self.tempUsername = username
                        message: Dict = {'author' : 'Server', 'message' : 'Authentication required...', 'authRequired' : True}
                        return(message)
        message: Dict = {'author' : 'Server', 'message' : 'User does not exist.'}
        return(message)

    @CommandHandler
    async def handleIdentifyPassword(self, data) -> None:
        if len(data) > 0 and self.tempUsername is not None:
            tempPassword = sha256(data.encode('utf-8')).hexdigest()
            async with aiosqlite.connect('Message.db') as db:
                async with db.execute('SELECT * FROM accounts WHERE `username` = :username AND `password` = :password', {'username' : self.tempUsername, 'password' : tempPassword}) as cursor:
                    result = await cursor.fetchall()
                    if len(result) > 0:
                        self.clientHash = '_' + self.tempUsername.lower()
                        handshake: Dict = await self.makeHandshake()
                        await self.send('handshake', handshake)
                        message: Dict = {'author' : 'Server', 'message' : 'Success!'}
                        return(message)
        message: Dict = {'author' : 'Server', 'message' : 'Authentication failed.'}
        return(message)

    def isJson(self, object):
        try:
            json.loads(object)
        except ValueError as e:
            return False
        return True
                        
    async def send(self, type: str, data: dict) -> None:
        local: Union[Dict, str] = {'type' : type, 'data' : data}
        local = json.dumps(local)
        self.log(f'SEND => {local}')
        await self.websocket.send(local)

    async def recv(self, message: str) -> None:
        self.log(f'RECV <= {message}')
        if(message[0] == '/' and message.split(' ')[0][1:] in self.commands):
            data = message.split(' ')
            await self.commands[data[0][1:]](data[1:])
        else:
            if self.isJson(message):
                recvObj = json.loads(message)
                if 'auth' in recvObj:
                    await self.handleIdentifyPassword(recvObj['auth'])
            else:
                await self.handleSendMessage(message)

    async def makeHandshake(self) -> str:
        handshake: Union[Dict, str] = {'clientId' : self.clientId, 'clientHash': self.clientHash}
        handshake = json.dumps(handshake)
        return handshake

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