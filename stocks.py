import time, socket, inspect, smtplib, ssl, json, getopt, sys, os
from yahoo_fin.stock_info import *
from cursesmenu import *
from cursesmenu.items import *
from os.path import expanduser
socket.setdefaulttimeout(5)

###[ UI START ]###

class runui:
    def select(u):
        while True:
            u.ticker = input("Enter a 1-5 character stock, exclude '$.'\n> ")
            if len(u.ticker) >= 5:
                continue
            try:
                get_live_price(u.ticker)
                break
            except:
                print("Not a valid/supported stock.")
                continue

    def geninf(u):
        qtab = json.dumps(get_quote_table(u.ticker), indent = 2)
        qtab1 = qtab.replace('    ','').replace('  ','').replace('"', '').replace('{', '').replace('}', '').replace(',', '')
        qtab2 = qtab1.splitlines()
        while("" in qtab2):
            qtab2.remove("")
        qtab3 = str("\n".join(qtab2))
        val = get_stats_valuation(u.ticker)
        val = val.iloc[:,:2]
        val.columns = ["Attribute", "Recent"]
        per = float(val[val.Attribute.str.contains("Trailing P/E")].iloc[0,1])
        psr = float(val[val.Attribute.str.contains("Price/Sales")].iloc[0,1])
        peg = float(val[val.Attribute.str.contains("PEG")].iloc[0,1])
        cprice = get_live_price(u.ticker)
        print(qtab3, "\nTrailing P/E: %f\nPrice/Sales: %f\nPrice/Earnings-To-Growth: %f\nCurrent Price: $%f" % (per, psr, peg, cprice))
        input()

    def earnhist(u):
        for i in range(6):
            try:
                ehist = json.dumps(get_earnings_history(u.ticker)[i], indent = 2)
                ehist1 = ehist.replace('    ','').replace('  ','').replace('[', '').replace(']', '').replace('"', '').replace('{', '').replace('}', '').replace(',', '')
                ehist2 = ehist1.splitlines()
                while("" in ehist2):
                    ehist2.remove("")
                ehist3 = str("\n".join(ehist2))
                print("\n#%d\n" % i, ehist3)
                i = i + 1
            except IndexError:
                pass
        input()

    def financials(u):
        fin = get_financials(u.ticker, yearly = True, quarterly = False)
        input(fin)

    def ui(u):
        menu = CursesMenu("PyStocks UI", "Main Menu")
        f1 = FunctionItem("Select a Stock", runui.select, [u])
        f2 = FunctionItem("General Information", runui.geninf, [u])
        f3 = FunctionItem("Earnings History", runui.earnhist, [u])
        f4 = FunctionItem("Financials Information", runui.financials, [u])
        menu.append_item(f1)
        menu.append_item(f2)
        menu.append_item(f3)
        menu.append_item(f4)
        menu.show()

###[ UI END ]###

###[ DAEMON START ]###

class daemon:
    def arg(u, argv):
        ticker = ''
        email = ''
        try:
            opts, args = getopt.getopt(argv,"hut:e:",['ticker=', 'email='])
        except getopt.GetoptError:
            print('[GetOpt/Argument Error]')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print('[daemon] - stocks.py -t <ticker> -e <email>\n[ui] - stocks.py -u')
                sys.exit()
            if opt == '-u':
                runui.ui(u)
                quit()
            elif opt in ("-t", "--ticker"):
                u.ticker = arg
            elif opt in ("-e", "--email"):
                u.email = arg
        d.tickpick()

    def infograb(u):
        val = get_stats_valuation(u.ticker)
        val = val.iloc[:,:2]
        val.columns = ["Attribute", "Recent"]
        per = float(val[val.Attribute.str.contains("Trailing P/E")].iloc[0,1])
        psr = float(val[val.Attribute.str.contains("Price/Sales")].iloc[0,1])
        peg = float(val[val.Attribute.str.contains("PEG")].iloc[0,1])
        u.cprice = get_live_price(u.ticker)
        u.info = str("Price/Earnings Rato: %f\nPrice/Sales Ratio: %f\nPEG: %f\nCurrent Price: %f" % (per, psr, peg, u.cprice)) 
        u.pf.write(u.info)

    def tickpick(u):
        stockhome = os.path.join(expanduser("~"), "pystock")
        u.smtpfile = os.path.join(stockhome, "smtp.txt")
        u.pricefile = os.path.join(stockhome, "price.txt")
        u.sf = open(u.smtpfile, "r")
        u.pf = open(u.pricefile, "w")
        d.infograb()
        d.smtpinit()  

###[ MAILER START ]###

    def smtpinit(u):
        if os.path.exists(u.smtpfile) == False:
            ans = input("Default SMTP File (smtp.txt in pystocks folder) could not be located.\nWould you like to select another?\n(Y)/(N)\n> ")
            if ans.lower == 'y':
                while True:
                    u.smtpfile = input("SMTP Server\nFormat must be: host|port|user|pass\nDefault SMTP file is in the 'pystock' folder:\n> ")
                    if os.path.exists(u.smtpfile) == False:
                        print("File is nonexistent")
                        continue
                    break
            if ans.lower == 'n':
                quit()
        try:
            smtp = u.sf.read().rstrip("\n")
            srv = smtp.split('|')
            u.host = srv[0]
            u.port = int(srv[1])
            u.user = srv[2]
            u.psk = srv[3]
            u.sf.close()
        except:
            print("SMTP Config Issue. Revise your configuration file.")
        d.connect()

    def connect(u):
        while True:
            context = ssl.create_default_context()
            try:
                server = smtplib.SMTP(u.host, u.port)
                server.ehlo()
                server.starttls(context=context)
                server.login(u.user, u.psk)
                u.server = server
                print("Connected to SMTP Server")
                break
            except ValueError:
                print("Could not connect to SMTP Server.")
                print("Error. Reconfigure SMTP Entries.")
                quit()
        d.send()

    def send(u):
        server = u.server
        subject = str("PyStock Update for: %s" % u.ticker)
        while True: 
            print("30min timer initiated")
            time.sleep(1800)
            oldprice = u.cprice
            d.infograb()
            negch = (((u.cprice - oldprice) / oldprice) * 100) 
            if negch < -5:
                body = str(u.info + "\n" + "Percent change: %f%." % abs(negch))
                message = f'Subject: {subject}\n\n{body}'
                server.sendmail(u.user, u.email, message) 
                print("Update email sent") 

###[ MAILER END ]###

d = daemon()
d.arg(sys.argv[1:])
