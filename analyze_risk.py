import os
from openai import OpenAI

# 配置 DeepSeek API
# DeepSeek 的 API 完全兼容 OpenAI 的 Python SDK
API_KEY = "sk-8dcdcfca47114552ae156a5fda66da0b"
BASE_URL = "https://api.deepseek.com"

def generate_risk_summary(mda_text):
    """
    调用 DeepSeek API 对传入的 MD&A 文本输出风险预警摘要，返回总结字符串
    """
    if not mda_text or not mda_text.strip():
        return "未能提取到有效的 MD&A 文本，无法进行风险分析。"

    # 为了防止文本过长超出大模型上下文限制，截取前 30000 字符
    max_length = 30000
    if len(mda_text) > max_length:
        mda_text = mda_text[:max_length]

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    prompt = f"""
你是一位资深的金融分析师。请阅读以下从上市公司年度报告中提取的“管理层讨论与分析(MD&A)”文本，并总结出该公司的【风险预警摘要】。

请分点列出（如宏观经济风险、行业竞争风险、原材料价格波动风险、汇率风险等），要求语言精简、重点突出、切中要害。

财报文本内容如下：
{mda_text}
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat", 
            messages=[
                {"role": "system", "content": "你是一个专业的金融分析助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        result = response.choices[0].message.content
        return result
        
    except Exception as e:
        return f"DeepSeek API 调用失败：{e}"

if __name__ == "__main__":
    # 测试代码
    target_file = "宁德时代_MD&A提取结果.txt"
    if os.path.exists(target_file):
        with open(target_file, "r", encoding="utf-8") as f:
            text = f.read()
        print(generate_risk_summary(text))
