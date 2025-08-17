import telebot
import requests
import time

# Senin bot tokenin
TOKEN = "7591570412:AAGJ43nkH6ZZikX6VMJGCXVbpyUxyrDb8OA"
bot = telebot.TeleBot(TOKEN)

# =========================
# COIN LİSTESİ (ilk 500)
# =========================
coin_list = {}

def load_coin_list():
    global coin_list
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 500, "page": 1}
    res = requests.get(url, params=params, timeout=10)
    data = res.json()
    coin_list = {}
    for coin in data:
        coin_list[coin["id"]] = {
            "symbol": coin["symbol"].lower(),
            "name": coin["name"].lower()
        }
    print(f"✅ {len(coin_list)} coin yüklendi.")

def find_coin(user_input):
    user_input = user_input.lower()
    for coin_id, info in coin_list.items():
        if user_input == info["symbol"] or user_input == info["name"] or user_input == coin_id:
            return coin_id
    return None

# =========================
# FİYAT ÇEKME
# =========================
def get_coin_price(coin_id):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd"}
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if coin_id in data:
            return data[coin_id]["usd"]
        return None
    except Exception as e:
        print("Fiyat alınamadı:", e)
        return None

# =========================
# TELEGRAM KOMUTLARI
# =========================
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Merhaba! 👋\n"
        "Coin fiyatı: /price coinadı (örn: /price btc) 🚀\n"
        "İlk 10 coin: /top10\n"
        "En çok yükselen 10 coin: /gainers 📈\n"
        "En çok düşen 10 coin: /losers 📉"
    )

@bot.message_handler(commands=["price"])
def coin_price(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Kullanım: /price coinadı\nÖrnek: /price btc")
            return

        user_coin = parts[1].lower()
        coin_id = find_coin(user_coin)

        if not coin_id:
            bot.reply_to(message, f"⚠️ '{user_coin}' bulunamadı. İlk 500 coinden birini dene.")
            return

        price = get_coin_price(coin_id)
        if price:
            bot.reply_to(message, f"💰 {coin_id.upper()} Fiyatı: ${price}")
        else:
            bot.reply_to(message, f"⚠️ {coin_id.upper()} fiyatı alınamadı.")
    except Exception as e:
        bot.reply_to(message, f"Hata oluştu: {e}")

@bot.message_handler(commands=["top10"])
def top10_prices(message):
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1}
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        msg = "📊 İlk 10 Coin Fiyatı:\n\n"
        for coin in data:
            msg += f"#{coin['market_cap_rank']} {coin['name']} ({coin['symbol'].upper()}): ${coin['current_price']}\n"

        bot.reply_to(message, msg)
    except Exception as e:
        bot.reply_to(message, f"Hata oluştu: {e}")

@bot.message_handler(commands=["gainers"])
def top_gainers(message):
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 100, "page": 1}
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        sorted_data = sorted(data, key=lambda x: x["price_change_percentage_24h"] or 0, reverse=True)
        msg = "📈 Günün En Çok Yükselen 10 Coini:\n\n"
        for coin in sorted_data[:10]:
            msg += f"{coin['name']} ({coin['symbol'].upper()}): {coin['price_change_percentage_24h']:.2f}%\n"
        bot.reply_to(message, msg)
    except Exception as e:
        bot.reply_to(message, f"Hata oluştu: {e}")

@bot.message_handler(commands=["losers"])
def top_losers(message):
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 100, "page": 1}
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        sorted_data = sorted(data, key=lambda x: x["price_change_percentage_24h"] or 0)
        msg = "📉 Günün En Çok Düşen 10 Coini:\n\n"
        for coin in sorted_data[:10]:
            msg += f"{coin['name']} ({coin['symbol'].upper()}): {coin['price_change_percentage_24h']:.2f}%\n"
        bot.reply_to(message, msg)
    except Exception as e:
        bot.reply_to(message, f"Hata oluştu: {e}")

# =========================
# BOTU BAŞLAT
# =========================
print("Bot çalışıyor...")
load_coin_list()  # ilk 500 coini yükle
while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print("Hata:", e)
        time.sleep(15)
