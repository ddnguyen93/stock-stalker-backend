from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import datetime
import dotenv
import os

from resources.alerts import AlertsCheck, Alerts, AlertsList
from resources.favourties import Favourites, FavouritesList
from resources.stock import Stock, UpdateStock
from resources.user import CheckToken, TokenRefresh, UserRegister, User, UserLogin, UserVerify
from resources.search import SearchTicker
from resources.sector import Sector


from sched_config import run_scheduler

dotenv.load_dotenv()

app = Flask(__name__)

secret = os.getenv("SECRET_KEY")
app.secret_key = secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=15)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

api = Api(app)

jwt = JWTManager(app)

api.add_resource(Favourites, '/favourites')
api.add_resource(FavouritesList, '/favourites_list')
api.add_resource(User, '/user/<string:user_id>')
api.add_resource(UserRegister, '/register')
api.add_resource(UserVerify, '/verify')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(CheckToken, '/check_token')
api.add_resource(Stock, '/stock/<string:ticker>')
api.add_resource(UpdateStock, '/updatestock')
api.add_resource(SearchTicker, '/search/<string:search_input>')
api.add_resource(Sector, '/sector/<string:sector_name>')
api.add_resource(Alerts, '/alerts')
api.add_resource(AlertsList, '/alertslist')
api.add_resource(AlertsCheck, '/alerts_check')


if __name__ == '__main__':
    run_scheduler()
    app.run(port=5000, debug=True)

# use_reloader=False