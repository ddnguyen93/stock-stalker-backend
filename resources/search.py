from flask_restful import Resource, reqparse
from models.stock import StockModel
from recommended_list import find_matches


from flask_jwt_extended import (
    jwt_required,
)

class SearchTicker(Resource):
    def get(self, search_input):
        recommended_list = find_matches(search_input)

        return {'recommended_list': recommended_list}