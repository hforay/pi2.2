import pyodbc

class Access:
    def __init__(self,connexion):
        self._conn = pyodbc.connect(connexion)
        self._cursor = self._conn.cursor()
    
    def getConnection(self):
        return self._conn

    def getCursor(self):
        return self._cursor
    
    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

    def execute(self, requete):
        self._cursor.execute(requete)

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchone(self):
        return self._cursor.fetchone()

    def query(self, requete):
        self._cursor.execute(requete)
        return self.fetchall()
    
    def create(self, requete):
        return self._cursor.execute(requete)
    
    def insert(self, requete, value):
        self._cursor.execute(requete, value)