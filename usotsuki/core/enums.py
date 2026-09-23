from enum import IntEnum, Enum, auto

class Ranks(IntEnum):
    FOUR = 0
    FIVE = 1
    SIX = 2
    SEVEN = 3
    QUEEN = 4
    JACK = 5
    KING = 6
    ACE = 7
    TWO = 8
    THREE = 9

class Suits(IntEnum):
    DIAMONDS = 0
    SPADES = 1
    HEARTS = 2
    CLUBS = 3

class Actions(Enum):
    RAISE = auto()
    FOLD = auto()
    ACCEPT = auto()

class Teams(Enum):
    ODD = "odd team"
    EVEN = "even team"

class GameState(Enum):
    PLAYING = auto()
    ROUND_END = auto()
    MATCH_END = auto()
    
    MENU = auto()