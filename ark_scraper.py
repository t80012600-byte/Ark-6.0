"""
=============================================================================
ARK 7.2: THE ULTIMATE QUANTITATIVE & MACRO PIPELINE (WHALE SNIPER EDITION)
=============================================================================
Architectural Note for Future Maintainers / AI Agents:
1. Exponential Backoff: Bypasses API rate limits.
2. Smart Calendar Routing: 
   - Morning (05:00-11:59): Full Macro + 13 Quant Weapons + News.
   - Night (12:00-04:59): Full Macro + News (Pre-US Market/Night Check).
   - Weekend Quiet: Sat afternoon & Sunday, News ONLY.
3. Sandbox Fuse: TA is isolated. Drops NaN data to prevent Z-Score crashing.
4. Objective Macro (v7.2 Upgrade): 
   - Displays Open/Close and Body%. 
   - Integrates Gap Analysis (Open vs Prev Close) to detect Fake Breakouts (⚠️).
   - [HOTFIX] Replaced yf.download with yf.Ticker().history to prevent 'Series' float casting error caused by yfinance MultiIndex updates.
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
TZ_TW = pytz.timezone('Asia/Taipei')
TARGET_STOCK = "2891.TW" # 鎖定標的：中信金

# --- 2. 軍規級容錯防禦模組 (Exponential Backoff) ---
def fetch_with_retry(func, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            if attempt == retries - 1:
                return f"[資料異常] {str(e)}"
            time.sleep(delay * (2 ** attempt))

# --- 3. 擴充版：全球總經與外資透視雷達 (v7.2 主力意圖解碼 + 防閃退版) ---
def get_macro_data():
    """抓取美股、美債等數據，並結合跳空缺口與K線實體抓出主力意圖"""
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
            # [HOTFIX] 改用 Ticker().history() 避開 yfinance 回傳 MultiIndex Series 的 Bug
            try:
                data = yf.Ticker(ticker).history(period="5d", auto_adjust=False)
                data = data.dropna()
                
                if len(data) >= 2:
                    # 強制轉為純量 float，避免資料結構異常
                    prev_close = float(data['Close'].iloc[-2]) 
                    open_price = float(data['Open'].iloc[-1])  
                    close_price = float(data['Close'].iloc[-1]) 
                    
                    # 計算 K 線實體大小 (收盤-開盤的幅度)
                    if open_price != 0:
                        body_pct = ((close_price - open_price) / open_price) * 100
                    else:
                        body_pct = 0
                    
                    # 終極主力意圖判定邏輯
                    if open_price > prev_close and body_pct < -0.5:
                        icon = "⚠️高檔倒貨(誘多)" 
                    elif open_price < prev_close and body_pct > 0.5:
                        icon = "🟢低檔承接(洗盤)" 
                    elif body_pct > 0.5:
                        icon = "📈" 
                    elif body_pct < -0.5:
                        icon = "📉" 
                    else:
                        icon = "➖" 
                        
                    report.append(f"🔹 {name}: 收 {close_price:.2f} (開 {open_price:.2f} | 實體 {body_pct:+.2f}%) {icon}")
                elif len(data) == 1:
                    close_price = float(data['Close'].iloc[-1])
                    report.append(f"🔹 {name}: 收 {close_price:.2f} (數據不足無法比對)")
                else:
                    report.append(f"⚠️ {name}: [無報價/休市]")
            except Exception as e:
                report.append(f"⚠️ {name}: [資料解析失敗]")
                
        return "\n".join(report)
    return fetch_with_retry(_fetch)

# --- 4. 中信金專屬：主力情緒新聞雷達 ---
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
        return "\n".join(news_list)
    return fetch_with_retry(_fetch)

# --- 5. 終極沙盒：中信金 13 項微觀量化武器 (防彈裝甲版) ---
def run_sandbox_ta():
    report = "📊 【中信金 網格量化沙盒】\n"
    try:
        data = yf.Ticker(TARGET_STOCK).history(period="100d", auto_adjust=False)
        if data.empty:
            raise ValueError("歷史資料回傳空白")
            
        # [防禦機制] 清除 Yahoo 週末與異常空值 (防止 Z-Score 當機)
        data = data.dropna()

        close_price = data['Close'].iloc[-1]
        report += f"🎯 基準收盤價: {close_price:.2f}\n"

        # Pivot Points
        high = data['High'].iloc[-2]
        low = data['Low'].iloc[-2]
        close_prev = data['Close'].iloc[-2]
        pivot = (high + low + close_prev) / 3
        s1 = (pivot * 2) - high
        s2 = pivot - (high - low)
        report += f"🛡️ S1伏擊區: {s1:.2f} | 💀 S2極限: {s2:.2f}\n"

        # ATR & 季線 Bias
        data.ta.atr(length=14, append=True)
        data.ta.sma(length=60, append=True)
        atr = data['ATRr_14'].iloc[-1]
        bias_60 = ((close_price - data['SMA_60'].iloc[-1]) / data['SMA_60'].iloc[-1]) * 100
        
        # [軍規級 Z-Score 手工計算]
        mean_20 = data['Close'].rolling(window=20).mean().iloc[-1]
        std_20 = data['Close'].rolling(window=20).std().iloc[-1]
        zscore = (close_price - mean_20) / std_20 if std_20 != 0 else 0
        
        report += f"⚡ 波幅(ATR): {atr:.2f} | 📏 乖離(Z): {zscore:.2f}\n"
        report += f"🌊 季線安全氣囊: {bias_60:.1f}%\n"

        # RSI, MFI, Williams
        data.ta.rsi(length=14, append=True)
        data.ta.mfi(length=14, append=True)
        data.ta.willr(append=True)
        rsi = data['RSI_14'].iloc[-1]
        mfi = data['MFI_14'].iloc[-1]
        willr = data['WILLR_14'].iloc[-1]
        report += f"📉 RSI: {rsi:.1f} | 💰 MFI(籌碼): {mfi:.1f}\n"
        report += f"🐍 威廉觸底指標: {willr:.0f}\n"

        # MACD, KD
        data.ta.macd(append=True)
        data.ta.stoch(append=True)
        macd_hist = data['MACDh_12_26_9'].iloc[-1]
        k = data['STOCHk_14_3_3'].iloc[-1]
        d = data['STOCHd_14_3_3'].iloc[-1]
        report += f"🌪️ MACD柱狀: {macd_hist:.3f}\n"
        report += f"🇹🇼 KD共識: K{k:.0f}/D{d:.0f}\n"

    except Exception as e:
        report += f"⚠️ 沙盒保險絲已熔斷 (底層保護)\n原因: {e}\n(為求純淨，本日屏蔽技術面數據)\n"
    
    return report

# --- 6. 通訊兵部屬 (LINE Push API) ---
def send_line_alert(message):
    if not LINE_TOKEN or not LINE_USER_ID:
        print("未偵測到 LINE 金鑰。")
        return
    
    # [v7.1 修復] 放寬字數限制至 4000，防止新聞與宏觀數據被截斷
    safe_message = message[:4000] + "\n...(情報過大，啟動安全截斷)" if len(message) > 4000 else message
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

# --- 7. 系統主引擎：智能日曆分流 ---
if __name__ == "__main__":
    now_tw = datetime.now(TZ_TW)
    weekday = now_tw.weekday()
    hour = now_tw.hour

    header = f"🚀 【方舟 7.2 死神母艦】\n時間: {now_tw.strftime('%m-%d %H:%M')}\n" + "-"*20 + "\n"
    final_report = header

    # 嚴格定義時間區間：清晨 5 點到中午 12 點才算早晨
    is_morning = 5 <= hour < 12 
    is_weekend_quiet = (weekday == 5 and hour >= 12) or (weekday == 6)

    if is_weekend_quiet:
        final_report += "🌙 [週末情報監聽模式]\n(市場休市，微觀雷達關閉)\n\n"
        final_report += get_news()
    else:
        if is_morning:
            final_report += "☀️ [晨間刺刀肉搏模式]\n\n"
            final_report += run_sandbox_ta() + "\n"
            final_report += "🌍 [全球總經與外資雷達]\n"
            final_report += get_macro_data() + "\n"
            final_report += get_news()
        else:
            final_report += "🌙 [夜間宏觀預警模式]\n\n"
            final_report += "🌍 [全球總經與外資雷達]\n"
            final_report += get_macro_data() + "\n"
            final_report += get_news()

    send_line_alert(final_report)
    print("方舟 7.2 任務完成，安全撤退。")
