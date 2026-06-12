import akshare as ak
import pandas as pd
import time
import os

def get_financial_data(symbol):
    """
    调用 akshare 获取同花顺的财务摘要数据，并返回 pandas DataFrame
    """
    try:
        # indicator="按年度" 表示获取年度财务数据
        df = ak.stock_financial_abstract_ths(symbol=symbol, indicator="按年度")
        return df
    except Exception as e:
        print(f"获取 {symbol} 财务数据时发生错误：{e}")
        return None

def get_zscore_data(symbol):
    """
    获取计算 Z-Score 所需的资产负债表与利润表最新数据（新浪财经接口）。
    返回一个包含计算所需核心字段的字典。
    """
    try:
        df_bs = ak.stock_financial_report_sina(stock=symbol, symbol="资产负债表")
        df_is = ak.stock_financial_report_sina(stock=symbol, symbol="利润表")
        
        if df_bs is None or df_bs.empty or df_is is None or df_is.empty:
            return None
            
        # 取最新一期财报的数据（第一行）
        latest_bs = df_bs.iloc[0]
        latest_is = df_is.iloc[0]
        
        # 安全获取数值，如果缺失返回0
        def safe_float(val):
            try:
                return float(val) if pd.notna(val) else 0.0
            except:
                return 0.0

        z_data = {
            "总资产": safe_float(latest_bs.get("资产总计", 0)),
            "流动资产": safe_float(latest_bs.get("流动资产合计", 0)),
            "流动负债": safe_float(latest_bs.get("流动负债合计", 0)),
            "总负债": safe_float(latest_bs.get("负债合计", 0)),
            "归母所有者权益": safe_float(latest_bs.get("归属于母公司股东权益合计", 0)) or safe_float(latest_bs.get("所有者权益(或股东权益)合计", 0)),
            "未分配利润": safe_float(latest_bs.get("未分配利润", 0)),
            "营业总收入": safe_float(latest_is.get("营业总收入", 0)),
            "利润总额": safe_float(latest_is.get("利润总额", 0)),
            "财务费用": safe_float(latest_is.get("财务费用", 0)),
            "报告日": latest_bs.get("报告日", "未知时间")
        }
        return z_data
    except Exception as e:
        print(f"获取 {symbol} Z-Score 数据时发生错误：{e}")
        return None

if __name__ == "__main__":
    # 测试代码
    df = get_financial_data("300750")
    if df is not None:
        print(df.head())
    
    print("\nZ-Score Data:", get_zscore_data("300750"))
