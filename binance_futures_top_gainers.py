import requests
import os

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

def get_futures_tickers():
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
    response = requests.get(url)
    return response.json()

def format_symbol(symbol):
    return symbol.replace("USDT", "/USDT")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

def main():
    data = get_futures_tickers()
    data = [x for x in data if x["symbol"].endswith("USDT")]
    
    sorted_data = sorted(data, key=lambda x: float(x["priceChangePercent"]), reverse=True)
    top_gainers = sorted_data[:5]
    top_losers = sorted_data[-5:]

    def format_entry(entry):
        pct = float(entry["priceChangePercent"])
        mark = "🔥" if abs(pct) > 60 else ""
        return f"{format_symbol(entry['symbol'])}: `{pct:+.2f}%` {mark}"

    message = "*📈 币安合约涨跌榜（4H）*\n\n"
    message += "*🚀 涨幅前5:*\n"
    message += "\n".join([format_entry(e) for e in top_gainers]) + "\n\n"
    message += "*💥 跌幅前5:*\n"
    message += "\n".join([format_entry(e) for e in top_losers])

    send_telegram_message(message)

if __name__ == "__main__":
    main()
