from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List


@dataclass
class Player:
    """Represents a player in the farming board game."""

    name: str
    coins: int = 0
    crops: int = 0
    stocks: int = 0

    def harvest(self) -> int:
        """Harvest crops yielding 30-100 coins and storing one crop."""
        gain = random.randint(30, 100)
        self.coins += gain
        self.crops += 1
        return gain

    def visit_merchant(self) -> bool:
        """Sell one crop to a travelling merchant for 200 coins."""
        if self.crops <= 0:
            return False
        self.crops -= 1
        self.coins += 200
        return True

    def buy_stock(self, game: Game, shares: int = 1) -> bool:
        """Buy stock at the current market price."""
        cost = shares * game.stock_price
        if self.coins < cost:
            return False
        self.coins -= cost
        self.stocks += shares
        return True


class BotPlayer(Player):
    """Simple bot that automatically performs a series of actions each turn."""

    def take_turn(self, game: Game) -> None:
        self.harvest()
        self.visit_merchant()
        if self.coins >= game.stock_price:
            self.buy_stock(game)


class Game:
    """Core game engine managing players and stock price."""

    def __init__(self, players: List[Player]):
        self.players = players
        self.stock_price = 100

    def update_stock_price(self) -> int:
        """Update stock price by -100% to +300%."""
        change = random.randint(-100, 300)
        self.stock_price = max(0, int(self.stock_price * (1 + change / 100)))
        return self.stock_price
