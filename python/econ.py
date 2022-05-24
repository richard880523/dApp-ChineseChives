
from binance.spot import Spot 


def klines(symbol, interval, num = 1000):
    assert 0 < num and num <= 1000
    client = Spot()
    return client.klines(symbol, interval, limit=num)

## [TODO]: Economic Indicator Here ~


if __name__ == "__main__":
    # Test Section
    print( klines("ETHUSDT", '1m', 100) )
