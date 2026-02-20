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
if not os.path.exists(SESSION_DIR): os.makedirs(SESSION_DIR)

AD_MESSAGE = """
🎁 XOCDIA88 Tặng Ae GiftCode May Mắn Lên Đến 88K
🐶 Mời 2 Bạn Nhận Code Đánh Lên 50K Rút
😁😀😐😁 @xocdia88thuongcoderbot
💫 Lấy Nhiều Acc Mà Bào Nha Anh Chị Em - Rút Ngon Vaii
📱 Code random có thể dồn rút luôn📱
"""

# Biến kiểm soát trạng thái spam
is_spamming = False

app = Flask('')
@app.route('/')
def home(): return "Hệ thống Clone đang chạy..."
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
master_bot = TelegramClient('master_bot', API_ID, API_HASH)

@master_bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if event.sender_id != ADMIN_ID: return
    msg = (
        "✅ **Hệ thống Master Bot sẵn sàng!**\n\n"
        "1️⃣ `/add` : Nạp số điện thoại mới.\n"
        "2️⃣ `/join @link` : Dàn clone vào nhóm.\n"
        "3️⃣ `/spam @link` : Bắt đầu spam liên tục (10s/lần).\n"
        "4️⃣ `/stop` : Dừng hệ thống spam."
    )
    await event.reply(msg)

# --- LỆNH DỪNG SPAM ---
@master_bot.on(events.NewMessage(pattern='/stop'))
async def stop_spam(event):
    global is_spamming
    if event.sender_id != ADMIN_ID: return
    is_spamming = False
    await event.reply("🛑 Đã nhận lệnh dừng spam!")

# --- CHỨC NĂNG SPAM LIÊN TỤC 10S ---
@master_bot.on(events.NewMessage(pattern='/spam'))
async def start_spam(event):
    global is_spamming
    if event.sender_id != ADMIN_ID: return
    
    try:
        target = event.text.split(' ', 1)[1]
        sessions = [f for f in os.listdir(SESSION_DIR) if f.endswith('.session')]
        
        if not sessions:
            await event.reply("❌ Không có tài khoản nào!")
            return

        is_spamming = True
        await event.reply(f"🚀 Bắt đầu spam liên tục vào {target} (Mỗi 10s một lượt)...")

        while is_spamming:
            for s_file in sessions:
                if not is_spamming: break # Kiểm tra lệnh dừng ngay trong lượt gửi
                
                c = TelegramClient(os.path.join(SESSION_DIR, s_file), API_ID, API_HASH)
                try:
                    await c.connect()
                    await c.send_message(target, AD_MESSAGE)
                    print(f"✅ Acc {s_file} đã gửi.")
                except Exception as e:
                    print(f"❌ Lỗi acc {s_file}: {e}")
                finally:
                    await c.disconnect()
            
            # Sau khi cả dàn gửi xong 1 lượt, nghỉ 10s rồi lặp lại
            if is_spamming:
                await asyncio.sleep(10) 
                
    except Exception as e:
        await event.reply(f"⚠️ Lỗi: {str(e)}")

# --- GIỮ NGUYÊN CÁC PHẦN CÒN LẠI (ADD, JOIN, HANDLE_DOCS) ---
@master_bot.on(events.NewMessage(pattern='/add'))
async def add_account(event):
    if event.sender_id != ADMIN_ID: return
    async with master_bot.conversation(event.chat_id) as conv:
        await conv.send_message("📞 Nhập số (+84...):")
        phone = (await conv.get_response()).text.strip()
        s_name = os.path.join(SESSION_DIR, f"{phone.replace('+', '')}.session")
        client = TelegramClient(s_name, API_ID, API_HASH)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                await client.send_code_request(phone)
                await conv.send_message("📩 Nhập OTP:")
                otp = (await conv.get_response()).text.strip()
                try: await client.sign_in(phone, otp)
                except errors.SessionPasswordNeededError:
                    await conv.send_message("🔒 Nhập Pass 2FA:")
                    pwd = (await conv.get_response()).text.strip()
                    await client.sign_in(password=pwd)
            await conv.send_message(f"✅ Thành công: {phone}")
        except Exception as e: await conv.send_message(f"❌ Lỗi: {e}")
        finally: await client.disconnect()

@master_bot.on(events.NewMessage())
async def handle_docs(event):
    if event.sender_id != ADMIN_ID or not event.document: return
    if event.document.attributes[0].file_name.endswith('.session'):
        path = await event.download_media(file=SESSION_DIR)
        await event.reply(f"📥 Đã nhận file session: `{os.path.basename(path)}`")

@master_bot.on(events.NewMessage(pattern='/join'))
async def join_groups(event):
    if event.sender_id != ADMIN_ID: return
    try:
        target = event.text.split(' ', 1)[1]
        sessions = [f for f in os.listdir(SESSION_DIR) if f.endswith('.session')]
        await event.reply(f"🔄 {len(sessions)} clone đang vào nhóm...")
        for s_file in sessions:
            c = TelegramClient(os.path.join(SESSION_DIR, s_file), API_ID, API_HASH)
            try:
                await c.connect()
                await c(JoinChannelRequest(target))
                await asyncio.sleep(2)
            except: pass
            finally: await c.disconnect()
        await event.reply(f"✅ Đã xong lệnh Join.")
    except: await event.reply("Sai cú pháp `/join @link`")

async def main():
    await master_bot.start(bot_token=BOT_TOKEN)
    print("Bot online!")
    await master_bot.run_until_disconnected()

if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    loop.run_until_complete(main())
