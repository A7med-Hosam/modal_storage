import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path
import numpy as np
from get_live_candles import get_live_candles
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates
from time import sleep

script_dir = Path(__file__).parent

# coin_name = "BTCUSDT"
# interval = 3
# file_name = f'{coin_name}_{interval}m'

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
                if i != len(data)-1:
                    trade_status = open_trade(balance, data[i], trade_id,leverage)
                else:
                    print("skip ", i)
            # if trade_status and str(trade_id) in trades:
            #     balance, trade_id, trade_status = close_trade(balance, data[i], trade_id)
            tops.append(top)

        if rw_bottom(data, i, order):
            bottom = [i, i - order, data[i - order], data[i]]
            bottoms.append(bottom)
            if trade_status and str(trade_id) in trades: 
                if i != len(data)-1:
                    balance, trade_id, trade_status = close_trade(balance, data[i], trade_id)
                else:
                    print("skip ", i)
            # if not trade_status:
            #     trade_status = open_trade(balance, data[i], trade_id,leverage)

        if balance < lowest_balance:
            lowest_balance = balance
        if lowest_balance < .4 * balance:
            continue

    return tops, bottoms, balance, trades, lowest_balance

# Main execution
fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 10), gridspec_kw={'height_ratios': [4, 1.5]})

coin_name_ = "MOODENGUSDT"
interval_ = 1
duration_ = interval_ * 0.3

initial_balance_ = 10
leverage_ = 10

days_ago = 0

# days_ago_enhance = 0.0 if days_ago == 0 else days_ago

from get_best_order_parameter import get_best_order_parameter
best_order_parameter = 25
best_order_parameter = get_best_order_parameter(initial_balance_,coin_name_,interval_,leverage_,interval_,days_ago)

def animate(i):
    coin_name = coin_name_
    interval = interval_
    duration = duration_

    initial_balance = initial_balance_
    leverage = leverage_

    order_parameter = best_order_parameter

    get_live_candles(coin_name,duration,interval,days_ago)
    
    ax1.cla()
    ax2.cla()
    script_dir = Path(__file__).parent
