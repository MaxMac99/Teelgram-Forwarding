import os
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

source_chat_ids = []
destination_chat_ids = []


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
    
    global source_chat_ids
    source_chat_ids = []
    source_chat_titles = ""
    for chat_id in chat_answer['source_chat_title']:
        source_chat_ids.append(chat_map[chat_id].id)
        source_chat_titles += chat_id + ", "
    
    global destination_chat_ids
    destination_chat_ids = []
    destination_chat_titles = ""
    for chat_id in chat_answer['destination_chat_title']:
        destination_chat_ids.append(chat_map[chat_id].id)
        destination_chat_titles += chat_id + ", "
    
    print("Forwarding messages from", source_chat_titles[:-2], "to", destination_chat_titles[:-2])


@client.on(events.NewMessage())
async def message_handler(event):
    if event.message.raw_text is not None and event.chat_id in source_chat_ids and not event.message.sender.is_self:
        name = None
        if event.message.sender.first_name is not None and event.message.sender.last_name is not None:
            name = f"{event.message.sender.first_name} {event.message.sender.last_name}"
        elif event.message.sender.first_name is not None:
            name = f"{event.message.sender.first_name}"
        elif event.message.sender.last_name is not None:
            name = f"{event.message.sender.last_name}"
        elif event.message.sender.username is not None:
            name = f"{event.message.sender.username}"
        
        if name is not None:
            info = f"Neue Nachricht von {name}:\n{event.message.raw_text}"
        else:
            info = f"Neue Nachricht:\n{event.message.raw_text}"
        
        for chat_id in destination_chat_ids:
            await client.send_message(chat_id, info)


if __name__ == '__main__':
    try:
        print('(Press Ctrl+C to stop this)')
        client.loop.run_until_complete(prepare())
        client.run_until_disconnected()
    finally:
        client.disconnect()