import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

# Замените на ваши данные
API_TOKEN = ''
AUTH_TOKEN = ''
EVENT_ID = 0
USER_ID = ''  # Укажите здесь ID пользователя
CHECK_INTERVAL = 61  # Интервал проверки в секундах
# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

def get_event_data(event_id, auth_token):
    url = f"https://api.timepad.ru/v1/events/{event_id}"
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        
        is_registration_open = data.get("registration_data", {}).get("is_registration_open")
        tickets_total = data.get("registration_data", {}).get("tickets_total")
        ticket_limit = data.get("tickets_limit")
        status = data.get("status")
        
        ticket_type = data.get("ticket_types", [])
        tickets_info = []
        for ticket in ticket_type:
            info = {
            'id': ticket.get('id'),
            'name': ticket.get('name'),
            'remaining': ticket.get('remaining', 0),  # Если 'remaining' нет, устанавливаем 0
            'status': ticket.get('status')
            }
            tickets_info.append(info)
            
        return {
            "is_registration_open": is_registration_open,
            "tickets_total": tickets_total,
            "ticket_limit": ticket_limit,
            "status": status,
            "tickets": tickets_info
        }
        
        
    else:
        return None

async def check_event():
    
    while True:
        
        event_data = get_event_data(EVENT_ID, AUTH_TOKEN)

        if event_data:
            # Проверка на изменение
            if (event_data["is_registration_open"] != False): await bot.send_message(USER_ID, f"is_registration_open = {event_data['is_registration_open']}")
            elif event_data["tickets_total"] != 1041: await bot.send_message(USER_ID, f"tickets_total = {event_data['tickets_total']}\n")
            elif event_data["ticket_limit"] != 0: await bot.send_message(USER_ID, f"ticket_limit = {event_data['ticket_limit']}\n")
            elif event_data["status"] != "ok": await bot.send_message(USER_ID, f"status = {event_data['status']}")
            else: print("Билета нету |0|")
            
            i = 1            
            for ticket in event_data['tickets']: 
                if ticket['remaining'] != 0: await bot.send_message(USER_ID, f"ticket-id = {ticket['id']}\nticket-name = {ticket['name']}\nticket-remaining = {ticket['remaining']}")
                elif ticket['status'] not in ("crowd", "closed"): await bot.send_message(USER_ID, f"ticket-id = {ticket['id']}\nticket-name = {ticket['name']}\nticket-status = {ticket['status']}")
                else: print(f"Билета нету |{i}|")   
                i += 1
                
        else:
            await bot.send_message(USER_ID, "ОШИБКА ПРИ ПОЛУЧЕНИИ ДАННЫХ")
            print("Ошибка при получении данных")

        await asyncio.sleep(CHECK_INTERVAL)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Бот запущен и будет проверять события каждую минуту.")

async def on_startup(dp):
    asyncio.create_task(check_event())

if __name__ == '__main__':
    # Запускаем бота и задачу проверки событий
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
    