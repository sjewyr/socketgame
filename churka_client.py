import asyncio
import os
import sys
import threading
import time
import aioconsole
import dotenv
import pynput
from PyQt6 import QtWidgets as qtw
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot, QObject, QTimer
import qasync
from PyQt6.QtNetwork import QTcpSocket, QAbstractSocket
from abilities import Ability, ABILITIES

dotenv.load_dotenv('.env', override=True)

HOST = os.getenv('CHURKA_SERVER_ADDR')
PORT = int(os.getenv('CHURKA_SERVER_PORT'))

class MyQAbility(qtw.QWidget):
    def __init__(self, ability: Ability):
        super().__init__()
        self.ability: Ability = ability
        self.cooldown_label = qtw.QLabel(f"cd: {self.ability.base_cooldown}")
        self.label = qtw.QLabel(self.ability.name)
        self.descr = qtw.QLabel(self.ability.description)
        layout = qtw.QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(qtw.QLabel(f"[{self.ability.key}]"))
        layout.addWidget(self.label)
        layout.addWidget(self.descr)
        layout.addWidget(self.cooldown_label)
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.reset)
        

    def reset(self):
        if self.ability.cooldown > 0:
            self.ability.cooldown -= 1
            self.label.setText(f'{self.ability.name} ({self.ability.cooldown}/{self.ability.base_cooldown})')
        else:
            self.label.setText(self.ability.name)

    def use(self):
        if self.ability.cooldown:
            return False
        self.ability.cooldown = self.ability.base_cooldown
        self.label.setText(f'{self.ability.name} ({self.ability.cooldown}/{self.ability.base_cooldown})')
        self.timer.start()
        return True


class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.player = Player()
        self.setWindowTitle("Churka Server")
        self.sock = QTcpSocket()
        self.sock.connectToHost(HOST, PORT)
        self.sock.readyRead.connect(self.readed)
        
        self.stall = True
        self.sock.setSocketOption(QAbstractSocket.SocketOption.LowDelayOption, 1)

        self.label = qtw.QLabel("Churka Client")
        self.label2 = qtw.QLabel("label2")
        self.label2.setText(f'Гражданство: {str(self.player.churka)}')
        self.enemy_churka = 1000
        self.enemychurka = qtw.QLabel(f"Гражданство второй чурки: {str(1000)}")
        self.abilities = {val.key: MyQAbility(val) for val in ABILITIES}
        self.pause = qtw.QLabel(f"GAME IS NOT STARTED... WAITING FOR SECOND PLAYER TO CONNECT")
        
        self.setFixedSize(500, 500)
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        for _, ability in self.abilities.items():
            layout.addWidget(ability)
        layout.addWidget(self.label)
        layout.addWidget(self.pause)
        layout.addWidget(self.label2)
        layout.addWidget(self.enemychurka)





    @pyqtSlot(object)
    def update_text(self, data):
        self.label2.setText(data.decode())

    @pyqtSlot()
    def readed(self):
        data = self.sock.readAll().data().decode().strip()
        if data == 'gay':
            self.player.churka -= 10
            self.label2.setText(f'Гражданство: {str(self.player.churka)}')
        if data.startswith('take'):
            data = data.split('take ')[1]

            self.player.churka = int(data)
            self.label2.setText(f'Гражданство: {str(self.player.churka)}')
        if data == 'start':
            self.stall = False
            self.pause.setText("")
        if data.startswith('enemy'):
            data = data.split('enemy ')[1]
            self.enemy_churka = int(data)
            self.enemychurka.setText(f"Гражданство второй чурки: {self.enemy_churka}")


    def keyPressEvent(self, event):
        if self.stall:
            return
        if isinstance(event, QKeyEvent):
            key_text = event.text()
            self.label.setText(f"Last Key Pressed: {key_text}")
            asyncio.create_task(self.write_key(key_text))

    async def write_key(self, key_text):
        if key_text in self.abilities:
            ability = self.abilities[key_text]
            if not ability.use():
                return
            self.sock.write((ability.ability.name+'\n').encode())
            self.sock.flush()
    

        

class Player():
    def __init__(self):
        self.churka = 1000




async def main():
    try:
        app = qtw.QApplication(sys.argv)
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        window = MainWindow()
        window.show()
        # Corrected: Directly running loop.run_forever() without 'with' block
        loop.run_forever()
        
        

        
    except ConnectionRefusedError:
        print("Server not running. Please start churka_server.py")

asyncio.run(main())