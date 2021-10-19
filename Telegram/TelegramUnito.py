from telegram.ext import Updater
import os
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler,Filters,MessageHandler,CommandHandler
from telegram import InlineKeyboardButton,ReplyKeyboardMarkup, InlineKeyboardMarkup, Update
############################### Bot ############################################
import telepot
import re

import json
from pprint import pprint
import requests

##AGGIUNGERE MESSAGGIO INIZIALE CHE DICE DI SCRIVERE /start
# listaFarmers=lista["list"]

SIGNIN, ADMIN , ADMIN_TYPING, ADMIN_TYPING_2, ADMIN_TYPING_3, LEVEL1, FARMER , FARMER_TYPING, FARMER_TYPING_2= range(9)

SERVER_file=json.load(open('utils.json','r'))
SERVER=SERVER_file['SERVER']
listaFarmers=json.loads(requests.get(url=SERVER+"/farmers").text)

keyboardPrincipale= [[InlineKeyboardButton(text=f'Aggiungere, modificare, rimuovere un item', callback_data='AMR')],
            [InlineKeyboardButton(text=f'Controllare attuatori', callback_data='AS')],
            [InlineKeyboardButton(text=f'Statistiche', callback_data='SF')],
            [InlineKeyboardButton(text=f'Torna al log in', callback_data='start')]]
reply_markupPrincipale = InlineKeyboardMarkup(keyboardPrincipale)

def menuprincipaleFarmer(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text('Scegli tra:', reply_markup=reply_markupPrincipale)
  return FARMER

def start(update: Update, context: CallbackContext) -> int:
  if update.message != None:
    user = update.message.from_user
    newid=str(user.id)
  else:
    user=context.user_data
    newid= update.effective_chat.id
            
  fp=open("telegram_catalog.json","r")
  catalog=json.load(fp)
  loggedUsers=catalog["LOGGED_USERS"]
  fp.close()
  new=0
  
  for i in range(len(loggedUsers)):
    if newid in loggedUsers[i].values() :
      update.message.reply_text(f"Hi, welcome back")
      new=1
  if new==0:
    newUser={"CHATID":newid, "TYPE": "","LOGID":""}
    loggedUsers.append(newUser)
    update.message.reply_text(f"Hey, it seems that you are new here! Welcome!")

  update_catalog(loggedUsers)
  update.message.reply_text("Chi sei?",reply_markup=main_menu_keyboard())
  


def update_catalog(loggedUsers):
  fp=open("telegram_catalog.json",'r')
  catalog=json.load(fp)
  fp.close()
  catalog["LOGGED_USERS"]=loggedUsers
  json.dump(catalog,open("telegram_catalog.json","w"),indent=4)

def main_menu(update: Update, context: CallbackContext) -> int:
    update.callback_query.message.edit_text(main_menu_message(),reply_markup=main_menu_keyboard())

def first_menu(update: Update, context: CallbackContext) -> int:
    update.callback_query.message.edit_text(first_menu_message(),reply_markup=first_menu_keyboard())



def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton(text=f'Admin', callback_data='signinA')],
                [InlineKeyboardButton(text=f'Farmer', callback_data='signinF')],
                [InlineKeyboardButton(text=f'User', callback_data='signinU')]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
tipo= ''

