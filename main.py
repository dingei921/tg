import os
import requests
from datetime import datetime

def send_to_telegram(message):
    bot_token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    if not bot_token or not chat_id:
        print("❗ Telegram 环境变量未设置")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print("📨 消息已发送至 Telegram")
        else:
            print("⚠️ Telegram 推送失败:", r.text)
    except Exception as e:
        print("❌ Telegram 推送异常:", str(e))

def get_contract_gainers_and_losers():
    url = 'https://fapi.binance.com/fapi/v1/ticker/24hr'

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        usdt_pairs = [item for item in data if item['symbol'].endswith('USDT')]
        for item in usdt_pairs:
            item['priceChangePercent'] = float(item['priceChangePercent'])

        top_gainers = sorted(usdt_pairs, key=lambda x: x['priceChangePercent'], reverse=True)[:5]
        top_losers = sorted(usdt_pairs, key=lambda x: x['priceChangePercent'])[:5]

        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')

        telegram_msg = f"*📊 Binance 合约涨跌榜（每4小时更新）*\n🕒 {now}\n\n"
        telegram_msg += "*📈 涨幅前五:*\n"
        for item in top_gainers:
            symbol = item['symbol']
            percent = item['priceChangePercent']
            if percent > 100:
                line = f"- {symbol}: *+{percent:.2f}%* 🔥🚀🚀"
            elif percent > 60:
                line = f"- {symbol}: +{percent:.2f}% 🚀"
            else:
                line = f"- {symbol}: +{percent:.2f}%"
            telegram_msg += line + "\n"

        telegram_msg += "\n*📉 跌幅前五:*\n"
        for item in top_losers:
            symbol = item['symbol']
            percent = item['priceChangePercent']
            if percent < -100:
                line = f"- {symbol}: *{percent:.2f}%* 💥🔥"
            elif percent < -60:
                line = f"- {symbol}: {percent:.2f}% 💥"
            else:
                line = f"- {symbol}: {percent:.2f}%"
            telegram_msg += line + "\n"

        # 写入 README（本地更新，不提交）
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(telegram_msg.replace("*", ""))

        # 发送 Telegram
        send_to_telegram(telegram_msg)

    except Exception as e:
        print("❌ 获取币安数据失败:", str(e))

if __name__ == "__main__":
    get_contract_gainers_and_losers()
