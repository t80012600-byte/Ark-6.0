"""
=============================================================================
ARK 6.0: THE ULTIMATE QUANTITATIVE & MACRO PIPELINE (IMMORTAL TURTLE EDITION)
=============================================================================
Deep Audited Defenses:
1. XML Timeout Shield: Feedparser is wrapped in requests.get() to prevent hanging.
2. Dynamic Column Binding: Immune to pandas_ta future version column naming changes.
3. NaN Filtration: Protects float formatting and math operations from None/NaN crashes.
4. Independent Blast Doors & 0.4% Tolerance Sandbox implemented.
=============================================================================
"""

import os
import time
import requests
import feedparser
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime
import pytz

# --- 1. 基礎設施與金鑰掛載 ---
LINE_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")
AV_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY") 
TZ_TW = pytz.timezone('Asia/Taipei')
TARGET_STOCK = "2891.TW"

# --- 2. 軍規級容錯防禦模組 ---
def fetch_with_retry(func, retries=3, delay=3):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            if attempt == retries - 1:
                return f"⚠️ [系統防禦] 節點連線逾時或受阻"
            time.sleep(delay * (2 ** attempt))

# --- 3. 獨立防爆門：全球總經雷達 ---
def get_macro_data():
    def _fetch():
        tickers = {
            "VIX (恐慌指數)": "^VIX",
            "US10Y (美債10年)": "^TNX",
            "TLT (20年美債價格)": "TLT",
            "USD/TWD (台幣匯率)": "TWD=X",
            "CL=F (原油通膨)": "CL=F",
            "HYG (高收益垃圾債)": "HYG",
            "TSM (台積電夜盤)": "TSM",
            "EWT (外資台灣ETF)": "EWT",
            "EEM (外資新興ETF)": "EEM",
            "XLF (美國金融ETF)": "XLF",
            "Nasdaq (科技板塊)": "^IXIC"
        }
        report = []
        for name, ticker in tickers.items():
            try:
                # 抓取 5 天確保能避開單日休市造成的空表
                data = yf.Ticker(ticker).history(period="5d", auto_adjust=False)
                if not data.empty:
                    # 濾除 NaN 幽靈數據
                    data = data.dropna(subset=['Close'])
                    if not data.empty:
                        close_price = float(data['Close'].iloc[-1])
                        report.append(f"🔹 {name}: {close_price:.2f}")
                    else:
                        report.append(f"⚠️ {name}: [無有效報價]")
                else:
                    report.append(f"⚠️ {name}: [無報價/休市]")
            except Exception:
                report.append(f"⚠️ {name}: [資料庫異常]")
        return "\n".join(report)
    return fetch_with_retry(_fetch)

# --- 4. 主力情緒新聞雷達 (防掛死封裝) ---
def get_news():
    def _fetch():
        url = "https://news.google.com/rss/search?q=中信金+OR+金融股+OR+外資+OR+聯準會&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        # 絕對防禦：不讓 feedparser 自己連線，由 requests 強制 10 秒超時控管
        res = requests.get(url, timeout=10)
        feed = feedparser.parse(res.content)
        
        news_list = []
        for i, entry in enumerate(feed.entries[:5]):
            title = entry.title
            if len(title) > 32:
                title = title[:32] + "..."
            news_list.append(f"📰 {title}")
        if not news_list:
            return "📰 目前無重大相關新聞。"
        return "\n".join(news_list)
    return fetch_with_retry(_fetch)

# --- 工具函數：動態萃取指標 (免疫套件改版) ---
def get_ta_val(df, prefix):
    cols = [c for c in df.columns if c.startswith(prefix)]
    if not cols:
        raise ValueError(f"無法產生指標: {prefix}")
    val = df[cols[0]].iloc[-1]
    if pd.isna(val):
        raise ValueError(f"指標 {prefix} 產生無效空值")
    return float(val)

