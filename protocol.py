from enum import Enum


class MESSAGE(Enum):
    START = "start"
    TAKE = "take"
    ENEMY = "enemy"
    WIN = "win"
    LOSE = "lose"
    KYS = "kys"


def encode(message: MESSAGE, data=None):
    return (
        (message.value + " " + str(data) + "\n").encode()
        if data
        else (message.value + "\n").encode()
    )
