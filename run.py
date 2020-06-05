import os
import sys
import logging
import argparse
from PyInquirer import prompt, Validator, ValidationError
from telegram.client import Telegram


if __name__ == '__main__':
    root = logging.getLogger()
    root.setLevel(logging.ERROR)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    parser = argparse.ArgumentParser()
    parser.add_argument('--api_id', help='API ID')
    parser.add_argument('--api_hash', help='API Hash')
    parser.add_argument('--phone', help='Your phone number')
    args = parser.parse_args()

    db_encryption_key = os.getenv("TELEGRAM_DB_ENCRYPTION_KEY", "IAmJustAKeyPleaseChangeMeNow")

    api_question = []
    if args.phone is None:
        api_question.append({
            'type': 'input',
            'name': 'phone',
            'message': 'What is you phone number?'
        })
    else:
        phone = args.phone
    if args.api_hash is None:
        api_question.append({
            'type': 'input',
            'name': 'api_hash',
            'message': 'What is you API Hash?'
        })
    else:
        phone = args.api_hash
    if args.api_id is None:
        api_question.append({
            'type': 'input',
            'name': 'api_id',
            'message': 'What is you API ID?'
        })
    else:
        phone = args.api_id
    
    print()
    if len(api_question):
        api_answer = prompt(api_question)
        if 'api_id' in api_answer:
            api_id = api_answer['api_id']
        if 'api_hash' in api_answer:
            api_hash = api_answer['api_hash']
        if 'phone' in api_answer:
            phone = api_answer['phone']

    tg = Telegram(
        api_id, api_hash, db_encryption_key, phone
    )

    tg.login()

    result = tg.get_chats(9223372036854775807)
    result.wait()

    if result.error:
        print(f'get chats error: {result.error_info}')

    chats = result.update['chat_ids']

    result = tg.get_me()
    result.wait()

    my_id = result.update['id']
    
    chat_map = {}
    chat_choices = []
    for chat_id in chats:
        r = tg.get_chat(chat_id)
        r.wait()
        chat_map[r.update['title']] = r.update
        chat_choices.append({
            'name': r.update['title']
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
    chat_answer = prompt(chat_question)
    
    source_chat_ids = []
    for chat_id in chat_answer['source_chat_title']:
        source_chat_ids.append(chat_map[chat_id]['id'])
    
    destination_chat_ids = []
    for chat_id in chat_answer['destination_chat_title']:
        destination_chat_ids.append(chat_map[chat_id]['id'])

    def message_handler(update):
        message = update['message']
        chat_id = message['chat_id']
        sender_id = message['sender_user_id']

        if chat_id in source_chat_ids:
            message_content = message['content']
            message_text = message_content.get('text', {}).get('text', '')

            if message_text != '':
                for dest_chat_id in destination_chat_ids:
                    result = tg.send_message(dest_chat_id, message_text)
                    result.wait()
                    if result.error:
                        print(f'send message error: {result.error_info}')

    tg.add_message_handler(message_handler)
    tg.idle()