# & C:/Users/kinga/AppData/Local/Programs/Python/Python311/python.exe f:/Files/LinuxProgrammingFiles/tests/Algorithmic_Trading/strategies/my_strategies/my_rw_long_strategy/rw_strategy_deepseek.py

    BTCUSDT_1m_Live = "BTCUSDT_1m_Live"
    BTCUSDT_3m_Live = 'BTCUSDT_3m_Live'

    # coin_name = BTCUSDT_1m_Live  
    coin_name = f"{coin_name}_{interval}m_Live"
    # Load and prepare data
    data = pd.read_csv(f'{script_dir}/{coin_name}.csv')

    # data = data[-1000:]
    data['date'] = data['date'].astype('datetime64[s]')
    data = data.sort_index()

    ohlc = data.loc[:, ['date', 'open', 'high', 'low', 'close']]
    ohlc['date'] = data['date'].astype('datetime64[s]')
    ohlc['date'] = ohlc['date'].apply(mpl_dates.date2num)
    ohlc = ohlc.astype(float)
    data = data.set_index('date')

    plt.cla()
    # ax1.plot(data.index, data['close'], label=f'{coin_name}', linewidth=1, color='cyan')
    candles = candlestick_ohlc(ax1, ohlc.values, width=0.32*interval/1000,colorup="#009411", colordown="#ff0000", alpha=1)
    lines, patches = candles
    patches[-1].set_label(coin_name)

    date_format = mpl_dates.DateFormatter('%d-%m %H:%M')
    ax1.xaxis.set_major_formatter(date_format)

    
    # Find optimal order parameter
    initial_balance = initial_balance
    leverage = leverage
    
    tops, bottoms, balance, trades, lowest_balance = rw_extremes(data['close'].to_numpy(), order_parameter,initial_balance,leverage)
    

    # Plot price data
    
    
    # Plot tops and bottoms
    idx = data.index
    for top in tops:
        ax1.plot(idx[top[1]], top[2], marker='o', color="#a13491ac", markersize=4, alpha=0.7)
        ax1.plot(idx[top[0]], top[3], marker='^', color="#00ff40ff", markersize=6, alpha=0.7)
    
    for bottom in bottoms:
        ax1.plot(idx[bottom[1]], bottom[2], marker='o', color="#6fc4299c", markersize=4, alpha=0.7)
        ax1.plot(idx[bottom[0]], bottom[3], marker='v', color='orange', markersize=6, alpha=0.7)
    
    # Plot trade entries and exits
    for trade_id, trade in trades.items():
        if trade['exit_price'] is not None:
            entry_idx = trade['entry_index']
            exit_idx = trade['exit_index']
            
            # Draw trade line from entry to exit
            ax1.plot([idx[entry_idx], idx[exit_idx]], 
                    [trade['entry_price'], trade['exit_price']], 
                    color="#02fa1f" if trade['pnl'] > 0 else 'red', 
                    linewidth=1, alpha=0.7)

    
    ax1.set_title(f'{coin_name}Testing (Duration= {duration}D, Order={order_parameter}, Final Balance=${balance:.2f})')
    ax1.set_ylabel('Price (USD)')

    ax1.grid(True, alpha=0.3)
    
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
    ax2.plot(trade_dates, equity_curve, color='white', linewidth=0.3)
    ax2.fill_between(trade_dates, equity_curve, initial_balance, where=[x >= initial_balance for x in equity_curve],
                    alpha=0.3, color="green", interpolate=True)
    ax2.fill_between(trade_dates, equity_curve, initial_balance, where=[x <= initial_balance for x in equity_curve], 
                    alpha=0.3, color="red", interpolate=True)
    ax2.axhline(y=initial_balance, color='gray', linestyle='--', alpha=0.3)
    ax2.set_title('Equity Curve')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Account Balance (USD)')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Create performance summary
    profitable_trades = sum(1 for trade in trades.values() if trade['pnl'] is not None and trade['pnl'] > 0)
    total_trades = len(trades)
    win_rate = profitable_trades / total_trades if total_trades > 0 else 0
    
    total_fees = 0
    for trade in trades.values():
        total_fees += trade['fees'] if "fees" in trade else 0
    
    # Add text box with performance metrics
    textstr = '\n'.join((
        f'Initial Balance: ${initial_balance}',
        f'Leverage: {leverage_}x',
        f'Final Balance: ${balance:.2f}',
        f'Total Fees: ${total_fees:.4f}',
        f'Return: + {100*(balance-initial_balance)/initial_balance:.2f}%',
        f'Total Trades: {total_trades}',
        f'Winner : {profitable_trades}',
        f'Win Rate: {win_rate:.2%}',
        f'Order Parameter: {order_parameter}',
        f'Lowest Balance: ${lowest_balance:.2f}'))
    
    props = dict(boxstyle='round', facecolor='black', alpha=0.4)
    ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=11,
            verticalalignment='top', bbox=props, color='white')
    
    
    # Print trade details
    print("Trade Details:")
    print("=" * 80)
    for trade_id, trade in trades.items():
        if trade['exit_price'] is not None:
            print(f"Trade {int(trade_id)+1}: Entry=${trade['entry_price']:.7f}, Exit=${trade['exit_price']:.7f}, "
                  f"PnL=${trade['pnl']:.2f},fees=${trade['fees']} Return={trade['pnl']*leverage/(trade['entry_price']*trade['shares'])*100:.2f}%")
    
    print("=" * 80)
    print(f"Summary: {profitable_trades} profitable trades out of {total_trades} "
          f"(Win Rate: {win_rate:.2%}), Final Balance: ${balance:.2f} Order {order_parameter} ")
    ax1.legend(loc='lower left',fontsize=9)
    plt.savefig(f'{script_dir}/live_plot.png')
    


while True:
    animate(0)
    sleep(.5)

# anim = FuncAnimation(fig2, animate, interval=2000,cache_frame_data=False)
# plt.tight_layout()
# plt.show()
