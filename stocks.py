import json
from yahoo_fin.stock_info import get_data, tickers_sp500, tickers_nasdaq, tickers_other, get_quote_table, get_earnings_history

def tickpick(ticker):
    qtable = json.dumps(get_quote_table(ticker), indent = 2)
    ehist = json.dumps(get_earnings_history(ticker), indent = 2)
    tickinfo = qtable + '\n' + ehist
    return tickinfo

usrtick = input("Enter a 1-5 Letter Stock Ticker\n> ")
print(tickpick(usrtick))
#print(info)
