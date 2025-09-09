# import matplotlib
# matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path
from get_live_candles import get_live_candles
script_dir = Path(__file__).parent


coin_name = "JASMYUSDT"
interval = 1
file_name = f'{coin_name}_{interval}m'

plt.style.use('dark_background')
def animate(i):
    plt.cla()
    get_live_candles(coin_name,0.12,interval)
    data = pd.read_csv(f'{script_dir}/{file_name}_Live.csv')
    data['date'] = data['date'].astype('datetime64[s]')
    # data = data.set_index('date')
    data = data.sort_index()
    # plt.plot(x, y1, label='ETHUSDT_1m')
    # plt.plot(x, y2, label='Channel 2')
    plt.plot(data['date'], data['close'], label=file_name, linewidth=0.8, color='yellow')
    plt.legend(loc='upper right')
    plt.tight_layout()
    print("live chart working")
    print(20*"=") 
    plt.savefig(f'{script_dir}/live_plot.png')
    print("plot saved")

anim = FuncAnimation(plt.gcf(), animate, interval=2000,cache_frame_data=False)
plt.tight_layout()
plt.show()
