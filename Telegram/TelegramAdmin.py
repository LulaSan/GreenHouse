from requests.sessions import Request
from telegram.ext import Updater
import os
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler,Filters,MessageHandler
from telegram import InlineKeyboardButton,ReplyKeyboardMarkup, InlineKeyboardMarkup, Update
import telepot
import json
from pprint import pprint
import requests

# login funziona -> cambiare solo LOG id list per admin (ora uso i log id dei farmer)
# display delle greenhouse e selezione -> OK
# arrivato a LEVEL1 statistiche ok

SIGNIN, ADMIN , ADMIN_TYPING, ADMIN_TYPING_2, ADMIN_TYPING_3, LEVEL1= range(6)
CATALOG = "c:/Users/Claudio Mariuzzo/Desktop/Telegram progetto/telegram_catalog.json"
SERVER = "http://localhost:2000" #teoricamente leggere da un file JSON

### !!!!!!!!!!!!!!!!!!!!!!!!!!! da modificare nel caso in cui ci siano più greenhose !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
listaAdmin=json.loads(requests.get(url=SERVER+"/farmers").text)
greenhousesinfo = json.loads(requests.get(url=SERVER+f"/greenhouses").text) 
greenhouselist = [] 
greenhouselist.append(greenhousesinfo[0]["NAME"])
greenhouse_id = greenhousesinfo[0]["GREENHOUSE_ID"]
############################### Bot ############################################

def start(update: Update, context: CallbackContext) -> int:
  user = update.message.from_user
  
  fp=open(CATALOG,"r")
  catalog=json.load(fp)
  loggedUsers=catalog["LOGGED_USERS"]
  fp.close()
  new=0
  newid=str(user.id)
  for i in range(len(loggedUsers)):
    if newid in loggedUsers[i].values() :
      update.message.reply_text(f"Hi, welcome back")
      new=1
  if new==0:
    newUser={"CHATID":newid, "TYPE": "","LOGID":""}
    loggedUsers.append(newUser)
    update.message.reply_text(f"Hey, it seems that you are new here! Welcome!")

  update_catalog(loggedUsers)
  update.message.reply_text(main_menu_message(),reply_markup=main_menu_keyboard())

def main_menu(update: Update, context: CallbackContext) -> int:
    update.callback_query.message.edit_text(main_menu_message(),reply_markup=main_menu_keyboard())

def first_menu(update: Update, context: CallbackContext) -> int:
    update.callback_query.message.edit_text(first_menu_message(),reply_markup=first_menu_keyboard())

def sign_in(update: Update, context: CallbackContext) -> int:

  tipo=update.callback_query.data[-1]
  fp=open(CATALOG,'r')
  catalog=json.load(fp)
  fp.close()
  loggedUsers=catalog["LOGGED_USERS"]
  oldid=str(update.effective_chat["id"])
  for i in range(len(loggedUsers)):
    if oldid== loggedUsers[i]["CHATID"]:
      loggedUsers[i]["TYPE"]=str(tipo)
      update_catalog(loggedUsers)
      pprint(loggedUsers)

  update.callback_query.message.edit_text(f"Ok now log in write your id ")

  return SIGNIN

def sign_in_credenziali(update: Update, context: CallbackContext) -> int:
    pprint("sto entrando del sign_in_credd")
    text = update.message.text # splitto il testo
    
    #salvo il LOG ID dell'utente
    fp=open(CATALOG,'r')
    catalog=json.load(fp)
    fp.close()
    loggedUsers=catalog["LOGGED_USERS"]
    oldid=str(update.effective_chat["id"])
    trovato=0

    # METTERE LA LISTA APPROPIATA PER GLI ADMIN
    for i in range(len(listaAdmin)):
      if text == listaAdmin[i]['FARMER_ID']:
        pprint(listaAdmin[i])
        trovato=1
        user_data=context.user_data # li salvo o qui
        user_data["LOGID"]= text
        pprint(user_data)

        for j in range(len(loggedUsers)):  # o qui
          if oldid == loggedUsers[j]["CHATID"]:
            loggedUsers[j]["LOGID"]=str(text)
            update_catalog(loggedUsers)
            pprint(loggedUsers)
            
        #display greenhouse list
        pprint(greenhouselist)
        update.message.reply_text(text=f"\nBenvenuto!\nEcco le greenhouse disponibili \n{greenhouselist}\nA quale greenhouse sei interessato?\n")
        return ADMIN

    if trovato==0:
      update.message.reply_text('LOG_ID sbagliato, riprova')
      return SIGNIN

