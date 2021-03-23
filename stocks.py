import inspect
import json
from yahoo_fin.stock_info import *
from cursesmenu import *
from cursesmenu.items import *

def ui():
    menu = CursesMenu("PyStocks", "Main Menu")

    f1 = FunctionItem("Select a Stock", select)
    f2 = FunctionItem("General Information", geninf)
    f3 = FunctionItem("Earnings History", earnhist)
    f4 = FunctionItem("Financials Information", financials)
    #f5 = FunctionItem("Options Data", lister)

    menu.append_item(f1)
    menu.append_item(f2)
    menu.append_item(f3)
    menu.append_item(f4)
    #menu.append_item(f5)

    menu.show()

def select():
    global ticker
    while True:
        ticker = input("Enter a 1-5 character stock, exclude '$.'\n> ")
        if len(ticker) >= 5:
            continue
        try:
            get_live_price(ticker)
            break
        except:
            print("Not a valid/supported stock.")
            continue

def geninf():
    global ticker
    qtab = json.dumps(get_quote_table(ticker), indent = 2)
    qtab1 = qtab.replace('    ','').replace('  ','').replace('"', '').replace('{', '').replace('}', '').replace(',', '')
    qtab2 = qtab1.splitlines()
    while("" in qtab2):
        qtab2.remove("")
    qtab3 = str("\n".join(qtab2))
    val = get_stats_valuation(ticker)
    val = val.iloc[:,:2]
    val.columns = ["Attribute", "Recent"]
    per = float(val[val.Attribute.str.contains("Trailing P/E")].iloc[0,1])
    psr = float(val[val.Attribute.str.contains("Price/Sales")].iloc[0,1])
    peg = float(val[val.Attribute.str.contains("PEG")].iloc[0,1])
    cprice = get_live_price(ticker)
    print(qtab3, "\nTrailing P/E: %f\nPrice/Sales: %f\nPrice/Earnings-To-Growth: %f\nCurrent Price: $%d" % (per, psr, peg, cprice))
    input()

def earnhist():
    global ticker

    for i in range(6):
        ehist = json.dumps(get_earnings_history(ticker)[i], indent = 2)
        ehist1 = ehist.replace('    ','').replace('  ','').replace('[', '').replace(']', '').replace('"', '').replace('{', '').replace('}', '').replace(',', '')
        ehist2 = ehist1.splitlines()
        while("" in ehist2):
            ehist2.remove("")
        ehist3 = str("\n".join(ehist2))
        print("\n#%d\n" % i, ehist3)
        i = i + 1

    input()

def financials():
    global ticker
    fin = get_financials(ticker, yearly = True, quarterly = False)
    input(fin)

ui()
