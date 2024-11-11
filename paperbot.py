import requests
from dbconnect import UsersData, Trades
import json
import telebot
from telebot import types
from telebot.util import antiflood, extract_arguments
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')



db_users = UsersData()
db_trades = Trades()
db_users.setup()
db_trades.setup()

bot = telebot.TeleBot(TOKEN)





"""working with api for mc, price changes and pnl"""
def get_url(addr: str):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{addr}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return "failed to connect try again later"
    
    
def get_mc(addr: str):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{addr}"
    response = requests.get(url)
    if response.status_code == 200:
        mc = response.json()['pairs'][0]["fdv"]
        return mc
    else:
        return "failed to connect try again later"
    

def get_name(addr: str):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{addr}"
    response = requests.get(url)
    if response.status_code == 200:
        mc = response.json()['pairs'][0]['baseToken']['name']
        return mc
    else:
        return "failed to connect try again later"


def get_price(addr: str):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{addr}"
    response = requests.get(url)
    if response.status_code == 200:
        mc = response.json()['pairs'][0]['priceUsd']
        return mc
    else:
        return "failed to connect try again later"

def get_username(user_id):
    try:
        user = bot.get_chat(user_id)
        if user.username:
            return user.username
        else:
            return user.first_name
    except Exception as e:
        print(e)
        return None

def get_symbol(addr: str):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{addr}"
    response = requests.get(url)
    if response.status_code == 200:
        mc = response.json()['pairs'][0]['baseToken']['symbol']
        return mc
    else:
        return "failed to connect try again later"


def leaders(message):
    try:
        lead = db_users.get_all_stats()
        print(f"{lead}")
        x = dict(lead)
        sorted_users = sorted(x.items(), key=lambda x: x[1], reverse=True)[:10]
        msg = "*LeaderBoard For Top 10 Trades*\n\n"
        for user, stats in sorted_users:
            msg += f"*@{get_username(user)} {db_users.get_wallet(user)[:7]}... : ${stats}*\n"
        bot.send_message(message.chat.id, msg, parse_mode='Markdown', disable_web_page_preview=True)

    except Exception as e:
        print(e)


#start and help command helper
@bot.message_handler(commands=['start'])
def send_welcome(message):
    owner_id = message.chat.id
    db_users.add_user(owner_id)
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Demo account', callback_data='demo_acc')
    btn2 = types.InlineKeyboardButton('Start trading', callback_data='s')
    markup.add(btn2,btn1)
    welcome_message = """
Welcome to BlazeX Paper Trade Bot!!
    
You can trade Real-Time Base, Eth and Sol tokens with this Bot with virtual money, to learn to trade risk free and craft new strategies, monitoring your trades and more!

To begin trading, paste a contract address on any of the following Networks (Base, Eth, Sol) and follow the steps after!
"""
    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)
            



@bot.message_handler(commands=['balance'])
def send_balance(message):
    owner_id = message.chat.id
    bal = db_users.get_balance(owner_id)
    welcome_message = f"You have ${round(bal,2)} left!!!"
    bot.reply_to(message, welcome_message)


@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = """ 🔥 *BlazeX  Paper Trade Bot* 🔥
    
    Each account has a default balance of $1000.
To trade a token, paste the contract address of the token you want to trade and select the desired amount
click the sell button to sell the token and take profits'
Have fun trading and do not lose your capital!!!
*COMMANDS*
Use /alltrades command to see all trades
/balance command to view your balance
/resetbalance to reset your balance
/cleartrades clears all previous trades

⚠️⚠️ PLEASE NOTE YOU CANNOT TRADE 2 TOKENS AT A TIME ⚠️⚠️



    """
    bot.reply_to(message, help_message)


@bot.message_handler(commands=['resetuserbalance'])
def reset(message):
    messager = message.chat.id
    if str(messager) == "7034272819" or str(messager) == "1739436078":
        owner = extract_arguments(message.text)
        db_users.update_balance(1000, owner)
        bot.reply_to(message, "Your balance has been set back to a $1000 :)")
    else:
        bot.reply_to(message, "you're not allowed to perform this action!   ")

@bot.message_handler(commands=['resetbalance'])
def rbal(message):
    bot.send_message(message.chat.id, f"Tag an admin in th group with the code`{message.chat.id}` to reset Your Balance", parse_mode='Markdown')    

