from flask_restful import Resource, reqparse
import yfinance as yf
import pandas as pd
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)
import datetime
import numpy as np



from recommended_list import find_matches
from models.stock import StockModel
# from models.user import UserModel

class Stock(Resource):
    # @jwt_required()
    def get(self, ticker):

        stock_data = StockModel.find_by_ticker(ticker.lower()).first()
        if stock_data:
            return stock_data.json()

        else: 
            stock = yf.Ticker(ticker)
            data_info = stock.info
            data_hist = stock.history(period="14mo")

            if data_hist.empty:
                recommended_list = find_matches(ticker)
                return {'message': "Ticker does not exist.", 'recommended_list': recommended_list}
            else:                
                data_hist.index = data_hist.index.astype(str)

                data = []
                for index, row in data_hist.iterrows():
                    if not (np.isnan(row['Close'])):
                        dataPoint = {"date": index, "price": round(row['Close'],2)}
                        data.append(dataPoint)

                stock_data = StockModel(ticker=ticker.lower(), hist_data=data, full_name=data_info['longName'], sector=data_info['sector'])
                stock_data.save()
                return stock_data.json()

    

class UpdateStock(Resource):
    def get(self):
        StockModel.update_all_stocks()
        return {'message': "All stocks updated"}