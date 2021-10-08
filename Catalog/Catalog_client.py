import json
import time
import requests 
import datetime

class AdminClient():
    def __init__(self,AdminList):
        self.AdminList=AdminList
    def showlist(self):
        listaadmin=self.AdminList.copy()
        prettylist=json.dumps(listaadmin,indent=4)
        return prettylist

class PlantClient():
    def __init__(self,PlantsList):
        self.PlantsList=PlantsList
    
    def showlist(self):
        listapiante=self.PlantsList.copy()
        prettylist=json.dumps(listapiante,indent=4)

        return prettylist


    def search(self,PlantID,oggetto=None):
        self.PlantID=PlantID 
        self.oggetto=oggetto
        trovato=None
        nontrovato=1
        for i in range(len(self.PlantsList)): 
            if self.PlantsList[i]["PLANT_ID"]==self.PlantID:
                # è la plant giusta - tutte le info
                if (self.oggetto==None):
                    trovato=(self.PlantsList[i])
                    nontrovato=0
                elif (self.oggetto!=None ): # info sull'oggetto
                    if self.oggetto in self.PlantsList[i].keys():
                        trovato=(self.PlantsList[i][self.oggetto])
                        nontrovato=0
                    else:
                        return f' Non esiste questa Key '
        if nontrovato==1:
            return f' Nulla corrisponde alla tua ricerca, riprova!'
        else:
            return str(trovato)
    
    def addplant(self,deviceID,newDevice):
        self.deviceID=deviceID
        self.newDevice=(newDevice) #this must be a dictionary
        modifica=0
        for i in range(len(self.PlantsList)):
            if self.deviceID==self.PlantsList[i]["PLANT_ID"] :
                modifica=1
                parametriDaMod=newDevice.copy()
                keysDaMod=list(parametriDaMod.keys())
                valuesdaMod=list(parametriDaMod.values())
                for key in range(len(keysDaMod)):
                    if keysDaMod[key] in self.PlantsList[i].keys(): #cerco tra le key ognuna di quelle presente nel body della richiesta
                        self.PlantsList[i][keysDaMod[key]]=valuesdaMod[key]
                self.updateJson()
                return f' Ho modificato quello che mi hai chiesto correttamente'
        
        if modifica==0:
            plantIDnew=self.newDevice["PLANT_ID"]
            newinformations={
            "BROKER_HOST": "10.42.0.1", 
            "BROKER_PORT": 1884, 
            "STATUS_TOPIC": "/p4iot/plants/{}/status".format(plantIDnew),
            "COMMANDS_TOPIC": "/p4iot/plants/{}/commands/+".format(plantIDnew),
            "SENSORS_TOPIC": "/p4iot/plants/{}/sensors".format(plantIDnew)}
            # newinformations=json.dumps(newinformations1)
            deviceCompleto = {**newDevice, **newinformations}
            self.PlantsList.append(deviceCompleto)
            #updating Json
            self.updateJson()

            return f'Il Catalogo è stato aggiornato correttamente'
    
    def removeplant(self,deviceID):
        self.deviceID=deviceID
        for i in range(len(self.PlantsList)):
            if self.deviceID==self.PlantsList[i]["PLANT_ID"] :
                del self.PlantsList[i]
                self.updateJson()
        return "l'elemento è stato rimosso"

    def updateJson(self):
        fp=open("Catalog.json",'r')
        catalog=json.load(fp)
        fp.close()
        catalog["Plants"]=self.PlantsList
        json.dump(catalog,open("Catalog.json",'w'),indent=4)


class StatisticClient():
    def __init__(self,StatisticList):
        self.StatisticList=StatisticList

    def search(self,statistic):
        self.statistic=statistic
        trovato=None
        nontrovato=1
        if statistic in self.StatisticList[0].keys(): #water_period o temperature_period             
            trovato=self.StatisticList[0][self.statistic]
            nontrovato=0
        if nontrovato==1:
            return f' Nulla corrisponde alla tua ricerca, riprova!'
        else:
            return str(trovato)
    
    def modify(self,statistic,valore):
        self.statistic=statistic
        nontrovato=1
        if statistic in self.StatisticList[0].keys(): # se statstic è una key del dizionario, water_period o temperature_period             
            self.StatisticList[0][self.statistic]=valore #a quella key scrivi il valore
            nontrovato=0
            trovato=self.StatisticList[0]
            fp=open("Catalog.json",)
            catalog=json.load(fp)
            # catalog["Statistics"][0].update(self.StatisticList)
            catalog["Statistics"][0][statistic]=valore
            json.dump(catalog,open("Catalog.json",'w'),indent=4)
            fp.close()
        if nontrovato==1:
            return f' Nulla corrisponde alla tua ricerca, riprova!'
        else:
            return str(trovato) 

