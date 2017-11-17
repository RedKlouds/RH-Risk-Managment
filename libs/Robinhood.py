
import getpass
import json
import requests
import urllib.request, urllib.parse, urllib.error
import app_setup
            
import queue
import threading
class Robinhood:

    endpoints = {
            "login": "https://api.robinhood.com/api-token-auth/",
            "investment_profile": "https://api.robinhood.com/user/investment_profile/",
            "logout": "https://api.robinhood.com/api-token-logout/",
            "accounts":"https://api.robinhood.com/accounts/",
            "ach_iav_auth":"https://api.robinhood.com/ach/iav/auth/",
            "ach_relationships":"https://api.robinhood.com/ach/relationships/",
            "ach_transfers":"https://api.robinhood.com/ach/transfers/",
            "applications":"https://api.robinhood.com/applications/",
            "dividends":"https://api.robinhood.com/dividends/",
            "edocuments":"https://api.robinhood.com/documents/",
            "instruments":"https://api.robinhood.com/instruments/",
            "margin_upgrades":"https://api.robinhood.com/margin/upgrades/",
            "markets":"https://api.robinhood.com/markets/",
            "notifications":"https://api.robinhood.com/notifications/",
            "orders":"https://api.robinhood.com/orders/",
            "password_reset":"https://api.robinhood.com/password_reset/request/",
            "portfolios":"https://api.robinhood.com/portfolios/",
            "positions":"https://api.robinhood.com/positions/",
            "quotes":"https://api.robinhood.com/quotes/",
            "historicals":"https://api.robinhood.com/quotes/historicals/",
            "document_requests":"https://api.robinhood.com/upload/document_requests/",
            "user":"https://api.robinhood.com/user/",
            "watchlists":"https://api.robinhood.com/watchlists/",
            "news":"https://api.robinhood.com/midlands/news/",
            "movers":"https://api.robinhood.com/midlands/movers/sp500/"
    }

    session = None
    username = None
    password = None
    headers = None
    auth_token = None

    ##############################
    #Logging in and initializing
    ##############################

    def __init__(self):
        """ default constructor for the object"""
        self.session = requests.session()
        self.session.proxies = urllib.request.getproxies()
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-Robinhood-API-Version": "1.0.0",
            "Connection": "keep-alive",
            "User-Agent": "Robinhood/823 (iPhone; iOS 8.1.2; Scale/2.00)"
        }

        self.session.headers = self.headers
        self._userData = app_setup.AppSetup()

    def cleanupPassword(self):
        """Testing purposes"""
        self._userData.cleanUp()

    def login_prompt(self):
        """Prompts user for username and password and calls login()."""
        username = input("Username: ")
        password = getpass.getpass()
        return self._login(username=username, password=password)
    
    def login(self):
        """Facade relay method to relay a login session"""
        return self._login(self._userData.getRobinhoodUserName(), self._userData.getRobinhoodPassword())
    
    def _login(self, username, password):
        """private method to login into robinhood"""
        self.username = username
        self.password = password
        data = urllib.parse.urlencode({"password" : self.password, "username" : self.username})
        res = self.session.post(self.endpoints['login'], data=data)
        res = res.json()
        try:
            self.auth_token = res['token']
        except KeyError:
            print("[-] Error logging in please reenter username and password")
            usr = str(input("Username: " ))
            pas = str(input("password: "))

            self._userData.changeUserData(usr, pas)

            print("[+] relogging now.... ")
            self.login()
            #return False
        self.headers['Authorization'] = 'Token '+self.auth_token
        print('[+] successfully logged in')
        return True


    def logout(self):
        """ log out method to log out of robinhood account """
        try:
           
            self.session.post(self.endpoints['logout'])
            print("[+] successfully logged out")
            return True
        except Exception as e:
            print("ERROR %s" % e)
            return False



    def investment_profile(self):
        self.session.get(self.endpoints['investment_profile'])

    def instruments(self, stock=None):
        res = self.session.get(self.endpoints['instruments'], params={'query':stock.upper()})
        res = res.json()
        return res['results']

    def getFundamentals(self, stock):
        """
            Returns a Json dictionary with the following structure
            {
                'open':,
                'market_cap':,
                'average_volume':,
                'high':,
                'pe_ratio':,
                'low':,
                'high_52_weeks':,
                'dividend_yield':,
                'low_52_weeks':,
                'volume':
            }
        """
        price = self.quote_data(stock.upper())
        fundamental_endpoint = 'https://api.robinhood.com/fundamentals/%s/'% \
        stock.upper()
        return_data = self.session.get(fundamental_endpoint).json()
        return_data['last_trade_price'] = price['last_trade_price']
        return_data['symbol'] = stock.upper()
        return return_data


    def quote_data(self, stock=None):
        # Prompt for stock if not entered

        if stock is None:
            stock = input("Symbol: ");
        url = str(self.endpoints['quotes']) + str(stock) + "/"
        #Check for validity of symbol
        try:
            res = json.loads((urllib.request.urlopen(url)).read().decode('utf-8'));
            if len(res) > 0:
                return res;
            else:
                raise NameError("Invalid Symbol: " + stock);
        except (ValueError):
            raise NameError("Invalid Symbol: " + stock);

    def get_quote(self, stock=None):
        data = self.quote_data(stock)
        return data["symbol"]

    def get_historical_quotes(self,symbol,interval,span,bounds='regular'):
        # Valid combination
        # interval = 5minute | 10minute + span = day, week
        # interval = day + span = year
        # interval = week
        # bounds can be 'regular' for regular hours or 'extended' for extended hours
        res = self.session.get(self.endpoints['historicals'], params={'symbols':','.join(symbol).upper(), 'interval':interval, 'span':span, 'bounds':bounds})
        return res.json()

    def get_news(self, symbol):
        return self.session.get(self.endpoints['news']+symbol.upper()+"/").json()


    def print_quote(self, stock=None):
        data = self.quote_data(stock)
        print((data["symbol"] + ": $" + data["last_trade_price"]));

    def print_quotes(self, stocks):
        for i in range(len(stocks)):
            self.print_quote(stocks[i]);

    def ask_price(self, stock=None):
        return self.quote_data(stock)['ask_price'];

    def ask_size(self, stock=None):
        return self.quote_data(stock)['ask_size'];

    def bid_price(self, stock=None):
        return self.quote_data(stock)['bid_price'];

    def bid_size(self, stock=None):
        return self.quote_data(stock)['bid_size'];

    def last_trade_price(self, stock=None):
        return self.quote_data(stock)['last_trade_price'];

    def previous_close(self, stock=None):
        return self.quote_data(stock)['previous_close'];


    def previous_close_date(self, stock=None):
        return self.quote_data(stock)['previous_close_date'];

    def adjusted_previous_close(self, stock=None):
        return self.quote_data(stock)['adjusted_previous_close'];

    def symbol(self, stock=None):
        return self.quote_data(stock)['symbol'];

    def last_updated_at(self, stock=None):
        return self.quote_data(stock)['updated_at'];


    def get_account(self):
        res = self.session.get(self.endpoints['accounts'])
        res = res.json()
        return res['results'][0]

    def get_url(self,url):
        return self.session.get(url).json()

        ##############################
        # PORTFOLIOS DATA
        ##############################

    def portfolios(self):
        """Returns the user's portfolio data."""
        return self.session.get(self.endpoints['portfolios']).json()['results'][0]

    def adjusted_equity_previous_close(self):
        return float(self.portfolios()['adjusted_equity_previous_close'])

    def equity(self):
        return float(self.portfolios()['equity'])

    def equity_previous_close(self):
        return float(self.portfolios()['equity_previous_close'])

    def excess_margin(self):
        return float(self.portfolios()['excess_margin'])

    def extended_hours_equity(self):
        return float(self.portfolios()['extended_hours_equity'])

    def extended_hours_market_value(self):
        return float(self.portfolios()['extended_hours_market_value'])

    def last_core_equity(self):
        return float(self.portfolios()['last_core_equity'])

    def last_core_market_value(self):
        return float(self.portfolios()['last_core_market_value'])

    def market_value(self):
        return float(self.portfolios()['market_value'])

    def order_history(self):
        """
            show the orders that were placed
        """
        return self.session.get(self.endpoints['orders']).json()

    def dividends(self):
        """
            return the divends stocks
        """
        return self.session.get(self.endpoints['dividends']).json()

    def cancelMostRecentOrder(self):
        """            
            This fucntion will cancel the most recent order that was placed
        """
        temp_list = self.order_history()['results'][0]['cancel']
        return self.session.post(temp_list)


        ###############################
        #        Position DATA
        ###############################
    def addToWatchlist(self, stock_idx):
        try:
            stock_instrument = self.instruments(stock_idx)[0]
            print(stock_instrument['id'])
    

            data = 'symbols=%s' % stock_idx.upper()
            self.session.post(self.endpoints['watchlists']+'/Default/bulk_add/', data =
            data)
        except Exception:
            pass

        #######################
        #   watch lists
        #       ->
        ########################
    
    def p_url(self, q, url):
        
        d = self.session.get(url['instrument']).json()
        q.put(d)

    def watchlist1(self):
        """
        Postcondition: returns a list of dictionary instrument objects with
        """
        #get the stock watchlist which returns an list of instruments, 
        #assuming instruments are just stock objects 

        watch_list_instruments = self.session.get(self.endpoints['watchlists']\
        + '/Default/?cursor=$cursor').json()
        #returns a dictonary query with cursor to next and prev
        #access the 'results'
        print('starting the threading')
        
        q = queue.Queue()
        watch_list_instruments = watch_list_instruments['results']
        for u in watch_list_instruments:
            t = threading.Thread(target=self.p_url, args=(q,u))
            t.daemon = True
            t.start()
        return q


    def watchlist(self):
        """
        Postcondition: returns a list of dictionary instrument objects with
        """
        #get the stock watchlist which returns an list of instruments, 
        #assuming instruments are just stock objects 
        watch_list_instruments = self.session.get(self.endpoints['watchlists']\
        + '/Default/?cursor=$cursor').json()
        #returns a dictonary query with cursor to next and prev
        #access the 'results'
        watch_list_instruments = watch_list_instruments['results']
        #break down all the data
        x = list()
        for i in watch_list_instruments:
            x.append(self.session.get(i['instrument']).json())
        #returns x gives a list of of dictonary containig all instruments
        return x

        #######################
        #  simple watch list
        #       ->
        ########################
    def simplewl(self):
        """
            Returns a watch list of all the instruments
        """
        return self.session.get(self.endpoints['watchlists']+ 'Default/' ).json()


        #######################
        #   positions
        #       ->
        ########################
    def topMovers(self, direction):
        """ 
            Returns the top 10 out of sp500 top movers and returns a list of
            dictionary
        """
        ep = "%s?direction=%s" %(self.endpoints['movers'], direction)
        r = self.session.get(ep)
        data = json.loads(r.text)['results']
        #data = data['results']
        return data
        #for i in data:
        #    print(i['symbol'])
        
        print(data[0])    
    def positions(self):
        """Returns the user's positions data."""
        return self.session.get(self.endpoints['positions']).json()



        #######################
        #   stocks owned
        #       ->
        ########################
    def securities_owned(self):
        """
        Returns a list of symbols of securities of which there are more
        than zero shares in user's portfolio.
        """
        positions = self.positions()
        securities = []
        for position in positions['results']:
            quantity = float(position['quantity'])
            if quantity > 0:
                securities.append(self.session.get(position['instrument']).json()['symbol'])
        return securities



        ##############################
        #       PLACE ORDER
        ##############################
        #    #   types:
        #        #   -market
        #        #   -limit
        #        #   -StopLoss
        #        #   -Stoplimit
        ##############################
    def place_order(self, instrument, order_type, quantity, bid_price, transaction=None):
        """
            Function Description: Places an order in RH
        """
        if bid_price == None and order_type == None:
            bid_price = self.quote_data(instrument['symbol'])['bid_price']
            order_type = 'market'
             
        data =\
        'account=%s&instrument=%s&price=%f&quantity=%d&side=%s&symbol=%s&time_in_force=gfd&trigger=immediate&type=%s' % (
            self.get_account()['url'],
            urllib.parse.unquote(instrument['url']),
            float(bid_price),
            quantity,
            transaction,
            instrument['symbol'],
            order_type
                    )

        res = self.session.post(self.endpoints['orders'], data=data)
        return res

        #######################
        #   place_buy_order
        #       ->
        ########################
    def place_buy_order(self, symbol, buy_type=None, bid_price = None, quantity=1):
        """
            Function Description: Places a buy order 
            If there is a buyprice we make a limit buy,
             otherwise if there isn't a buy price
            default to market price
            PRECONDITIONS: 
                -String Stock Symbol
                -String Buy_type
                    - makret
                    - limit
                -bid_price int/float
        """
        stock_instrument = None
        try:
            #get the stock instrument
            stock_instrument = self._makeInstrument(symbol)
        except NameError as e:
            print(e)
        transaction = "buy"
        return self.place_order(stock_instrument, buy_type, quantity, bid_price, transaction)

        #######################
        #   place_buy_order
        #  
        ########################
    def place_sell_order(self, symbol, sell_type=None, bid_price=None,quantity=1):
        stock_instrument = self._makeInstrument(symbol)
        transaction = "sell"
        return self.place_order(stock_instrument, sell_type,quantity, bid_price, transaction)

        #######################
        #   _Make Instrument
        # 
        ########################
    def _makeInstrument(self, symbol):
        
        """
            Function Description: makes an stock instrument
        """
        #make the instrument to return, but check it first
        ret_instrument = self.instruments(symbol)
        if len(ret_instrument) == 0:#no symbol found throw exception
            raise NameError("Invalid Symbol: " + symbol);
        return ret_instrument[0]

        #######################
        #   reorganizes watch list
        #  
        ########################

    def reorganize(self):
        return self.session.post(self.endpoints['watchlists'] +
        '/$watchlistName/reorder/{ids}')

        #######################
        #   place_buy_order
        #     
        ########################
    def makewl(self):
        self.session.post(self.endpoints['watchlists'], data ='name=DANNY')


