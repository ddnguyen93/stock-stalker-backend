from db import db
from models.stock import StockModel
from models.alert import AlertModel
from send_email import send_verify_email, send_alert_email

class UserModel(db.Document):
    first_name = db.StringField(required=True)
    last_name = db.StringField(required=True)
    email = db.StringField(required=True)
    password = db.StringField(required=True)
    favourites_list = db.ListField(db.ObjectIdField())
    alerts = db.EmbeddedDocumentListField(AlertModel)
    verification = db.BooleanField(required=True, default=False)

    def json(self):
        alert_list = []
        for alert in self.alerts:
            alert_list.append(alert.json())
        return {
            '_id': str(self.id), 
            'first_name': self.first_name, 
            'last_name': self.last_name, 
            'email': self.email, 
            'password': self.password, 
            'favourites': self.favourites_list, 
            'alerts': alert_list
        }

    def add_to_fav(self, ticker):
        stock = StockModel.find_by_ticker(ticker).first()
        if str(stock.id) not in self.favourites_list: 
            self.favourites_list.append(str(stock.id))
            self.save()
        return 

    def remove_from_fav(self, ticker):
        stock = StockModel.find_by_ticker(ticker).first()
        if str(stock.id) in self.favourites_list:
            self.favourites_list.remove(str(stock.id))
            self.save()

    def send_email(self, jwt):
        send_verify_email(self.email, jwt)

    meta = {
        # 'db_alias': 'shop',
        'collection': 'users'
    }

    @classmethod
    def find_by_email(cls, email):
        return cls.objects(email=email)

    @classmethod
    def find_by_user_id(cls, _id):
        return cls.objects(id=_id)

    @classmethod
    def check_all_alerts(cls):
        for user in cls.objects:
            for alert in user.alerts:
                if alert.triggered == True:
                    continue
                data = alert.check_alert()
                if not data:
                    continue
                send_alert_email(user.email, data)
                alert.triggered = True
            user.save()