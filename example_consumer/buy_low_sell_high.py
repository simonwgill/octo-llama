import pickle
import random
import uuid
from llama.llama import Llama
from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily
from pycassa.index import *
from pycassa.cassandra import ttypes
import datetime


class Buyer(Llama):
    def __init__(self, client, qname, trend=5):
        super(Buyer, self).__init__(client, uuid.uuid4().hex)
        self.holdings = {}
        self.cash = 100000.0
        self.history = {}
        self.trend = trend
        self.pool = ConnectionPool('example_consumer_Buyer')
        self.stored_holdings = ColumnFamily(self.pool, 'Holdings')
        self.quote_history = ColumnFamily(self.pool, 'Quotes')
        self.stored_cash = ColumnFamily(self.pool, 'Cash')

        try:
          cash = self.stored_cash.get('current')
          self.cash = cash['amount']
        except ttypes.NotFoundException:
          self.stored_cash.insert('current', { 'amount': self.cash })

        for symbol, columns in self.stored_holdings.get_range():
          self.holdings[symbol] = (columns['number_of_shares'], columns['price'], columns['cost'])

        date_expression = create_index_expression('timestamp', datetime.date.today(), GT)
        date_clause = create_index_clause([date_expression], count=1000)

        for key, columns in self.quote_history.get_range():
          symbol = columns['symbol']
          price = columns['price']
          self.add_quote(symbol, price)

    def add_quote(self, symbol, price):
        if symbol not in self.history: 
            self.history[symbol] = [price]
        else:
            self.history[symbol].append(price)

        if len(self.history[symbol]) >= self.trend:
            price_low = min(self.history[symbol][-self.trend:])
            price_max = max(self.history[symbol][-self.trend:])
            price_avg = sum(self.history[symbol][-self.trend:])/self.trend
            #print "Recent history of %s is %s" % (symbol, self.history[symbol][-self.trend:])
        else:
            price_low, price_max, price_avg = (-1, -1, -1)
            print "%s quotes until we start deciding whether to buy or sell %s" % (self.trend - len(self.history[symbol]), symbol)
            #print "Recent history of %s is %s" % (symbol, self.history[symbol])

        return (price_low, price_max, price_avg)


    def do_message(self, quote):
        symbol, price, date, counter = quote
        #print "Thinking about whether to buy or sell %s at %s" % (symbol, price)

        price_low, price_max, price_avg = self.add_quote(symbol, price)

        self.save_quote(symbol, price)

        if price_low == -1: return

        #print "Trending minimum/avg/max of %s is %s-%s-%s" % (symbol, price_low, price_avg, price_max)
        #for symbol in self.holdings.keys():
        #    print "self.history[symbol][-1] = %s" % self.history[symbol][-1]
        #    print "self.holdings[symbol][0] = %s" % self.holdings[symbol][0]
        #    print "Value of %s is %s" % (symbol, float(self.holdings[symbol][0])*self.history[symbol][-1])
        value = sum([self.holdings[symbol][0]*self.history[symbol][-1] for symbol in self.holdings.keys()])
        print "Net worth is %s + %s = %s" % (self.cash, value, self.cash + value)

        if symbol not in self.holdings:
            if price < 1.01*price_low:
                shares_to_buy = random.choice([10, 15, 20, 25, 30])
                print "I don't own any %s yet, and the price is below the trending minimum of %s so I'm buying %s shares." % (symbol, price_low, shares_to_buy)
                cost = shares_to_buy * price
                print "Cost is %s, cash is %s" % (cost, self.cash)
                if cost < self.cash:
                    self.buy_holdings(symbol, shares_to_buy, price, cost)
                    self.update_cash(-cost)
                    print "Cash is now %s" % self.cash
                else:
                    print "Unfortunately, I don't have enough cash at this time."
        else:
            if price > self.holdings[symbol][1] and price > 0.99*price_max:
                print "+++++++ Price of %s is higher than my holdings, so I'm going to sell!" % symbol
                sale_value = self.holdings[symbol][0] * price
                print "Sale value is %s" % sale_value
                print "Holdings value is %s" % self.holdings[symbol][2]
                print "Total net is %s" % (sale_value - self.holdings[symbol][2])
                self.update_cash(sale_value)
                print "Cash is now %s" % self.cash
                self.sell_holdings(symbol)

    def update_cash(self, change):
      self.cash += change
      cash = self.stored_cash.get('current')
      cash['amount'] = self.cash
      self.stored_cash.insert('current', cash)

    def buy_holdings(self, symbol, shares_to_buy, price, cost):
      self.holdings[symbol] = (shares_to_buy, price, cost)
      stored_holding = {'number_of_shares': shares_to_buy, 'price': price, 'cost': cost}
      self.stored_holdings.insert(symbol, stored_holding)

    def sell_holdings(self, symbol):
      del self.holdings[symbol]
      self.stored_holdings.remove(symbol)

    def save_quote(self, symbol, price):
      key = str(uuid.uuid4())
      self.quote_history.insert(key, { 'symbol': symbol, 'price': price })
