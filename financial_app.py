import streamlit as st
import os
import boto3
import tempfile
from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, TextLoader

# ================= 🔐 密钥配置区 =================
os.environ["AWS_ACCESS_KEY_ID"] = "YOUR_AWS_ACCESS_KEY"
os.environ["AWS_SECRET_ACCESS_KEY"] = "YOUR_AWS_SECRET_ACCESS_KEY"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# ================= ⚙️ 页面配置 =================
st.set_page_config(page_title="AI 投资分析师 (Stable Long-Context)", page_icon="📈", layout="wide")

model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# ================= 🛠️ 核心功能函数 =================

@st.cache_resource
def get_llm():
    """初始化 AWS Bedrock LLM"""
    boto3_session = boto3.Session()
    bedrock_client = boto3_session.client(service_name="bedrock-runtime")
    return ChatBedrock(
        model_id=model_id,
        client=bedrock_client,
        model_kwargs={"temperature": 0.0, "max_tokens": 4096} # 降低随机性
    )

def extract_full_text(uploaded_files):
    """读取所有上传文件的完整文本，不切片，保持全文逻辑"""
    combined_text = ""
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in uploaded_files:
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            
            # 加载全文
            if file.name.lower().endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            else:
                loader = TextLoader(file_path, encoding='utf-8')
            
            docs = loader.load()
            content = "\n".join([doc.page_content for doc in docs])
            combined_text += f"\n\n--- Start of Document: {file.name} ---\n{content}\n--- End of Document ---\n"
    return combined_text

# ================= 🧠 英文逻辑核心 Prompt =================
# 强制 AI 在内部使用英文思考，输出使用中文
analyst_template = """
Role: Senior Buy-side Analyst. Focus on Relative Valuation (P/E & PEG).
Reasoning in ENGLISH, Report in CHINESE.

<thought_process>
1. **Metadata**: Identify Company Name and the specific Fiscal Period.
2. **Unit Audit**: Detect if figures are Millions/Thousands.
3. **Data Extraction**: 
   - Current Stock Price: ${market_price}
   - Net Income (TTM or Current Quarter Annualized)
   - Diluted Shares Outstanding
   - Diluted EPS
   - Forward Guidance (Revenue/EPS for next quarter/year)
3. **Valuation Logic (STRICT HIERARCHY)**:
   - **Step A: Calculate Quarterly Forward EPS**
     - Use Guidance if available, otherwise use Current Q EPS. 
   - **Step B: ANNUALIZE the EPS (CRITICAL)**
     - **Forward Annual EPS = Quarterly Forward EPS * 4**
   - **Step C: Calculate Forward P/E**
     - **P/E = ${market_price} / Forward Annual EPS**
   - **Step D: Calculate PEG**
     - **PEG = (Forward P/E) / {growth_rate}**
4. **Rating Logic**: The final rating MUST align with the PEG and P/E analysis. Do NOT let "company leadership" override extreme valuation multiples.
</thought_process>

---
[CONTEXT]: {full_text}

请生成投资简报（中文）：

**[公司名称] (股票代码) - [财报季度/年度] 投资分析报告**

一、 关键财务指标

- **业绩摘要**：营收/利润/EPS 的数值及变动。
- **看涨/看跌要点**：财报中最核心的 2-3 个驱动力与隐忧。
- **管理层立场**：[看涨/中性/看跌] — 简述语气与指引。

二、 相对估值矩阵 (Relative Valuation)
- **前瞻市盈率 (Forward P/E)**：展示计算过程（股价 / 预期每股收益）。
- **PEG 比率**：展示计算过程（P/E / {growth_rate}% 增长率）。
- **行业对比简述**：简评该估值在当前行业背景下处于什么位置（低估/合理/溢价）。

三、 评级 & 理由
- **最终评级**：[买入/持有/卖出]
- **核心逻辑**：基于 P/E 和 PEG 的绝对数值。
- **审计结论**：明确指出当前股价是“低估”、“合理”还是“严重泡沫”。
- **风险提示**：针对该公司的核心业务风险。
---
[OUTPUT FORMAT RULE]:
1. 你必须首先输出 <thought_process> 标签。
2. 在标签内，详细记录你的 Unit Audit, Data Extraction, 和 Math Logic。
3. 必须以 </thought_process> 结束该部分。
4. 紧接着输出中文投资报告。
5. 禁止合并或忽略标签，这是程序解析的唯一标准。
"""

# ================= 🖥️ UI 界面逻辑 =================
st.title("AI Investment Copilot")
st.caption("Claude 3.5 Sonnet")

with st.sidebar:
    st.header("1. 估值参数")
    current_price = st.number_input("当前股价 (USD)", value=190.0)
    growth_rate = st.slider("预期增长率 (%)", 0, 100, 50)
    st.divider()
    uploaded_files = st.file_uploader("上传财报 (PDF/TXT)", type=['pdf', 'txt'], accept_multiple_files=True)
    
    st.divider()
    process_btn = st.button("🚀 开始全文分析", type="primary")
    
    if st.button("🗑️ 重置分析师记忆"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- 主程序逻辑 ---
if process_btn and uploaded_files:
    try:
        llm = get_llm()
        
        with st.spinner("1/2 正在提取全文数据 (保持勾稽关系)..."):
            full_context_text = extract_full_text(uploaded_files)
            # 存储全文以便追问
            st.session_state.full_context = full_context_text

        with st.spinner("2/2 AI 正在进行英文逻辑推演并翻译报告..."):
            # 组装 Prompt
            final_prompt = analyst_template.format(
                full_text=full_context_text,
                market_price=current_price,
                growth_rate=growth_rate
            )
            
            # 直接调用 LLM，不再通过复杂的 Chain
            response = llm.invoke(final_prompt)
            st.session_state.report = response.content

    except Exception as e:
        st.error(f"❌ 分析失败: {str(e)}")

# --- 结果展示 ---
if "report" in st.session_state:
    st.markdown("---")
    
    # 尝试分离 Thought Process (如果 AI 输出了标签)
    raw_output = st.session_state.report
    if "<thought_process>" in raw_output and "</thought_process>" in raw_output:
        thought, report = raw_output.split("</thought_process>")
        with st.expander("🔍 查看 AI 内部逻辑审计"):
            st.write(thought.replace("<thought_process>", "").strip())
        st.markdown(report.strip())
    else:
        st.markdown(raw_output)