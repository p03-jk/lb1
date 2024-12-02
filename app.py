from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import pika

app = Flask(__name__)

# LINE Bot Config
LINE_CHANNEL_ACCESS_TOKEN = 'UqV6DLsCuoaM2m5diuRKuvLXhonHhEL9B1lhJNtiy286jMg2NehbPukAhHq5ZXga0nCldSJV09tuzCnX2u+dT7x3RoSRn9A8zGGycJKrSEAHZn6gLVl8RUAvWscv8Se2EwdUklkRwv6vJSWVLy7k9QdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '1cee78c1b031649c5fdee7c8ed92d61b'
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# CloudAMQP Config
CLOUDAMQP_URL = 'amqps://luowgrgi:2jwvJ-bGBqen2MVrYasWxj8Ovb_9R3RH@possum.lmq.cloudamqp.com/luowgrgi'
params = pika.URLParameters(CLOUDAMQP_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='light_control')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.lower()
    if msg in ["เปิดไฟ", "ปิดไฟ"]:
        channel.basic_publish(exchange='', routing_key='light_control', body=msg)
        reply = f"ส่งคำสั่ง '{msg}' ไปที่ ESP8266 แล้ว"
    else:
        reply = "คำสั่งไม่ถูกต้อง (ใช้ 'เปิดไฟ' หรือ 'ปิดไฟ')"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run()
