import mysql.connector

class DataBase():
    def __enter__(self):
        self.cnx = mysql.connector.connect(user='root', database='whats_pplaying')
        self.cursor = self.cnx.cursor()
        return self

    def commit(self, query, args={}):
        self.cursor.execute(query, args)
        self.cnx.commit()

    def excuteAll(self, query, args={}):
        self.cursor.execute(query, args)
        return self.cursor.fetchall()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.cnx.close()