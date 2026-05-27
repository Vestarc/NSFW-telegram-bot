# Telegram NSFW Bot

A Telegram bot that demonstrates  using SPICY API via  MuleRouter API endpoints (image/video generation, face-swap, etc.). This repository is an educational demo and not a hosted service.

> Important: this project includes references to endpoints capable of adult-oriented generation. Use responsibly, follow all laws, and never process images of people without their explicit consent. please refer to your local laws to ensure you align with them. 

> This repository is provided for demonstration purposes only. The author is not responsible for misuse of the code or ideas in this project.

## Features

- Telegram bot (Python) that accepts messages, commands and file uploads
- Example integrations for image/video generation and face-swap via spicy api 

## Ethics (read before use)

- Do not upload or process images of real people without their consent.
- Do not use copyrighted or private material without permission.
- Protect secrets: keep `TELEGRAM_TOKEN` and `MULE_API_KEY` out of source control.
- This repository is a technical illustration only. The author does not provide or operate a public generation service.
- i will not be held liable if you are caught using this code or idea for illegal or mulicious purposes .

## Requirements

- Python 3.10+ recommended
- A MuleRouter account and API key (`MULE_API_KEY`)
- A Telegram bot token (`TELEGRAM_TOKEN`)

Optional tools:

- `ngrok` or a public tunnel if you want to use webhooks locally
  ```
  ngrok http 5000
  ```
- use the url provided as the webhook url during local development. 

## Setup

1. Clone the repository and open it in VS Code or your editor.
2. Vist the spicy api dicord channel https://discord.gg/rbtMVrjJ   here you will be guided on how to:                         
  - Create a MuleRouter account and get an API key:
  - Visit https://www.mulerouter.ai/
  - Sign in or create a new account
  - Open your account dashboard and generate an API key
  - Copy the key into `MULE_API_KEY`
  - get access to spicy api models and documetation sites 
  - demos

3. Create a Telegram bot token:
  - Open Telegram and start a chat with [@BotFather](https://t.me/BotFather)
  - Send `/newbot`
  - Follow the prompts to choose a name and username
  - Copy the token BotFather gives you into `TELEGRAM_TOKEN`

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Configure environment variables (example `.env`):

```text
TELEGRAM_TOKEN=your-telegram-token
MULE_API_KEY=your-mulerouter-key
# Optional: WEBHOOK_URL=https://your-public-url
```

6. Run the bot (replace `main.py` if your entrypoint differs):

```powershell
python main.py
```

## Configuration

- `TELEGRAM_TOKEN`: Telegram bot token from BotFather
- `MULE_API_KEY`: MuleRouter API key or token
- `WEBHOOK_URL` (optional): public URL for webhooks, if you want to receive messages 

## How it works 

1. Telegram client → bot receives a message or file
2. Bot translates the user request into a MuleRouter API call
3. Bot creates a task on MuleRouter and polls for completion, if needed
4. Bot returns the generated result or task status to the user. If you want to change the bot behavior or output style, update the prompt logic in `mule.py`.
>NOTE THAT THE PROMPT IS IN MULE.PY if you need to change the prmpt please visit mule.py and chnage it. the bot currently doesnt have caption management 
## Docs
- MuleRouter API docs: https://www.mulerouter.ai/docs/
- Telegram BotFather help: https://core.telegram.org/bots/features#botfather
- Example endpoints (MuleRouter docs):
  - Image / video generation: https://www.mulerouter.ai/docs/api-reference/endpoint/carrothub/wan2.7-i2v-spicy/generation
  - Face swap: https://www.mulerouter.ai/docs/api-reference/endpoint/carrothub/face-swap/generation

## Disclaimer

This repository is a technical demonstration. The author does not endorse or host any adult or illegal services. Always comply with local laws, platform terms of service, and privacy/consent requirements.

---
