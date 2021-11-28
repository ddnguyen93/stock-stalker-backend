from flask_restful import Resource

from models.stock import StockModel

class Sector(Resource):
    def get(self, sector_name):
        sector_list_class = StockModel.objects(sector=sector_name)
        sector_list_obj = []
        for stock in sector_list_class:
            sector_list_obj.append(stock.json())
        return {'sector_list': sector_list_obj}