class GreenhouseClient():
    def __init__(self,GreenhousesList):
        self.GreenhousesList=GreenhousesList
    
    def showlist(self):
        prettylist=json.dumps(self.GreenhousesList,indent=4)
        return prettylist

    def search(self,GreenhouseID,oggetto=None):
        self.GreenhouseID=GreenhouseID 
        self.oggetto=oggetto
        trovato=None
        nontrovato=1
        for i in range(len(self.GreenhousesList)): 
            if self.GreenhousesList[i]["GREENHOUSE_ID"]==self.GreenhouseID:
                # è la Greenhouse giusta - tutte le info
                if (self.oggetto==None):
                    trovato=(self.GreenhousesList[i])
                    nontrovato=0
                elif (self.oggetto!=None ): # info sull'oggetto
                    if self.oggetto in self.GreenhousesList[i].keys():
                        trovato=(self.GreenhousesList[i][self.oggetto])
                        nontrovato=0
                    else:
                        return f' Non esiste questa Key '
        if nontrovato==1:
            return f' Nulla corrisponde alla tua ricerca, riprova!'
        else:
            return str(trovato)
    
    def addgreenhouse(self,newID,newDevice):
        self.newID=newID
        self.newDevice=newDevice #this must be a dictionary
        modificaG=0
        for i in range(len(self.GreenhousesList)):
            if self.newID==self.GreenhousesList[i]["GREENHOUSE_ID"] :
                modificaG=1
                parametriDaMod=newDevice.copy()
                keysDaMod=list(parametriDaMod.keys())
                valuesdaMod=list(parametriDaMod.values())
                for key in range(len(keysDaMod)):
                    if keysDaMod[key] in self.GreenhousesList[i].keys(): #cerco tra le key ognuna di quelle presente nel body della richiesta
                        self.GreenhousesList[i][keysDaMod[key]]=valuesdaMod[key]
                self.updateJson()
                return f' Ho modificato quello che mi hai chiesto correttamente'
        
        if modificaG==0:
            GreenhouseIDnew=self.newDevice["GREENHOUSE_ID"]
            newinformations={
            "BROKER_HOST": "10.42.0.1", 
            "BROKER_PORT": 1884, 
            "STATUS_TOPIC": "/p4iot/greenhouses/{}/status".format(GreenhouseIDnew),
            "COMMANDS_TOPIC": "/p4iot/greenhouses/{}/commands/+".format(GreenhouseIDnew),
            "SENSORS_TOPIC": "/p4iot/greenhouses/{}/sensors".format(GreenhouseIDnew)}
            deviceCompleto = {**newDevice, **newinformations}
            self.GreenhousesList.append(deviceCompleto)
            #updating Json
            self.updateJson()            
            return f'Il Catalogo è stato aggiornato correttamente'

    def removegreenhouse(self,deviceID):
        self.deviceID=deviceID
        for i in range(len(self.GreenhousesList)):
            if self.deviceID==self.GreenhousesList[i]["GREENHOUSE_ID"] :
                del self.GreenhousesList[i]
                
        #rimuovo pianta nella lista delle piante
        fp=open("Catalog.json",'r')
        catalog=json.load(fp)
        plantlist=catalog["Plants"]
        plantlistcopia=plantlist.copy()
        already_removed=0;
        fp.close()
        for j in range(len(plantlist)) :
                if plantlist[j]["GREENHOUSE_ID"]==self.deviceID:
                    already_removed+=1
                    del plantlistcopia[j-already_removed]
                
        catalog["Plants"]=plantlistcopia
        json.dump(catalog,open("Catalog.json",'w'),indent=4)
        self.updateJson()
        return "l'elemento è stato rimosso "    
    def updateJson(self):
        fp=open("Catalog.json",'r')
        catalog=json.load(fp)
        fp.close()
        catalog["Greenhouses"]=self.GreenhousesList
        json.dump(catalog,open("Catalog.json",'w'),indent=4)
        
