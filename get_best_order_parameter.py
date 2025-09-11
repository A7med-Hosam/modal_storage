import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from get_live_candles import get_live_candles

# Set the style for better visualization
plt.style.use('dark_background')

# Functions to detect local tops and bottoms
def rw_top(data: np.array, curr_index: int, order: int) -> bool:
    if curr_index < order * 2 + 1:
        return False

    top = True
    k = curr_index - order
    v = data[k]
    for i in range(1, order + 1):
        if data[k + i] > v or data[k - i] > v:
            top = False
            break
    
    return top

def rw_bottom(data: np.array, curr_index: int, order: int) -> bool:
    if curr_index < order * 2 + 1:
        return False

    bottom = True
    k = curr_index - order
    v = data[k]
    for i in range(1, order + 1):
        if data[k + i] < v or data[k - i] < v:
            bottom = False
            break
    
    return bottom

def rw_extremes(data: np.array, order: int, balance, leverage):
    tops = []
    bottoms = []
    lowest_balance = balance
    trades = {}
    trade_id = 0
    trade_status = False

    def open_trade(balance, entry_price, trade_id, leverage):
        shares = leverage * balance / entry_price
        trades[f'{trade_id}'] = {
            "shares": float(f"{float(shares):.8f}"),
            "entry_price": float(entry_price),
            "entry_index": i,
            "exit_price": None,
            "exit_index": None,
            "pnl": None,
        }
        return True  # Balance goes to 0 when we open a trade

    def close_trade(balance, exit_price, trade_id):
        shares = trades[f'{trade_id}']['shares']
        new_balance = exit_price * shares
        old_balance = shares * trades[f'{trade_id}']['entry_price']
        pnl = float(f"{float(new_balance - old_balance):.2f}")
        fees = new_balance *0.001
        pnl = pnl-fees
        trades[f'{trade_id}']["fees"] = float(f"{float(fees):.5f}")
        trades[f'{trade_id}']["exit_price"] = float(f"{float(exit_price):.5f}")
        trades[f'{trade_id}']["exit_index"] = i
        trades[f'{trade_id}']["pnl"] = pnl
        # print(trades[f'{trade_id}']["exit_price"])
        new_balance = balance + pnl
        return new_balance, trade_id + 1, False

    for i in range(len(data)):
        if rw_top(data, i, order):
            top = [i, i - order, data[i - order], data[i]]
            if not trade_status:
                trade_status = open_trade(balance, data[i], trade_id,leverage)
            # if trade_status and str(trade_id) in trades:
            #     balance, trade_id, trade_status = close_trade(balance, data[i], trade_id)
            tops.append(top)

        if rw_bottom(data, i, order):
            bottom = [i, i - order, data[i - order], data[i]]
            bottoms.append(bottom)
            if trade_status and str(trade_id) in trades: 
                balance, trade_id, trade_status = close_trade(balance, data[i], trade_id)
            # if not trade_status:
            #     trade_status = open_trade(balance, data[i], trade_id,leverage)

        if balance < lowest_balance:
            lowest_balance = balance
        if lowest_balance < .4 * balance:
            continue

    return tops, bottoms, balance, trades, lowest_balance

# Main execution
# if __name__ == "__main__":
def get_best_order_parameter(initial_balance,coin_name,duration,leverage,interval=1,days_ago=0):
    
    get_live_candles(coin_name,duration,interval,days_ago)
    script_dir = Path(__file__).parent
# & C:/Users/kinga/AppData/Local/Programs/Python/Python311/python.exe f:/Files/LinuxProgrammingFiles/tests/Algorithmic_Trading/strategies/my_strategies/my_rw_long_strategy/rw_strategy_deepseek.py
    MOODENGUSDT_1m_Live = 'MOODENGUSDT_1m_Live'
    ETHUSDT_1m_Live = 'ETHUSDT_1m_Live'
    BIOUSDT_1m_Live = 'BIOUSDT_1m_Live'
    BTCUSDT_1m_Live = 'BTCUSDT_1m_Live'
    MOODENGUSDT_1m_Live = 'MOODENGUSDT_1m_Live'
    JASMYUSDT_1m_Live = 'JASMYUSDT_1m_Live'
    ETHUSDT_1m_Live = 'ETHUSDT_1m_Live'
    
    coin_name = f"{coin_name}_{interval}m_Live"

# & C:/Users/kinga/AppData/Local/Programs/Python/Python311/python.exe f:/Files/LinuxProgrammingFiles/tests/Algorithmic_Trading/strategies/my_strategies/my_rw_long_strategy/rw_strategy_deepseek.py

    # Load and prepare data
    data = pd.read_csv(f'{script_dir}/{coin_name}.csv')
    data['date'] = data['date'].astype('datetime64[s]')
    data = data.set_index('date')
    data = data.sort_index()
    
    # Find optimal order parameter
    initial_balance = initial_balance
    leverage = leverage

    highest_balance = initial_balance
    best_order_parameter = 3
    test_range= range(3, 80)
    orders = list(test_range)
    results_df = pd.DataFrame(index=orders)
    test_values = []
    trades_count = []
    test_results = []
    orders_winrates = []
    

    for test_num in test_range:
        tops, bottoms, balance, trades, lowest_balance = rw_extremes(data['close'].to_numpy(), test_num,initial_balance, leverage)
        test_results.append((test_num, balance, len(trades)))
        test_values.append(balance/initial_balance)
        trades_count.append(len(trades))
        profitable_trades = sum(1 for trade in trades.values() if trade['pnl'] is not None and trade['pnl'] > 0)
        total_trades = len(trades)
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0
        orders_winrates.append(win_rate)

        if balance > highest_balance :
            highest_balance = balance
            best_order_parameter = test_num

    
    # Run with optimal parameter
    print(best_order_parameter)
    tops, bottoms, balance, trades, lowest_balance = rw_extremes(data['close'].to_numpy(), best_order_parameter,initial_balance,leverage)

    # Create equity curve
    equity_curve = [initial_balance]  # Starting balance
    trade_dates = [data.index[0]]
    
    for trade_id, trade in trades.items():
        if trade['exit_price'] is not None:
            # Calculate balance after this trade
            new_balance = equity_curve[-1] + trade['pnl']
            equity_curve.append(new_balance)
            trade_dates.append(data.index[trade['exit_index']])
    
    # Plot equity curve
  
    # Create performance summary
    profitable_trades = sum(1 for trade in trades.values() if trade['pnl'] is not None and trade['pnl'] > 0)
    total_trades = len(trades)
    win_rate = profitable_trades / total_trades if total_trades > 0 else 0
    
    # Add text box with performance metrics

    # Print trade details
    print("Trade Details:")
    print("=" * 80)
    for trade_id, trade in trades.items():
        if trade['exit_price'] is not None:
            print(f"Trade {int(trade_id)+1}: Entry=${trade['entry_price']:.7f}, Exit=${trade['exit_price']:.7f}, "
                  f"PnL=${trade['pnl']:.2f},fees=${trade['fees']} Return={trade['pnl']*leverage/(trade['entry_price']*trade['shares'])*100:.2f}%")
    
    print("=" * 80)
    print(f"{coin_name} Summary: {profitable_trades} profitable trades out of {total_trades} "
          f"(Win Rate: {win_rate:.2%}), Final Balance: ${balance:.2f} Order {best_order_parameter} ")
    
    return best_order_parameter

# get_best_order_parameter("BTCUSDT",5.25,1)
