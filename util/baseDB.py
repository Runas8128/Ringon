import sqlite3

class DB:
    """Base class for SQLite3 DB

    This class offers simple SQL query executor

    Parameters
    ----------
    * dbPath: :class:`str`
        - specifies db file to connect

    ."""
    def __init__(self, dbPath: str):
        self.dbCon = sqlite3.connect(dbPath)

        # This enables to access query result with row name
        # ex) res["row"]
        self.dbCon.row_factory = sqlite3.Row
    
    def _runSQL(self, query: str, *parameters):
        """Run SQL query with parameters

        Query will be run in its own connected database
        based on sqlite3 syntax

        This method is for derived-class only.
        
        Parameters
        ----------
        * query: :class:`str`
            - Query you want to run.
        * parameters: Union[:class:`dict`, :class:`list`, :class:`tuple`]
            - Parameters for your query. It can be `dict` for named parameter.
        
        Return value
        ------------
        Result for your query. Type: List[:class:`Tuple`]

        ."""
        if len(parameters) > 0 and isinstance(parameters[0], (dict, list, tuple)):
            parameters = parameters[0]
        cur = self.dbCon.cursor()
        cur.execute(query, parameters)
        self.dbCon.commit()
        return cur.fetchall()
