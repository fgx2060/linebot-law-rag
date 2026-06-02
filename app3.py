# ===== 載入需要的套件 =====

import os  # 讀取系統環境變數
import re  # 使用正規表達式處理字串
from dotenv import load_dotenv  # 載入 .env 檔案

from flask import Flask, abort, request  # Flask Web 框架
from linebot import LineBotApi, WebhookHandler  # LINE Bot SDK
from linebot.exceptions import InvalidSignatureError  # LINE 簽章驗證錯誤
from linebot.models import MessageEvent, TextMessage, TextSendMessage  # LINE 訊息模型

import requests  # 發送 HTTP Request 給 AnythingLLM


# ===== 載入 .env 設定檔 =====

# 讀取專案目錄下的 .env 檔案
load_dotenv()


# ===== 從環境變數取得設定 =====

# LINE Messaging API Access Token
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# LINE Messaging API Secret
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

# AnythingLLM API Endpoint
ANYTHINGLLM_API_URL = os.getenv('ANYTHINGLLM_API_URL')

# AnythingLLM API 金鑰
ANYTHINGLLM_API_KEY = os.getenv('ANYTHINGLLM_API_KEY')


# ===== 初始化 LINE Bot =====

# 建立 LINE Bot API 物件
# 用來發送訊息給使用者
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# 建立 Webhook Handler
# 用來驗證並解析 LINE 傳來的事件
handler = WebhookHandler(LINE_CHANNEL_SECRET)


# ===== 建立 Flask App =====

app = Flask(__name__)


# ==========================================================
# Webhook 接收入口
# LINE 所有事件都會送到這裡
# ==========================================================
@app.route('/webhook', methods=['POST'])
def webhook():

    # 從 Header 取得 LINE 簽章
    signature = request.headers['X-Line-Signature']

    # 取得原始 Request Body
    body = request.get_data(as_text=True)

    try:
        # 驗證簽章並解析事件
        handler.handle(body, signature)

    except InvalidSignatureError:
        # LINE 簽章驗證失敗
        abort(400)

    except Exception as e:
        # 其他錯誤
        print(f'[ERROR] Webhook 處理錯誤：{e}')
        abort(400)

    # 回傳 HTTP 200 給 LINE
    return 'OK'


# ==========================================================
# 文字訊息事件處理器
# 使用者傳送文字訊息時會觸發
# ==========================================================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # 使用者輸入的文字
    user_msg = event.message.text

    # LINE 回覆 Token
    # 每個訊息事件都有唯一 reply_token
    reply_token = event.reply_token

    try:

        # ===== AnythingLLM API Header =====
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {ANYTHINGLLM_API_KEY}',
        }

        # ===== 傳送給 AnythingLLM 的資料 =====
        data = {
            'message': user_msg
        }

        # ===== 呼叫 AnythingLLM API =====
        response = requests.post(
            ANYTHINGLLM_API_URL,
            headers=headers,
            json=data
        )

        # API 呼叫成功
        if response.status_code == 200:

            # 解析 JSON
            result = response.json()

            # 印出回傳內容供除錯
            print('[AnythingLLM 回傳]', result)

            # 取得 AI 回覆內容
            raw_answer = result.get(
                'textResponse',
                '無法理解你的問題，請換個方式問我。'
            )

            # ====================================
            # 移除 DeepSeek / 推理模型的 think 標籤
            # 例如：
            #
            # <think>
            # 我正在思考...
            # </think>
            #
            # 最終只保留正式回答
            # ====================================
            answer = re.sub(
                r'<think>.*?</think>',
                '',
                raw_answer,
                flags=re.DOTALL
            ).strip()

        else:
            # API 回傳錯誤狀態碼
            answer = (
                f'API 呼叫失敗（狀態碼 {response.status_code}）'
            )

    except Exception as e:

        # 執行過程發生例外
        answer = f'發生錯誤：{str(e)}'

    # ===== 回覆訊息給 LINE 使用者 =====
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=answer)
    )


# ==========================================================
# 主程式入口
# ==========================================================
if __name__ == '__main__':

    # 啟動 Flask Server
    # http://localhost:5500
    app.run(port=5500)