@bot.message_handler(commands=['cleartrades'])
def cleartrades(message):
    owner = message.chat.id
    db_trades.delete_all_trades(owner)
    bot.send_message(message.chat.id, "Cleared all trades!!!")




 
@bot.message_handler(commands=['alltrades'])
def alltrades(message):
    owner = message.chat.id
    try:
        trade_history = db_trades.get_all_trades(owner)
        messages = "*All Trades*!\n\n"
        for trade in trade_history:
            messages += f"💰 *{get_name(trade[3])}({trade[7]}) ${trade[1]} (B) ---> ${trade[2]} (S). Pnl {trade[4]}x | Amt: ${trade[5]} Profit: ${trade[5]*trade[4]}*\n\n"
            
        bot.send_message(message.chat.id,messages, parse_mode='Markdown')
    except Exception as e:
        print(e)
        print(messages)
              
 
@bot.message_handler(commands=['resetall'])
def reset_all(message):
    if message.chat.id == 7034272819:
        users = db_users.get_users()
        for user in users:
            db_users.update_balance(1000, user)
        bot.send_message(message.chat.id, "done")
    else:
            bot.send_message(message.chat.id, "youre not allowes to use this")
    print("done")


 
        
#Dev commands 

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    print(message.from_user.id)
    messager = message.chat.id
    if str(messager) == "7034272819" or str(messager) == "6219754372":
        send = bot.send_message(message.chat.id,"Enter message to broadcast")
        bot.register_next_step_handler(send,sendall)
        
    else:
        bot.reply_to(message, "You're not allowed to use this command")
        
        
        
def sendall(message):
    users = db_users.get_users()
    for chatid in users:
        try:
            msg = antiflood(bot.send_message, chatid, message.text)
        except Exception as e:
            print(e)
        
    bot.send_message(message.chat.id, "done")
    

@bot.message_handler(commands=['userno'])
def userno(message):
    print(message.from_user.id)
    messager = message.chat.id
    if str(messager) == "7034272819" or str(messager) == "6219754372":
        x = db_users.get_users()
        bot.reply_to(message,f"Total bot users: {len(x)}")
    else:
        bot.reply_to(message, "admin command")
        
        
    
