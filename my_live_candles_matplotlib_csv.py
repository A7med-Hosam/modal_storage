
import random
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path
from get_live_candles import get_live_candles
script_dir = Path(__file__).parent


# plt.style.use('fivethirtyeight')
plt.style.use('dark_background')

x_vals = []
y_vals = []

index = count()

coin_name = "JASMYUSDT"
interval = 1
file_name = f'{coin_name}_{interval}m'

# plot_count = 1

def animate(i):
    plt.cla()
    get_live_candles(coin_name,0.12,interval)
    data = pd.read_csv(f'{script_dir}/{file_name}_Live.csv')
    data['date'] = data['date'].astype('datetime64[s]')
    # data = data.set_index('date')
    data = data.sort_index()



    plt.plot(data['date'], data['close'], label=file_name, linewidth=0.8, color='yellow')

    # plt.plot(x, y1, label='ETHUSDT_1m')
    # plt.plot(x, y2, label='Channel 2')

    plt.legend(loc='upper right')
    plt.tight_layout()
    print("live chart working")
    print(20*"=") 
    plot_count=0
    plot_count+=1
    if plot_count == 4:
        plt.savefig(f'{script_dir}/live_plot.png')
        print("plot saved")
        plot_count = 1


ani = FuncAnimation(plt.gcf(), animate, interval=1000,cache_frame_data=False)

plt.tight_layout()
# ani.save()
plt.show()