def test():
    import json
    x = Robinhood()
    print('logging in')
    print(x.login())
    print("positions")

  
    print(json.dumps(x.positions(), indent=2))
    print('\t\twatchlist test')
    #print(json.dumps(x.watchlist(), indent=2))
    
    
    #x.addToWatchlist('MDR') 
    z = x.watchlist()
    
    #result = x['results']
    for i in range(len(z)):
        print('%s \t %s\n%s' % (i, z[i]['symbol'],z[i]['fundamentals']))
    
    #print(json.loads(x.simplewl(), indent=2))

    #x.reorganize()

def watchListTest():
    r = Robinhood()
    r.login()
    r.addToWatchlist('UMX')
    r.addToWatchlist('SKLN')
    #z = r.watchlist()
    #for i in z:
    #    print("%s \n" % i['symbol'])
def testPlaceLimitOrder():
    r = Robinhood()
    r.login()
    i = r.instruments("SKLN")[0]
    #r.place_order(i,1,1.50,'buy')
    #r.place_buy_order('SKLN','limit',bid_price=1.60)
    r.place_sell_order('SKLN','limit',bid_price=1.50)
    #r.place_buy_order('DCTH')
    #r.place_buy_order('DCTH','limit',bid_price=0.04)
    #print(r.quote_data('DCTH'))
    #r.place_buy_order('DCTH')
    #r.place_sell_order('DCTH','limit',bid_price=0.057)
    r.place_sell_order('DCTH','stop loss',bid_price=0.033)
def testLogout():
    r = Robinhood()
    r.login()
    print("Logging out now..")
    r.logout()
def testMovers():
    r = Robinhood()
    r.topMovers('up')
if __name__ == '__main__':
    #test()
    #watchListTest()
    #testPlaceLimitOrder()
    #testLogout()
    testMovers()
