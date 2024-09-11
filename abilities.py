class Ability:
    def __init__(self, key, name, cooldown, description, fn):
        self.key = key
        self.name = name
        self.base_cooldown = cooldown
        self.cooldown = 0
        self.description = description
        self.fn = fn

    def calculate(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


def deport(*args, **kwargs):
    enemy = kwargs.pop("enemy")
    kwargs.pop("player")
    return (1000 - enemy) * 0.1


def heroin(*args, **kwargs):
    return 50


ABILITIES = [
    Ability("q", "Депортация", 10, "10% от недостающего гражданства цели", deport),
    Ability("w", "Подкинуть героин", 3, "-50 гражданства", heroin),
]
