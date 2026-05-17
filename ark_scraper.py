"""
=============================================================================
ARK 6.0: THE ULTIMATE QUANTITATIVE & MACRO PIPELINE (ABSOLUTE DEFENSE EDITION)
=============================================================================
Architectural Defenses:
1. Independent Blast Doors: Each macro ticker fails independently.
2. Cross-Validation Sandbox: 0.4% price tolerance fuse.
3. Length Check: Prevents moving average mathematical crashes.
4. Transmission Armor: 3x Retry mechanism implemented for LINE API dispatch.
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
TARGET_STOCK = "2891.TW" # 鎖定標的：中信金

# --- 2. 軍規級容錯防禦模組 ---
def fetch_with_retry(func, retries=3, delay=3):
    """執行指數退避重試，慢速但絕對穩健"""
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            if attempt == retries - 1:
                return f"⚠️ [系統防禦] 節點重試失敗"
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
                data = yf.download(ticker, period="1d", auto_adjust=False, progress=False)
                if not data.empty:
                    close_price = float(data['Close'].iloc[-1])
                    report.append(f"🔹 {name}: {close_price:.2f}")
                else:
                    report.append(f"⚠️ {name}: [無報價/休市]")
            except Exception:
                report.append(f"⚠️ {name}: [資料源異常]")
        return "\n".join(report)
    return fetch_with_retry(_fetch)

# --- 4. 主力情緒新聞雷達 ---
def get_news():
    def _fetch():
        url = "https://news.google.com/rss/search?q=中信金+OR+金融股+OR+外資+OR+聯準會&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        feed = feedparser.parse(url)
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

# --- 5. 終極沙盒：交叉比對與微觀武器 ---
def run_sandbox_ta():
    report = "📊 【中信金 網格量化沙盒】\n"
    try:
        data = yf.Ticker(TARGET_STOCK).history(period="100d", auto_adjust=False)
        
        # 防呆檢查：資料不足 60 天絕對不硬算
        if data.empty or len(data) < 60:
            raise ValueError("歷史資料受損或不足，保護機制啟動")

        close_price = data['Close'].iloc[-1]
        
        # Alpha Vantage 交叉驗證保險絲 (容錯 0.4%)
        if AV_API_KEY and AV_API_KEY != "None":
            try:
                av_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={TARGET_STOCK}&apikey={AV_API_KEY}"
                av_data = requests.get(av_url, timeout=10).json()
                if "Global Quote" in av_data and "05. price" in av_data["Global Quote"]:
                    av_price = float(av_data["Global Quote"]["05. price"])
                    diff = abs(close_price - av_price) / close_price
                    if diff > 0.004:
                        raise ValueError(f"驗證熔斷 (Yahoo:{close_price}, AV:{av_price})")
            except ValueError as ve:
                raise ve # 價格衝突，強制熔斷
            except Exception:
                pass # 若 AV 斷線，信任 Yahoo 繼續運算

        report += f"🎯 基準收盤價: {close_price:.2f}\n"

        # Pivot Points (S1/S2)
        high = data['High'].iloc[-2]
        low = data['Low'].iloc[-2]
        close_prev = data['Close'].iloc[-2]
        pivot = (high + low + close_prev) / 3
        s1 = (pivot * 2) - high
        s2 = pivot - (high - low)
        report += f"🛡️ S1伏擊區: {s1:.2f} | 💀 S2極限: {s2:.2f}\n"

        # ATR, Z-Score, Bias 60MA
        data.ta.atr(length=14, append=True)
        data.ta.zscore(length=20, append=True)
        data.ta.sma(length=60, append=True)
        atr = float(data['ATRr_14'].iloc[-1])
        zscore = float(data['Z_20'].iloc[-1])
        bias_60 = ((close_price - float(data['SMA_60'].iloc[-1])) / float(data['SMA_60'].iloc[-1])) * 100
        report += f"⚡ 波幅(ATR): {atr:.2f} | 📏 乖離(Z): {zscore:.2f}\n"
        report += f"🌊 季線安全氣囊: {bias_60:.1f}%\n"

        # RSI, MFI, Williams %R
        data.ta.rsi(length=14, append=True)
        data.ta.mfi(length=14, append=True)
        data.ta.willr(append=True)
        rsi = float(data['RSI_14'].iloc[-1])
        mfi = float(data['MFI_14'].iloc[-1])
        willr = float(data['WILLR_14'].iloc[-1])
        report += f"📉 RSI: {rsi:.1f} | 💰 MFI: {mfi:.1f}\n"
        report += f"🐍 威廉觸底指標: {willr:.0f}\n"

        # MACD, KD
        data.ta.macd(append=True)
        data.ta.stoch(append=True)
        macd_hist = float(data['MACDh_12_26_9'].iloc[-1])
        k = float(data['STOCHk_14_3_3'].iloc[-1])
        d = float(data['STOCHd_14_3_3'].iloc[-1])
        report += f"🌪️ MACD柱狀: {macd_hist:.3f}\n"
        report += f"🇹🇼 KD共識: K{k:.0f}/D{d:.0f}\n"

    except Exception as e:
        report += f"⚠️ 沙盒保險絲已熔斷 (資料交叉保護)\n原因: {e}\n(為求純淨，本日屏蔽技術面數據)\n"
    
    return report

# --- 6. 通訊兵重裝甲部屬 (LINE API 附帶重試機制) ---
def send_line_alert(message):
    if not LINE_TOKEN or not LINE_USER_ID:
        print("系統日誌: 未偵測到 LINE 金鑰，停止發送。")
        return
    
    # 執行字數安全截斷
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
    
    # 【防禦升級】通訊兵防彈衣：重試 3 次
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                print("系統日誌: 戰報成功抵達指揮所！")
                return
            else:
                print(f"系統日誌: 發送失敗 (HTTP {response.status_code})，準備重試...")
        except Exception as e:
            print(f"系統日誌: 網路瞬斷 ({e})，準備重試...")
        time.sleep(3)
    print("系統日誌: 3 次通訊皆失敗，放棄發送。")

# --- 7. 系統主引擎：智能日曆分流 ---
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
