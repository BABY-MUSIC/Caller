import os
import time
import requests
import subprocess
from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

# ================== CONFIG ==================
API_ID = int(os.getenv("API_ID", "24168862"))       
API_HASH = os.getenv("API_HASH", "916a9424dd1e58ab7955001ccc0172b3")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8288250166:AAFRLjfT3JUCIxVqwGbTMC1D69AeLxHwNNA")
OWNER_ID = int(os.getenv("OWNER_ID", "6657539971"))

REQUIRED_CHANNELS = [
    ("ᴊᴏɪɴ", "https://t.me/Userfindnum_india"),
    ("ᴊᴏɪɴ", "https://t.me/+yf3D2oZeWJNjZDE9"),
    ("ᴊᴏɪɴ", "https://t.me/RadhikaCommunity"), 
    ("ᴊᴏɪɴ", "https://t.me/+KO-NImIfAwM5NDll")
]

CHANNEL_USERNAMES = [
    "Userfindnum_india",
    "Userfindnum_india", 
    "RadhikaCommunity",
    "RadhikaCommunity"
]

START_IMG = "https://files.catbox.moe/2y5o3g.jpg"
API_URL = "https://restless-feather-4eb3.factotask.workers.dev/num-trial-api?num={}"


# ---------------- TIME SYNC -----------------
def sync_time():
    try:
        subprocess.run(['ntpdate', '-s', 'pool.ntp.org'], timeout=10)
        print("✅ Time synced using ntpdate")
    except:
        try:
            subprocess.run(['htpdate', '-s', 'google.com'], timeout=10)
            print("✅ Time synced using htpdate")
        except:
            try:
                response = requests.head('http://google.com', timeout=5)
                if 'date' in response.headers:
                    print(f"ℹ️ Server Time : {response.headers['date']}")
            except:
                print("⚠️ Could not sync time automatically")
    time.sleep(2)


sync_time()

app = Client(
    "NumberInfoBot", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN,
    workers=2,
    sleep_threshold=30
)


# ---------------- CHECK SUB -----------------
async def check_sub(client, user_id):
    for channel_username in CHANNEL_USERNAMES:
        try:
            member = await client.get_chat_member(channel_username, user_id)
            if member.status not in [
                enums.ChatMemberStatus.MEMBER, 
                enums.ChatMemberStatus.ADMINISTRATOR, 
                enums.ChatMemberStatus.OWNER
            ]:
                return False
        except:
            return False
    return True


# ---------------- REPLY KEYBOARD -----------------
def contact_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Share Your Contact", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


# ---------------- HANDLE CONTACT -----------------
@app.on_message(filters.contact)
async def contact_handler(client, message):
    user_id = message.from_user.id
    if not await check_sub(client, user_id):
        channel_buttons = [
            [
                InlineKeyboardButton(f"{REQUIRED_CHANNELS[0][0]}", url=REQUIRED_CHANNELS[0][1]),
                InlineKeyboardButton(f"{REQUIRED_CHANNELS[1][0]}", url=REQUIRED_CHANNELS[1][1])
            ],
            [
                InlineKeyboardButton(f"{REQUIRED_CHANNELS[2][0]}", url=REQUIRED_CHANNELS[2][1]),
                InlineKeyboardButton(f"{REQUIRED_CHANNELS[3][0]}", url=REQUIRED_CHANNELS[3][1])
            ],
            [InlineKeyboardButton("Verify ✅", callback_data="verify_channels")]
        ]
        await message.reply(
            "⚠️ You must join all channels first!",
            reply_markup=InlineKeyboardMarkup(channel_buttons)
        )
        return

    number = str(message.contact.phone_number)[-10:]  # last 10 digit
    await process_number(client, message, number)


# ---------------- HANDLE TEXT -----------------
@app.on_message(filters.text)
async def get_number(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    if not await check_sub(client, user_id):
        channel_buttons = [
            [
                InlineKeyboardButton(f"{REQUIRED_CHANNELS[0][0]}", url=REQUIRED_CHANNELS[0][1]),
                InlineKeyboardButton(f"{REQUIRED_CHANNELS[1][0]}", url=REQUIRED_CHANNELS[1][1])
            ],
            [
                InlineKeyboardButton(f"{REQUIRED_CHANNELS[2][0]}", url=REQUIRED_CHANNELS[2][1]),
                InlineKeyboardButton(f"{REQUIRED_CHANNELS[3][0]}", url=REQUIRED_CHANNELS[3][1])
            ],
            [InlineKeyboardButton("Verify ✅", callback_data="verify_channels")]
        ]
        await message.reply(
            "⚠️ You must join all channels first!",
            reply_markup=InlineKeyboardMarkup(channel_buttons)
        )
        return

    if text.isdigit() and len(text) == 10:
        await process_number(client, message, text)
    else:
        await message.reply("❌ Please provide a valid 10-digit number.", reply_markup=contact_keyboard())


# ---------------- PROCESS NUMBER -----------------
async def process_number(client, message, number):
    await message.reply_chat_action(enums.ChatAction.TYPING)
    url = API_URL.format(number)

    try:
        response = requests.get(url, timeout=10).json()
        if not response:
            await message.reply("⚠️ No details found for this number.")
            return

        all_results = ""
        for i, data in enumerate(response, start=1):
            result = f"""
📌 **Result :- {i}**

👤 Name :- `{data.get('name', 'N/A')}`
👨‍👦 Father :- `{data.get('father_name', 'N/A')}`
📱 Mobile :- `{data.get('mobile', 'N/A')}`
📞 Alt Mobile :- `{data.get('alt_mobile', 'N/A')}`
🌐 Circle :- `{data.get('circle', 'N/A')}`
🏠 Address :- `{data.get('address', 'N/A')}`
🆔 Aadhar :- `{data.get('id_number', 'N/A')}`
✉️ Email :- `{data.get('email', 'N/A')}`
━━━━━━━━━━━━━━━
"""
            all_results += result

        if len(all_results) > 4000:
            for chunk in [all_results[i:i+4000] for i in range(0, len(all_results), 4000)]:
                await message.reply(chunk)
        else:
            await message.reply(all_results)

    except Exception:
        await message.reply("⚠️ No details found or error occurred.")


# ---------------- VERIFY CALLBACK -----------------
@app.on_callback_query(filters.regex("verify_channels"))
async def verify_channels(client, callback_query):
    if not await check_sub(client, callback_query.from_user.id):
        await callback_query.answer("❌ Still not joined all channels!", show_alert=True)
        return
    await callback_query.answer("✅ Verification successful!", show_alert=True)
    await callback_query.message.reply("📩 Now send me a 10-digit number or share your contact.", 
                                       reply_markup=contact_keyboard())


# ---------------- RUN -----------------
if __name__ == "__main__":
    print("🤖 Number Info Finder Bot is starting...")
    app.run()
