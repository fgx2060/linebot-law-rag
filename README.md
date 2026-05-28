# linebot-law-rag
基於 RAG 架構的本地法規檢索與諮詢 LINE Bot 助理，結合 AnythingLLM 與 Ollama，兼顧隱私與安全。
# ⚖️ 法規檢索與諮詢 AI 助理 (LINE + AnythingLLM + Ollama)
---
## 📖 專案簡介
本專題以「LINE Bot 串接本地 RAG 問答系統」為核心，開發一套能於本地端運行的 **法規檢索與諮詢 AI 助理**。  
系統結合 **LINE Bot (Frontend)**、**AnythingLLM (中介檢索層)** 與 **Ollama (本地 LLM)**，實現即時法規查詢與自然語言回覆。

---

## ✨ 系統特色
- **本地部署**：所有資料處理與模型推論皆於本地完成，保障隱私。  
- **自然語言檢索**：支援使用者直接輸入問題，系統自動檢索法條並生成回覆。  
- **LINE 介面**：使用熟悉的 LINE 對話框，降低學習門檻。  
- **高擴充性**：可替換模型（Llama 3 / Qwen 等）或新增法規來源。  

---

## 🏗️ 系統架構
使用者 → LINE Bot → Flask Webhook → AnythingLLM (RAG) → Ollama → 回覆答案

- **Frontend**：LINE Bot Messaging API  
- **Webhook / 應用層**：Flask（驗證、流程控制、訊息轉發）  
- **檢索層**：AnythingLLM（文件上傳 → 向量化 → 語意檢索）  
- **推論層**：Ollama（本地模型，根據檢索結果生成答案）  
- **資料層**：知識庫（全國法規資料庫）

---

## 🛠️ 環境需求

### Python 套件
`requirements.txt`：
```txt
flask
line-bot-sdk
requests
python-dotenv
```
其他工具

- AnythingLLM (v1.8.1-r2) → 向量檢索與知識庫管理
- Ollama (本地模型推論服務)
- Ngrok → 測試 Webhook 對外公開

📖 文件
📄 專題報告：《專題報告.pdf》
