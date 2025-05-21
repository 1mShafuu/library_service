import json
from database import DatabaseConnection
from library import Library
from reports import Reports
from menus import main_menu
from celery import Celery
import time

app = Celery('main', broker='redis://localhost:6379/0')
app.conf.broker_connection_retry_on_startup = True



@app.task
def notify_after_ten_seconds():
    time.sleep(10)
    print("HelloworldformCelery")


def load_db_config(config_file: str) -> dict:  # загружаем config бд из json
    with open(config_file, 'r') as f:
        return json.load(f)


def main():
    print("Sending task...")
    notify_after_ten_seconds.delay()
    db_config = load_db_config('db_config.json')

    with DatabaseConnection(db_config) as db:
        library = Library(db)
        reports = Reports(db)
        main_menu(library, reports)


if __name__ == "__main__":
    main()
