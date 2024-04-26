from AgentBasedModel.simulator import SimulatorInfo
import AgentBasedModel.utils.math as math

import matplotlib.pyplot as plt
import pandas as pd


def plot_book_stat(
        info:    SimulatorInfo,
        idx:     int,
        stat:    str = 'quantity',
        rolling: int   = 1,
        figsize: tuple = (6, 6)
    ):
    """Lineplot ExchangeAgent`s Order Book chosen statistic

    :param info: SimulatorInfo instance
    :param idx: ExchangeAgent id
    :param stat: Order Book statistic to plot, defaults 'quantity'
    :param rolling: MA applied to list, defaults to 1
    :param figsize: figure size, defaults to (6, 6)
    """
    plt.figure(figsize=figsize)
    plt.title(
             f'Exchange{idx}: Order Book {stat} by order type ' if rolling == 1
        else f'Exchange{idx}: Order Book {stat} by order type  (MA {rolling})'
    )
    plt.xlabel('Iterations')
    plt.ylabel(f'Order {stat}')

    iterations = range(rolling - 1, len(info.dividends[idx]))
    v_bid = math.rolling([v[stat]['bid'] for v in info.orders[idx]], rolling)
    v_ask = math.rolling([v[stat]['ask'] for v in info.orders[idx]], rolling)
    
    plt.plot(iterations, v_bid, label='bid', color='green')
    plt.plot(iterations, v_ask, label='ask', color='red')

    plt.legend()
    plt.show()


def print_book(info: SimulatorInfo, idx: int, n=5):
    val = pd.concat([
        pd.DataFrame({
            'Sell': [v.price for v in info.exchanges[idx].order_book['ask']],
            'Quantity': [v.qty for v in info.exchanges[idx].order_book['ask']]
            }).groupby('Sell').sum().reset_index().head(n),
        pd.DataFrame({
            'Buy': [v.price for v in info.exchanges[idx].order_book['bid']],
            'Quantity': [v.qty for v in info.exchanges[idx].order_book['bid']]
        }).groupby('Buy').sum().reset_index().sort_values('Buy', ascending=False).head(n)
    ])
    print(val[['Buy', 'Sell', 'Quantity']].fillna('').to_string(index=False))

    
def plot_book(info: SimulatorInfo, idx: int, bins=50, figsize=(6, 6)):
    bid = list()
    for order in info.exchanges[idx].order_book['bid']:
        for p in range(order.qty):
            bid.append(order.price)

    ask = list()
    for order in info.exchanges[idx].order_book['ask']:
        for p in range(order.qty):
            ask.append(order.price)

    plt.figure(figsize=figsize)
    plt.title('Order book')
    plt.hist(bid, label='bid', color='green', bins=bins)
    plt.hist(ask, label='ask', color='red', bins=bins)
    plt.show()
    
    
def plot_full_book(info: SimulatorInfo, idx: int, figsize=(12, 12), bins=10, width_constant = 0.7):
    
    """
    the same graph but with orders separation
    
    """
    
    # general settings
    
    cur_price = info.exchanges[idx].price()
    
    plt.figure(figsize=figsize)
    plt.title('Order book. Stacked orders')
    
    colors_bid = ['green', 'limegreen']
    colors_ask = ['red', 'coral']
    
    
    # slice calculations
    
    # bid
    bids = info.exchanges[idx].order_book['bid']    
    bids_prices = set()
    
    for bid in bids:
        bids_prices.add(bid.price)
        
    bids_prices = sorted(list(bids_prices), reverse=True)
    bids_depth = len(bids_prices)
    
    best_bid = bids_prices[0]
    worst_bid = bids_prices[-1]
    
    
    # ask
    asks = info.exchanges[idx].order_book['ask']    
    asks_prices = set()
    
    for ask in asks:
        asks_prices.add(ask.price)
        
    asks_prices = sorted(list(asks_prices))
    asks_depth = len(asks_prices)
    
    best_ask = asks_prices[0]
    worst_ask = asks_prices[-1]
    
    
    # bid slices initialization
    slice_length_bid = (best_bid - worst_bid) / bins
    
    slices_bid = []
    for i in range(bins):
        cur_slice = (best_bid - slice_length_bid * i, best_bid - slice_length_bid * (i + 1))
        slices_bid.append(cur_slice)
        
        
    # ask slices initialization
    slice_length_ask = (worst_ask - best_ask) / bins
    
    slices_ask = []
    for i in range(bins):
        cur_slice = (best_ask + slice_length_ask * i, best_ask + slice_length_ask * (i + 1))
        slices_ask.append(cur_slice)
    
    
    # optimal for vizualization bar width
    slice_length = min(slice_length_bid, slice_length_ask)
    
    
    # bid orders separation and plotting

    i = 0
    bids_separated = [[] for i in range(bins)]
    for bid in bids:
        i = 0
        s = slices_bid[i]
        
        while (not (s[1] <= bid.price <= s[0]) and (i != 49)):
            i += 1
            s = slices_bid[i]
        bids_separated[i].append(bid)
    
    color_count = 0
    for i in range(bins):
        orders_history = 0
        x = (slices_bid[i][0] + slices_bid[i][1])/2
        
        for bid in bids_separated[i]:
            plt.hist(x=x, height=bid.qty, label='bid', color=colors_bid[color_count%2], 
                     bottom=orders_history, width=slice_length * width_constant)
            
            orders_history += bid.qty
            
            color_count += 1

    print(best_bid, worst_bid)
    
    
    # ask_orders separation and plotting
    
    i = 0
    asks_separated = [[] for i in range(bins)]
    
    for ask in asks:
        i = 0
        s = slices_ask[i]
        
        while (not (s[0] <= ask.price <= s[1]) and (i != 49)):
            i += 1
            s = slices_ask[i]
        asks_separated[i].append(ask)
    
    
    color_count = 0
    for i in range(bins):
        orders_history = 0
        x = (slices_ask[i][0] + slices_ask[i][1])/2
        
        for ask in asks_separated[i]:
            plt.hist(x=x, height=ask.qty, label='ask', color=colors_ask[color_count%2], 
                     bottom=orders_history, width=slice_length * width_constant)
            
            orders_history += ask.qty
            
            color_count += 1

    print(best_ask, worst_ask)

    plt.show()
    