import os
import json
import asyncio

from telethon import TelegramClient, events
from PyInquirer import prompt, Validator, ValidationError

SESSION = "forwarding"
API_ID = os.getenv('TELEGRAM_API_ID', None)
API_HASH = os.getenv('TELEGRAM_API_HASH', None)
PHONE = os.getenv('TELEGRAM_PHONE', None)
PASSWORD = os.getenv('TELEGRAM_PASSWORD', None)

if API_ID is None:
    raise Exception("Could not find API ID in environment")

if API_HASH is None:
    raise Exception("Could not find API Hash in environment")

if PHONE is None:
    raise Exception("Could not find Phone number in environment")

client = TelegramClient(SESSION, API_ID, API_HASH).start(PHONE, PASSWORD)


async def prepare():
    dialogs = await client.get_dialogs()
    chat_map = {}
    chat_choices = []
    for dialog in dialogs:
        chat_map[dialog.title] = dialog
        chat_choices.append({
            'name': dialog.title
        })
    chat_question = [
        {
            'type': 'checkbox',
            'name': 'source_chat_title',
            'message': 'What chat would you like to copy from?',
            'choices': chat_choices
        },
        {
            'type': 'checkbox',
            'name': 'destination_chat_title',
            'message': 'What chat would you like to forward to?',
            'choices': chat_choices
        }
    ]
    print()
    chat_answer = prompt(chat_question)
    
    source_chat_ids = []
    for chat_id in chat_answer['source_chat_title']:
        chat = chat_map[chat_id]
        source_chat_ids.append({"name": chat.title, "id": chat.id})
    
    destination_chat_ids = []
    for chat_id in chat_answer['destination_chat_title']:
        chat = chat_map[chat_id]
        destination_chat_ids.append({"name": chat.title, "id": chat.id})
    
    with open('config.json', 'w') as config:
        json.dump({"source": source_chat_ids, "destination": destination_chat_ids}, config)
    

if __name__ == '__main__':
    try:
        print('(Press Ctrl+C to stop this)')
        client.loop.run_until_complete(prepare())
    finally:
        client.disconnect()