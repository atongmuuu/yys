import requests

def send_feishu_webhook(message, name = "李子豪"):
    # 替换为你的飞书 Webhook URL
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/f1fe9e02-592b-42c0-bc82-c5b896c132cb"
    
    # 构造 Webhook 消息体
    webhook_message = {
        "msg_type": "text",
        "content": {
            "text": name + "\n" + message
        }
    }
    
    # 发送 POST 请求到飞书 Webhook
    response = requests.post(webhook_url, json=webhook_message)
    
    # 检查请求是否成功
    if response.status_code == 200:
        pass
    else:
        print(f"\n消息发送失败，状态码: {response.status_code}, 响应内容: {response.text}")

send_feishu_webhook("测试消息，次数")