@bot.message_handler(func=lambda message: len(message.text) == 43 or len(message.text) == 44 or len(message.text))
def trade(message):
    try:
        token = message.text
        x = get_url(token)
        if x['pairs'][0]['chainId'] == "solana":
            chart = x['pairs'][0]['url']
            chain = x['pairs'][0]['chainId']
            name = get_name(token)
            symbol = get_symbol(token)
            price = x['pairs'][0]['priceUsd']
            m5_PC = x['pairs'][0]['priceChange']['m5']
            h1_PC = x['pairs'][0]['priceChange']['h1']
            h6_PC = x['pairs'][0]['priceChange']['h6']
            mc = get_mc(token)
            owner = message.chat.id
            db_trades.add_trade(owner=owner,contract_address= token, chain=chain)
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("💰Buy $500", callback_data='buy10')
            btn2 = types.InlineKeyboardButton("💰Buy $50", callback_data='buy50')
            btn3 = types.InlineKeyboardButton("💰Buy $100", callback_data='buy100')
            btn5 = types.InlineKeyboardButton("💰Buy $1000", callback_data='buy1000')
            btn4 = types.InlineKeyboardButton("Cancel ❌️", callback_data='cancel')
            
            markup.add(btn2,btn3,btn1,btn5,btn4)
            new_message = f"""   🔥 *BlazeX  Paper Trade Bot* 🔥
            
💡*{name}({symbol})*
💡*CA:* `{token}`

ℹ️ Market Cap: $ *{mc: ,}*

ℹ️ Price: _${price}_

ℹ️ Price Change:
```
5m: {m5_PC}%
1h: {h1_PC}%
6h: {h6_PC}%
```

[Chart]({chart}) | [solscan](solscan.io/token/{token}) | [STB](https://t.me/SolanaTradingBot?start={token}-sC101ly6J) | [bonk](https://t.me/bonkbot_bot?start=ref_op68n_ca_{token})
"""
            bot.send_message(message.chat.id, new_message, reply_markup= markup, parse_mode='Markdown', disable_web_page_preview=True)
            
            
            
        elif x['pairs'][0]['chainId'] == "ethereum" or x['pairs'][0]['chainId'] == "base":
            
            
            chart = x['pairs'][0]['url']
            chain = x['pairs'][0]['chainId']
            name = get_name(token)
            symbol = get_symbol(token)
            price = x['pairs'][0]['priceUsd']
            m5_PC = x['pairs'][0]['priceChange']['m5']
            h1_PC = x['pairs'][0]['priceChange']['h1']
            h6_PC = x['pairs'][0]['priceChange']['h6']
            mc = get_mc(token)
            ether = f"[etherscan](etherscan.io/address/{token})"
            base = f"[basescan](basescan.org/address/{token})"
            owner = message.chat.id
            db_trades.add_trade(owner=owner,contract_address= token, chain=chain)
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("💰Buy $500", callback_data='buy10')
            btn2 = types.InlineKeyboardButton("💰Buy $50", callback_data='buy50')
            btn3 = types.InlineKeyboardButton("💰Buy $100", callback_data='buy100')
            btn5 = types.InlineKeyboardButton("💰Buy $1000", callback_data='buy1000')
            btn4 = types.InlineKeyboardButton("Cancel ❌️", callback_data='cancel')
            
            markup.add(btn2,btn3,btn1,btn5,btn4)
            new_message = f"""   🔥 *BlazeX  Paper Trade Bot* 🔥
            
💡*{name}({symbol})*
💡*CA:* `{token}`

ℹ️ Market Cap: $ *{mc: ,}*

ℹ️ Price: _${price}_

ℹ️ Price Change:
```
5m: {m5_PC}%
1h: {h1_PC}%
6h: {h6_PC}%
```

[Chart]({chart}) | { ether if x['pairs'][0]['chainId'] == "ethereum" else base }
"""
            bot.send_message(message.chat.id, new_message, reply_markup= markup, parse_mode='Markdown', disable_web_page_preview=True)

            
            
        else: bot.send_message(message.chat.id, "We could not identify the chain\nPlease make sure Ca is only Sol, base or Eth contract :)")
        
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id,"make sure you pasted a valid contract address or try again :)")
        


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    owner = call.message.chat.id
    token = "78b5bwHGyfK3yrDT2Crf2sEEzxAHs13q9dUwrF8uWihw" if db_trades.retrieve_last_ca(owner) == None else db_trades.retrieve_last_ca(owner)
    name = get_name(token)
    symbol = get_symbol(token)
    if call.data == "buy10":
        try:
            if get_mc(token)  >= 100:
                if db_users.get_balance(owner) >= 500:
                    buyamt10 = 500
                    buymc = get_mc(token)
                    price = get_price(token)
                    token_balance = (500/float(price))
                    x = get_url(token)
                    chain = x['pairs'][0]['chainId']
                    
                    pnl = (get_mc(token)-buymc)/buymc*100
                    print(buymc)
                    bot.send_message(call.message.chat.id, f"attempting a $500 buy at ${buymc: ,} Market Cap")
                    
                    db_trades.update_trade(owner=owner, contract_address= token, chain=chain , buy_mc= buymc, token_balance=token_balance)
                    
                    new_markup1 = types.InlineKeyboardMarkup(row_width=1)
                    sellbtn1 = types.InlineKeyboardButton("🚀 Sell", callback_data= 'sell10')
                    refresh2 = types.InlineKeyboardButton("♻️ Refresh", callback_data="sellRefresh21")
                    new_markup1.add(sellbtn1,refresh2)
                    message_ = f""" 🔥 *BlazeX  Paper Trade Bot* 🔥
                    
    💡 *{name}({symbol})*: `{token}`

    💰 *Buy amt : $500*

    💰*Prof: {round(pnl, 2)}% | ${round((get_mc(token)/buymc)*500, 2)}*

    ℹ️ *Bal: {round(token_balance, 2)} {name}*

    ℹ️ *Buy MC: ${buymc: ,}*

    ℹ️ *Current MC: ${get_mc(token): ,}*
    """
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text = message_ , reply_markup=new_markup1, parse_mode= "Markdown")
                    bot.send_message(call.message.chat.id, f"Bought $500 worth of {name} ")
                    owner = call.message.chat.id
                    bal = db_users.get_balance(owner)
                    balc = bal - buyamt10
                    db_users.update_balance(balc, owner)
                    print(db_users.get_balance(owner))
                else:
                    bot.send_message(owner, "Blanace Lower that buy amount")
            else:
                bot.send_message(call.message.chat.id, "Low Market Cap, cannot buy")
        except Exception as e:
            print(e)
                
                
    elif call.data == "buy50":
        try:
            if get_mc(token)  >= 100:
                if db_users.get_balance(owner) >= 50:
                    buyamt50 = 50
                    buymc2 = get_mc(token)
                    price = get_price(token)
                    token_balance = (50/float(price))
                    x = get_url(token)
                    chain = x['pairs'][0]['chainId']
                    pnl = (get_mc(token)-buymc2)/buymc2*100
                    bot.send_message(call.message.chat.id, f"attempting a $50 buy at ${buymc2: ,} Market Cap")
                    
                    db_trades.update_trade(owner=owner, contract_address= token,chain= chain, buy_mc= buymc2, token_balance=token_balance)
                    
                    new_markup1 = types.InlineKeyboardMarkup(row_width=1)
                    sellbtn50 = types.InlineKeyboardButton("🚀 Sell", callback_data= 'sell50')
                    refresh50 = types.InlineKeyboardButton("♻️ Refresh", callback_data="sellRefresh22")
                    new_markup1.add(sellbtn50,refresh50)
                    message_ = f""" 🔥 *BlazeX  Paper Trade Bot* 🔥
                    
    💡 *{name}({symbol})*: `{token}`

    💰 *Buy amt: $50*

    💰*Prof: {round(pnl, 2)}% | ${round((get_mc(token)/buymc2)*50, 2)}*

    ℹ️ *Bal: {round(token_balance, 2)} {name}*

    ℹ️ *Buy MC: ${buymc2: ,}*

    ℹ️ *Current MC: ${get_mc(token): ,}*
    """
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text = message_ , reply_markup=new_markup1, parse_mode= "Markdown")
                    bot.send_message(call.message.chat.id, f"Bought $50 worth of {name} ")
                    owner = call.message.chat.id
                    bal = db_users.get_balance(owner)
                    balc = bal - buyamt50
                    db_users.update_balance(balc, owner)
                    print(db_users.get_balance(owner))
                    
                else:
                    bot.send_message(owner, "Balance lower than buy amount")
                
            else:
                bot.send_message(call.message.chat.id, "Low Market Cap, cannot buy")
        except Exception as e:
            print(e)
        
    elif call.data == "buy100":
        try:
            if get_mc(token)  >= 100:
                if db_users.get_balance(owner) >= 100:
                    buyamt100 = 100
                    buymc3 = get_mc(token)
                    price = get_price(token)
                    token_balance = (100/float(price))
                    pnl = (get_mc(token)-buymc3)/buymc3*100
                    x = get_url(token)
                    chain = x['pairs'][0]['chainId']
                    bot.send_message(call.message.chat.id, f"attempting a $100 buy at ${buymc3: ,} Market Cap")
                    
                    db_trades.update_trade(owner=owner, contract_address= token, chain=chain, buy_mc= buymc3, token_balance= token_balance)
                    
                    new_markup1 = types.InlineKeyboardMarkup(row_width=1)
                    sellbtn100 = types.InlineKeyboardButton("🚀 Sell", callback_data= 'sell100')
                    refresh100 = types.InlineKeyboardButton("♻️ Refresh", callback_data="sellRefresh23")
                    new_markup1.add(sellbtn100,refresh100)
                    message_ = f""" 🔥 *BlazeX  Paper Trade Bot* 🔥
                    
    💡 *{name}({symbol})*: `{token}`

    💰 *Buy amt: $100*

    💰*Prof: {round(pnl, 2)}% | ${round((get_mc(token)/buymc3)*100, 2)}*

    ℹ️ *Bal: {round(token_balance, 2)} {name}*

    ℹ️ *Buy MC: ${buymc3: ,}*

    ℹ️ *Current MC: ${get_mc(token): ,}*
    """
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text = message_ , reply_markup=new_markup1, parse_mode= "Markdown")
                    bot.send_message(call.message.chat.id, f"Bought $100 worth of {name} ")
                    owner = call.message.chat.id
                    bal = db_users.get_balance(owner)
                    balc = bal - buyamt100
                    db_users.update_balance(balc, owner)
                    print(db_users.get_balance(owner))
                else:
                    bot.send_message(owner, "Balance lower than ")
            else:
                bot.send_message(call.message.chat.id, "Low Market Cap, cannot buy")
        except Exception as e:
            print(e)
            
            
    elif call.data == "buy1000":
        try:
            if get_mc(token)  >= 100:
                if db_users.get_balance(owner) >= 1000:
                    buyamt100 = 1000
                    buymc3 = get_mc(token)
                    price = get_price(token)
                    token_balance = (1000/float(price))
                    pnl = (get_mc(token)-buymc3)/buymc3*100
                    x = get_url(token)
                    chain = x['pairs'][0]['chainId']
                    bot.send_message(call.message.chat.id, f"attempting a $1000 buy at ${buymc3: ,} Market Cap")
                    
                    db_trades.update_trade(owner=owner, contract_address= token, chain=chain, buy_mc= buymc3, token_balance= token_balance)
                    
                    new_markup1 = types.InlineKeyboardMarkup(row_width=1)
                    sellbtn100 = types.InlineKeyboardButton("🚀 Sell", callback_data= 'sell1000')
                    refresh100 = types.InlineKeyboardButton("♻️ Refresh", callback_data="sellRefresh24")
                    new_markup1.add(sellbtn100,refresh100)
                    message_ = f""" 🔥 *BlazeX  Paper Trade Bot* 🔥
                    
    💡 *{name}({symbol})*: `{token}`

    💰 *Buy amt: $1000*

    💰*Prof: {round(pnl, 2)}% | ${round((get_mc(token)/buymc3)*1000, 2)}*

    ℹ️ *Bal: {round(token_balance, 2)} {name}*

    ℹ️ *Buy MC: ${buymc3: ,}*

    ℹ️ *Current MC: ${get_mc(token): ,}*
    """
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text = message_ , reply_markup=new_markup1, parse_mode= "Markdown")
                    bot.send_message(call.message.chat.id, f"Bought $1000 worth of {name} ")
                    owner = call.message.chat.id
                    bal = db_users.get_balance(owner)
                    balc = bal - buyamt100
                    db_users.update_balance(balc, owner)
                    print(db_users.get_balance(owner))
                    
                else:
                    bot.send_message(owner, "balance so low")
            else:
                bot.send_message(call.message.chat.id, "Low Market Cap, cannot buy")
        except Exception as e:
            print(e)
        
    elif call.data == "cancel":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        db_trades.delete_last_ca(owner)
        
        
        
    elif call.data == "sellRefresh21":
        print("yessssssssssssssssssssssssssssssssssss")
        refmark = types.InlineKeyboardMarkup(row_width=1)
        sellb = types.InlineKeyboardButton("🚀 Sell", callback_data= 'sell10')
        rf = types.InlineKeyboardButton("♻️ Refresh", callback_data="sellRefresh21")
        refmark.add(sellb,rf)
        buymcr = db_trades.retrieve_last_buycap(owner)
        pnl = (get_mc(token)-buymcr)/buymcr*100
        tb = db_trades.retrieve_token_bal(owner=owner)
        
        message1_ = f""" 🔥 *BlazeX  Paper Trade Bot* 🔥
                
💡 *{name}({symbol})*: `{token}`

💰 *Buy amt: $500*

💰*Prof: {round(pnl, 2)}% | ${round((get_mc(token)/buymcr)*500, 2)}*

 ℹ️ *Bal: {round(tb, 3)} {name}*

 ℹ️ *Buy Mc: ${buymcr: ,}*

 ℹ️ *Current Mc: ${get_mc(token): ,}*
"""
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text = message1_ , reply_markup=refmark, parse_mode= "Markdown")
        
        
        
    elif call.data == "sellRefresh22":
        print("yessssssssssssssssssssssssssssssssssss")
        refmark2 = types.InlineKeyboardMarkup(row_width=1)
        sellb2 = types.InlineKeyboardButton("🚀 Sell", callback_data= 'sell50')
        rf2 = types.InlineKeyboardButton("♻️ Refresh", callback_data="sellRefresh22")
        refmark2.add(sellb2,rf2)
        buymcr2 = db_trades.retrieve_last_buycap(owner)
        pnl = (get_mc(token)-buymcr2)/buymcr2*100
        tb = db_trades.retrieve_token_bal(owner=owner)
        message2_ = f""" 🔥 *BlazeX  Paper Trade Bot* 🔥
                
💡 *{name}({symbol})*: `{token}`

💰 *Buy amt: $50*

💰*Prof: {round(pnl, 2)}% | ${round((get_mc(token)/buymcr2)*50, 2)}*

 ℹ️ *Bal: {round(tb, 3)} {name}*

 ℹ️ *Buy Mc: ${buymcr2: ,}*

 ℹ️ *Current Mc: ${get_mc(token): ,}*
"""
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text = message2_ , reply_markup=refmark2, parse_mode= "Markdown")
        
        
        
    elif call.data == "sellRefresh23":
        print("yessssssssssssssssssssssssssssssssssss")
        refmark3 = types.InlineKeyboardMarkup(row_width=1)
        sellb3 = types.InlineKeyboardButton("🚀 Sell", callback_data= 'sell100')
        rf3 = types.InlineKeyboardButton("♻️ Refresh", callback_data="sellRefresh23")
        refmark3.add(sellb3,rf3)
        buymcr3 = db_trades.retrieve_last_buycap(owner)
        pnl = (get_mc(token)-buymcr3)/buymcr3*100
        tb = db_trades.retrieve_token_bal(owner=owner)
        message3_ = f""" 🔥 *BlazeX  Paper Trade Bot* 🔥
                
💡 *{name}({symbol})*: `{token}`

💰 *Buy amt: $100*

💰*Prof: {round(pnl, 2)}% | ${round((get_mc(token)/buymcr3)*100, 2)}*

 ℹ️ *Bal: {round(tb, 3)} {name}*

 ℹ️ *Buy MC: ${buymcr3: ,}*

 ℹ️ *Current Mc: ${get_mc(token): ,} *
"""
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text = message3_ , reply_markup=refmark3, parse_mode= "Markdown")
       
       
    
    elif call.data == "sellRefresh24":
        print("yessssssssssssssssssssssssssssssssssss")
        refmark3 = types.InlineKeyboardMarkup(row_width=1)
        sellb3 = types.InlineKeyboardButton("🚀 Sell", callback_data= 'sell1000')
        rf3 = types.InlineKeyboardButton("♻️ Refresh", callback_data="sellRefresh24")
        refmark3.add(sellb3,rf3)
        buymcr3 = db_trades.retrieve_last_buycap(owner)
        pnl = (get_mc(token)-buymcr3)/buymcr3*100
        tb = db_trades.retrieve_token_bal(owner=owner)
        message3_ = f""" 🔥 *BlazeX  Paper Trade Bot* 🔥
                
💡 *{name}({symbol})*: `{token}`

💰 *Buy amt: $1000*

💰*Prof: {round(pnl, 2)}% | ${round((get_mc(token)/buymcr3)*1000, 2)}*

 ℹ️ *Bal: {round(tb, 3)} {name}*

 ℹ️ *Buy MC: ${buymcr3: ,}*

 ℹ️ *Current Mc: ${get_mc(token):,} *
"""
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text = message3_ , reply_markup=refmark3, parse_mode= "Markdown")
       
        
        
    elif call.data == 'sell10': 
        buy = db_trades.retrieve_last_buycap(owner)
        print(buy)
        x = get_url(token)
        chain = x['pairs'][0]['chainId']
        bot.send_message(call.message.chat.id, f"selling {name} at ${get_mc(token):,} mc")
        current = get_mc(token)
        pnl_calc = current / buy
        pnl = round(pnl_calc, 2)
        #print(pnl)
        profit = 500*pnl
        #print(profit)
        bal = db_users.get_balance(owner)
        print(bal)
        bal_calc = bal + profit
        bc = round(bal_calc,2)
        db_trades.update_trade(owner=owner, contract_address=token, buy_mc= buy, sell_mc= current, pnl = pnl, buy_amount= 500, chain=chain)
        #print(db_trades.get_all_trades(owner))
        db_users.update_balance(bc,owner)
        bot.send_message(call.message.chat.id, f"Successfully sold {name} at {get_mc(token):,} mc with a gain of {pnl}x")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
    elif call.data == 'sell50': 
        buy = db_trades.retrieve_last_buycap(owner)
        print(buy)
        x = get_url(token)
        chain = x['pairs'][0]['chainId']
        bot.send_message(call.message.chat.id, f"selling {name} at ${get_mc(token):,} mc")
        current = get_mc(token)
        pnl_calc = current / buy
        pnl = round(pnl_calc, 2)
        print(pnl)
        profit = 50*pnl
        print(profit)
        bal = db_users.get_balance(owner)
        bal_calc = bal + profit
        bc = round(bal_calc,2)
        db_trades.update_trade(owner=owner, contract_address=token, buy_mc= buy, sell_mc= current, pnl = pnl, buy_amount= 50, chain=chain)
        #print(db_trades.get_all_trades(owner))
        db_users.update_balance(bc, owner)
        bot.send_message(call.message.chat.id, f"Successfully sold {name} at {get_mc(token):,} mc with a gain of {pnl}x")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
    elif call.data == 'sell100': 
        buy = db_trades.retrieve_last_buycap(owner)
        print(buy)
        x = get_url(token)
        chain = x['pairs'][0]['chainId']
        bot.send_message(call.message.chat.id, f"selling {name} at ${get_mc(token):,} mc")
        current = get_mc(token)
        pnl_calc = current / buy
        pnl = round(pnl_calc, 2)
        print(pnl)
        profit = 100*pnl
        print(profit)
        bal = db_users.get_balance(owner)
        bal_calc = bal + profit
        db_trades.update_trade(owner=owner, contract_address=token, buy_mc= buy, sell_mc= current, pnl = pnl, buy_amount= 100, chain=chain)
        #print(db_trades.get_all_trades(owner))
        bc = round(bal_calc,2)
        db_users.update_balance(bc, owner)
        bot.send_message(call.message.chat.id, f"Successfully sold {name} at {get_mc(token):,} mc with a gain of {pnl}x")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        
    elif call.data == 'sell1000': 
        buy = db_trades.retrieve_last_buycap(owner)
        print(buy)
        x = get_url(token)
        chain = x['pairs'][0]['chainId']
        bot.send_message(call.message.chat.id, f"selling {name} at ${get_mc(token):,} mc")
        current = get_mc(token)
        pnl_calc = current / buy
        pnl = round(pnl_calc, 2)
        print(pnl)
        profit = 1000*pnl
        print(profit)
        bal = db_users.get_balance(owner)
        bal_calc = bal + profit
        db_trades.update_trade(owner=owner, contract_address=token, buy_mc= buy, sell_mc= current, pnl = pnl, buy_amount= 1000, chain=chain)
        #print(db_trades.get_all_trades(owner))
        bc = round(bal_calc,2)
        db_users.update_balance(bc, owner)
        bot.send_message(call.message.chat.id, f"Successfully sold {name} at {get_mc(token):,} mc with a gain of {pnl}x")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        
    elif call.data == "s":
        bot.send_message(owner, "Paste a contract Address to start trading!")
        bot.delete_message(owner, call.message.message_id)
        
        
    elif call.data == 'demo_acc':
        wallet = db_users.get_wallet(owner)
        bal = db_users.get_balance(owner)
        msg = f"""@{get_username(owner)} Your Wallet: `{wallet}` has a balance of *{bal}*.
To Participate in the competition, You'll need to update your wallet address using the *update Wallet* button below.

Use the leaderboard button to see your position in the competition


        
        """
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Update Wallet', callback_data='update')
        btn2 = types.InlineKeyboardButton('LeaderBoard', callback_data='leader')
        markup.add(btn1,btn2)
        bot.send_message(owner, msg,parse_mode='Markdown', reply_markup=markup)
        
        
    elif call.data == 'update':
        y = bot.send_message(owner, "Send wallet address")
        bot.register_next_step_handler(y, wally)
        
    elif call.data == 'leader':
        leaders(call.message)
        
        
        
def wally(message):
    y = str(message.text)
    if y.startswith('0x'):
        db_users.update_wallet(y, message.chat.id)
        bot.send_message(message.chat.id, "Wallet has been successfuly updated!!!")
    else:
        bot.send_message(message.chat.id, "Wallet should be an ethereum wallet") 
        
bot.infinity_polling()