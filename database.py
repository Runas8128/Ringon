from typing import Union

import sqlite3

class _dbCon:
    def __init__(self):
        self.con = sqlite3.connect('.db')
    
    def __enter__(self):
        return self.con.cursor()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.commit()
    
    def close(self):
        self.con.close()

class SQLGen:
    def __init__(self):
        self.query = ''
    
    def getQuery(self):
        return self.query

class DB:
    def __init__(self):
        self.con = _dbCon()
    
    def run(self, sql: Union[str, SQLGen]):
        with self.con as con:
            if isinstance(sql, SQLGen):
                sql = sql.getQuery()
            return con.execute(sql)

class DataType:
    NUL  = 'NULL'
    INT  = 'INTEGER'
    REAL = 'REAL'
    TXT  = 'TEXT'
    BLOB = 'BLOB'

class ColumnGen(SQLGen):
    def __init__(self, name: str, _type: str):
        self.query = name + ' ' + _type
    
    def Primary(self):
        self.query += ' PRIMARY KEY '
        return self
    
    def NotNull(self):
        self.query += ' NOT NULL '
        return self
    
    def Default(self, value: str):
        self.query += ' DEFAULT ' + str(value)
        return self
    
    def Unique(self):
        self.query += ' UNIQUE '
        return self
    
    def Check(self, expr: str):
        self.query += ('CHECK (' + expr + ') ')
        return self

class TableGen(SQLGen):
    def __init__(self, name: str, skip: bool = True):
        self.query = 'CREATE TABLE '
        if skip:
            self.query += 'IF NOT EXISTS '
        self.query += name
        self.query += '('
    
    def addColumn(self, column: Union[str, ColumnGen]):
        if isinstance(column, ColumnGen):
            column = column.getQuery()
        
        if self.query[-1] != '(':
            self.query += ', '
        self.query += column
        
        return self
    
    def woRowID(self):
        if self.query[-1] != ')':
            self.query += ')'
        self.query += ' WITHOUT ROWID'
        return self
    
    def getQuery(self):
        if self.query[-1] != 'D':
            self.query += ')'
        self.query += ';'
        return self.query

db = DB()
