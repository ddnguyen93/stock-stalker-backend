from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from models.stock import StockModel
from models.user import UserModel

import datetime

scheduler = APScheduler()


def job():
    print(datetime.datetime.now())

def run_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(StockModel.update_all_stocks, 'cron', day_of_week='mon-fri', hour='14-21', minute='0')
    scheduler.add_job(StockModel.update_all_stocks, 'cron', day_of_week='mon-fri', hour='14-21', minute='15')
    scheduler.add_job(StockModel.update_all_stocks, 'cron', day_of_week='mon-fri', hour='14-21', minute='30')
    scheduler.add_job(StockModel.update_all_stocks, 'cron', day_of_week='mon-fri', hour='14-21', minute='45')

    scheduler.add_job(UserModel.check_all_alerts, 'cron', day_of_week='mon-fri', hour='14-21', minute='2')
    scheduler.add_job(UserModel.check_all_alerts, 'cron', day_of_week='mon-fri', hour='14-21', minute='17')
    scheduler.add_job(UserModel.check_all_alerts, 'cron', day_of_week='mon-fri', hour='14-21', minute='32')
    scheduler.add_job(UserModel.check_all_alerts, 'cron', day_of_week='mon-fri', hour='14-21', minute='47')

    scheduler.start()

