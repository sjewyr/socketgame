import random


class CalculationResult:
    def __init__(
        self,
        enemy: int = None,
        player: int = None,
        block: int = None,
        damage_boost: int = None,
        shield: int = None,
    ):
        self.enemy = enemy
        self.player = player
        self.block = block
        self.damage_boost = damage_boost
        self.shield = shield


class CalculationInput:
    def __init__(self, enemy, player, damage_boost) -> None:
        self.enemy = enemy
        self.player = player
        self.damage_boost = damage_boost


class Ability:
    def __init__(self, key, name, cooldown, energy, description, fn):
        self.key = key
        self.name = name
        self.base_cooldown = cooldown
        self.cooldown = 0
        self.energy = energy
        self.description = description
        self.fn = fn

    def calculate(self, args: CalculationInput) -> CalculationResult:
        return self.fn(args)


def deport(args: CalculationInput) -> CalculationResult:
    enemy = args.enemy
    return CalculationResult(enemy=(1000 - enemy) * 0.15)


def heroin(args: CalculationInput) -> CalculationResult:
    damage = 50 + args.damage_boost
    return CalculationResult(enemy=damage)


def eat_shawarma(args: CalculationInput) -> CalculationResult:
    player = args.player
    max_health = 1100 - player
    return CalculationResult(player=min(75, max_health))


def atomic_churka(args: CalculationInput) -> CalculationResult:
    damage = args.damage_boost + 300
    return CalculationResult(enemy=damage, player=-1 * damage)


def block(args: CalculationInput) -> CalculationResult:
    return CalculationResult(block=8)


def push_ups(args: CalculationInput) -> CalculationResult:
    return CalculationResult(damage_boost=15)


def shield(args: CalculationInput) -> CalculationResult:
    return CalculationResult(shield=500)


def steal_kosar(args: CalculationInput) -> CalculationResult:
    damage = random.randint(25, 250) + args.damage_boost
    return CalculationResult(enemy=damage)


ABILITIES = [
    Ability("q", "Депортация", 10, 250, "15% от недостающего гражданства цели", deport),
    Ability("w", "Подкинуть героин", 2, 50, "-50 гражданства", heroin),
    Ability("e", "Есть шаурму", 2, 100, "+75 гражданства", eat_shawarma),
    Ability(
        "r",
        "Подорваться кхерам",
        15,
        400,
        "Отнимает 300 гражданства у цели и 300 у игрока",
        atomic_churka,
    ),  # noqa: E501
    Ability(
        "t",
        "Мусорнуться",
        16,
        300,
        "Отражает следующее действие в течении 8 секунд",
        block,
    ),
    Ability("a", "Анжуманя", 5, 250, "+15 к наносимому урону навсегда", push_ups),
    Ability(
        "s",
        "Украсть косарь",
        5,
        150,
        "Наносит че-то около 140 урона в среднем хз",
        steal_kosar,
    ),
    Ability(
        "z",
        "Нацепить модные цацки",
        15,
        250,
        "Дает временный щит на 500(-10/с) хп",
        shield,
    ),
]
