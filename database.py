from typing import Union

import sqlite3

class SQLGen:
    def __init__(self):
        self.query = ''
    
    def getQuery(self):
        return self.query

class DataType:
    NUL  = 'NULL'
    INT  = 'INTEGER'
    REAL = 'REAL'
    TXT  = 'TEXT'
    BLOB = 'BLOB'

class ColumnGen(SQLGen):
    def __init__(self, name: str, _type: str):
        self.query = [name, _type]
    
    def Primary(self):
        self.query.append('PRIMARY KEY')
        return self
    
    def NotNull(self):
        self.query.append('NOT NULL')
        return self
    
    def Default(self, value: str):
        if isinstance(value, str):
            value = f"'{value}"
        self.query.append(f'DEFAULT {value}')
        return self
    
    def Unique(self):
        self.query.append('UNIQUE')
        return self
    
    def Check(self, expr: str):
        self.query.append(f'CHECK ({expr})')
        return self
    
    def getQuery(self):
        return ' '.join(self.query)

class TableGen(SQLGen):
    def __init__(self, name: str, skip: bool = True, woRowID: bool = False):
        self.head = 'CREATE TABLE '
        if skip:
            self.head += 'IF NOT EXISTS '
        self.head += name
        
        self.__columns = []

        self.woRowID = woRowID
    
    def addColumn(self, column: Union[str, ColumnGen]):
        if isinstance(column, ColumnGen):
            column = column.getQuery()
        self.__columns.append(column)
        return self
    
    def getQuery(self):
        if len(self.__columns) == 0:
            raise Exception
        
        query = f"{self.head} ({', '.join(self.__columns)})"
        if self.woRowID:
            query += ' WITHOUT ROWID'
        query += ';'

        return query

class InsertGen(SQLGen):
    def __init__(self, tableName: str):
        self.head = f'INSERT INTO {tableName} '
        self.__columns = []
        self.__values = []
    
    def setValue(self, colName: str, value):
        if isinstance(value, str):
            value = f"'{value}'"
        
        self.__columns.append(colName)
        self.__values.append(value)
    
    def getQuery(self):
        return f"{self.head} ({', '.join(self.__columns)}) VALUES ({', '.join(self.__values)})"

class DB:
    def __init__(self):
        self.con = sqlite3.connect('.db')
    
    def run(self, sql: Union[str, SQLGen]):
        cur = self.con.cursor()

        if isinstance(sql, SQLGen):
            sql = sql.getQuery()

        result = cur.execute(sql)
        self.con.commit()
        return result

db = DB()
