import sys,time,argparse, schedule, queue, json
import threading
sys.path.insert(0, 'libs/Robinhood-API')
from Robinhood import Robinhood
#################
# Description: place a buy order of the stock, then start the analysys
# In the analysis we will take the 
# - Make an automatic trailing amiunt
#
################

#set a goal to follow

class _Platform:
   #TODO 
   # -Need to make sure orders that are placed under $1.00 cannot have sub
   # pennies (ie 1.021)
   # -Need to make a data structure that will store, (stack) transactions, so
   # that when need to cancel do not REFERENCE the LAST order but the stacks
   # last transaction FOR THIS INDEX, therefore we can have concurrent order
   # placement
   # -Statistics analyzer saying what price needs to be reached inorder to
   # achieve goals, and risk

    
    def __init__(self, symbol, equity, risk_lose, reward_win):
            
        self.symbol = symbol
        self.equity = float(equity)
        self.risk_lose = float(risk_lose)
        self.reward_win = float(reward_win)
        self.r = Robinhood()
        self.r.login() #login
        
        self.transaction_queue = queue.Queue()
        self.buying_queue = queue.Queue()

    def calculate_reward(self, num_shares):
        #calculate the reward 
        eq_reward_amount = self.equity + self.reward_win
        reward_limit_price = round(eq_reward_amount/num_shares,3)
        print("[+] Reward Sell limit to: %s" % reward_limit_price)
        return reward_limit_price #return the pps to sell at specific limit
    
    def calculate_num_shares(self, price_per_share):
        #calc numer of shares given pps
        num_shares = int(int(self.equity)/float(price_per_share))
        return num_shares
    #def calculate_statistics(self, risk_limit, reward_limit, num_shares,

    def set_stop_limit(self, num_shares):
        #sets the stop limit and the stop loss triggers
        #calcualte the stop loss amount; we will use 10% of risk price
        eq_risk_amount = self.equity - self.risk_lose #amount you will end up
        #post risk amount
        
        sell_limit_price = round(eq_risk_amount/num_shares,3)
        #calcualte 10% of the sell_limit_price
        stop_loss_price = round(.10 * sell_limit_price, 2)
        stop_loss_price = round(sell_limit_price - stop_loss_price, 2)
        

        print("[+] Setting Stop limit to %s | Stop Loss to %s | real eq %s "
        %(sell_limit_price, sell_limit_price, self.equity))


        #do what the fcuntion says make it set the new prices
        #result = self.r.place_sell_limit(self.symbol,stop_loss_price,sell_limit_price,num_shares)
        result = self.r.place_sell_limit(self.symbol,sell_limit_price,sell_limit_price,num_shares)
        if not (result.status_code == 201):
            print(result.text)
            raise Exception('Error setting stop limit')
        time.sleep(2)
        #return result
        temp_result = json.loads(result.text)
        #if no error store the transaction stop limit into the trasnaction queue
        self.transaction_queue.put(temp_result) #put json in it

        return sell_limit_price


    def checkIfFilled(self):
        ti = 0
        trans = self.buying_queue.get()
        while ti != 20:
            time.sleep(1)
            print('[*] Wating... Checking...')
            if self.r.get_order(trans['id'])['state'] =='filled':
            #if self.r.last_order_placed()['state'] == 'filled':
                print('{++} Order was Filled')
                return True
            ti += 1
        self.r.cancel_order(trans['cancel'])#get cancel url to make post to

        #self.cancel_last_order()
        return False

    def convert_price(self, _price):

        temp_p = float(_price)
        if temp_p < 1.0:
            return round(temp_p,4)
        else:
            return round(temp_p,2)
            
    def start(self):
        print('[+] Beginning....')
        #get the current price of the last traded price stock
        #convert the numbres, below 1.00 by 4 places above by 2
        current_price = self.convert_price(self.r.last_trade_price(self.symbol))
        
        #calculate the number of shares we can purchase
        num_Shares = self.calculate_num_shares(current_price)
        print('[+] Placing first but order @ %s ' % current_price)

        #returns a response object 
        #place a limit buy order
        result = self.r.place_buy_order(self.symbol,'limit',current_price,num_Shares)
        result = json.loads(result.text)
        #enQueue the order
        self.buying_queue.put(result)

        print('[++] Result of buy order %s' % result)

        real_eq = self.convert_price(num_Shares * current_price) # real price of eq
        
        self.equity = real_eq


        #check if order was executed
        #if ... then while loop 

        if self.checkIfFilled():
            #been filled so proceed

        #sleep here, and recheck if the order has been filled if not then do not
        #proceed, else proceed
            #set stop loss and stop limits
            curr_risk_limit = self.set_stop_limit(num_Shares)
            
            #set the current price
            curr_price = self.convert_price(self.r.last_trade_price(self.symbol))
            reward_price = self.convert_price((self.calculate_reward(num_Shares)))
            
            #TODO
            #Need to check if the curr price is lower than the stop loss price,
            #if we are still holding sell it to the market
            

            #start the while loop to check
            #flag to signal execute of program
            alive = True
            while(alive):
                time.sleep(2)

                last_price =\
                self.convert_price(self.r.last_trade_price(self.symbol))
                print('Checking price, Current: %s, New %s' %(curr_price,
                last_price))    
                if last_price >= reward_price:
                    #the current price has reached out goal, sell out
                    print("[+] Target price Reached")

                    trans = self.transaction_queue.get()#get the most recent
                    #transacton

                    self.r.cancel_order(trans['cancel'])
                    #self.cancel_last_order()
                    self.r.place_sell_order(self.symbol,'limit',reward_price,num_Shares)
                    #given a 15 second iterations check if its sold
                    for i in range(15):
                        #check
                        trans_id = trans['id']
                        x = self.r.get_order(trans_id)['state']
                        if x == 'filled':
                            print('successfully sold to reward goals')
                            break
                    break 
                    
                elif last_price > curr_price:
                    print("[+] Setting higher Risk")
                    #we have a larger new price
                    
                    #NEED cancel the last order
                    time.sleep(2) 
                    
                    trans = self.transaction_queue.get()
                    #get the last inserted item
                     
                    self.r.cancel_order(trans['cancel'])
                    
                    #self.cancel_last_order()

                    
                    #move our stop loss and stop limits up
                    #inserts a new transaction into the queue
                    self.set_stop_limit(num_Shares)

                    
                    curr_price = last_price
                #elif last_price =< curr_risk_limit:
                    #the current price is less than our risk limit
                    #check if we are still holding shares
                    #for i in range(15):
                        #given 15 iterations or seconds
                        #keep checking


        else:
            print("Order took to long to execute another day friends")
            #self.cancel_last_order()
        print('finished running...')
    def __str__(self):
        return "Symbol %s |Equity %s |Risk Amt %s |Reward Amt %s" % (self.symbol,self.equity, self.risk_lose, self.reward_win)

    def cancel_last_order(self):
        result = self.r.cancelMostRecentOrder()
        if not (result.status_code == 200):
            raise Exception("Something broke, cannot cancel order")

            
#class NewsRoom:
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Stock Automated risk reward\
    manager, and trailing stop analyzer program')
    parser.add_argument('-s','--symbol', help='Stock Symbol', required=True)
    parser.add_argument('-e','--equity', help='Equity Amount to use', required=True)
    parser.add_argument('-l','--lose', help='Risk Amount', required=True)
    parser.add_argument('-w','--win', help='Reward Amount', required=True)
    parser.add_argument('-p','--premarket', help='premarket start', nargs='?')

    parser.add_argument('-n','--now', help='execute not', nargs='?')
    #parser.add_argument('-p','--pennyS'
    parser.add_argument('-D','--debug',help='set to t for debugging\
    mode',nargs='?')
    args = vars(parser.parse_args())
    
    platf = _Platform(args['symbol'], args['equity'],args['lose'],args['win'])
    
    
    #schedule.every().day.at("13:30").do(platf.start)
    #platf.start()
    
    print(platf)    
    
    if args['debug']:
        platf.start()
        print('debugging checked')
        platf.cancel_last_order()

    elif args['premarket']:
        schedule.every().day.at("13:30").do(platf.start)
        while True:
            schedule.run_pending()
        #platf.start()
    elif args['now']:
        platf.start()
