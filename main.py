import os
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events, errors
from telethon.tl.functions.channels import JoinChannelRequest

# --- CẤU HÌNH ---
API_ID = 36437338 
API_HASH = '18d34c7efc396d277f3db62baa078efc'
BOT_TOKEN = '8499499024:AAFSifEjBAKL2BSmanDDlXuRGh93zvZjM78'
ADMIN_ID = 7816353760 

SESSION_DIR = 'sessions'
if not os.path.exists(SESSION_DIR): 
    os.makedirs(SESSION_DIR)

AD_MESSAGE = """
🎁 XOCDIA88 Tặng Ae GiftCode May Mắn Lên Đến 88K
🐶 Mời 2 Bạn Nhận Code Đánh Lên 50K Rút
😁😀😐😁 @xocdia88thuongcoderbot
💫 Lấy Nhiều Acc Mà Bào Nha Anh Chị Em - Rút Ngon Vaii
📱 Code random có thể dồn rút luôn📱
"""

# --- WEB SERVER (GIỮ SỐNG RENDER) ---
app = Flask('')

@app.route('/')
def home(): 
    return "Hệ thống Clone đang chạy..."

def run_web():
    # Render sử dụng cổng từ biến môi trường PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- KHỞI TẠO EVENT LOOP VÀ BOT ---
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
master_bot = TelegramClient('master_bot', API_ID, API_HASH)

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

@master_bot.on(events.NewMessage())
async def handle_docs(event):
    if event.sender_id != ADMIN_ID or not event.document: return
    if event.document.attributes[0].file_name.endswith('.session'):
        path = await event.download_media(file=SESSION_DIR)
        await event.reply(f"📥 Đã nạp clone: `{os.path.basename(path)}`")

@master_bot.on(events.NewMessage(pattern='/join'))
async def join_groups(event):
    if event.sender_id != ADMIN_ID: return
    try:
        parts = event.text.split(' ', 1)
        if len(parts) < 2: return
        target = parts[1]
        sessions = [f for f in os.listdir(SESSION_DIR) if f.endswith('.session')]
        await event.reply(f"🔄 Đang cho {len(sessions)} clone tham gia nhóm {target}...")
        
        for s_file in sessions:
            client = TelegramClient(os.path.join(SESSION_DIR, s_file), API_ID, API_HASH)
            try:
                await client.connect()
                await client(JoinChannelRequest(target))
                await asyncio.sleep(5) 
            except Exception as e:
                print(f"Lỗi join {s_file}: {e}")
            finally:
                await client.disconnect()
        await event.reply(f"✅ Đã thực hiện xong lệnh Join.")
    except Exception as e:
        await event.reply(f"❌ Lỗi: {str(e)}")

@master_bot.on(events.NewMessage(pattern='/setmsg'))
async def set_msg(event):
    global AD_MESSAGE
    if event.sender_id != ADMIN_ID: return
    parts = event.text.split('/setmsg ', 1)
    if len(parts) > 1:
        AD_MESSAGE = parts[1]
        await event.reply(f"📝 Đã cập nhật nội dung quảng cáo!")

@master_bot.on(events.NewMessage(pattern='/spam'))
async def start_spam(event):
    if event.sender_id != ADMIN_ID: return
    try:
        parts = event.text.split(' ', 1)
        if len(parts) < 2: return
        target_group = parts[1]
        sessions = [f for f in os.listdir(SESSION_DIR) if f.endswith('.session')]
        
        if not sessions:
            await event.reply("❌ Không có tài khoản nào trong hệ thống!")
            return

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
        await event.reply(f"🏁 Đã hoàn thành đợt spam.")
    except Exception as e:
        await event.reply(f"⚠️ Lỗi cú pháp hoặc hệ thống: {str(e)}")

async def main():
    # Khởi chạy bot quản lý
    await master_bot.start(bot_token=BOT_TOKEN)
    print("Master Bot đã sẵn sàng trên Render!")
    await master_bot.run_until_disconnected()

if __name__ == "__main__":
    # Chạy Web Server bằng thread riêng để không chặn Bot
    Thread(target=run_web, daemon=True).start()
    # Chạy loop chính
    loop.run_until_complete(main())
    
