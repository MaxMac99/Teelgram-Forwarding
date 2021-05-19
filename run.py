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

client = TelegramClient("config/" + SESSION, API_ID, API_HASH).start(PHONE, PASSWORD)

source_chat_ids = {}

def print_chat_rules():
    print("Forwarding messages")
    for source_content in source_chat_ids:
        destination_str = ""
        for destination_content in source_chat_ids[source_content]['destinations']:
            destination_str += destination_content['name'] + ", "
        print(f"{source_chat_ids[source_content]['name']} to {destination_str[:-2]}")


async def prepare():
    dialogs = await client.get_dialogs()
    chat_map = {}
    chat_map_titles = {}
    chat_choices = []
    for dialog in dialogs:
        chat_map[dialog.id] = dialog
        chat_map_titles[dialog.name] = dialog.id
        chat_choices.append({
            'name': dialog.name
        })

    if os.path.exists('config/config.json'):
        with open('config/config.json') as config:
            saved_config = json.load(config)
            for chat in saved_config:
                destinations = []
                source_chat = chat_map[chat['id']]
                for dest_chat in chat['destinations']:
                    destinations.append({"name": chat_map[dest_chat['id']].title, "id": chat_map[dest_chat['id']].id})
                source_chat_ids[source_chat.id] = {
                    "id": source_chat.id,
                    "name": source_chat.title,
                    "destinations": destinations
                }
            print_chat_rules()
    else:
        destination_chat_choices = chat_choices.copy()
        chat_choices.insert(0, "End")
        chat_question_1 = [
            {
                'type': 'list',
                'name': 'source_chat_title',
                'message': 'What chat would you like to copy from?',
                'choices': chat_choices
            }
        ]
        chat_question_2 = [
            {
                'type': 'checkbox',
                'name': 'destination_chat_title',
                'message': 'What chat would you like to forward to?',
                'choices': destination_chat_choices
            }
        ]
        print()
        saved_config = []
        chat_answer_1 = prompt(chat_question_1)
        while chat_answer_1['source_chat_title'] != "End":
            chat = chat_map[chat_map_titles[chat_answer_1['source_chat_title']]]
            destinations = []
            chat_answer_2 = prompt(chat_question_2)
            for chat_id in chat_answer_2['destination_chat_title']:
                dest_chat = chat_map[chat_map_titles[chat_id]]
                destinations.append({"name": dest_chat.title, "id": dest_chat.id})
            source_chat_ids[chat.id] = {
                "id": chat.id,
                "name": chat.title,
                "destinations": destinations
            }
            saved_config.append({
                'id': chat.id,
                'name': chat.title,
                'destinations': [{'id': dest['id'], 'name': dest['name']} for dest in destinations]
            })
            chat_answer_1 = prompt(chat_question_1)
        
        print_chat_rules()
        with open('config/config.json', 'w') as config:
            json.dump(saved_config, config)


if __name__ == '__main__':
    client.loop.run_until_complete(prepare())


@client.on(events.NewMessage(chats=list(source_chat_ids.keys())))
async def message_handler(event):
    try:
        if event.message.raw_text is not None and event.chat_id in source_chat_ids:
            name = None
            if hasattr(event.message.sender, 'first_name') and event.message.sender.first_name is not None and hasattr(event.message.sender, 'last_name') and event.message.sender.last_name is not None:
                name = f"{event.message.sender.first_name} {event.message.sender.last_name}"
            elif hasattr(event.message.sender, 'first_name') and event.message.sender.first_name is not None:
                name = f"{event.message.sender.first_name}"
            elif hasattr(event.message.sender, 'last_name') and event.message.sender.last_name is not None:
                name = f"{event.message.sender.last_name}"
            elif hasattr(event.message.sender, 'username') and event.message.sender.username is not None:
                name = f"{event.message.sender.username}"
            
            if name is not None:
                info = f"<b>{name}</b>:\n{event.message.raw_text}"
            else:
                info = f"<b>Neue Nachricht</b>:\n{event.message.raw_text}"
            
            destinations = source_chat_ids[event.chat_id]['destinations']
            for destination in destinations:
                await client.send_message(destination['id'], info, parse_mode='html')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    try:
        print('(Press Ctrl+C to stop this)')
        client.run_until_disconnected()
    finally:
        client.disconnect()