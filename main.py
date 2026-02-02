import os
import random
import asyncio
from telethon import TelegramClient, events
from flask import Flask
from threading import Thread
import google.generativeai as genai

# --- CẤU HÌNH WEB GIỮ BOT SỐNG TRÊN RENDER ---
app = Flask('')
@app.route('/')
def home(): return "Bot Sao789 đang hoạt động!"
def run_web(): app.run(host='0.0.0.0', port=8080)

# --- CẤU HÌNH AI (GEMINI) ---
genai.configure(api_key="THAY_API_KEY_GEMINI_TAI_DAY")
model = genai.GenerativeModel('gemini-pro')

# --- CẤU HÌNH TELEGRAM ---
api_id = 1234567          # Thay api_id của bạn
api_hash = 'your_hash'    # Thay api_hash của bạn
target_group = 'sao789fan'

client = TelegramClient('session_render', api_id, api_hash)

async def get_ai_reply(user_msg):
    try:
        prompt = (
            f"Bạn là một người chơi lâu năm trong nhóm Sao789. "
            f"Hãy trả lời tin nhắn sau cực kỳ ngắn gọn, dùng ngôn ngữ dân chơi, thân thiện. "
            f"Dùng các từ như: ae, húp, uy tín, soi cầu, lộc, kkk, bú, căng. "
            f"Tin nhắn: '{user_msg}'"
        )
        response = model.generate_content(prompt)
        return response.text
    except:
        return random.choice(["Húp lộc thôi ae", "Uy tín quá bác", "Kèo này thơm", "Lên là lên"])

@client.on(events.NewMessage(chats=target_group))
async def handler(event):
    # Không tự trả lời mình
    me = await client.get_me()
    if event.sender_id == me.id: return
    
    # Tỷ lệ trả lời 25% để giống người thật
    if random.random() < 0.25:
        # Giả lập thời gian đọc tin (5-15 giây)
        await asyncio.sleep(random.randint(5, 15))
        
        reply_content = await get_ai_reply(event.text)
        
        async with client.action(event.chat_id, 'typing'):
            # Giả lập thời gian gõ chữ
            await asyncio.sleep(len(reply_content) * 0.1)
            await event.reply(reply_content)
            print(f"Đã chat: {reply_content}")

async def bot_main():
    await client.start()
    print("Bot đã online!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    Thread(target=run_web).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot_main())

