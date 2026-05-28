import os
import smtplib
from email.mime.text import MIMEText
from data.download import load_local_data

def detect_volatility_anomaly(ticker, sigma_threshold=2.0):
    """特定の銘柄が、直近で過去のボラティリティから見て異常な動きをしたか検知する関数"""
    
    local_data = load_local_data(ticker)
    df = local_data["history"] # ローカルデータからヒストリカルデータを取得
    
    df = df.sort_index() # 日付の重複排除やソートを念のため実行
    
    df['Return'] = df['Close'].pct_change() # 「前日比（リターン）」の列を作る
    
    # 3. 過去90日間の「移動平均」と「移動標準偏差（σ）」をローリング計算
    # 💡 rolling(90) で直近90日間をスライドさせながら統計値を算出します
    window_size = 90
    df['Rolling_Mean'] = df['Return'].rolling(window=window_size).mean()
    df['Rolling_Std'] = df['Return'].rolling(window=window_size).std()
    
    # 4. 異常値の境界線（上限・下限）を計算
    # 💡 平均値 ± (設定したシグマ倍 * 標準偏差)
    df['Upper_Bound'] = df['Rolling_Mean'] + (sigma_threshold * df['Rolling_Std'])
    df['Lower_Bound'] = df['Rolling_Mean'] - (sigma_threshold * df['Rolling_Std'])
    
    # 5. ─── 🚨 最新日のデータをピンポイントでチェック 🚨 ───
    latest_row = df.iloc[-1]
    latest_date = df.index[-1]
    latest_return = latest_row['Return']
    upper = latest_row['Upper_Bound']
    lower = latest_row['Lower_Bound']
    
    # 判定ロジック
    is_anomaly = False
    status = "正常"
    
    if latest_return > upper:
        is_anomaly = True
        status = "🚨 異常急騰（ボラティリティ上抜け）"
    elif latest_return < lower:
        is_anomaly = True
        status = "🚨 異常急落（ボラティリティ下抜け）"
        
    return {
        "ticker": ticker,
        "date": latest_date.strftime('%Y-%m-%d'),
        "is_anomaly": is_anomaly,
        "status": status,
        "return_pct": f"{latest_return * 100:.2f}%",
        "sigma_range": f"[{lower*100:.2f}% 〜 {upper*100:.2f}%]"
    }


def send_email_notification(message_text):
    """PythonからあなたのiPhoneメールへアラートを送信する関数"""
    # ─── ⚙️ 設定部分 ───
    sender_email = os.environ.get("GMAIN_MAIL_ADDRESS")
    sender_password = os.environ.get("GMAIL_APP_PASSWORD")
    receiver_email = os.environ.get("ICLOUD_MAIL_ADDRESS")
    
    # メッセージの組み立て
    msg = MIMEText(message_text, "plain", "utf-8")
    msg["Subject"] = "🚨 市場急変アラート(自動検知)"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    
    try:
        # Gmailのサーバー経由で安全に送信
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("📨 iPhone宛てに通知メールを送信しました！")
    except Exception as e:
        print(f"メール送信エラー: {e}")

def run_morning_research(portfolio_tickers):
    """毎朝実行されるリサーチのメイン処理"""
    print("⏰ 朝の定期リサーチを開始します...")
    
    anomalies_found = []
    
    # 1. 保有・監視銘柄をすべてスキャン
    for ticker in portfolio_tickers:
        try:
            # 2シグマの枠で異常チェック
            result = detect_volatility_anomaly(ticker, sigma_threshold=2.0)
            
            if result['is_anomaly']:
                anomalies_found.append(result)
                
        except Exception as e:
            print(f"【{ticker}】スキャンエラー: {e}")
            
    # 2. 🚨 異常が見つかった場合のみ、メッセージを組み立ててiPhoneに通知！
    if anomalies_found:
        notification_body = "🚨 【市場急変アラート】ボラティリティ異常検知！\n"
        notification_body += "昨晩の米国市場（または直近営業日）で限界突破の動きをした銘柄があります。\n\n"
        
        for item in anomalies_found:
            notification_body += f"• *{item['ticker']}* ({item['date']})\n"
            notification_body += f"  状況: {item['status']}\n"
            notification_body += f"  値動き: *{item['return_pct']}* (普段の許容枠: {item['sigma_range']})\n"
            notification_body += f"  👉 `Page 4` を開いて公式IR（10-Q）やCopilot要約をチェックしてください。\n"
            notification_body += "-" * 30 + "\n"
            
        print("💡 異常を検知したため、通知を送ります。")
        send_email_notification(notification_body)
    else:
        print("✅ 全銘柄、普段のボラティリティの範囲内（正常）でした。通知はスキップします。")

# 🧪 テスト実行
if __name__ == "__main__":
    # あなたの監視リスト
    my_portfolio = ["VOO", "NVDA", "AMD", "GOOG"]
    
    # テストとして、2シグマの閾値で引っかかるか実行してみる
    run_morning_research(my_portfolio)