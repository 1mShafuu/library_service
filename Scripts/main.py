import json
from database import DatabaseConnection
from library import Library
from reports import Reports
from menus import main_menu

def load_db_config(config_file: str) -> dict:
    #Загружаем конфигурацию базы данных postgres из файла JSON
    with open(config_file, 'r') as f:
        return json.load(f)

def main():
    db_config = load_db_config('db_config.json')

    with DatabaseConnection(db_config) as db:
        library = Library(db)
        reports = Reports(db)
        main_menu(library, reports)

if __name__ == "__main__":
    main()
