import streamlit as st
import pandas as pd
import get_financial_data
import anomaly_detection
import extract_mda
import analyze_risk

st.set_page_config(page_title="智能财报分析与预警系统", layout="wide", page_icon="📈")

# 缓存机制包装函数，提升性能
@st.cache_data(show_spinner=False, ttl=3600)
def fetch_financial_data(symbol):
    return get_financial_data.get_financial_data(symbol)

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_zscore(symbol):
    return anomaly_detection.calculate_zscore(symbol)

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_mda_text(symbol, stock_name):
    return extract_mda.extract_mda_text(symbol, stock_name)

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_risk_summary(mda_text):
    return analyze_risk.generate_risk_summary(mda_text)


st.title("📈 A股上市公司智能财报分析与风险预警系统")
st.markdown("""
这款基于大语言模型 (DeepSeek) 和大数据会计专业知识构建的智能化系统，旨在为您提供自动化、深度的上市企业基本面分析与暴雷排查服务。
""")

st.sidebar.header("🔍 配置选项")
symbol = st.sidebar.text_input("请输入股票代码 (如 300750)", value="300750")
stock_name = st.sidebar.text_input("请输入股票简称 (如 宁德时代)", value="宁德时代")
analyze_button = st.sidebar.button("一键生成分析报告", type="primary")

if analyze_button:
    if not symbol or not stock_name:
        st.sidebar.warning("请填写完整的股票代码和名称！")
    else:
        with st.spinner(f"正在获取 {stock_name} 的结构化财务数据..."):
            df = fetch_financial_data(symbol)
            
        if df is None or df.empty:
            st.error(f"获取 {stock_name} ({symbol}) 的财务数据失败，它可能不是 A 股的标准股票或接口异常。")
        else:
            tab1, tab2, tab3 = st.tabs(["📊 财务看板与趋势", "🚨 异常与破产预警", "🧠 DeepSeek AI 审计"])
            
            with tab1:
                st.subheader("核心财务数据看板")
                
                # 构建漂亮的 KPI 仪表盘
                try:
                    latest = df.iloc[0]
                    prev = df.iloc[1] if len(df) > 1 else None
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    def safe_metric(col, label, field):
                        val = latest.get(field, "N/A")
                        delta = ""
                        if prev is not None and field in prev:
                            try:
                                v_new = float(str(val).replace('%', '').replace('亿', '').replace('万', '').replace(',', ''))
                                v_old = float(str(prev[field]).replace('%', '').replace('亿', '').replace('万', '').replace(',', ''))
                                change = (v_new - v_old) / abs(v_old) * 100
                                delta = f"{change:.2f}%"
                            except:
                                pass
                        col.metric(label=label, value=str(val), delta=delta)

                    safe_metric(col1, "营业总收入", "营业总收入")
                    safe_metric(col2, "净利润", "净利润")
                    safe_metric(col3, "净资产收益率(ROE)", "净资产收益率")
                    safe_metric(col4, "销售毛利率", "销售毛利率")
                    st.divider()
                except Exception as e:
                    pass

                st.dataframe(df, use_container_width=True)
                
                # 趋势图
                year_col = df.columns[0]
                try:
                    df_chart = df.copy().set_index(year_col).iloc[::-1]
                    if "净资产收益率" in df_chart.columns:
                        s_roe = df_chart["净资产收益率"].astype(str).str.replace("%", "").astype(float)
                        st.write("📈 净资产收益率 (ROE) 历史趋势：")
                        st.line_chart(s_roe)
                except Exception as e:
                    pass

            with tab2:
                st.subheader("Altman Z-Score 破产预警模型")
                with st.spinner("正在拉取资产负债表与利润表，计算 Z-Score..."):
                    z_result = fetch_zscore(symbol)
                
                if z_result:
                    score = z_result['score']
                    status = z_result['status']
                    color = z_result['color']
                    
                    if color == "green":
                        st.success(f"**Z-Score 评分：{score}** —— 判定结果：**{status}**。企业财务状况良好，破产概率极低。（报告期：{z_result['report_date']}）")
                    elif color == "orange":
                        st.warning(f"**Z-Score 评分：{score}** —— 判定结果：**{status}**。企业处于灰色地带，需关注资金链和盈利能力。（报告期：{z_result['report_date']}）")
                    else:
                        st.error(f"**Z-Score 评分：{score}** —— 判定结果：**{status}**。⚠️ 企业具有极高的财务危机甚至破产风险！（报告期：{z_result['report_date']}）")
                else:
                    st.warning("未能成功获取三大报表数据，无法计算 Z-Score。")

                st.divider()
                st.subheader("量化财务异动监控")
                st.markdown("扫描最近两期核心财务报表数据，监控是否存在同比超过 30% 断崖式下跌的危险信号。")
                anomalies = anomaly_detection.detect_financial_anomalies(df)
                
                if not anomalies:
                    st.success("✅ 未发现核心财务指标存在同比严重恶化的异常情况。")
                else:
                    st.error(f"⚠️ 警报：发现 {len(anomalies)} 项高风险异常指标！")
                    for anom in anomalies:
                        st.warning(f"**{anom['metric']}**: 由 {anom['prev_value']} 暴跌至 {anom['latest_value']}，同比变动 **{anom['change_rate']}**。")
            
            with tab3:
                st.subheader("管理层讨论与分析 (MD&A) NLP 解析")
                with st.spinner("正在提取并处理 MD&A 文本，请耐心等待..."):
                    mda_text = fetch_mda_text(symbol, stock_name)
                    
                if not mda_text:
                    st.error("无法提取到该公司的 MD&A 文本，原因可能为近期未披露年报、或 PDF 加密防篡改限制。")
                else:
                    with st.spinner("正在将文本提交至 DeepSeek (大语言模型) 进行逻辑推理与风险归纳..."):
                        risk_summary = fetch_risk_summary(mda_text)
                    
                    st.success("🤖 DeepSeek 深度审计分析完成：")
                    st.markdown(risk_summary)
