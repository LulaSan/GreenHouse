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

SIGNIN, SIGNIN_PULSANTI, ADMIN , ADMIN_TYPING, ADMIN_TYPING_2, LEVEL1, FARMER , FARMER_TYPING, FARMER_TYPING_2 , USER, USER_TYPING= range(11)

SERVER_file=json.load(open('utils.json','r'))
SERVER=SERVER_file['SERVER']
listaFarmers=json.loads(requests.get(url=SERVER+"/farmers").text)
listaAdmins=json.loads(requests.get(url=SERVER+"/admins").text)
listaUsers=json.loads(requests.get(url=SERVER+"/users").text)
def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton(text=f'Admin', callback_data='signinA')],
                [InlineKeyboardButton(text=f'Farmer', callback_data='signinF')],
                [InlineKeyboardButton(text=f'User', callback_data='signinU')]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

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
  update.message.reply_text("Who are you?",reply_markup=main_menu_keyboard())
  return SIGNIN_PULSANTI
 

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
  update.callback_query.message.edit_text(f"Ok! To Log in just write your ID or to go back write 'Start'")

  return SIGNIN

def sign_in_credenziali(update: Update, context: CallbackContext) -> int:
    pprint("sto entrando del sign_in_cred")
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
                user_data["LOGID"]= text # Il LOGID è l'input da tastiera, ed è nel catalog il FARMER_ID
                pprint(user_data)

                for j in range(len(loggedUsers)):  # o qui
                    if oldid == loggedUsers[j]["CHATID"]:
                        loggedUsers[j]["LOGID"]=str(text)
                        update_catalog(loggedUsers)
                        pprint(loggedUsers)

                        update.message.reply_text(f'Welcome {user_data["LOGID"]}! \n Write "Start" if you want to go back to log in \nChoose between:', reply_markup=reply_markupPrincipale_FARMER)
                        return FARMER
        
    elif tipo=='A':
        for i in range(len(listaAdmins)):
            if text == listaAdmins[i]['ADMIN_ID']:
                pprint(listaAdmins[i])
                trovato=1
                user_data=context.user_data # li salvo o qui
                user_data["ADMIN_ID"]= text
                pprint(user_data)

                for j in range(len(loggedUsers)):  # o qui
                    if oldid == loggedUsers[j]["CHATID"]:
                        loggedUsers[j]["LOGID"]=str(text)
                        update_catalog(loggedUsers)
                        pprint(loggedUsers)
                        
                    #display greenhouse list
                    pprint(greenhouselist)
                    update.message.reply_text(text=f"\Welcome Admin!\n Here there are the available greenhouses \n{greenhouselist}\n Which greenhouse do you want to manage?\n")
                    return ADMIN
                

    elif tipo=='U':
        for i in range(len(listaUsers)):
            if text == listaUsers[i]['USER_ID']:
                pprint(listaUsers[i])
                trovato=1
                user_data=context.user_data # li salvo o qui
                user_data["USER_ID"]= text
                pprint(user_data)

                for j in range(len(loggedUsers)):  # o qui
                    if oldid == loggedUsers[j]["CHATID"]:
                        loggedUsers[j]["LOGID"]=str(text)
                        update_catalog(loggedUsers)
                        pprint(loggedUsers)
                        
                    #display greenhouse list
                    update.message.reply_text(text=f"\nWelcome User\n, choose an option or digit 'Start' to come back to LOG IN", reply_markup=keyboardPrincipale_USER())
                    return USER
    if trovato==0:
        update.message.reply_text('Ups! Wrong LOG_ID, try again.')
        return SIGNIN

        

        



def update_catalog(loggedUsers):
  fp=open("telegram_catalog.json",'r')
  catalog=json.load(fp)
  fp.close()
  catalog["LOGGED_USERS"]=loggedUsers
  json.dump(catalog,open("telegram_catalog.json","w"),indent=4)

def done(update: Update, _: CallbackContext) -> int:
    update.message.reply_text("nothing")

################ USER#############################################################################################

def keyboardPrincipale_USER():
  keyboardPrincipale= [[InlineKeyboardButton(text=f'Buy something', callback_data='compra_user')]]
  return InlineKeyboardMarkup(keyboardPrincipale) 

