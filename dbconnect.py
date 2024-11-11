import sqlite3
"""
saves all the users of bot in a database for advance purposes

"""

class UsersData:


    def __init__(self, dbname = "user.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)


    def setup(self):
        statement1 = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, chatid INTEGER UNIQUE, balance INTEGER DEFAULT 1000, wallet TEXT DEFAULT '0x00000000000000' )"
        self.conn.execute(statement1)
        self.conn.commit()


    def add_user(self, username_):
        statement = "INSERT OR IGNORE INTO users (chatid) VALUES (?)"
        args = (username_, )
        self.conn.execute(statement, args)
        self.conn.commit()
    

    def update_balance(self, amount, userid):
        statement = "UPDATE users SET balance = ? WHERE chatid = ?"
        args = (amount, userid)
        self.conn.execute(statement, args)
        self.conn.commit()
        
        
        
    def get_balance(self, owner):
        statement = "SELECT balance FROM users WHERE chatid = ?"
        args = (owner,)
        cursor = self.conn.execute(statement, args)
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    
    
    def update_wallet(self, amount, userid):
        statement = "UPDATE users SET wallet = ? WHERE chatid = ?"
        args = (amount, userid)
        self.conn.execute(statement, args)
        self.conn.commit()
        
        
        
    def get_wallet(self, owner):
        statement = "SELECT wallet FROM users WHERE chatid = ?"
        args = (owner,)
        cursor = self.conn.execute(statement, args)
        result = cursor.fetchone()
        if result:
            return result[0]
        return None


    def get_users(self):
        statement = "SELECT chatid FROM users"
        return [x[0] for x in self.conn.execute(statement)]
    
    
    def get_all_stats(self):
        statement = "SELECT chatid, balance FROM users"
        return [x for x in self.conn.execute(statement)]




class Trades:
    
    def __init__(self, dbname="trades.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.setup()
        
    def setup(self):
        statement = """CREATE TABLE IF NOT EXISTS trades (
                        owner TEXT,
                        buy_mc INTEGER,
                        sell_mc INTEGER,
                        contract_address TEXT,
                        pnl INTEGER,
                        buy_amount INTEGER,
                        token_balance INTEGER,
                        chain TEXT
                    )"""
        self.conn.execute(statement)
        self.conn.commit()
        
    def add_trade(self, owner, contract_address, chain, buy_mc=None, sell_mc=None, pnl=None, buy_amount=None, token_balance=None):
        try:
            statement = "INSERT INTO trades (owner, buy_mc, sell_mc, contract_address, pnl, buy_amount, token_balance, chain) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            args = (owner, buy_mc, sell_mc, contract_address, pnl, buy_amount, token_balance, chain)
            self.conn.execute(statement, args)
            self.conn.commit()
            return "Trade added successfully"
        except Exception as e:
            return str(e)
    
    def retrieve_last_ca(self, owner):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''SELECT contract_address FROM trades WHERE owner = ? ORDER BY ROWID DESC LIMIT 1''', (owner,))
            last_ca = cursor.fetchone()
            if last_ca:
                return last_ca[0]
            else:
                return None
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
        
    def retrieve_last_buycap(self, owner):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''SELECT buy_mc FROM trades WHERE owner = ? ORDER BY ROWID DESC LIMIT 1''', (owner,))
            last_buy_mc = cursor.fetchone()
            if last_buy_mc:
                return last_buy_mc[0]
            else:
                return None
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
        
    def retrieve_token_bal(self, owner):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''SELECT token_balance FROM trades WHERE owner = ? ORDER BY ROWID DESC LIMIT 1''', (owner,))
            last_tok_bal = cursor.fetchone()
            if last_tok_bal:
                return last_tok_bal[0]
            else:
                return None
        except Exception as e:
            return str(e)
        finally:
            cursor.close()

    def update_trade(self, owner, contract_address,chain, buy_mc=None, sell_mc=None, pnl=None, buy_amount=None, token_balance=None):
        try:
            statement = "UPDATE trades SET buy_mc=?, sell_mc=?, pnl=?, buy_amount=?, token_balance=?, chain=? WHERE owner=? AND contract_address=?"
            args = (buy_mc, sell_mc, pnl, buy_amount, token_balance, chain, owner, contract_address)
            self.conn.execute(statement, args)
            self.conn.commit()
            return "Trade updated successfully"
        except Exception as e:
            return str(e)

    def get_all_trades(self, owner):
        try:
            statement = "SELECT owner, buy_mc, sell_mc, contract_address, pnl, buy_amount, token_balance, chain FROM trades WHERE owner = ?"
            args = (owner, )
            cursor = self.conn.cursor()
            cursor.execute(statement, args)
            trades = cursor.fetchall()
            return trades
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
    
    
    
    def delete_last_ca(self, owner):
        try:
            # Create a cursor object from the connection
            cursor = self.conn.cursor()
            
            # Execute SQL query to retrieve the last contract address for the given owner
            cursor.execute('''SELECT contract_address FROM trades WHERE owner = ? ORDER BY ROWID DESC LIMIT 1''', (owner,))
            
            # Fetch the result of the query
            last_ca = cursor.fetchone()
            
            if last_ca:
                # Extract the contract address from the fetched result
                last_ca = last_ca[0]

                # Delete the last entry with the retrieved contract address
                cursor.execute('''DELETE FROM trades WHERE contract_address = ?''', (last_ca,))
                self.conn.commit()  # Commit the changes to the database
                print("Last entry deleted successfully.")
            else:
                print("No entries found for the specified owner.")
        except Exception as e:
            print("An error occurred:", e)
    
    
    def delete_all_trades(self, owner):
        try:
            statement = "DELETE FROM trades WHERE owner = ? " 
            args = (owner, )
            self.conn.execute(statement, args)
            self.conn.commit()
            
        except Exception as e:
            print(e)
            
            
if __name__ == "__main__":
    trades = Trades()
    trades.add_trade("Alice", "0x1234", buy_mc=1000, sell_mc=500, pnl=200, buy_amount=300, token_balance=1000, chain="ETH")
    print(trades.get_all_trades("Alice"))