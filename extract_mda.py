import akshare as ak
import pandas as pd
import requests
import os
import pdfplumber
import re

def download_latest_annual_report(symbol, name, output_dir="."):
    """
    使用 akshare 获取最新的年度报告 PDF 下载链接并下载
    """
    print(f"正在查询 {name} ({symbol}) 的公告信息...")
    import datetime
    end_date = datetime.datetime.now().strftime("%Y%m%d")
    # 往前推两年
    start_date = (datetime.datetime.now() - datetime.timedelta(days=730)).strftime("%Y%m%d")
    
    # 获取巨潮资讯的公告报告数据，增加时间范围参数以确保能抓到近期的年报
    try:
        df = ak.stock_zh_a_disclosure_report_cninfo(
            symbol=symbol, 
            start_date=start_date, 
            end_date=end_date
        )
    except KeyError:
        print(f"未找到 {name} ({symbol}) 在 {start_date} 到 {end_date} 期间的任何公告。它可能已经退市或更改了代码。")
        return None
    
    # 过滤出“年度报告”且不包含无关公告（如摘要、半年度、说明会、征集、提示等）
    annual_reports = df[
        df["公告标题"].str.contains("年度报告") & 
        (~df["公告标题"].str.contains("半年度|摘要|取消|英文|说明会|征集|提示|公告|补充|意见|决议|制度|通知"))
    ]
    
    if annual_reports.empty:
        print(f"未找到 {name} 的年度报告。")
        return None
    
    # 取最新的一份年度报告
    latest_report = annual_reports.iloc[0]
    title = latest_report["公告标题"]
    page_url = latest_report["公告链接"]
    
    # 巨潮资讯接口返回的是网页版详情页 URL，我们需要通过解析参数，拼接出真正的 PDF 下载直链
    # 例如：http://www.cninfo.com.cn/new/disclosure/detail?stockCode=600519&announcementId=1219495818&announcementTime=2024-04-03
    # 转换为：http://static.cninfo.com.cn/finalpage/2024-04-03/1219495818.PDF
    import urllib.parse
    parsed_url = urllib.parse.urlparse(page_url)
    params = urllib.parse.parse_qs(parsed_url.query)
    
    if "announcementId" in params and "announcementTime" in params:
        ann_id = params["announcementId"][0]
        # 时间可能有小时部分，这里只取日期部分
        ann_date = params["announcementTime"][0].split(" ")[0] 
        pdf_url = f"http://static.cninfo.com.cn/finalpage/{ann_date}/{ann_id}.PDF"
    else:
        pdf_url = page_url
        
    print(f"找到最新年报：{title}")
    print(f"真实下载链接：{pdf_url}")
    
    # 清理文件名中的特殊字符
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
    pdf_path = os.path.join(output_dir, f"{name}_{safe_title}.pdf")
    
    # 下载 PDF
    if not os.path.exists(pdf_path):
        print("正在下载 PDF 文件，这可能需要一点时间...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(pdf_url, headers=headers)
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        print(f"PDF 下载完成：{pdf_path}")
    else:
        print(f"PDF 文件已存在：{pdf_path}")
        
    return pdf_path

def extract_mda_from_pdf(pdf_path):
    """
    使用 pdfplumber 解析 PDF，并利用简单的规则提取“管理层讨论与分析”章节
    """
    if not pdf_path:
        return
    
    print("正在解析 PDF 提取文本，请稍候...")
    mda_text = ""
    is_mda_section = False
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                # 简单的启发式规则寻找章节开始和结束
                # 判断是否是目录页：如果一页里面同时出现了第三节、第四节、第五节，那肯定是目录
                is_toc_page = ("第三节" in text and "第四节" in text and "第五节" in text)
                
                if not is_toc_page:
                    if "第三节" in text and "管理层讨论与分析" in text.replace(" ", ""):
                        is_mda_section = True
                    
                    # 如果遇到下一节（通常是“第四节 公司治理”或“第五节”），则停止提取
                    if is_mda_section and ("第四节" in text or "第五节" in text) and "公司治理" in text.replace(" ", ""):
                        break
                
                if is_mda_section and not is_toc_page:
                    mda_text += text + "\n"
                    
        return mda_text
    except Exception as e:
        print(f"解析 PDF 发生错误: {e}")
        return ""

def extract_mda_text(symbol, name, output_dir="."):
    """
    下载指定股票的最新年报并提取 MD&A 文本，返回提取到的字符串。
    """
    pdf_path = download_latest_annual_report(symbol, name, output_dir)
    if pdf_path:
        mda_content = extract_mda_from_pdf(pdf_path)
        return mda_content
    return ""

if __name__ == "__main__":
    # 测试代码
    symbol = "300750"
    name = "宁德时代"
    mda_content = extract_mda_text(symbol, name)
    if mda_content:
        print(f"成功提取了 {len(mda_content)} 个字符的 MD&A 文本。")
    else:
        print("提取失败。")