def displaylist_USER(update: Update, context: CallbackContext) -> int:
  user_data=context.user_data
  itemstobuy=json.loads(requests.get(url=f"{SERVER}/itemstobuy").text)
  update.callback_query.message.edit_text(text=f"\nHere there are available items: \n{itemstobuy}\n"
                                     "\n If you want to buy something, write in this order :  Farmer ID, item name and desired quantity \n "
                                         "\n If you want to go back to main menu write 'Principale' ")
  return USER_TYPING

def buyitemuser(update: Update, context: CallbackContext) -> int:
  pprint("sto entrando in buyitemuser")
  user_data=context.user_data
  # farmerid=user_data["LOGID"]
  text = update.message.text.split(" ")
  if text[0] == "Principale":
    update.message.reply_text('Choose between:', reply_markup=keyboardPrincipale_USER())
    return USER
  farmerID=text[0]
  item=text[1]
  quantita=text[2]
  r=requests.post(f"{SERVER}/buyitem/{farmerID}/{item}/{quantita}").text
  itemstobuy=json.loads(requests.get(url=f"{SERVER}/itemstobuy").text)
  update.message.reply_text(f"Ok, done! . Here there is the modified list : \n {itemstobuy} \n Try again if you want to modify something else \n Write 'Principale' to go pack to the main menu")

  return USER_TYPING












##############################################################################################
#######################################################°°ADMIN###################################################################à
#############################################################################

greenhousesinfo = json.loads(requests.get(url=SERVER+f"/greenhouses").text) 
greenhouselist = [] 
for greenhouse in greenhousesinfo:
    greenhouselist.append(greenhouse["GREENHOUSE_ID"])
    
    
   
#greenhouse_id = greenhousesinfo[0]["GREENHOUSE_ID"] ########## il primo sempre?

def id_greenhouse(update: Update, context: CallbackContext) -> int:
      text = update.message.text # splitto il testo
       
      if text in greenhouselist :
        update.message.reply_text(text=first_menu_message(),reply_markup=first_menu_keyboard())
        user_data=context.user_data # APRO IL DIZIONARIO DEGLI APPUNTI
        user_data["CHOSEN_GREENHOUSEID"]= text # questa è la greenhouse di cui l'admin vuole sapere di più
        greenhouse_id=user_data["CHOSEN_GREENHOUSEID"]
        pprint(user_data)
        return LEVEL1
      else:
        update.message.reply_text(text=f"Ups! Greenhouse not found, try again.")
        return ADMIN
   

