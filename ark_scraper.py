"""
=============================================================================
ARK 6.0: THE ULTIMATE QUANTITATIVE & MACRO PIPELINE (DEATH STAR EDITION)
=============================================================================
Architectural Note for Future Maintainers / AI Agents:
1. Exponential Backoff: Bypasses API rate limits.
2. Smart Calendar Routing: 
   - Morning (07:30): Full Macro + 13 Quant Weapons + News.
   - Night (22:00): Full Macro + News (Pre-US Market).
   - Weekend (Sat Night / Sun): News ONLY (Radar Silence for static markets).
3. Sandbox Fuse: Technical analysis is isolated. If data is polluted, the fuse 
   blows, shielding the main macro report.
4. Payload Truncation: Complies with LINE Push 1000-char limits.
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
AV_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY") # 沙盒擴充備用金鑰
TZ_TW = pytz.timezone('Asia/Taipei')
TARGET_STOCK = "2891.TW" # 鎖定標的：中信金

# --- 2. 軍規級容錯防禦模組 (Exponential Backoff) ---
def fetch_with_retry(func, retries=3, delay=2):
    """執行指數退避重試，防止網路瞬斷"""
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            if attempt == retries - 1:
                return f"[資料異常] {str(e)}"
            time.sleep(delay * (2 ** attempt))

# --- 3. 擴充版：全球總經與外資透視雷達 ---
def get_macro_data():
    """抓取美股、美債、VIX、匯率及外資ETF，強制鎖死還原權值陷阱"""
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
            data = yf.download(ticker, period="1d", auto_adjust=False, progress=False)
            if not data.empty:
                close_price = float(data['Close'].iloc[-1])
                report.append(f"🔹 {name}: {close_price:.2f}")
            else:
                report.append(f"⚠️ {name}: [無報價/休市]")
        return "\n".join(report)
    return fetch_with_retry(_fetch)

# --- 4. 中信金專屬：主力情緒新聞雷達 ---
def get_news():
    """抓取中信金專屬新聞，並執行字數截斷防禦"""
    def _fetch():
        # 鎖定中信金與金融大局關鍵字
        url = "https://news.google.com/rss/search?q=中信金+OR+金融股+OR+外資+OR+聯準會&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        feed = feedparser.parse(url)
        news_list = []
        for i, entry in enumerate(feed.entries[:5]):
            title = entry.title
            if len(title) > 32:
                title = title[:32] + "..."
            news_list.append(f"📰 {title}")
        return "\n".join(news_list)
    return fetch_with_retry(_fetch)

# --- 5. 終極沙盒：中信金 13 項微觀量化武器 ---
def run_sandbox_ta():
    """隔離沙盒運算區：若資料庫污染或誤差過大，保險絲自動熔斷"""
    report = "📊 【中信金 網格量化沙盒】\n"
    try:
        # 抓取 100 天歷史資料，確保平滑指標(MACD/季線)準確
        data = yf.Ticker(TARGET_STOCK).history(period="100d", auto_adjust=False)
        if data.empty:
            raise ValueError("Yahoo API 歷史資料回傳空白")

        close_price = data['Close'].iloc[-1]
        report += f"🎯 基準收盤價: {close_price:.2f}\n"

        # [空間防禦] Pivot Points (S1/S2)
        high = data['High'].iloc[-2]
        low = data['Low'].iloc[-2]
        close_prev = data['Close'].iloc[-2]
        pivot = (high + low + close_prev) / 3
        s1 = (pivot * 2) - high
        s2 = pivot - (high - low)
        report += f"🛡️ S1伏擊區: {s1:.2f} | 💀 S2極限: {s2:.2f}\n"

        # [波動與極限] ATR, Z-Score, Bias 60MA
        data.ta.atr(length=14, append=True)
        data.ta.zscore(length=20, append=True)
        data.ta.sma(length=60, append=True)
        atr = data['ATRr_14'].iloc[-1]
        zscore = data['Z_20'].iloc[-1]
        bias_60 = ((close_price - data['SMA_60'].iloc[-1]) / data['SMA_60'].iloc[-1]) * 100
        report += f"⚡ 波幅(ATR): {atr:.2f} | 📏 乖離(Z): {zscore:.2f}\n"
        report += f"🌊 季線安全氣囊: {bias_60:.1f}%\n"

        # [左側情緒] RSI, MFI, Williams %R
        data.ta.rsi(length=14, append=True)
        data.ta.mfi(length=14, append=True)
        data.ta.willr(append=True)
        rsi = data['RSI_14'].iloc[-1]
        mfi = data['MFI_14'].iloc[-1]
        willr = data['WILLR_14'].iloc[-1]
        report += f"📉 RSI: {rsi:.1f} | 💰 MFI(籌碼): {mfi:.1f}\n"
        report += f"🐍 威廉觸底指標: {willr:.0f}\n"

        # [動能與共識] MACD, KD
        data.ta.macd(append=True)
        data.ta.stoch(append=True)
        macd_hist = data['MACDh_12_26_9'].iloc[-1]
        k = data['STOCHk_14_3_3'].iloc[-1]
        d = data['STOCHd_14_3_3'].iloc[-1]
        report += f"🌪️ MACD柱狀: {macd_hist:.3f}\n"
        report += f"🇹🇼 KD共識: K{k:.0f}/D{d:.0f}\n"

    except Exception as e:
        # 保險絲熔斷機制
        report += f"⚠️ 沙盒保險絲已熔斷 (容錯保護啟動)\n原因: {e}\n(請總司令直接查看券商APP獲取微觀數據)\n"
    
    return report

# --- 6. 通訊兵部屬 (LINE Push API) ---
def send_line_alert(message):
    """保留您的 Push API 專線，並執行 1000 字元截斷防禦"""
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
    requests.post(url, headers=headers, json=payload)

# --- 7. 系統主引擎：智能日曆分流 (Smart Routing) ---
if __name__ == "__main__":
    now_tw = datetime.now(TZ_TW)
    weekday = now_tw.weekday()
    hour = now_tw.hour

    header = f"🚀 【方舟 6.0 死神母艦】\n時間: {now_tw.strftime('%m-%d %H:%M')}\n" + "-"*20 + "\n"
    final_report = header

    # 狀態判斷
    is_weekend_quiet = (weekday == 5 and hour > 12) or (weekday == 6) # 週六過午與週日全天
    is_morning = hour < 12

    if is_weekend_quiet:
        # 【週末休眠模式】：關閉算力，只報新聞
        final_report += "🌙 [週末情報監聽模式]\n(市場休市，微觀雷達關閉)\n"
        final_report += get_news()
    else:
        if is_morning:
            # 【晨間全武裝模式】 (包含週六早上：結算美股週五戰果)
            final_report += "☀️ [晨間刺刀肉搏模式]\n\n"
            final_report += run_sandbox_ta() + "\n"
            final_report += "🌍 [全球總經與外資雷達]\n"
            final_report += get_macro_data() + "\n"
            final_report += get_news()
        else:
            # 【夜間宏觀模式】 (週一至週五晚上)
            final_report += "🌙 [美股夜間預警模式]\n\n"
            final_report += "🌍 [全球總經與外資雷達]\n"
            final_report += get_macro_data() + "\n"
            final_report += get_news()

    # 發射戰報
    send_line_alert(final_report)
    print("方舟 6.0 任務完成，安全撤退。")