# --- 5. 終極沙盒：交叉比對與微觀武器 ---
def run_sandbox_ta():
    report = "📊 【中信金 網格量化沙盒】\n"
    try:
        data = yf.Ticker(TARGET_STOCK).history(period="100d", auto_adjust=False)
        
        if data.empty or len(data) < 65:
            raise ValueError("歷史資料不足 65 天，強制保護")

        # 清理可能含有 NaN 的收盤價，確保基準價純淨
        data = data.dropna(subset=['Close', 'High', 'Low'])
        close_price = float(data['Close'].iloc[-1])
        
        # Alpha Vantage 交叉驗證
        if AV_API_KEY and AV_API_KEY != "None":
            try:
                av_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={TARGET_STOCK}&apikey={AV_API_KEY}"
                av_data = requests.get(av_url, timeout=10).json()
                if "Global Quote" in av_data and "05. price" in av_data["Global Quote"]:
                    av_price = float(av_data["Global Quote"]["05. price"])
                    diff = abs(close_price - av_price) / close_price
                    if diff > 0.004:
                        raise ValueError(f"數據分歧過大熔斷 (Yahoo:{close_price}, AV:{av_price})")
            except ValueError as ve:
                raise ve 
            except Exception:
                pass 

        report += f"🎯 基準收盤價: {close_price:.2f}\n"

        # Pivot Points
        high = float(data['High'].iloc[-2])
        low = float(data['Low'].iloc[-2])
        close_prev = float(data['Close'].iloc[-2])
        pivot = (high + low + close_prev) / 3
        s1 = (pivot * 2) - high
        s2 = pivot - (high - low)
        report += f"🛡️ S1伏擊區: {s1:.2f} | 💀 S2極限: {s2:.2f}\n"

        # 執行技術指標運算
        data.ta.atr(length=14, append=True)
        data.ta.zscore(length=20, append=True)
        data.ta.sma(length=60, append=True)
        data.ta.rsi(length=14, append=True)
        data.ta.mfi(length=14, append=True)
        data.ta.willr(append=True)
        data.ta.macd(append=True)
        data.ta.stoch(append=True)

        # 動態安全萃取數值
        atr = get_ta_val(data, 'ATRr')
        zscore = get_ta_val(data, 'Z_')
        sma60 = get_ta_val(data, 'SMA_60')
        rsi = get_ta_val(data, 'RSI_')
        mfi = get_ta_val(data, 'MFI_')
        willr = get_ta_val(data, 'WILLR_')
        macd_hist = get_ta_val(data, 'MACDh')
        k = get_ta_val(data, 'STOCHk')
        d = get_ta_val(data, 'STOCHd')

        bias_60 = ((close_price - sma60) / sma60) * 100

        report += f"⚡ 波幅(ATR): {atr:.2f} | 📏 乖離(Z): {zscore:.2f}\n"
        report += f"🌊 季線安全氣囊: {bias_60:.1f}%\n"
        report += f"📉 RSI: {rsi:.1f} | 💰 MFI: {mfi:.1f}\n"
        report += f"🐍 威廉觸底指標: {willr:.0f}\n"
        report += f"🌪️ MACD柱狀: {macd_hist:.3f}\n"
        report += f"🇹🇼 KD共識: K{k:.0f}/D{d:.0f}\n"

    except Exception as e:
        report += f"⚠️ 沙盒保險絲已熔斷 (底層保護)\n原因: {e}\n(為求純淨，本日屏蔽技術面數據)\n"
    
    return report

# --- 6. 通訊兵重裝甲部屬 ---
def send_line_alert(message):
    if not LINE_TOKEN or not LINE_USER_ID:
        print("未偵測到 LINE 金鑰。")
        return
    
    safe_message = message[:900] + "\n...(情報過大，啟動安全截斷)" if len(message) > 900 else message

    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_TOKEN}'
    }
    payload = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": safe_message}]
    }
    
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                print("戰報發送成功！")
                return
        except Exception:
            pass
        time.sleep(3)
    print("通訊徹底失敗。")

# --- 7. 主引擎 ---
if __name__ == "__main__":
    now_tw = datetime.now(TZ_TW)
    weekday = now_tw.weekday()
    hour = now_tw.hour

    header = f"🚀 【方舟 6.0 死神母艦】\n時間: {now_tw.strftime('%m-%d %H:%M')}\n" + "-"*20 + "\n"
    final_report = header

    is_weekend_quiet = (weekday == 5 and hour > 12) or (weekday == 6)
    is_morning = hour < 12

    if is_weekend_quiet:
        final_report += "🌙 [週末情報監聽模式]\n(市場休市，微觀雷達關閉)\n"
        final_report += get_news()
    else:
        if is_morning:
            final_report += "☀️ [晨間刺刀肉搏模式]\n\n"
            final_report += run_sandbox_ta() + "\n"
            final_report += "🌍 [全球總經與外資雷達]\n"
            final_report += get_macro_data() + "\n\n"
            final_report += get_news()
        else:
            final_report += "🌙 [美股夜間預警模式]\n\n"
            final_report += "🌍 [全球總經與外資雷達]\n"
            final_report += get_macro_data() + "\n\n"
            final_report += get_news()

    send_line_alert(final_report)