# funzioni primo menu:
def Statistics(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text("Choose an option: ",reply_markup=Statistics_keyboard())
  return LEVEL1


def NewParametersGreenhouse(update: Update, context: CallbackContext) -> int:
  text = update.message.text.split(" ")
  user_data=context.user_data
  greenhouse_id=user_data["CHOSEN_GREENHOUSEID"]
  greenhouse = json.loads(requests.get(url=f"{SERVER}/greenhouse/{greenhouse_id}").text)

  if text[0] == "Principale":
    update.message.reply_text('Scegli tra:', reply_markup=first_menu_keyboard())
    return LEVEL1

  elif text[0] == "1":
    #greenhouse[0]["THRESHOLD_HUMID_MIN"]= int(text[1])
    new_value = {"THRESHOLD_HUMID_MIN": int(text[1])}
    res = requests.post(SERVER+f"/greenhouse/{greenhouse_id}",json=new_value)
    update.message.reply_text(text="New threshold updated")
    
    keyboard = [[
      InlineKeyboardButton("Main menu", callback_data="main_fm"),
      ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text="Main menu", reply_markup=reply_markup)
    return LEVEL1
       
  elif text[0] == "2":
    new_value = {"THRESHOLD_HUMID_MAX": int(text[1])}
    res = requests.post(SERVER+f"/greenhouse/{greenhouse_id}",json=new_value)
    update.message.reply_text(text="New threshold updated")
    
    keyboard = [[
      InlineKeyboardButton("Main menu", callback_data="main_fm"),
      ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text="Main menu", reply_markup=reply_markup)
    return LEVEL1

  elif text[0] == "3":
    new_value = {"THRESHOLD_BRIGHT_MIN": int(text[1])}
    res = requests.post(SERVER+f"/greenhouse/{greenhouse_id}",json=new_value)
    update.message.reply_text(text="New threshold updated")
    
    keyboard = [[
      InlineKeyboardButton("Main menu", callback_data="main_fm"),
      ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text="Main menu", reply_markup=reply_markup)
    return LEVEL1
  elif text[0] == "4":
    new_value = {"THRESHOLD_BRIGHT_MAX": int(text[1])}
    res = requests.post(SERVER+f"/greenhouse/{greenhouse_id}",json=new_value)
    update.message.reply_text(text="New threshold updated")
    
    keyboard = [[
      InlineKeyboardButton("Main menu", callback_data="main_fm"),
      ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text="Main menu", reply_markup=reply_markup)
    return LEVEL1
  elif text[0] == "5":
    new_value = {"THRESHOLD_TEMPER_MIN": int(text[1])}
    res = requests.post(SERVER+f"/greenhouse/{greenhouse_id}",json=new_value)
    update.message.reply_text(text="New threshold updated")
    
    keyboard = [[
      InlineKeyboardButton("Main menu", callback_data="main_fm"),
      ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text="Main menu", reply_markup=reply_markup)
    return LEVEL1
  elif text[0] == "6":
    new_value = {"THRESHOLD_TEMPER_MAX": int(text[1])}
    res = requests.post(SERVER+f"/greenhouse/{greenhouse_id}",json=new_value)
    update.message.reply_text(text="New threshold updated")
    
    keyboard = [[
      InlineKeyboardButton("Main menu", callback_data="main_fm"),
      ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text="Main menu", reply_markup=reply_markup)
    return LEVEL1
  else:
    update.message.reply_text('Wrong command, try again')
    return ADMIN_TYPING_2
 

def Green_House_Parameters(update: Update, context: CallbackContext) -> int:
  user_data=context.user_data
  greenhouse_id=user_data["CHOSEN_GREENHOUSEID"]
  THRESHOLD_HUMID_MIN=requests.get(url=f"{SERVER}/greenhouse/{greenhouse_id}/THRESHOLD_HUMID_MIN").text
  THRESHOLD_HUMID_MAX=requests.get(url=f"{SERVER}/greenhouse/{greenhouse_id}/THRESHOLD_HUMID_MAX").text
  THRESHOLD_BRIGHT_MIN=requests.get(url=f"{SERVER}/greenhouse/{greenhouse_id}/THRESHOLD_BRIGHT_MIN").text
  THRESHOLD_BRIGHT_MAX=requests.get(url=f"{SERVER}/greenhouse/{greenhouse_id}/THRESHOLD_BRIGHT_MAX").text
  THRESHOLD_TEMPER_MIN=requests.get(url=f"{SERVER}/greenhouse/{greenhouse_id}/THRESHOLD_TEMPER_MIN").text
  THRESHOLD_TEMPER_MAX=requests.get(url=f"{SERVER}/greenhouse/{greenhouse_id}/THRESHOLD_TEMPER_MAX").text
  update.callback_query.message.reply_text(text=f"If you want to modify some parameter write the correspondant number + new value:\n"
  "Accanto è indicato il valore attuale"
  f"1) Low humidity threshold: {THRESHOLD_HUMID_MIN}\n"
  f"2) High humidity threshold: {THRESHOLD_HUMID_MAX}\n"
  f"3) Low bright threshold:{THRESHOLD_BRIGHT_MIN} \n"
  f"4) High bright threshold: {THRESHOLD_BRIGHT_MAX}\n"
  f"5) Low temperature threshold: {THRESHOLD_TEMPER_MIN} \n"
  f"6) High temperature threshold:{THRESHOLD_TEMPER_MAX} \n"
  "\n scrivi 'Principale' se vuoi tornare al menu principale")
    
  return ADMIN_TYPING_2

def Actuators(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text("Choose an option:",reply_markup=actuator_control_keyboard())
  return LEVEL1


# funzioni secondo livello:
def ThingsBoard(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text(text="Thingsboard link: ")
  keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data="main_fm"),
            InlineKeyboardButton("Last menu", callback_data="b1_1")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
  update.callback_query.message.reply_text(text="Choose an option:", reply_markup=reply_markup)
  return LEVEL1

def NewThreshold_period(update: Update, context: CallbackContext) -> int:
  user_data=context.user_data
  adminid=user_data["ADMIN_ID"]
  text = update.message.text.split(" ")
  tipologia=text[0]
  
  if text[0] == "Principale":
    update.message.reply_text('Choose an option:', reply_markup=first_menu_keyboard())
    return LEVEL1
  elif text[0] != "Principale" and text[0] != "water" and text[0] != "temperature" :
    update.message.reply_text('Wrong command, try again.')
    return ADMIN_TYPING

  elif text[0] == 'Water':
    res = requests.post(SERVER+f"/statistic/water_period/{text[1]}")
    water_period=json.loads(requests.get(url=SERVER+"/statistic/water_period").text)
    
    update.message.reply_text(text=f" Actual water period = {water_period} \n"  
                                           "To modify the period write temperature or water followe by the new value in seconds \n"
                                           "or write 'principale' to go back to main menu")
   

    return ADMIN_TYPING
  elif text[0] == 'Temperature' :
    res = requests.post(SERVER+f"/statistic/temperature_period/{text[1]}")
    temperature_period=json.loads(requests.get(url=SERVER+"/statistic/temperature_period").text)
    update.message.reply_text(text=f" ctual temperature period = {temperature_period} \n  "
                                           "To modify the period write Temperature or Water followed by the new value in seconds \n"
                                           "or write 'principale' to go back to main menu")
    return ADMIN_TYPING

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
            InlineKeyboardButton("Main Menu", callback_data="main_fm"),
            InlineKeyboardButton("Last Menu", callback_data="b1_4")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Choose an option:", reply_markup=reply_markup    )
  return LEVEL1

def CloseWindows(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text("Window closed")
  #comando che disattiva la pompa
  with open("Sensors.json", "r+") as outfile:
    data = json.load(outfile)
    data['Windows']= 'Close'
    outfile.seek(0)  # rewind
    json.dump(data, outfile)
    outfile.truncate()
  
  keyboard = [
        [
            InlineKeyboardButton("Main Menu",callback_data="main_fm"),
            InlineKeyboardButton("Last Menu", callback_data="b1_4")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Choose an option:", reply_markup=reply_markup
    )
  return LEVEL1

def VentOFF(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text("Fan OFF")
  #comando che disattiva la pompa
  with open("Sensors.json", "r+") as outfile:
    data = json.load(outfile)
    data['Vent']= 'Off'
    outfile.seek(0)  # rewind
    json.dump(data, outfile)
    outfile.truncate()

  keyboard = [
        [
            InlineKeyboardButton("Main Menu", callback_data="main_fm"),
            InlineKeyboardButton("Last Menu", callback_data="b1_4")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Choose an option:", reply_markup=reply_markup
    )
  return LEVEL1

def VentON(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text("Fan ON")
  #comando che disattiva la pompa
  with open("Sensors.json", "r+") as outfile:
    data = json.load(outfile)
    data['Vent']= 'On'
    outfile.seek(0)  # rewind
    json.dump(data, outfile)
    outfile.truncate()

  keyboard = [
        [
            InlineKeyboardButton("Main Menu", callback_data="main_fm"),
            InlineKeyboardButton("Last Menu", callback_data="b1_4")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Choose an option:", reply_markup=reply_markup
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
                [InlineKeyboardButton(text=f'Visualize plants and items sold', callback_data='b1_3')],
                [InlineKeyboardButton(text=f'Manage actuators', callback_data='b1_4')]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 

def Statistics_keyboard():
  keyboard = [[InlineKeyboardButton("ThingsBoard - Statistics ", callback_data="b2_1")],
              [InlineKeyboardButton("Modify sampling threshold ", callback_data="b2_2")],
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
  return 'Please, select one of the following action or write "Start" to go back to LOG IN : '

def actuator_control_message():
  return 'Which actuator do you want to control? '

def NewThreshold_message(update: Update, context: CallbackContext) -> int:
  water_period=json.loads(requests.get(url=SERVER+"/statistic/water_period").text)
  temperature_period=json.loads(requests.get(url=SERVER+"/statistic/temperature_period").text)
  update.callback_query.message.reply_text(text=f" Actual temperature period = {temperature_period} \n Actual water period = {water_period} \n  "
                                           "To modify the period write temperature or water followe by the new value in seconds \n"
                                           "or write 'principale' to go back to main menu")
  return ADMIN_TYPING


def ItemMessage(update: Update, context: CallbackContext) -> int:
  user_data=context.user_data
  greenhouse_id=user_data["CHOSEN_GREENHOUSEID"]
  plant_in_greenhouse = []
  plants = json.loads(requests.get(url=f"{SERVER}/plants").text)
  items_greenhouse=  json.loads(requests.get(url=f"{SERVER}/items_greenhouse/{greenhouse_id}").text)
  farmers_ids=  json.loads(requests.get(url=f"{SERVER}/farmers_greenhouse/{greenhouse_id}").text)
  for plant in plants:
    if plant["GREENHOUSE_ID"]==greenhouse_id:
      plant_in_greenhouse.append(plant["PLANT_NAME"])
   
  keyboard = [[ InlineKeyboardButton("Main Menu", callback_data="main_fm") ]]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text=f"\n The plants in this GreenHouse are : \n{plant_in_greenhouse} \n" 
                                           f"\n The farmers in this GreenHouse are: \n {farmers_ids} \n"
                                          f" \n The items for sale in this GreenHouse are: \n {items_greenhouse} \n",reply_markup=reply_markup)
  return LEVEL1


    ####################################################### FARMER ###################################
    #####################################################################################
    #################################################
keyboardPrincipale= [[InlineKeyboardButton(text=f'Add, modify or remove an item', callback_data='AMR')],
            [InlineKeyboardButton(text=f'Manage actuators', callback_data='AS')],
            [InlineKeyboardButton(text=f'Statistics', callback_data='SF')]]
reply_markupPrincipale_FARMER = InlineKeyboardMarkup(keyboardPrincipale)

def menuprincipaleFarmer(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text('Choose an action or write "Start" to go back to LOG IN', reply_markup=reply_markupPrincipale_FARMER)
  return FARMER  

def displaylist(update: Update, context: CallbackContext) -> int:
  user_data=context.user_data
  #1. stampo lista  2. chiedo di scrivere se nuovo nome item, prezzo e quantità separati da spazi
  #3. chiedo di scrivere "modifica prezzo patate 2/ modifica quantità patate 3 "
  farmerid=user_data["LOGID"]
  singolo=json.loads(requests.get(url=SERVER+f"/farmer/{farmerid}").text)
  items=singolo["ITEMS_SELL"]
  update.callback_query.message.edit_text(text=f"\n Here there are your available items  \n{items}\n"
                                     "● To ADD something write:  write 'add <item name>, <price> e <quanity> separated by one space\n"
                                     "● To MODIFY something write:  write 'modify 'price' or 'quanity', <item name>, new value separated by one space\n "
                                     "● To REMOVE something write:  write 'remove <item name> separated by one space\n"
                                          " >>  For Example: modify Pomodoro price 3"
                                     "● To go back to main menu write Principale  ")
  return FARMER_TYPING

def uporadditemfarmer(update: Update, context: CallbackContext) -> int:
  pprint("sto entrando in upporadditem")
  user_data=context.user_data
  farmerid=user_data["LOGID"]
  text = update.message.text.split(" ")

  if text[0] == "modify":
    item=text[2]
    if text[1]== "price":
      prezzo= int(text[3])
      r=requests.post(url=SERVER+f"/uporadditem/{farmerid}/{item}/{prezzo}/None")
    elif text[1]== "quantity" :
      quantita=int(text[3])
      p=requests.post(url=f"{SERVER}/uporadditem/{farmerid}/{item}/None/{quantita}")
    
    singolo=json.loads(requests.get(url=f"{SERVER}/farmer/{farmerid}").text)
    items=singolo["ITEMS_SELL"]
    update.message.reply_text(f"Ok,done.Here there is the modified list\n {items} \n Try again if you want to modify something else or write Principale to go back to the main menu")
    return FARMER_TYPING
  elif text[0] == "add":
    item=text[1]
    prezzo=int(text[2])
    quantita=int(text[3])
    requests.post(f"{SERVER}/uporadditem/{farmerid}/{item}/{prezzo}/{quantita}")
    singolo=json.loads(requests.get(url=f"{SERVER}/farmer/{farmerid}").text)
    items=singolo["ITEMS_SELL"]
    update.message.reply_text(f"Ok,done.Here there is the modified list\n {items} \n Try again if you want to modify something else or write Principale to go back to the main menu")
    
    return FARMER_TYPING
  elif text[0] =="remove":
    item=text[1]
    requests.delete(f"{SERVER}/deleteitem/{farmerid}/{item}")
    singolo=json.loads(requests.get(url=f"{SERVER}/farmer/{farmerid}").text)
    items=singolo["ITEMS_SELL"]
    update.message.reply_text(f"Ok,done.Here there is the modified list\n {items} \n Try again if you want to modify something else or write Principale to go back to the main menu")
    
    return FARMER_TYPING

  elif text[0] == "Principale":
    update.message.reply_text('Write "Start" if you want to go back to LOG IN \n Choose between:', reply_markup=reply_markupPrincipale_FARMER)
    return FARMER

  
def attuatoriscelte(update: Update, context: CallbackContext) -> int:
  keyboard = [
        [
            InlineKeyboardButton("Modify humidity threshold", callback_data="newthreshold_humidity"),
            InlineKeyboardButton("Turn ON or OFF the pump", callback_data="pompaonoff"),
            InlineKeyboardButton("Main Menu", callback_data="principale")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.edit_text(text="Choose an option:", reply_markup=reply_markup)
  return FARMER

def pompaonoff(update: Update, context: CallbackContext) -> int:
  keyboard = [
        [
            InlineKeyboardButton("Pump ON", callback_data="PompaON"),
            InlineKeyboardButton("Pump OFF", callback_data="PompaOFF"),
            InlineKeyboardButton("Last Menu", callback_data="AS")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.edit_text(text="Choose an option:", reply_markup=reply_markup
    )
  return FARMER

def PompaON(update: Update, context: CallbackContext) -> int:
  
  update.callback_query.message.edit_text(" Pump ON")
  #comando che attiva la pompa
  keyboard = [
        [
            InlineKeyboardButton("Main Menu", callback_data="principale"),
            InlineKeyboardButton("Last Menu", callback_data="AS")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Choose an option:", reply_markup=reply_markup)
  return FARMER
def PompaOFF(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text(" Pump OFF")
  #comando che disattiva la pompa
  keyboard = [
        [
            InlineKeyboardButton("Main Menu", callback_data="principale"),
            InlineKeyboardButton("Last Menu", callback_data="AS")
        ]
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Choose an option:", reply_markup=reply_markup)
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

def NewThreshold_humidity_info(update: Update, context: CallbackContext) -> int: 
  user_data=context.user_data
  farmerid=user_data["LOGID"]
  listacrops=listaCROPS(farmerid)
  
  update.callback_query.message.edit_text(text=f"{listacrops}")
  update.callback_query.message.reply_text(text="● If you want to modify the minimum value, write <plant name> + min + new value \n"
  "● If you want to modify the maximum value, write <plant name> + max + new value \n"
  "Example: 'Peperoncino min 44'\n"
  "● Write Principale to go back to the main menu")
  return FARMER_TYPING_2

def NewThreshold_humidity_reply(update: Update, context: CallbackContext) -> int:
  user_data=context.user_data
  farmerid=user_data["LOGID"]
  text = update.message.text.split(" ")
  pianta= text[0]
  farmer=json.loads(requests.get(url=f"{SERVER}/farmer/{farmerid}").text)
  plants=json.loads(requests.get(url=f"{SERVER}/plants").text)
  cropsowned=farmer["CROPS_OWNED"]


  if text[0] == "Principale":
    update.message.reply_text('Scegli tra:', reply_markup=reply_markupPrincipale_FARMER)
    return FARMER

  elif text[1]=="min":
    for crop in cropsowned:
      for plant in plants:
        if plant["PLANT_ID"]== crop and plant["PLANT_NAME"]== pianta:
          plantid=plant["PLANT_ID"]
          modified_dict={"THRESHOLD_MOIST_MIN": int(text[2])}
          requests.post(url=f"{SERVER}/plant/{plantid}",json=modified_dict)
    lista=listaCROPS(farmerid)
    update.message.reply_text(f"Ok,done.Here there is the modified list\n {lista} \n Try again if you want to modify something else or write Principale to go back to the main menu")
    return FARMER_TYPING_2

  elif text[1]=="max":
    for crop in cropsowned:
      for plant in plants:
        if plant["PLANT_ID"]== crop and plant["PLANT_NAME"]== pianta:
          plantid=plant["PLANT_ID"]
          modified_dict={"THRESHOLD_MOIST_MAX": int(text[2])}
          requests.post(url=f"{SERVER}/plant/{plantid}",json=modified_dict)
    lista=listaCROPS(farmerid)
    update.message.reply_text(f"Ok,done.Here there is the modified list\n {lista} \n Try again if you want to modify something else or write Principale to go back to the main menu")
    return FARMER_TYPING_2
  return FARMER

def Statistiche_first(update: Update, context: CallbackContext) -> int:
  keyboard = [
      [
          InlineKeyboardButton("ThingsBoard - Statistics", callback_data="thingsboard"),
          InlineKeyboardButton("Main Menu", callback_data="principale"),

      ]
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.edit_text(text="Choose an option:", reply_markup=reply_markup)
  return FARMER

def ThingsBoardFarmer(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text(text="Thingsboard link:")
  keyboard = [
         [
            InlineKeyboardButton("Main Menu", callback_data="principale"),
            InlineKeyboardButton("Last Menu", callback_data="SF")
         ]
     ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.callback_query.message.reply_text(text="Choose an option:", reply_markup=reply_markup    )
  return FARMER


    

def main():

    token="1461734973:AAGtnon-G24cJcWVjVGbp7Lv1DIXhjJNT28" #CLod condiviso
    #token="1990658567:AAG5By57hC8Hbyp9Mc2FTqqsIw8VLV_MsDM" # GreenHOUSE2021

    updater = Updater(token,use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    #updater.dispatcher.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
  
    conv_handler = ConversationHandler(allow_reentry=True,
        entry_points=[CallbackQueryHandler(sign_in, pattern='signin'),CommandHandler('start', start)],
            states={
                SIGNIN_PULSANTI:[CallbackQueryHandler(sign_in, pattern='signin')],
                SIGNIN: [MessageHandler(Filters.regex('^Start$'), start),
                         MessageHandler(Filters.text,sign_in_credenziali),
                        ],
                #da sign in vado a sign in credenziali che legge il messaggio input
                ADMIN: [MessageHandler(Filters.text, callback= id_greenhouse)],

                LEVEL1 :[
                         MessageHandler(Filters.regex('^Start$'), start),
                         CallbackQueryHandler(first_menu_keyboard, pattern='first_menu'),
                         CallbackQueryHandler(first_menu, pattern='main_fm'),
                         CallbackQueryHandler(Statistics, pattern='b1_1'),
                         CallbackQueryHandler(ItemMessage, pattern='b1_3'),
                         CallbackQueryHandler(ThingsBoard, pattern='b2_1'),
                         CallbackQueryHandler(NewThreshold_message, pattern='b2_2'),
                         CallbackQueryHandler(Actuators, pattern='b1_4'),
                         CallbackQueryHandler(Green_House_Parameters, pattern='b1_2'),
                         CallbackQueryHandler(OpenWindows, pattern='OpenWindow'),
                         CallbackQueryHandler(CloseWindows, pattern='CloseWindow'),
                         CallbackQueryHandler(VentOFF, pattern='VentOFF'),
                         CallbackQueryHandler(VentON, pattern='VentON')],
                    
                ADMIN_TYPING : [MessageHandler(Filters.text, callback= NewThreshold_period)],
                ADMIN_TYPING_2 : [MessageHandler(Filters.text, callback= NewParametersGreenhouse)],
                               
                FARMER_TYPING : [MessageHandler(Filters.text, callback= uporadditemfarmer)],
                FARMER_TYPING_2 : [MessageHandler(Filters.text, callback= NewThreshold_humidity_reply)],
                FARMER : [ #premo aggiungi e legge il messaggio
                      MessageHandler(Filters.regex('^Start$'), start),
                      CallbackQueryHandler(displaylist, pattern='AMR'),
                      CallbackQueryHandler(attuatoriscelte, pattern='AS'),
                      CallbackQueryHandler(pompaonoff, pattern='pompaonoff'),
                      CallbackQueryHandler(PompaOFF, pattern='PompaOFF'),
                      CallbackQueryHandler(PompaON, pattern='PompaON'),
                      CallbackQueryHandler(NewThreshold_humidity_info, pattern='newthreshold_humidity'),
                      CallbackQueryHandler(menuprincipaleFarmer, pattern='principale'),
                    
                      CallbackQueryHandler(Statistiche_first, pattern='SF'),
                      CallbackQueryHandler(ThingsBoardFarmer, pattern='thingsboard'),

                      ],
                USER: [ MessageHandler(Filters.regex('^Start$'), start),
                        CallbackQueryHandler(displaylist_USER, pattern='compra_user')],
                USER_TYPING : [MessageHandler(Filters.text, callback= buyitemuser)]
                    
                      
            }, fallbacks=[MessageHandler(Filters.regex('^Done$'), done)])


    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__=="__main__":
    main()
