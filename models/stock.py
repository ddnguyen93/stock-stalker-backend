from db import db
import datetime
import yfinance as yf
import numpy as np

class StockModel(db.Document):
    ticker = db.StringField(required=True)
    full_name = db.StringField(required=True)
    sector = db.StringField(required=True)
    hist_data = db.ListField(required=True)
    update_time = db.DateTimeField(required=True, default=datetime.datetime.now)

    def json(self):
        return {'_id': str(self.id), 'ticker': self.ticker, 'full_name': self.full_name, 'sector': self.sector, 'hist_data': self.hist_data, 'update_time': str(self.update_time)}

    meta = {
        # 'db_alias': 'shop',
        'collection': 'stocks'
    }

    @classmethod
    def find_by_ticker(cls, ticker):
        return cls.objects(ticker=ticker.lower())

    @classmethod
    def find_by_id(cls, _id):
        return cls.objects(id=_id)

    @classmethod
    def update_all_stocks(cls):
        def fetchData(stock):
            yf_stock = yf.Ticker(stock.ticker)
            hist = yf_stock.history(period="14mo")
            hist.index = hist.index.astype(str)
            data = []
            for index, row in hist.iterrows():
                if not (np.isnan(row['Close'])):
                    dataPoint = {"date": index, "price": round(row['Close'],2)}
                    data.append(dataPoint)
            stock.hist_data = data
            stock.update_time = datetime.datetime.now()
            stock.save()
        
        for stock in cls.objects:
            try:           
                fetchData(stock)
            except:
                try:
                    fetchData(stock)
                except:
                    continue