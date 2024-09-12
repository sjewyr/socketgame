import asyncio
import asyncio.streams
import os
import sys
from enum import Enum

import aioconsole
import dotenv

from abilities import ABILITIES
from abilities import CalculationInput

ABILITIES_DICT = {v.name: v for v in ABILITIES}

dotenv.load_dotenv(".env", override=True)

HOST = os.getenv("CHURKA_SERVER_ADDR")
PORT = int(os.getenv("CHURKA_SERVER_PORT"))


class Player:
    def __init__(self, num, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.num: int = num
        self.reader: asyncio.StreamReader = reader
        self.writer: asyncio.StreamWriter = writer
        self.blocking: float = 0.0
        self.churka = 1000
        self.damage_boost = 0


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

    async def connection_callback(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        if self.player1:
            self.player2 = Player(2, reader, writer)
            self.state = State.PLAYING
            self.player1.writer.write("Starting\n".encode())
            self.player2.writer.write("Starting\n".encode())
            self.player2.writer.write("Starting".encode())
            await self.player2.writer.drain()
            self.player1.writer.write("Starting".encode())
            await self.player1.writer.drain()
            self.players = [self.player1, self.player2]

        else:
            self.player1 = Player(1, reader, writer)
            self.state = State.WAITING_FOR_SECOND_PLAYER
            self.player1.writer.write("Waiting for second player...\n".encode())
            await self.player1.writer.drain()

    async def stop_until_ready(self):
        while self.state == State.WAITING_FOR_FIRST_PLAYER:
            await asyncio.sleep(1)
            print("Waiting for first player...")
        while self.state == State.WAITING_FOR_SECOND_PLAYER:
            await asyncio.sleep(1)
            print("Waiting for second player...")
        print("Game started!")
        self.player1.writer.write("start".encode("utf8"))
        await self.player1.writer.drain()
        self.player2.writer.write("start".encode("utf8"))
        await self.player2.writer.drain()
        await asyncio.gather(
            self.handle_player_input(self.player1, self.player2),
            self.handle_player_input(self.player2, self.player1),
            self.derji_v_kurse(),
            self.mainloop(),
        )

    async def derji_v_kurse(self):
        while True:
            self.player1.writer.write(f"take {self.player1.churka}\n".encode())
            await self.player1.writer.drain()
            await asyncio.sleep(0.25)
            self.player1.writer.write(f"enemy {self.player2.churka}\n".encode())
            await self.player1.writer.drain()
            await asyncio.sleep(0.1)
            self.player2.writer.write(f"take {self.player2.churka}\n".encode())
            await self.player2.writer.drain()
            await asyncio.sleep(0.25)
            self.player2.writer.write(f"enemy {self.player1.churka}\n".encode())
            await self.player2.writer.drain()
            await asyncio.sleep(0.1)

            if self.player1.churka <= 0:
                self.player1.writer.write("win\n".encode())
                self.player2.writer.write("lose\n".encode())
                await self.player1.writer.drain()
                await self.player2.writer.drain()
                sys.exit()

            if self.player2.churka <= 0:
                self.player2.writer.write("win\n".encode())
                self.player1.writer.write("lose\n".encode())
                await self.player1.writer.drain()
                await self.player2.writer.drain()
                sys.exit()

    async def handle_player_input(self, player: Player, other: Player):
        while True:
            data = await player.reader.readline()
            if data:
                print(f"Player {player.num}: {data.decode().strip()}")
                data = data.decode().strip()
                if data in ABILITIES_DICT:
                    results = ABILITIES_DICT[data].calculate(
                        CalculationInput(
                            other.churka, player.churka, player.damage_boost
                        )
                    )
                    if results.enemy:
                        if not other.blocking:
                            other.churka -= int(results.enemy or 0)
                        else:
                            player.churka -= int(results.enemy or 0)
                            other.blocking = 0
                    player.churka += int(results.player or 0)
                    player.blocking += int(results.block or 0)
                    player.damage_boost += int(results.damage_boost or 0)

            if not data:
                break

            await aioconsole.aprint("User input receiving")

    async def mainloop(self):
        while True:
            for player in self.players:
                if player.blocking:
                    player.blocking = max(0, player.blocking - 0.1)

            await asyncio.sleep(0.1)


g = Game()


async def main():
    await asyncio.start_server(g.connection_callback, HOST, PORT)
    await g.stop_until_ready()
    while True:
        pass


asyncio.run(main())
