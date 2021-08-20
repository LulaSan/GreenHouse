from telegram.ext import Updater
import os
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler,Filters,MessageHandler
from telegram import InlineKeyboardButton,ReplyKeyboardMarkup, InlineKeyboardMarkup, Update
############################### Bot ############################################
import telepot
import re

import json
from pprint import pprint
import requests

##AGGIUNGERE MESSAGGIO INIZIALE CHE DICE DI SCRIVERE /start
listaFarmers=json.loads(requests.get(url="http://p4iotsmartgh2021.ddns.net:2000/farmers").text)
# listaFarmers=lista["list"]
SIGNIN, FARMER , FARMER_TYPING, FARMER_TYPING_2= range(4)
keyboardPrincipale= [[InlineKeyboardButton(text=f'Aggiungere, modificare, rimuovere un item', callback_data='b1_1')],
            [InlineKeyboardButton(text=f'Controllare attuatori', callback_data='b1_2')],
            [InlineKeyboardButton(text=f'Statistiche', callback_data='b1_3')],
            [InlineKeyboardButton(text=f'Torna al log in', callback_data='main')]]
reply_markupPrincipale = InlineKeyboardMarkup(keyboardPrincipale)

def menuprincipaleFarmer(update: Update, context: CallbackContext) -> int:
  update.callback_query.message.edit_text('Scegli tra:', reply_markup=reply_markupPrincipale)
  return FARMER

def start(update: Update, context: CallbackContext) -> int:
  user = update.message.from_user

  fp=open("telegram_catalog.json","r")
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
  update.message.reply_text("Chi sei?",reply_markup=main_menu_keyboard())


def update_catalog(loggedUsers):
  fp=open("telegram_catalog.json",'r')
  catalog=json.load(fp)
  fp.close()
  catalog["LOGGED_USERS"]=loggedUsers
  json.dump(catalog,open("telegram_catalog.json","w"),indent=4)



# def main_menu(update: Update, context: CallbackContext) -> int:
#   update.callback_query.message.edit_text("Chi sei?",reply_markup=main_menu_keyboard())


def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton(text=f'Admin', callback_data='signinA')],
                [InlineKeyboardButton(text=f'Farmer', callback_data='signinF')],
                [InlineKeyboardButton(text=f'User', callback_data='signinU')]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)




def sign_in(update: Update, context: CallbackContext) -> int:
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

  update.callback_query.message.edit_text(f"Ok now log in write your id ")

  return SIGNIN

def sign_in_credenziali(update: Update, context: CallbackContext) -> int:
    pprint("sto entrando del sign_in_credd")
    text = update.message.text # splitto il testo
    
    #salvo il LOG ID dell'utente
    fp=open("telegram_catalog.json",'r')
    catalog=json.load(fp)
    fp.close()
    loggedUsers=catalog["LOGGED_USERS"]
    oldid=str(update.effective_chat["id"])
    trovato=0
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

    if trovato==0:
      update.message.reply_text('LOG_ID sbagliato, riprova')
      return SIGNIN
  
    