def sign_in(update: Update, context: CallbackContext) -> int:
  global tipo
  ##registro la tipologia di utente che è l'ultima risposta data
  tipo=update.callback_query.data[-1]
  fp=open("telegram_catalog.json",'r')
  catalog=json.load(fp)
  fp.close()
  loggedUsers=catalog["LOGGED_USERS"]
  oldid=str(update.effective_chat["id"])
  
  for i in range(len(loggedUsers)):
    if oldid== loggedUsers[i]["CHATID"]:
      loggedUsers[i]["TYPE"]=str(tipo)
      update_catalog(loggedUsers)
      pprint(loggedUsers)

  keyboard = [
        [
            InlineKeyboardButton("Log in Menu", callback_data="start"),
            
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.edit_text(f"Ok now log in write your id or go back writing 'start'")

  return SIGNIN

def sign_in_credenziali(update: Update, context: CallbackContext) -> int:
    pprint("sto entrando del sign_in_credd")
    text = update.message.text # splitto il testo
    global tipo
    print(tipo)
    #salvo il LOG ID dell'utente
    fp=open("telegram_catalog.json",'r')
    catalog=json.load(fp)
    fp.close()
    loggedUsers=catalog["LOGGED_USERS"]
    oldid=str(update.effective_chat["id"])
    trovato=0
    
    if tipo== 'F':
        #cerco l'id scritto dall'utente nella lista farmers, se ha cambiato numero di accesso a telegram ma è sempre lo stesso utente sarà riconosciuto dal suo logid
        for i in range(len(listaFarmers)):
            pprint(listaFarmers)
            if listaFarmers[i]['FARMER_ID'] == text:
                pprint(listaFarmers[i])
                trovato=1
                user_data=context.user_data # li salvo o qui
                user_data["LOGID"]= text
                pprint(user_data)

            for j in range(len(loggedUsers)):  # o qui
                if oldid == loggedUsers[j]["CHATID"]:
                    loggedUsers[j]["LOGID"]=str(text)
                    update_catalog(loggedUsers)
                    pprint(loggedUsers)
                            
            update.message.reply_text('Scegli tra:', reply_markup=reply_markupPrincipale)
            return FARMER
        
    elif tipo=='A':
        for i in range(len(listaAdmin)):
            if text == listaAdmin[i]['ADMIN_ID']:
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

    elif tipo=='U':
        pass 
        #aggiungere##################################################

    if trovato==0:
      update.message.reply_text('LOG_ID sbagliato, riprova')
      return SIGNIN
  

def update_catalog(loggedUsers):
  fp=open("telegram_catalog.json",'r')
  catalog=json.load(fp)
  fp.close()
  catalog["LOGGED_USERS"]=loggedUsers
  json.dump(catalog,open("telegram_catalog.json","w"),indent=4)

def done(update: Update, _: CallbackContext) -> int:
    update.message.reply_text("niente")
##############################################################################################
#######################################################°°ADMIN###################################################################à
#############################################################################

listaAdmin=json.loads(requests.get(url=SERVER+"/admins").text)
greenhousesinfo = json.loads(requests.get(url=SERVER+f"/greenhouses").text) 
greenhouselist = [] 
greenhouselist.append(greenhousesinfo[0]["GREENHOUSE_ID"])
greenhouse_id = greenhousesinfo[0]["GREENHOUSE_ID"]

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
  greenhouse = json.loads(requests.get(url=f"{SERVER}/greenhouses/{greenhouse_id}").text)

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
          InlineKeyboardButton("Tornare al menu principale", callback_data="main_fm"),
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
          InlineKeyboardButton("Tornare al menu principale", callback_data="main_fm"),
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
          InlineKeyboardButton("Tornare al menu principale", callback_data="main_fm"),
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
          InlineKeyboardButton("Tornare al menu principale", callback_data="main_fm"),
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
          InlineKeyboardButton("Tornare al menu principale", callback_data="main_fm"),
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
          InlineKeyboardButton("Tornare al menu principale", callback_data="main_fm"),
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
            InlineKeyboardButton("Main menu", callback_data="main_fm"),
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
              InlineKeyboardButton("Tornare al menu principale", callback_data="main_fm"),
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
            InlineKeyboardButton("Tornare al menu principale", callback_data="main_fm"),
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
            InlineKeyboardButton("Tornare al menu principale", callback_data="main_fm"),
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
            InlineKeyboardButton("Tornare al menu principale", callback_data="main_fm"),
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
            InlineKeyboardButton("Tornare al menu principale", callback_data="main_fm"),
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
              [InlineKeyboardButton("Main menu", callback_data="main_fm")]]
  return InlineKeyboardMarkup(inline_keyboard=keyboard)

def actuator_control_keyboard():
    keyboard = [[InlineKeyboardButton(text=f'turn ON vent', callback_data='VentON')],
                [InlineKeyboardButton(text=f'turn OFF vent', callback_data='VentOFF')],
                [InlineKeyboardButton(text=f'OPEN windows', callback_data='OpenWindows')],
                [InlineKeyboardButton(text=f'CLOSE windows', callback_data='CloseWindows')],
                [InlineKeyboardButton(text=f'Main menu', callback_data='main_fm')]]
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


    ####################################################### FARMER ###################################
    #####################################################################################
    #################################################

def displaylist(update: Update, context: CallbackContext) -> int:
  user_data=context.user_data
  #1. stampo lista  2. chiedo di scrivere se nuovo nome item, prezzo e quantità separati da spazi
  #3. chiedo di scrivere "modifica prezzo patate 2/ modifica quantità patate 3 "
  farmerid=user_data["LOGID"]
  singolo=json.loads(requests.get(url=SERVER+f"/farmer/{farmerid}").text)
  items=singolo["ITEMS_SELL"]
  update.callback_query.message.edit_text(text=f"\nEcco gli items disponibili \n{items}"
                                     "se devi aggiungere, scrivi 'aggiungi <nome item>, <prezzo> e <quantità> separati da spazi\n"
                                     "oppure se devi modificare, scrivi ad esempio 'modifica prezzo patate 2' oppure' modifica quantità patate 3'\n "
                                     "se devi rimuovere scrivi rimuovi item, ad esempio 'rimuovi patate'\n"
                                     "per tornare al menu principale digita 'principale'  ")
  return FARMER_TYPING

def uporadditemfarmer(update: Update, context: CallbackContext) -> int:
  pprint("sto entrando in upporadditem")
  user_data=context.user_data
  farmerid=user_data["LOGID"]
  text = update.message.text.split(" ")

  if text[0] == "modifica":
    item=text[2]
    if text[1]== "prezzo":
      prezzo= int(text[3])
      r=requests.post(url=SERVER+f"/uporadditem/{farmerid}/{item}/{prezzo}/None")
    elif text[1]== "quantità" :
      quantita=int(text[3])
      p=requests.post(url=f"{SERVER}/uporadditem/{farmerid}/{item}/None/{quantita}")
    
    singolo=json.loads(requests.get(url=f"{SERVER}/farmer/{farmerid}").text)
    items=singolo["ITEMS_SELL"]
    update.message.reply_text(f"Ok,fatto. Ecco la lista modificata\n {items} \n Riprova se vuoi modificare altro\n digita 'principale' per tornare al menu inziale")
    return FARMER_TYPING
  elif text[0] == "aggiungi":
    item=text[1]
    prezzo=int(text[2])
    quantita=int(text[3])
    requests.post(f"{SERVER}/uporadditem/{farmerid}/{item}/{prezzo}/{quantita}")
    singolo=json.loads(requests.get(url=f"{SERVER}/farmer/{farmerid}").text)
    items=singolo["ITEMS_SELL"]
    update.message.reply_text(f"Ok,fatto. Ecco la lista modificata\n {items} \n Riprova se vuoi modificare altro\n digita 'principale' per tornare al menu inziale")
    
    return FARMER_TYPING
  elif text[0] =="rimuovi":
    item=text[1]
    requests.delete(f"{SERVER}/deleteitem/{farmerid}/{item}")
    singolo=json.loads(requests.get(url=f"{SERVER}/farmer/{farmerid}").text)
    items=singolo["ITEMS_SELL"]
    update.message.reply_text(f"Ok,fatto. Ecco la lista modificata\n {items} \n Riprova se vuoi modificare altro\n digita 'principale' per tornare al menu inziale")
    
    return FARMER_TYPING

  elif text[0] == "principale":
    update.message.reply_text('Scegli tra:', reply_markup=reply_markupPrincipale)
    return FARMER

  
def attuatoriscelte(update: Update, context: CallbackContext) -> int:
  keyboard = [
        [
            InlineKeyboardButton("Modificare la soglia dell'umidità", callback_data="newthreshold"),
            InlineKeyboardButton("Accendere o spegnere la pompa", callback_data="pompaonoff"),
            InlineKeyboardButton("Tornare al menu principale", callback_data="principale")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.edit_text(text="Cosa vuoi fare?", reply_markup=reply_markup
    )
  return FARMER

def pompaonoff(update: Update, context: CallbackContext) -> int:
  keyboard = [
        [
            InlineKeyboardButton("Pompa ON", callback_data="PompaON"),
            InlineKeyboardButton("Pompa OFF", callback_data="PompaOFF"),
            InlineKeyboardButton("Torna al menù precedente", callback_data="b1_2")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.edit_text(text="Cosa vuoi fare?", reply_markup=reply_markup
    )
  return FARMER

def PompaON(update: Update, context: CallbackContext) -> int:
  
  update.callback_query.message.edit_text(" Pompa accesa")
  #comando che attiva la pompa
  keyboard = [
        [
            InlineKeyboardButton("Tornare al menu principale", callback_data="principale"),
            InlineKeyboardButton("Torna al menù precedente", callback_data="b1_2")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Cosa vuoi fare?", reply_markup=reply_markup    )
  return FARMER
def PompaOFF(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text(" Pompa spenta")
  #comando che disattiva la pompa
  keyboard = [
        [
            InlineKeyboardButton("Tornare al menu principale", callback_data="principale"),
            InlineKeyboardButton("Torna al menù precedente", callback_data="b1_2")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Cosa vuoi fare?", reply_markup=reply_markup
    )
  return FARMER
def listaCROPS(farmerid):
  farmer=json.loads(requests.get(url=f"{SERVER}/farmer/{farmerid}").text)
  plants=json.loads(requests.get(url=f"{SERVER}/plants").text)
  cropsowned=farmer["CROPS_OWNED"]
  pprint(cropsowned)
  displaydict={"list":[]}
  #STAMPO LISTA PIANTE OWNED CON THRESHOLDS
  for crop in cropsowned:
      for plant in plants:
        if plant["PLANT_ID"] == crop:
          displaydict["list"].append({"CROP":plant["PLANT_NAME"],"THRESHOLD_MOIST_MIN":plant["THRESHOLD_MOIST_MIN"],"THRESHOLD_MOIST_MAX":plant["THRESHOLD_MOIST_MAX"]})
  
  return displaydict

def NewThreshold_info(update: Update, context: CallbackContext) -> int:
  user_data=context.user_data
  farmerid=user_data["LOGID"]
  listacrops=listaCROPS(farmerid)
  keyboard = [
        [
            InlineKeyboardButton("Tornare al menu principale", callback_data="principale"),
            InlineKeyboardButton("Torna al menù precedente", callback_data="b1_2")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.edit_text(text=f"{listacrops}")
  update.callback_query.message.reply_text(text="Se vuoi modificare il valore minimo scrivi nome pianta+min + nuovo valore\n"
  "se vuoi modificare il valore massimo scrivi nome pianta+ max+ nuovo valore\n"
  "ad esempio 'peperoncino min 54'\n"
  "oppure scegli un'opzione nei bottoni in basso",reply_markup=reply_markup)
  return FARMER

def NewThreshold_reply(update: Update, context: CallbackContext) -> int:
  user_data=context.user_data
  farmerid=user_data["LOGID"]
  text = update.message.text.split(" ")
  pianta= text[0]
  farmer=json.loads(requests.get(url=f"{SERVER}/farmer/{farmerid}").text)
  plants=json.loads(requests.get(url=f"{SERVER}/plants").text)
  cropsowned=farmer["CROPS_OWNED"]
  keyboard = [
        [
            InlineKeyboardButton("Tornare al menu principale", callback_data="principale"),
            InlineKeyboardButton("Torna al menù precedente", callback_data="b1_2")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  #update.message.reply_text(text="Cosa vuoi fare?", reply_markup=reply_markup    )
  

  if text[0] == "Principale":
    update.message.reply_text('Scegli tra:', reply_markup=reply_markupPrincipale)
    return FARMER

  elif text[1]=="min":
    for crop in cropsowned:
      for plant in plants:
        if plant["PLANT_ID"]== crop and plant["PLANT_NAME"]== pianta:
          plantid=plant["PLANT_ID"]
          modified_dict={"THRESHOLD_MOIST_MIN": int(text[2])}
          requests.post(url=f"{SERVER}/plant/{plantid}",json=modified_dict)
    lista=listaCROPS(farmerid)
    update.message.reply_text(text=f"Ecco la lista aggiornata\n {lista}\n puoi continuare oppure scegliere un'opzione dal menu", reply_markup=reply_markup )
    return FARMER
  elif text[1]=="max":
    for crop in cropsowned:
      for plant in plants:
        if plant["PLANT_ID"]== crop and plant["PLANT_NAME"]== pianta:
          plantid=plant["PLANT_ID"]
          modified_dict={"THRESHOLD_MOIST_MAX": int(text[2])}
          requests.post(url=f"{SERVER}/plant/{plantid}",json=modified_dict)
    lista=listaCROPS(farmerid)
    update.message.reply_text(text=f"Ecco la lista aggiornata\n {lista}, puoi continuare con un altro comando oppure cliccare su uno dei seguenti bottoni",reply_markup=reply_markup)
    return FARMER
  

def Statistiche_first(update: Update, context: CallbackContext) -> int:
  keyboard = [
      [
          InlineKeyboardButton("ThingsBoard - Grafici Statistiche", callback_data="thingsboard"),
          InlineKeyboardButton("Modificare threshold di sampling", callback_data="threshold_stat"),
          InlineKeyboardButton("Tornare al menu principale", callback_data="principale"),

      ]
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.edit_text(text="Cosa vuoi fare?", reply_markup=reply_markup)
  return FARMER

def ThingsBoard(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text(text="Ecco il link di thingsboard")
  keyboard = [
        [
            InlineKeyboardButton("Tornare al menu principale", callback_data="principale"),
            InlineKeyboardButton("Torna al menù precedente", callback_data="b1_3")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Cosa vuoi fare?", reply_markup=reply_markup    )
  return FARMER


def main():

    #token="1461734973:AAGtnon-G24cJcWVjVGbp7Lv1DIXhjJNT28"
    token="1990658567:AAG5By57hC8Hbyp9Mc2FTqqsIw8VLV_MsDM" #

    updater = Updater(token,use_context=True)
    #updater.dispatcher.add_handler(CommandHandler('start', start))
    #updater.dispatcher.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
  
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(sign_in, pattern='signin'),CommandHandler('start', start)],
            states={
                SIGNIN: [MessageHandler(Filters.text,sign_in_credenziali),
                        MessageHandler(Filters.regex('^start$'), start]
                #da sign in vado a sign in credenziali che legge il messaggio input
                ADMIN: [MessageHandler(Filters.text, callback= id_greenhouse)],

                LEVEL1 :[CallbackQueryHandler(first_menu_keyboard, pattern='first_menu'),
                         CallbackQueryHandler(first_menu, pattern='main_fm'),
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
                ADMIN_TYPING_3 : [MessageHandler(Filters.text, callback= add_remove_modify_item)],
                
                FARMER_TYPING : [MessageHandler(Filters.text, callback= uporadditemfarmer)],
                FARMER_TYPING_2 : [MessageHandler(Filters.text, callback= NewThreshold_reply)],
                FARMER : [ #premo aggiungi e legge il messaggio
                      CallbackQueryHandler(displaylist, pattern='AMR'),
                      CallbackQueryHandler(attuatoriscelte, pattern='AS'),
                      CallbackQueryHandler(pompaonoff, pattern='pompaonoff'),
                      CallbackQueryHandler(PompaOFF, pattern='PompaOFF'),
                      CallbackQueryHandler(PompaON, pattern='PompaON'),
                      CallbackQueryHandler(NewThreshold_info, pattern='newthreshold'),
                      CallbackQueryHandler(menuprincipaleFarmer, pattern='principale'),
                      
                      CallbackQueryHandler(Statistiche_first, pattern='SF'),
                      CallbackQueryHandler(ThingsBoard, pattern='thingsboard'),

                      
                      ]
                    
                      
            }, fallbacks=[MessageHandler(Filters.regex('^Done$'), done)])


    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__=="__main__":
    main()
