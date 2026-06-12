import pandas as pd
import get_financial_data

def calculate_zscore(symbol):
    """
    计算修正版 Altman Z-Score
    Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5
    """
    z_data = get_financial_data.get_zscore_data(symbol)
    if not z_data or z_data.get("总资产", 0) == 0:
        return None
    
    TA = z_data["总资产"]
    X1 = (z_data["流动资产"] - z_data["流动负债"]) / TA
    X2 = z_data["未分配利润"] / TA
    X3 = (z_data["利润总额"] + z_data["财务费用"]) / TA
    X4 = z_data["归母所有者权益"] / z_data["总负债"] if z_data["总负债"] != 0 else 0
    X5 = z_data["营业总收入"] / TA
    
    z_score = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 0.999 * X5
    
    if z_score > 2.9:
        status = "Safe (财务稳健)"
        color = "green"
    elif 1.8 <= z_score <= 2.9:
        status = "Grey (灰色预警)"
        color = "orange"
    else:
        status = "Distress (破产高危)"
        color = "red"
        
    return {
        "score": round(z_score, 2),
        "status": status,
        "color": color,
        "report_date": z_data["报告日"]
    }

def detect_financial_anomalies(df):
    """
    对核心财务指标 DataFrame 进行异常检测，
    对比最近两年数据的变化率。如果某些核心指标同比下滑超过 30%，则触发预警。
    """
    if df is None or df.empty or len(df) < 2:
        return []

    try:
        latest_year = df.iloc[0]
        prev_year = df.iloc[1]
    except Exception as e:
        return []

    anomalies = []
    key_metrics = ['净利润', '毛利率', '净资产收益率', '营业总收入', '基本每股收益']
    
    for col in df.columns:
        if any(metric in col for metric in key_metrics):
            try:
                val_latest_str = str(latest_year[col]).replace('%', '').replace('亿', '').replace('万', '').replace(',', '').strip()
                val_prev_str = str(prev_year[col]).replace('%', '').replace('亿', '').replace('万', '').replace(',', '').strip()
                
                if val_latest_str == 'nan' or val_prev_str == 'nan' or not val_latest_str or not val_prev_str:
                    continue
                
                val_latest = float(val_latest_str)
                val_prev = float(val_prev_str)
                
                if val_prev != 0:
                    change_rate = (val_latest - val_prev) / abs(val_prev)
                    
                    if change_rate <= -0.30:
                        anomalies.append({
                            "metric": col,
                            "latest_value": latest_year[col],
                            "prev_value": prev_year[col],
                            "change_rate": f"{change_rate * 100:.2f}%"
                        })
            except ValueError:
                continue

    return anomalies

if __name__ == "__main__":
    # 简单测试代码
    print("宁德时代 Z-Score:", calculate_zscore("300750"))
    
    df = get_financial_data.get_financial_data("300750")
    print("\n异常检测结果：")
    for anomaly in detect_financial_anomalies(df):
        print(anomaly)
