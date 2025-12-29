# 📈 AI Investment Copilot (AWS Bedrock Implementation)

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20EC2-orange.svg)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)
![LangChain](https://img.shields.io/badge/Framework-LangChain-green.svg)

> **Note:** This is a personal project exploring LLM applications in financial analysis. It is designed to assist in calculating valuation metrics from earnings reports.
> **Disclaimer:** This tool is for **educational and technical demonstration purposes only**. The generated analysis and metrics do not constitute financial advice. Users should verify all data independently and assume all risks associated with investment decisions.

## 📖 Introduction

I built this project to help investors efficiently extract key insights and valuation metrics from complex financial reports.

Financial documents are often dense and time-consuming to analyze. This tool leverages Amazon Bedrock to process full-text reports, summarizing core financial highlights and management guidance. It also implements a standardized calculation logic to derive metrics like Forward P/E and PEG, aiming to provide a consistent reference point for assessing a company's current valuation.

![Demo](./Assets/Demo.png)

## ✨ Key Features

* **Full-Context Analysis:** Ingests the entire PDF text to maintain data continuity across financial statements.
* **Automated Data Extraction:** Quickly identifies and extracts key financial figures (such as EPS, Net Income, and Revenue) from dense, multi-page earnings reports.
* **Hybrid Valuation Calculation:** Combines data extracted from the reports with user-provided parameters (such as Stock Price and Growth Rate) to calculate Forward P/E and PEG ratios based on standardized formulas.
* **Valuation-First Reporting:** The summary is structured to prioritize quantitative metrics (P/E and PEG), using these calculated figures as a consistent reference for the overall analysis.

## 🏗️ Architecture

Here is the system architecture for Financial Copilot.

![System Architecture](./Assets/Financial_Copilot_Diagram.png)

## ⚙️ Tech Stack
* **LLM:** Anthropic Claude 3.5 Sonnet (via AWS Bedrock)
* **Orchestration:** LangChain
* **Frontend:** Streamlit
* **Infrastructure:** AWS EC2 & IAM

## 🛠️ How to Run Locally

### 1. Prerequisites
* An AWS Account with access to **Bedrock** (Claude 3.5 Sonnet enabled).
* Python 3.9 or higher.

### 2. Installation
```bash
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name
pip install -r requirements.txt
```

### 3. Configuration
**Option A: Local Machine (Development)** Configure your AWS credentials using the AWS CLI:
```bash
aws configure
```
**Option B: EC2 Instance (Production - Recommended) Attach an IAM Role to your EC2 instance with the following permissions:
*AmazonBedrockFullAccess

### 4. Run the App
Launch the application using Streamlit:
```bash
streamlit run app.py
```

## 🧩 Challenges & Learnings
Building this project provided deep insights into deploying AI solutions on AWS and handling sensitive financial data logic:

Controlling AI Math: Standard LLMs often struggle with financial consistency. I learned to use "Thought Process" prompting and strict XML tags to force the model to show its math, which significantly reduced valuation errors.

Full-Context vs. RAG: I experimented with different data ingestion methods and found that for financial reports, feeding the full text is more reliable than RAG for maintaining the relationship between different financial tables.

### 🚧 Current Limitations & Future Work

* **DCF Modeling Complexity**: While the tool handles Relative Valuation (P/E & PEG) well, implementing a reliable **Discounted Cash Flow (DCF)** model remains a challenge. DCF requires multi-year forecasting and highly subjective assumptions (WACC, Terminal Growth) that current LLM logic can find difficult to stabilize without external spreadsheet integration.
* **Multi-Report Comparison**: The current version focuses on single-report analysis. Future iterations could explore comparing year-over-year (YoY) data across multiple PDF uploads.