def displaylist(update: Update, context: CallbackContext) -> int:
  user_data=context.user_data
  #1. stampo lista  2. chiedo di scrivere se nuovo nome item, prezzo e quantità separati da spazi
  #3. chiedo di scrivere "modifica prezzo patate 2/ modifica quantità patate 3 "
  farmerid=user_data["LOGID"]
  singolo=json.loads(requests.get(url=f"http://p4iotsmartgh2021.ddns.net:2000/farmer/{farmerid}").text)
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
      r=requests.post(f"http://p4iotsmartgh2021.ddns.net:2000/uporadditem/{farmerid}/{item}/{prezzo}/None")
    elif text[1]== "quantità" :
      quantita=int(text[3])
      p=requests.post(f"http://p4iotsmartgh2021.ddns.net:2000/uporadditem/{farmerid}/{item}/None/{quantita}")
    
    singolo=json.loads(requests.get(url=f"http://p4iotsmartgh2021.ddns.net:2000/farmer/{farmerid}").text)
    items=singolo["ITEMS_SELL"]
    update.message.reply_text(f"Ok,fatto. Ecco la lista modificata\n {items} \n Riprova se vuoi modificare altro\n digita 'principale' per tornare al menu inziale")
    return FARMER_TYPING
  elif text[0] == "aggiungi":
    item=text[1]
    prezzo=int(text[2])
    quantita=int(text[3])
    requests.post(f"http://p4iotsmartgh2021.ddns.net:2000/uporadditem/{farmerid}/{item}/{prezzo}/{quantita}")
    singolo=json.loads(requests.get(url=f"http://p4iotsmartgh2021.ddns.net:2000/farmer/{farmerid}").text)
    items=singolo["ITEMS_SELL"]
    update.message.reply_text(f"Ok,fatto. Ecco la lista modificata\n {items} \n Riprova se vuoi modificare altro\n digita 'principale' per tornare al menu inziale")
    
    return FARMER_TYPING
  elif text[0] =="rimuovi":
    item=text[1]
    requests.delete(f"http://p4iotsmartgh2021.ddns.net:2000/deleteitem/{farmerid}/{item}")
    singolo=json.loads(requests.get(url=f"http://p4iotsmartgh2021.ddns.net:2000/farmer/{farmerid}").text)
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
  farmer=json.loads(requests.get(url=f"http://p4iotsmartgh2021.ddns.net:2000/farmer/{farmerid}").text)
  plants=json.loads(requests.get(url="http://p4iotsmartgh2021.ddns.net:2000/plants").text)
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
  farmer=json.loads(requests.get(url=f"http://p4iotsmartgh2021.ddns.net:2000/farmer/{farmerid}").text)
  plants=json.loads(requests.get(url="http://p4iotsmartgh2021.ddns.net:2000/plants").text)
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
          requests.post(url=f"http://p4iotsmartgh2021.ddns.net:2000/plant/{plantid}",json=modified_dict)
    lista=listaCROPS(farmerid)
    update.message.reply_text(text=f"Ecco la lista aggiornata\n {lista}\n puoi continuare oppure scegliere un'opzione dal menu", reply_markup=reply_markup )
    return FARMER
  elif text[1]=="max":
    for crop in cropsowned:
      for plant in plants:
        if plant["PLANT_ID"]== crop and plant["PLANT_NAME"]== pianta:
          plantid=plant["PLANT_ID"]
          modified_dict={"THRESHOLD_MOIST_MAX": int(text[2])}
          requests.post(url=f"http://p4iotsmartgh2021.ddns.net:2000/plant/{plantid}",json=modified_dict)
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

#def Threshold_Stat(update: Update, context: CallbackContext) -> int:





  
  




def done(update: Update, _: CallbackContext) -> int:
    update.message.reply_text("niente")

######################################################################

############################# main #########################################
def main():

    token="1461734973:AAGtnon-G24cJcWVjVGbp7Lv1DIXhjJNT28"
    updater = Updater(token,use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
  
    conv_handler = ConversationHandler(
       entry_points=[CallbackQueryHandler(sign_in, pattern='signin')],
        states={
            FARMER_TYPING : [MessageHandler(Filters.text, callback= uporadditemfarmer)],
            FARMER_TYPING_2 : [MessageHandler(Filters.text, callback= NewThreshold_reply)],


            SIGNIN: [MessageHandler(Filters.text,sign_in_credenziali)],
              #da sign in vado a sign in credenziali che legge il messaggio input
             
            FARMER : [ #premo aggiungi e legge il messaggio
                      CallbackQueryHandler(displaylist, pattern='b1_1'),
                      CallbackQueryHandler(attuatoriscelte, pattern='b1_2'),
                      CallbackQueryHandler(pompaonoff, pattern='pompaonoff'),
                      CallbackQueryHandler(PompaOFF, pattern='PompaOFF'),
                      CallbackQueryHandler(PompaON, pattern='PompaON'),
                      CallbackQueryHandler(NewThreshold_info, pattern='newthreshold'),
                      CallbackQueryHandler(menuprincipaleFarmer, pattern='principale'),
                      
                      CallbackQueryHandler(Statistiche_first, pattern='b1_3'),
                      CallbackQueryHandler(ThingsBoard, pattern='thingsboard'),

                      
                      ]
                     
                      
                     # premo rimuovi e legge il messaggio
        }, fallbacks=[MessageHandler(Filters.regex('^Done$'), done)])

    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__=="__main__":
    main()