def update_catalog(loggedUsers):
  fp=open(CATALOG,'r')
  catalog=json.load(fp)
  fp.close()
  catalog["LOGGED_USERS"]=loggedUsers
  json.dump(catalog,open(CATALOG,"w"),indent=4)
                  
def done(update: Update, _: CallbackContext) -> int:
    update.message.reply_text("niente")

def id_greenhouse(update: Update, context: CallbackContext) -> int:
      text = update.message.text # splitto il testo
      if text in greenhouselist :
        update.message.reply_text(text=f"Bene! seleziona l'operazione che vuoi svolgere:",reply_markup=first_menu_keyboard())
        return LEVEL1
      else:
        update.message.reply_text(text=f"La greenhouse scelta non corrisponde, riprovare.")
        return ADMIN
      #se verificato-> return nuovo MENU
      #altrimenti return ADMIN e update.message.reply_text('LOG_ID sbagliato, riprova')

# funzioni primo menu:
def Statistics(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text("Cosa vuoi fare?",reply_markup=Statistics_keyboard())
  return LEVEL1


def NewParametersGreenhouse(update: Update, context: CallbackContext) -> int:
  text = update.message.text.split(" ")
  greenhouse = json.loads(requests.get(url=f"http://localhost:2000/greenhouses/{greenhouse_id}").text)

  if text[0] == "Principale":
    update.message.reply_text('Scegli tra:', reply_markup=first_menu_keyboard())
    return LEVEL1

  elif text[0] == "1":
    #greenhouse[0]["THRESHOLD_HUMID_MIN"]= int(text[1])
    new_value = {"THRESHOLD_HUMID_MIN": int(text[1])}
    res = requests.post(SERVER+f"/greenhouses/{greenhouse_id}",json=new_value)

    if res.status_code == 200:
      update.message.reply_text(text="New threshold updated")
      keyboard = [[
          InlineKeyboardButton("Tornare al menu principale", callback_data="main"),
          ]]
      reply_markup = InlineKeyboardMarkup(keyboard)
      update.message.reply_text(text="Torna al menu principale", reply_markup=reply_markup)
      return LEVEL1

    else:
      update.message.reply_text(text="Parametro non aggiornato, problema con il server riprovare più tardi")
      return ADMIN_TYPING_2
       
  elif text[0] == "2":
    new_value = {"THRESHOLD_HUMID_MAX": int(text[1])}
    res = requests.post(SERVER+f"/greenhouses/{greenhouse_id}",json=new_value)

    if res.status_code == 200:
      update.message.reply_text(text="New threshold updated")
      keyboard = [[
          InlineKeyboardButton("Tornare al menu principale", callback_data="main"),
          ]]
      reply_markup = InlineKeyboardMarkup(keyboard)
      update.message.reply_text(text="Torna al menu principale", reply_markup=reply_markup)
      return LEVEL1
      
    else:
      update.message.reply_text(text="Parametro non aggiornato, problema con il server riprovare più tardi")
      return ADMIN_TYPING_2

  elif text[0] == "3":
    new_value = {"THRESHOLD_BRIGHT_MIN": int(text[1])}
    res = requests.post(SERVER+f"/greenhouses/{greenhouse_id}",json=new_value)

    if res.status_code == 200:
      update.message.reply_text(text="New threshold updated")
      keyboard = [[
          InlineKeyboardButton("Tornare al menu principale", callback_data="main"),
          ]]
      reply_markup = InlineKeyboardMarkup(keyboard)
      update.message.reply_text(text="Torna al menu principale", reply_markup=reply_markup)
      return LEVEL1
      
    else:
      update.message.reply_text(text="Parametro non aggiornato, problema con il server riprovare più tardi")
      return ADMIN_TYPING_2
  elif text[0] == "4":
    new_value = {"THRESHOLD_BRIGHT_MAX": int(text[1])}
    res = requests.post(SERVER+f"/greenhouses/{greenhouse_id}",json=new_value)

    if res.status_code == 200:
      update.message.reply_text(text="New threshold updated")
      keyboard = [[
          InlineKeyboardButton("Tornare al menu principale", callback_data="main"),
          ]]
      reply_markup = InlineKeyboardMarkup(keyboard)
      update.message.reply_text(text="Torna al menu principale", reply_markup=reply_markup)
      return LEVEL1
      
    else:
      update.message.reply_text(text="Parametro non aggiornato, problema con il server riprovare più tardi")
      return ADMIN_TYPING_2
  elif text[0] == "5":
    new_value = {"THRESHOLD_TEMPER_MIN": int(text[1])}
    res = requests.post(SERVER+f"/greenhouses/{greenhouse_id}",json=new_value)

    if res.status_code == 200:
      update.message.reply_text(text="New threshold updated")
      keyboard = [[
          InlineKeyboardButton("Tornare al menu principale", callback_data="main"),
          ]]
      reply_markup = InlineKeyboardMarkup(keyboard)
      update.message.reply_text(text="Torna al menu principale", reply_markup=reply_markup)
      return LEVEL1
      
    else:
      update.message.reply_text(text="Parametro non aggiornato, problema con il server riprovare più tardi")
      return ADMIN_TYPING_2
  elif text[0] == "6":
    new_value = {"THRESHOLD_TEMPER_MAX": int(text[1])}
    res = requests.post(SERVER+f"/greenhouses/{greenhouse_id}",json=new_value)

    if res.status_code == 200:
      update.message.reply_text(text="New threshold updated")
      keyboard = [[
          InlineKeyboardButton("Tornare al menu principale", callback_data="main"),
          ]]
      reply_markup = InlineKeyboardMarkup(keyboard)
      update.message.reply_text(text="Torna al menu principale", reply_markup=reply_markup)
      return LEVEL1
      
    else:
      update.message.reply_text(text="Parametro non aggiornato, problema con il server riprovare più tardi")
      return ADMIN_TYPING_2
  else:
    update.message.reply_text('Comando non valido, riprovare')
    return ADMIN_TYPING_2
 


def Actuators(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text("Cosa vuoi fare?",reply_markup=actuator_control_keyboard())
  return LEVEL1


# funzioni secondo livello:
def ThingsBoard(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text(text="Ecco il link di thingsboard: ")
  keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data="main"),
            InlineKeyboardButton("Last menu", callback_data="b1_1")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
  update.callback_query.message.reply_text(text="Cosa vuoi fare?", reply_markup=reply_markup)
  return LEVEL1

def NewThreshold_period(update: Update, context: CallbackContext) -> int:
  user_data=context.user_data
  adminid=user_data["LOGID"]
  text = update.message.text.split(" ")
  
  if text[0] == "Principale":
    update.message.reply_text('Scegli tra:', reply_markup=first_menu_keyboard())
    return LEVEL1
  elif text[0] != "Principale" and text[0] != "periodo":
    update.message.reply_text('Comando non valido, riprovare')
    return ADMIN_TYPING
  else:
    
    res = requests.post(SERVER+f"/statistic/water_period/{text[1]}")
    if res.status_code == 200:
      update.message.reply_text(text="New threshold updated")
    else:
      update.message.reply_text(text="Parametro non aggiornato, problema con il server riprovare più tardi")
      return ADMIN_TYPING

    keyboard = [
          [
              InlineKeyboardButton("Tornare al menu principale", callback_data="main"),
              InlineKeyboardButton("Torna al menù precedente", callback_data="b1_1")
          ]
      ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text="Cosa vuoi fare?", reply_markup=reply_markup    )
  return LEVEL1

def OpenWindows(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text("Finestra aperta")
  ### comando che attiva la pompa -> aggiungere UNA POST PER CAMBIARE LO STATO DELLA POMPA ######
  with open("Sensors.json", "r+") as outfile:
    data = json.load(outfile)
    data['Windows']= 'Open'
    outfile.seek(0)  # rewind
    json.dump(data, outfile)
    outfile.truncate()

  keyboard = [
        [
            InlineKeyboardButton("Tornare al menu principale", callback_data="main"),
            InlineKeyboardButton("Torna al menù precedente", callback_data="b1_4")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Cosa vuoi fare?", reply_markup=reply_markup    )
  return LEVEL1

def CloseWindows(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text("Finestra chiusa")
  #comando che disattiva la pompa
  with open("Sensors.json", "r+") as outfile:
    data = json.load(outfile)
    data['Windows']= 'Close'
    outfile.seek(0)  # rewind
    json.dump(data, outfile)
    outfile.truncate()
  
  keyboard = [
        [
            InlineKeyboardButton("Tornare al menu principale", callback_data="main"),
            InlineKeyboardButton("Torna al menù precedente", callback_data="b1_4")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Cosa vuoi fare?", reply_markup=reply_markup
    )
  return LEVEL1

def VentOFF(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text(" Ventola spenta")
  #comando che disattiva la pompa
  with open("Sensors.json", "r+") as outfile:
    data = json.load(outfile)
    data['Vent']= 'Off'
    outfile.seek(0)  # rewind
    json.dump(data, outfile)
    outfile.truncate()

  keyboard = [
        [
            InlineKeyboardButton("Tornare al menu principale", callback_data="main"),
            InlineKeyboardButton("Torna al menù precedente", callback_data="b1_4")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Cosa vuoi fare?", reply_markup=reply_markup
    )
  return LEVEL1

def VentON(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text(" Ventola accesa")
  #comando che disattiva la pompa
  with open("Sensors.json", "r+") as outfile:
    data = json.load(outfile)
    data['Vent']= 'On'
    outfile.seek(0)  # rewind
    json.dump(data, outfile)
    outfile.truncate()

  keyboard = [
        [
            InlineKeyboardButton("Tornare al menu principale", callback_data="main"),
            InlineKeyboardButton("Torna al menù precedente", callback_data="b1_4")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Cosa vuoi fare?", reply_markup=reply_markup
    )
  return LEVEL1

def add_remove_modify_item(update: Update, context: CallbackContext) -> int:
  pass
############################ Keyboards #########################################
def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton(text=f'Admin', callback_data='signinA')],
                [InlineKeyboardButton(text=f'Farmer', callback_data='signinF')],
                [InlineKeyboardButton(text=f'User', callback_data='signinU')]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def first_menu_keyboard():
    keyboard = [[InlineKeyboardButton(text=f'Statistics', callback_data='b1_1')],
                [InlineKeyboardButton(text=f'Modify parameters of Greenhouse', callback_data='b1_2')],
                [InlineKeyboardButton(text=f'Add/remove/modify items', callback_data='b1_3')],
                [InlineKeyboardButton(text=f'Manage actuators', callback_data='b1_4')]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 

def Statistics_keyboard():
  keyboard = [[InlineKeyboardButton("ThingsBoard - Grafici Statistiche", callback_data="b2_1")],
              [InlineKeyboardButton("Modificare threshold di sampling", callback_data="b2_2")],
              [InlineKeyboardButton("Main menu", callback_data="main")]]
  return InlineKeyboardMarkup(inline_keyboard=keyboard)

def actuator_control_keyboard():
    keyboard = [[InlineKeyboardButton(text=f'turn ON vent', callback_data='VentON')],
                [InlineKeyboardButton(text=f'turn OFF vent', callback_data='VentOFF')],
                [InlineKeyboardButton(text=f'OPEN windows', callback_data='OpenWindows')],
                [InlineKeyboardButton(text=f'CLOSE windows', callback_data='CloseWindows')],
                [InlineKeyboardButton(text=f'Main menu', callback_data='main')]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
  
############################# Messages #########################################
def main_menu_message():
  return 'Who are you? Please, choose the option in main menu:'

def first_menu_message():
  return 'Please, select one of the following action: '

def actuator_control_message():
  return 'Which actuator do you want to control? '

def NewThreshold_message(update: Update, context: CallbackContext) -> int:
  period=json.loads(requests.get(url=SERVER+"/statistic/water_period").text)
  update.callback_query.message.reply_text(text=f"Il valore corrente è: {period}\n Se vuoi modificare il valore del periodo scrivi periodo + nuovo valore in secondi\n"
  "ad esempio 'periodo 10'\n"
  "scrivi 'Principale' se vuoi tornare al menu principale")
  return ADMIN_TYPING

def Green_House_Parameters(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.reply_text(text="Se vuoi modificare i parametri della greenhouse digita il numero relativo al parametro da modificare + il nuovo valore:\n"
  "1) Low humidity threshold\n"
  "2) High humidity threshold\n"
  "3) Low bright threshold\n"
  "4) High bright threshold\n"
  "5) Low temperature threshold\n"
  "6) High temperature threshold\n"

  "\nScrivi 'Principale' se vuoi tornare al menu principale")
  return ADMIN_TYPING_2

def Item_message(update: Update, context: CallbackContext) -> int:
  plant_in_greenhouse = []
  plants = json.loads(requests.get(url=f"http://localhost:2000/plants").text)
  for plant in plants:
    if plant["GREENHOUSE_ID"]==greenhouse_id:
      plant_in_greenhouse.append(plant)
  update.callback_query.message.reply_text(text=f"\nEcco gli items disponibili \n{items}"####   !!!!!!!!!!!!
                                     "se devi aggiungere, scrivi 'aggiungi <nome item>, <prezzo> e <quantità> separati da spazi\n"
                                     "oppure se devi modificare, scrivi ad esempio 'modifica prezzo patate 2' oppure' modifica quantità patate 3'\n "
                                     "se devi rimuovere scrivi rimuovi item, ad esempio 'rimuovi patate'\n"
                                     "per tornare al menu principale digita 'Principale' ")
  return ADMIN_TYPING_3

############################# Handlers #########################################

def main():

    token="1461734973:AAGtnon-G24cJcWVjVGbp7Lv1DIXhjJNT28"
    updater = Updater(token,use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    #updater.dispatcher.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
  
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(sign_in, pattern='signin')],
            states={
                SIGNIN: [MessageHandler(Filters.text,sign_in_credenziali)],
                #da sign in vado a sign in credenziali che legge il messaggio input
                ADMIN: [MessageHandler(Filters.text, callback= id_greenhouse)],

                LEVEL1 :[CallbackQueryHandler(first_menu_keyboard, pattern='first_menu'),
                         CallbackQueryHandler(first_menu, pattern='main'),
                         CallbackQueryHandler(Statistics, pattern='b1_1'),
                         CallbackQueryHandler(ThingsBoard, pattern='b2_1'),
                         CallbackQueryHandler(NewThreshold_message, pattern='b2_2'),
                         CallbackQueryHandler(Actuators, pattern='b1_4'),
                         CallbackQueryHandler(Green_House_Parameters, pattern='b1_2'),
                         CallbackQueryHandler(OpenWindows, pattern='OpenWindow'),
                         CallbackQueryHandler(CloseWindows, pattern='CloseWindow'),
                         CallbackQueryHandler(VentOFF, pattern='VentOFF'),
                         CallbackQueryHandler(VentON, pattern='VentON'),
                         CallbackQueryHandler(Item_message, pattern='item')],

                ADMIN_TYPING : [MessageHandler(Filters.text, callback= NewThreshold_period)],
                ADMIN_TYPING_2 : [MessageHandler(Filters.text, callback= NewParametersGreenhouse)],
                ADMIN_TYPING_3 : [MessageHandler(Filters.text, callback= add_remove_modify_item)]
                      
            }, fallbacks=[MessageHandler(Filters.regex('^Done$'), done)])


    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__=="__main__":
    main()
