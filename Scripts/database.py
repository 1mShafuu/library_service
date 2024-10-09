import psycopg2

class DatabaseConnection:
    def __init__(self, db_config):
        self.db_config = db_config
    
    def __enter__(self):
        self.conn = psycopg2.connect(**self.db_config)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

    def fetch_query(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params)
        self.conn.commit()

##