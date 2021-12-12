import sqlite3
import typing


class WorkspaceData:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.cursor.execute("CREATE TABLE IF NOT EXISTS watchlist(username TEXT,symbol TEXT, exchange TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS strategies(username TEXT, strategy_type TEXT, contract TEXT, exchange TEXT,timeframe TEXT, balance_pct REAL,take_profit REAL, stop_loss REAL, activation TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS login(username TEXT PRIMARY KEY, password TEXT, email TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS keys(username TEXT, binance_public_key TEXT, binance_private_key TEXT, bitmex_public_key TEXT, bitmex_private_key TEXT, FOREIGN KEY(username) REFERENCES login(username))")
        self.conn.commit()
    def add(self, table: str, data: typing.List[typing.Tuple]):
        table_data = self.cursor.execute(f"SELECT * FROM {table}")
        columns = [description[0] for description in table_data.description]
        sql_statement = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?']*len(columns))})"
        self.cursor.executemany(sql_statement, data)
        self.conn.commit()
    def save(self, table: str, data: typing.List[typing.Tuple], username):
        self.cursor.execute(f"DELETE FROM {table} WHERE USERNAME = '{username}'")

        table_data = self.cursor.execute(f"SELECT * FROM {table}")

        columns = [description[0] for description in table_data.description]

        sql_statement = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?']*len(columns))})"

        self.cursor.executemany(sql_statement, data)
        self.conn.commit()

    def get(self, table: str, username: str) -> typing.List[sqlite3.Row]:
        self.cursor.execute(f"SELECT * FROM {table} WHERE USERNAME='{username}'")
        data = self.cursor.fetchall()
        return data

#c = WorkspaceData()
#c.add('keys', [('Harsha', 'd5fd694f19a8c4feeec259e7d74e244d69f1bedf8af4a49c9387e2ea20a57433', 'b874a84f38efff2941fe2fcd86e83056a670d581e8187bd9641f263f5acfda26', 'YaTEaHBxKCB4t9XRCIlWd2Nq', 'FB-_2AK9FwGhBiAZQd59GhfHI2GCsffpq_aCKkfrUjRTELeX')])
