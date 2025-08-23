import random

from app.game import Player, BotPlayer, Game


def test_harvest_range():
    random.seed(0)
    p = Player("p")
    gain = p.harvest()
    assert 30 <= gain <= 100
    assert p.coins == gain
    assert p.crops == 1


def test_visit_merchant():
    p = Player("p", coins=0, crops=1)
    sold = p.visit_merchant()
    assert sold is True
    assert p.coins == 200
    assert p.crops == 0


def test_update_stock_price_range():
    random.seed(1)
    g = Game([Player("p")])
    price = g.update_stock_price()
    assert 0 <= price <= 400


def test_bot_turn():
    random.seed(2)
    bot = BotPlayer("bot")
    g = Game([bot])
    bot.take_turn(g)
    assert bot.coins >= 0
    assert bot.crops >= 0
