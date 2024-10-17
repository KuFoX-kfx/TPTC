import asyncio
import requests
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor




### API Tokens
## Replace the value with your own
# TG Bot API | Replace the value with your own
TG_API_TOKEN = """API_KEY"""
# TimePad API | Replace the value with your own
TIMEPAD_API_TOKEN = """API_KEY"""

### TG values
## Replace the value with your own
# Your TG ID
USER_ID = 0 

### Timepad values
## Replace the value with your own
# Event ID | # Replace the value with your own
EVENT_ID = 0
# Change value in connection with your event
TICKET_TOTAL = 0

## Don`t change if it is not required
# Is registration open
IS_REGISTRATION_OPEN = False
# Ticket limit for sale?
TICKET_LIMIT = 0
# Status of event?
STATUS = "ok"
# The number of tickets for which notifications are not received
TICKET_REMAINIG = 0

### Programm values
## Don`t change if it is not required
# Check interval (seconds) | Don`t set value less 60
CHECK_INTERVAL = 61  




bot = Bot(token=TG_API_TOKEN)
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
            'remaining': ticket.get('remaining', None),  # If there is no 'remaining', set None
            'status': ticket.get('status')
            }
            tickets_info.append(info)
            
        return {
            "Status" : True,
            "Status_code" : response.status_code,
            "Status_reason" : response.reason,
            "Data" : {
            "is_registration_open": is_registration_open,
            "tickets_total": tickets_total,
            "ticket_limit": ticket_limit,
            "status": status,
            "tickets": tickets_info
            }
            }
        
    elif response.status_code != 200:
        return {
            "Status" : False,
            "Status_code" : response.status_code,
            "Status_reason" : response.reason,
            "Data" : response.json()
        }
        
    else:
        return {
            "Status" : None,
        }
        

async def check_event():
    
    while True:
        
        event_data = get_event_data(EVENT_ID, TIMEPAD_API_TOKEN)

        if event_data['Status'] == True:
            message = ("")
            msg = ("")
            # Check change
            if event_data['Data']['is_registration_open'] != IS_REGISTRATION_OPEN: msg += (f"Is Registration Open = {event_data['Data']['is_registration_open']}\n")
            else: print("No ticket |1|")
            if event_data['Data']["tickets_total"] != TICKET_TOTAL: msg += (f"Tickets Total = {event_data['Data']['tickets_total']}\n")
            else: print("No ticket |2|")
            if event_data['Data']["ticket_limit"] != TICKET_LIMIT: msg += (f"Ticket Limit = {event_data['Data']['ticket_limit']}\n")
            else: print("No ticket |3|")
            if event_data['Data']["status"] != STATUS: msg += (f"Status = {event_data['Data']['status']}\n")
            else: print("No ticket |4|")
            
            if msg != "":
                message = (f"```TPTC_Event-{EVENT_ID}\n{msg}```")
                
            
            i = 5
            for ticket in event_data['Data']['tickets']: 
                if ticket['status'] != "closed" and ticket['status'] != "late":
                    if ticket['status'] != "crowd" and (ticket['remaining'] != 0 or ticket['remaining'] != None):
                        message += (f"```TPTC_Ticket-{ticket['id']}\nID = {ticket['id']}\nName = {ticket['name']}\nRemaining = {ticket['remaining']}\nStatus = {ticket['status']}```")
                print(f"No ticket |{i}|")   
                i += 1
                
            # Send message to TG about find someone
            if message != "":
                await bot.send_message(USER_ID, message, parse_mode="MARKDOWN")
        elif event_data['Status'] == False:
            # Send message when data error
            await bot.send_message(USER_ID, f"*ERROR RECEIVING DATA*\n\nCODE: `{event_data['Status_code']}`\nREASON: `{event_data['Status_reason']}`\nANSWER:\n```TPTC_(TimePad-Tickets-Checker)_By-KuFoX\n{event_data['Data']}```", parse_mode="MARKDOWN")


        await asyncio.sleep(CHECK_INTERVAL)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Bot work")

async def on_startup(dp):
    asyncio.create_task(check_event())

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
    