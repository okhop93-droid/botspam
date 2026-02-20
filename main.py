import os
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events, errors
from telethon.tl.functions.channels import JoinChannelRequest

# --- CẤU HÌNH (Giữ nguyên của bạn) ---
API_ID = 36437338 
API_HASH = '18d34c7efc396d277f3db62baa078efc'
BOT_TOKEN = '8499499024:AAFSifEjBAKL2BSmanDDlXuRGh93zvZjM78'
ADMIN_ID = 7816353760 

SESSION_DIR = 'sessions'
if not os.path.exists(SESSION_DIR): os.makedirs(SESSION_DIR)

AD_MESSAGE = """
🎁 XOCDIA88 Tặng Ae GiftCode May Mắn Lên Đến 88K
🐶 Mời 2 Bạn Nhận Code Đánh Lên 50K Rút
😁😀😐😁 @xocdia88thuongcoderbot
💫 Lấy Nhiều Acc Mà Bào Nha Anh Chị Em - Rút Ngon Vaii
📱 Code random có thể dồn rút luôn📱
"""

app = Flask('')
@app.route('/')
def home(): return "Hệ thống Clone đang chạy..."
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

master_bot = TelegramClient('master_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@master_bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if event.sender_id != ADMIN_ID: return
    msg = (
        "✅ **Hệ thống Master Bot sẵn sàng!**\n\n"
        "1️⃣ Gửi file `.session` để nạp acc.\n"
        "2️⃣ `/join @linkgroup` : Dàn clone tự tham gia nhóm.\n"
        "3️⃣ `/setmsg [nội dung]` : Đổi tin nhắn quảng cáo.\n"
        "4️⃣ `/spam @linkgroup` : Bắt đầu rải tin."
    )
    await event.reply(msg)

# Nạp file session qua Bot
@master_bot.on(events.NewMessage())
async def handle_docs(event):
    if event.sender_id != ADMIN_ID or not event.document: return
    if event.document.attributes[0].file_name.endswith('.session'):
        path = await event.download_media(file=SESSION_DIR)
        await event.reply(f"📥 Đã nạp clone: `{os.path.basename(path)}`")

# Lệnh cho dàn clone JOIN vào nhóm (Bắt buộc phải join mới spam được)
@master_bot.on(events.NewMessage(pattern='/join'))
async def join_groups(event):
    if event.sender_id != ADMIN_ID: return
    try:
        target = event.text.split(' ', 1)[1]
        sessions = [f for f in os.listdir(SESSION_DIR) if f.endswith('.session')]
        await event.reply(f"🔄 Đang cho {len(sessions)} clone tham gia nhóm {target}...")
        
        for s_file in sessions:
            client = TelegramClient(os.path.join(SESSION_DIR, s_file), API_ID, API_HASH)
            try:
                await client.connect()
                await client(JoinChannelRequest(target))
                await asyncio.sleep(5) # Tránh bị Telegram soi
            except Exception as e:
                print(f"Lỗi join: {e}")
            finally:
                await client.disconnect()
        await event.reply(f"✅ Đã xong lệnh Join.")
    except:
        await event.reply("⚠️ Sai cú pháp. VD: `/join @nhomchemgiovip`")

@master_bot.on(events.NewMessage(pattern='/setmsg'))
async def set_msg(event):
    global AD_MESSAGE
    if event.sender_id != ADMIN_ID: return
    AD_MESSAGE = event.text.split('/setmsg ', 1)[1]
    await event.reply(f"📝 Đã cập nhật nội dung!")

@master_bot.on(events.NewMessage(pattern='/spam'))
async def start_spam(event):
    if event.sender_id != ADMIN_ID: return
    try:
        target_group = event.text.split(' ', 1)[1]
        sessions = [f for f in os.listdir(SESSION_DIR) if f.endswith('.session')]
        await event.reply(f"🚀 Bắt đầu spam {target_group}...")

        for s_file in sessions:
            client = TelegramClient(os.path.join(SESSION_DIR, s_file), API_ID, API_HASH)
            try:
                await client.connect()
                await client.send_message(target_group, AD_MESSAGE)
                await asyncio.sleep(10) 
            except Exception as e:
                await event.reply(f"❌ `{s_file}` lỗi: {e}")
            finally:
                await client.disconnect()
    except:
        await event.reply("⚠️ Sai cú pháp. VD: `/spam @nhomchemgiovip`")

if __name__ == "__main__":
    Thread(target=run_web).start()
    master_bot.run_until_disconnected()
    
