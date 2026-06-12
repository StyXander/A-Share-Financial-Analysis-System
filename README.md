# 📈 A股上市公司智能财报分析与风险预警系统

基于大数据与 LLM (大语言模型) 的中国 A 股上市企业自动化财务分析与审计排雷工具。本项目不仅涵盖传统的量化指标分析，还利用大模型强大的理解能力对海量的财务文本进行深度自然语言处理。

## 🌟 核心功能

*   **📊 结构化财务数据获取**：一键获取并可视化展示近十年的核心财务摘要。
*   **🚨 财务异动量化监控**：对净利润、毛利率、ROE等核心指标进行自动回测，对同比断崖式下跌发出高风险预警。
*   **🧠 MD&A 文本 NLP 分析**：自动下载巨潮资讯网的原版年报 PDF，利用启发式算法精准提取“管理层讨论与分析”章节；调用 DeepSeek 大模型进行逻辑推理，归纳并输出企业风险预警摘要。
*   **🖥️ 可视化 Web UI**：基于 Streamlit 构建的现代数据大屏体验，仅需输入股票代码，后台即可全自动运转。

## 🛠️ 技术栈

*   **大语言模型 (LLM)**: DeepSeek API (兼容 OpenAI SDK)
*   **金融数据接口**: akshare
*   **文档解析与数据清洗**: pdfplumber, pandas, requests
*   **前端交互**: Streamlit

## 🚀 快速开始

### 1. 安装依赖环境
```bash
git clone https://github.com/your-username/smart-financial-warning-system.git
cd smart-financial-warning-system
pip install -r requirements.txt
```

### 2. 配置大模型 API Key
打开 `analyze_risk.py` 文件，找到 `API_KEY` 并替换为你自己的 DeepSeek API 密钥：
```python
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
```

### 3. 启动 Web 应用
在终端中执行以下命令：
```bash
streamlit run app.py
```
终端将会输出一个本地网址（通常为 `http://localhost:8501`），在浏览器中打开即可开始排雷！

## 📸 应用截图
*(请在将本项目推送到 GitHub 前，将网页运行的截图保存在此处，例如：)*
`![Dashboard Demo](demo.png)`

## ⚠️ 免责声明
本项目基于公开数据接口及大语言模型构建，仅作学术交流与大数据分析技术探讨之用。程序生成的量化警报与文字风险摘要均**不构成**任何财务审计结论或投资建议。请勿用于真实商业运作或炒股决策！
