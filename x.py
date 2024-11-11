import requests
from dbconnect import UsersData, Trades
import json
import telebot
from telebot import types
from telebot.util import antiflood

db_users = UsersData()
db_trades = Trades()
db_users.setup()
db_trades.setup()


def leaders():
    try:
        lead = db_users.get_all_stats()
        print(f"{lead}")
        x = dict(lead)
        sorted_users = sorted(x.items(), key=lambda x: x[1], reverse=True)[2:]
        print(sorted_users)
        msg = "*LeaderBoard\n*"
        for user, stats in sorted_users:
            msg += f"*{user} : {stats}*\n"
        #bot.send_message(message.chat.id, msg, parse_mode='Markdown')
        print(msg)
    except Exception as e:
        print(e)
        
        
        
leaders()

