import os
from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins
from dotenv import load_dotenv
import logging

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
TARGET_CHAT_ID = int(os.getenv('TARGET_CHAT_ID'))  # Your personal chat ID or another target chat ID
TARGET_BOT_USERNAME = '@MaestroSniperBot'  # The target bot username

# Initialize the Telegram client
client = TelegramClient('session_name', API_ID, API_HASH)

async def is_user_admin(chat, user_id):
    try:
        admins = await client.get_participants(chat, filter=ChannelParticipantsAdmins)
        return any(admin.id == user_id for admin in admins)
    except Exception as e:
        logging.error(f"Error fetching participants: {e}")
        return False

async def main():
    try:
        # Manually handling the sign-in process
        await client.connect()
        if not await client.is_user_authorized():
            result = await client.send_code_request(PHONE_NUMBER)
            print("Code sent...")
            phone_code = input("Please enter the verification code: ")
            await client.sign_in(PHONE_NUMBER, phone_code, phone_code_hash=result.phone_code_hash)
        
        print("Client Created and Logged In")

        @client.on(events.NewMessage)
        async def handler(event):
            chat = await event.get_chat()
            sender = await event.get_sender()
            text = event.raw_text

            chat_title = chat.title if hasattr(chat, 'title') else 'private chat'
            logging.info(f'Message from user {sender.id} in {chat_title}: "{text}"')

            if event.is_group:
                if await is_user_admin(chat, sender.id):
                    logging.info(f'User {sender.id} is an admin')
                    if text.lower().startswith("ca"):
                        extracted_string = text[2:].strip()  # Adjust index to extract right after "CA"
                        await client.send_message(TARGET_BOT_USERNAME, extracted_string)
                        logging.info(f'Forwarded message to {TARGET_BOT_USERNAME}: "{extracted_string}"')
                    else:
                        logging.info('Message does not start with "CA"')
                else:
                    logging.info(f"User {sender.id} is not an admin in {chat_title}")

        # Run the client until disconnected
        await client.run_until_disconnected()
    except Exception as e:
        logging.error(f"Error: {e}")

with client:
    client.loop.run_until_complete(main())
