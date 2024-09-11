import asyncio.streams
from enum import Enum
import asyncio

import aioconsole
from keyboard import play
from abilities import Ability, ABILITIES
import os
import dotenv

ABILITIES_DICT = {v.name: v for v in ABILITIES}

dotenv.load_dotenv('.env', override=True)

HOST = os.getenv('CHURKA_SERVER_ADDR')
PORT = int(os.getenv('CHURKA_SERVER_PORT'))

class Player:
    def __init__(self, num, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.num: int = num
        self.reader: asyncio.StreamReader = reader
        self.writer: asyncio.StreamWriter = writer
        self.churka = 1000



class State(Enum):
    NOT_CONNECTED = 0
    WAITING_FOR_FIRST_PLAYER = 1
    WAITING_FOR_SECOND_PLAYER = 2
    PLAYING = 3

class Game:
    def __init__(self):
        self.state = State.NOT_CONNECTED
        self.state = State.WAITING_FOR_FIRST_PLAYER
        self.player1 = None
        self.player2 = None
        self.players = []


    async def connection_callback(self, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        if self.player1:
            self.player2 = Player(2, reader, writer)
            self.state = State.PLAYING
            self.player1.writer.write('Starting\n'.encode())
            self.player2.writer.write('Starting\n'.encode())
            self.player2.writer.write('Starting'.encode())
            await self.player2.writer.drain()
            self.player1.writer.write('Starting'.encode())
            await self.player1.writer.drain()
            self.players = [self.player1, self.player2]
            
        else:
            self.player1 = Player(1, reader, writer)
            self.state = State.WAITING_FOR_SECOND_PLAYER
            self.player1.writer.write('Waiting for second player...\n'.encode())
            await self.player1.writer.drain()

    async def stop_until_ready(self):
        while self.state == State.WAITING_FOR_FIRST_PLAYER:
            await asyncio.sleep(1)
            print("Waiting for first player...")
        while self.state == State.WAITING_FOR_SECOND_PLAYER:
            await asyncio.sleep(1)
            print("Waiting for second player...")
        print("Game started!")
        self.player1.writer.write('start'.encode('utf8'))
        await self.player1.writer.drain()   
        self.player2.writer.write('start'.encode('utf8'))
        await self.player2.writer.drain()
        await asyncio.gather(self.handle_player_input(self.player1, self.player2), self.handle_player_input(self.player2, self.player1), self.derji_v_kurse())

    async def derji_v_kurse(self):
        while True:
            self.player1.writer.write(f'take {self.player1.churka}\n'.encode())
            await self.player1.writer.drain()
            await asyncio.sleep(0.25)
            self.player1.writer.write(f'enemy {self.player2.churka}\n'.encode())
            await self.player1.writer.drain()
            await asyncio.sleep(0.1)
            self.player2.writer.write(f'take {self.player2.churka}\n'.encode())
            await self.player2.writer.drain()
            await asyncio.sleep(0.25)
            self.player2.writer.write(f'enemy {self.player1.churka}\n'.encode())
            await self.player2.writer.drain()
            await asyncio.sleep(0.1)
    async def handle_player_input(self, player: Player, other: Player):
        while True:
            data = await player.reader.readline()
            if data:
                print(f"Player {player.num}: {data.decode().strip()}")
                data = data.decode().strip()
                if data in ABILITIES_DICT:
                    damage = ABILITIES_DICT[data].calculate(enemy=other.churka, player=player.churka)
                    other.churka -= int(damage)
                    

            if not data:
                break

            
            await aioconsole.aprint('User input receiving')








g = Game()

async def main():
    server = await asyncio.start_server(g.connection_callback, HOST, PORT)
    await g.stop_until_ready()
    while True:
        pass


asyncio.run(main())