class FarmerClient():
    def __init__(self,FarmersList):
        self.FarmersList=FarmersList

    def listforuser(self):
        display={}
        for i in range(len(self.FarmersList)):
            display={"FARMER_ID": self.FarmersList[i]["FARMER_ID"],
                    "Items":self.FarmersList[i]["ITEMS_SELL"]}
            dispjson=json.dumps(display,indent=4)

            return  dispjson
    
    def farmerslist(self):
        display={"list":[]}
        # display["list"]=self.FarmersList
        display=self.FarmersList
        displayjson=json.dumps(display,indent=4)
        return displayjson
        #return self.FarmersList
    
    def farmerlist(self,farmerID):
        for i in range(len(self.FarmersList)):
            if farmerID == self.FarmersList[i]["FARMER_ID"]:
                dispjson=json.dumps(self.FarmersList[i],indent=4)
                return dispjson
            

    def addfarmer(self, farmerID,newFarmer):
        self.farmerID=farmerID
        self.newFarmer=(newFarmer) #this must be a dictionary
        modifica=0
        for i in range(len(self.FarmersList)):
            if self.farmerID==self.FarmersList[i]["FARMER_ID"] :
                modifica=1
                parametriDaMod=newFarmer.copy()
                keysDaMod=list(parametriDaMod.keys())
                valuesdaMod=list(parametriDaMod.values())
                for key in range(len(keysDaMod)):
                    if keysDaMod[key] in self.FarmersList[i].keys(): #cerco tra le key ognuna di quelle presente nel body della richiesta
                        self.FarmersList[i][keysDaMod[key]]=valuesdaMod[key]
                self.updateJson()
                return f' Ho modificato quello che mi hai chiesto correttamente'
        
        if modifica==0:
            self.FarmersList.append(newFarmer)
            #updating Json
            self.updateJson()
            return f'Il Catalogo è stato aggiornato correttamente'
        
    def addItem(self,farmerID,item,price=None,quantity=None):
        self.price=price # la quantity deve essere la totale disponibile in quel momento
        self.quantity=quantity
        self.item=item
        update=0
        for i in range(len(self.FarmersList)):
            if farmerID==self.FarmersList[i]["FARMER_ID"]:
                for j in range(len(self.FarmersList[i]["ITEMS_SELL"])):
                    if item == self.FarmersList[i]["ITEMS_SELL"][j]["item"]: # se l'item già c'è faccio l'update della quantità o del prezzo
                        update=1
                        if self.price!="None":
                            self.FarmersList[i]["ITEMS_SELL"][j]["price"]=int(self.price)
                            
                        if self.quantity!="None": # se uno c'è e l'altro no, è un modo per non scambiare gli input
                            self.FarmersList[i]["ITEMS_SELL"][j]["quantityAvailable"]=int(self.quantity)
                        self.updateJson()
                        return(f"ho modificato {item}")

                if update==0: #se l'item non c'è lo aggiungo alla lista 
                    newitem={
                        "item":self.item,
                        "price":int(self.price),
                        "quantityAvailable":int(self.quantity)
                    }
                    self.FarmersList[i]["ITEMS_SELL"].append(newitem)
                    self.updateJson()
                    return (f"ho aggiunto {self.item}")
    def deleteItem(self,farmerID,item):
        self.item=item
        self.farmerID=farmerID
        farmerlistcopia=self.FarmersList.copy()
        for i in range(len(self.FarmersList)):
            if farmerID==self.FarmersList[i]["FARMER_ID"]:
                for j in range(len(self.FarmersList[i]["ITEMS_SELL"])):
                    if item == self.FarmersList[i]["ITEMS_SELL"][j]["item"]: # se l'item già c'è faccio l'update della quantità o del prezzo
                        del farmerlistcopia[i]["ITEMS_SELL"][j]
        
        self.FarmersList=farmerlistcopia
        self.updateJson()
        return f"ho rimosso {item}"
                                    
    def updateJson(self):
        fp=open("Catalog.json",'r')
        catalog=json.load(fp)
        fp.close()
        catalog["Farmers"]=self.FarmersList
        json.dump(catalog,open("Catalog.json",'w'),indent=4)
    
class UserClient():
    def __init__(self,UsersList):
        self.UsersList=UsersList
        #l'user potrà vedere una lista di ortaggi con prezzo e qt disponibile, identificati da un ID che è quello del farmer,
        #una volta scelto l'oggetto farà una request DELETE con farmerID e nome dell'item e quantità desiderata
  
    def buyitem(self,FarmerID,item,quantity):
        self.FarmerID=FarmerID
        self.quantity=(quantity)
        self.item=item
        fp=open("Catalog.json",'r')
        catalog=json.load(fp)
        FarmersList=catalog["Farmers"]
        farmerlistcopia=FarmersList.copy()
        fp.close()
        for i in range(len(FarmersList)):
            if FarmerID==FarmersList[i]["FARMER_ID"]:
                for j in range(len(FarmersList[i]["ITEMS_SELL"])):
                    if self.item == FarmersList[i]["ITEMS_SELL"][j]["item"]:
                        if int(quantity)<FarmersList[i]["ITEMS_SELL"][j]["quantityAvailable"]: #se ne vuole meno, aggiorno la quantità disponibile
                            FarmersList[i]["ITEMS_SELL"][j]["quantityAvailable"]+= -int(self.quantity)
                            nuovadisponibile=FarmersList[i]["ITEMS_SELL"][j]["quantityAvailable"]
                            self.updateJson(FarmersList)
                            return f" la quantità rimanente di {self.item} è {nuovadisponibile}"

                        elif int(quantity)==FarmersList[i]["ITEMS_SELL"][j]["quantityAvailable"]:#se vuole tutto ciò che è disponibile, elimino l'item
                                del farmerlistcopia[i]["ITEMS_SELL"][j]
                                FarmersList=farmerlistcopia
                                self.updateJson(FarmersList)
                                return "hai chiesto tutta la quanittà disponibile, l'item è ora terminato"

                        elif int(quantity)>FarmersList[i]["ITEMS_SELL"][j]["quantityAvailable"]: # se ne vuole trppo --> error
                            quantitadisponibile=FarmersList[i]["ITEMS_SELL"][j]["quantityAvailable"]
                            return f"Quantità richiesta non disponibile, la quantità disponibile è {quantitadisponibile}"
                        
    def updateJson(self,FarmersList):
        self.FarmersList=FarmersList
        fp=open("Catalog.json",'r')
        catalog=json.load(fp)
        fp.close()
        catalog["Farmers"]=self.FarmersList
        json.dump(catalog,open("Catalog.json",'w'),indent=4)


                        

                       

        
        
