import requests
import os

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

def get_futures_tickers():
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return []
    except ValueError as e:
        print(f"JSON 解析错误: {e}")
        return []

def send_telegram_message(message):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("错误：未设置 TG_BOT_TOKEN 或 TG_CHAT_ID 环境变量")
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, data=payload)
        if res.status_code != 200:
            print(f"Telegram 发送失败: {res.text}")
    except Exception as e:
        print(f"发送 Telegram 消息出错: {e}")

def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0

def format_symbol(symbol):
    return symbol.replace("USDT", "/USDT")

def main():
    data = get_futures_tickers()

    if not isinstance(data, list):
        print("API 返回非预期结构: ", data)
        return

    print(f"返回总记录数: {len(data)}")
    print("示例数据:", data[:1])

    # 宽松过滤含有 USDT 的合约
    filtered_data = [
        x for x in data
        if isinstance(x, dict)
        and "USDT" in x.get("symbol", "")
        and x.get("priceChangePercent") is not None
    ]

    print(f"USDT 合约数: {len(filtered_data)}")

    sorted_data = sorted(
        filtered_data,
        key=lambda x: safe_float(x.get("priceChangePercent")),
        reverse=True
    )

    top_gainers = sorted_data[:5]
    top_losers = sorted_data[-5:]

    def format_entry(entry):
        pct = safe_float(entry.get("priceChangePercent"))
        mark = "🔥" if abs(pct) >= 60 else ""
        symbol = format_symbol(entry["symbol"])
        return f"{symbol}: `{pct:+.2f}%` {mark}"

    message = "*📈 币安合约涨跌榜（最近24小时）*\n\n"

    message += "*🚀 涨幅前5:*\n"
    if top_gainers:
        message += "\n".join([format_entry(e) for e in top_gainers])
    else:
        message += "_无数据_"

    message += "\n\n*💥 跌幅前5:*\n"
    if top_losers:
        message += "\n".join([format_entry(e) for e in top_losers])
    else:
        message += "_无数据_"

    print("准备发送消息:\n", message)
    send_telegram_message(message)

if __name__ == "__main__":
    main()
