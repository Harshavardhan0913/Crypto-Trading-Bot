from database import WorkspaceData
from strategies import TechnicalStrategy,BreakoutStrategy


class Execute_strategy():
    def __init__(self, binance, bitmex, session):
        db = WorkspaceData()
        data = db.get('strategies', session['username'])
        exchange_type = {'binance': binance, 'bitmex': bitmex}
        for i, d in enumerate(data):
            strategy_type = d[1]
            element = d[2]
            exchange = d[3]
            timeframe = d[4]
            balance_pct = d[5]
            take_profit = d[6]
            stop_loss = d[7]
            activate = d[8]
            contract = exchange_type[exchange].contracts[element]
            if activate == 'ON':
                if strategy_type == 'Technical':
                    other_param = {'rsi_length': 0, 'ema_fast': 0, 'ema_slow': 0, 'ema_signal': 0}
                    new_strat = TechnicalStrategy(exchange_type[exchange], contract, exchange, timeframe, balance_pct, take_profit, stop_loss, other_param)
                else:
                    other_param = {'min_volume': 0}
                    new_strat = BreakoutStrategy(exchange_type[exchange], contract, exchange, timeframe, balance_pct, take_profit, stop_loss, other_param)
                new_strat.candles = exchange_type[exchange].get_historical_candles(contract, timeframe)

                if exchange == 'binance':
                    exchange_type[exchange].subscribe_channel([contract], 'aggTrade')
                    exchange_type[exchange].strategies[i] = new_strat
                    binance.add_log(f"{strategy_type} strategy on {element} / {timeframe} started ")
            elif activate == 'OFF':
                if i in exchange_type[exchange].strategies:
                    del exchange_type[exchange].strategies[i]
                    binance.add_log(f"{strategy_type} strategy on {element} / {timeframe} stopped ")





