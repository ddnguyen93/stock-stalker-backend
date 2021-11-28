from db import db
from models.stock import StockModel

class AlertModel(db.EmbeddedDocument):
    stock_id = db.ObjectIdField(required=True)
    trigger_price = db.FloatField(required=True)
    alert_type = db.StringField(required=True)
    operation = db.StringField(required=True)
    MA_period = db.IntField()
    triggered = db.BooleanField(required=True, default=False)

    def json(self):
        return {'stock_id': str(self.stock_id), 'trigger_price':self.trigger_price, 'operation': self.operation, 'alert_type': self.alert_type, 'MA_period': self.MA_period }

    def check_alert(self):
        stock = StockModel.find_by_id(self.stock_id).first()

        def data(current_value):
            data_obj={
                'full_name': stock.full_name,
                'ticker': stock.ticker,
                'current_price': "%.2f" % stock.hist_data[-1]['price'],
                'alert_type': self.alert_type,
                'MA_period': self.MA_period,
                'operator': self.operation,
                'trigger_price': "%.2f" % self.trigger_price,
                'current_value': "%.2f" % current_value,

            }
            return data_obj

        def greater_than(value, trigger):
            if value >= trigger:
                return data(value)
            else:
                return False

        def lesser_than(value, trigger):
            if value <= trigger:
                return data(value)
            else:
                return False
        
        if self.alert_type == "current":
            if self.operation == ">=":
                return greater_than(stock.hist_data[-1]['price'], self.trigger_price)
            elif self.operation == "<=":
                return lesser_than(stock.hist_data[-1]['price'], self.trigger_price)
        elif self.alert_type == "average":
            total = 0
            for i in range(-1*self.MA_period, 0):
                total += stock.hist_data[i]['price']
            average = total/self.MA_period

            if self.operation == ">=":
                return greater_than(average, self.trigger_price)
            elif self.operation == "<=":
                return lesser_than(average, self.trigger_price)
