import os  # 新增：用來讀取系統環境變數
import re  # 用來處理 <think> 標籤
from dotenv import load_dotenv  # 新增：用來載入 .env 檔案
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests

# 載入同資料夾底下的 .env 檔案內容
load_dotenv()

# ==== 從環境變數讀取設定 ====
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
ANYTHINGLLM_API_URL = os.getenv('ANYTHINGLLM_API_URL')
ANYTHINGLLM_API_KEY = os.getenv('ANYTHINGLLM_API_KEY')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print(f'[ERROR] Webhook 處理錯誤：{e}')
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    reply_token = event.reply_token

    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {ANYTHINGLLM_API_KEY}',
        }
        data = {'message': user_msg}
        response = requests.post(
            ANYTHINGLLM_API_URL, headers=headers, json=data
        )
        if response.status_code == 200:
            result = response.json()
            print('[AnythingLLM 回傳]', result)
            raw_answer = result.get(
                'textResponse', '無法理解你的問題，請換個方式問我。'
            )
            # 移除 <think>...</think> 的部分
            answer = re.sub(
                r'<think>.*?</think>', '', raw_answer, flags=re.DOTALL
            ).strip()
        else:
            answer = f'API 呼叫失敗（狀態碼 {response.status_code}）'
    except Exception as e:
        answer = f'發生錯誤：{str(e)}'

    line_bot_api.reply_message(reply_token, TextSendMessage(text=answer))


if __name__ == '__main__':
    app.run(port=5500)