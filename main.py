import os
import requests
 
import threading
from flask import Flask, request
from dotenv import load_dotenv

import mule

#load variables from .env file check example.env for referncce 
load_dotenv()
app = Flask(__name__)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
MULE_API_KEY = os.getenv('MULE_API_KEY')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'





def set_webhook():
   
    if not WEBHOOK_URL:
        print("Warning: WEBHOOK_URL not set in .env. Skipping automatic registration.")
        return

    url = f"{TELEGRAM_API_URL}/setWebhook"
    webhook_endpoint = f"{WEBHOOK_URL.rstrip('/')}/webhook"
    
    try:
        response = requests.post(url, json={'url': webhook_endpoint})
        response.raise_for_status()
        print(f"Webhook successfully set to: {webhook_endpoint}")
    except Exception as e:
        print(f"Failed to set webhook: {e}")

@app.route('/webhook', methods=['POST'])
def webhook_handler():
   
    try:
        update = request.get_json()
        if not update:
            return 'Invalid update', 400

        print(f"Received update: {update}")

        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']

            # Commands
            text_command = message.get('text', '')
            if text_command == '/start':
                welcome = (
                    "Send me an image and I’ll enhance it."
                )
                send_message(chat_id, welcome)
    
                return 'OK', 200
            # Other commands are not supported
    
            
            if 'photo' in message:
                photo = message['photo'][-1]
                file_id = photo['file_id']
                #the caption is intentionally ignored uses only code-side prompt.
                user_prompt = None

                if not TELEGRAM_BOT_TOKEN:
                    err_text = "Server is missing TELEGRAM_BOT_TOKEN configuration."
                    send_message(chat_id, err_text)
                    # _send_reply_to_target(message, err_text)
                    return 'OK', 200
                telegram_token = TELEGRAM_BOT_TOKEN
                mule_api_key = MULE_API_KEY

                send_message(chat_id, "Enhancing your image…")
                # _send_reply_to_target(message, "Enhancing your image…")

                def _work():
                    try:
                        if mule_api_key:
                            #use mule.py 
                            enhanced_url = mule.enhance_telegram_photo(
                                mule_api_key=mule_api_key,
                                telegram_bot_token=telegram_token,
                                file_id=file_id,
                                user_prompt=user_prompt,
                            )
                        else:
                            file_info_url = f"https://api.telegram.org/bot{telegram_token}/getFile?file_id={file_id}"
                            resp = requests.get(file_info_url).json()
                            if resp.get("ok"):
                                file_path = resp["result"]["file_path"]
                                enhanced_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"
                            else:
                                enhanced_url = None

                        if enhanced_url:
                            send_photo(chat_id, enhanced_url, caption="Here’s your enhanced image")
                        else:
                            raise Exception("Could not retrieve an image URL.")
                    except Exception as e:
                        print(f"Enhancement error: {e}")
                        err_text = "Sorry — I couldn’t enhance that image right now. Please try again."
                        send_message(chat_id, err_text)
                        # _send_reply_to_target(message, err_text)

                threading.Thread(target=_work, daemon=True).start()

            elif 'text' in message:
                reply_text = "Please send an image to enhance."
                send_message(chat_id, reply_text)
                

        return 'OK', 200
    except Exception as e:
        print(f"Error in webhook: {e}")
        return 'Internal Server Error', 500

def send_message(chat_id, text):
    url = f'{TELEGRAM_API_URL}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")
        return None

def send_photo(chat_id, photo, caption=None):
    url = f'{TELEGRAM_API_URL}/sendPhoto'
    payload = {
        'chat_id': chat_id,
        'photo': photo
    }
    if caption:
        payload['caption'] = caption
        
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result
    except Exception as e:
        print(f"Error sending photo to Telegram: {e}")
        return None

if __name__ == '__main__':
    set_webhook()
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
