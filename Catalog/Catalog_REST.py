import cherrypy
from Catalog_client import *


class CHERRY_CATALOG():
    exposed=True

    def __init__(self):
       fp=open("Catalog.json")
       catalog=json.load(fp)
       self.Admins=catalog["Admins"]
       self.admin=AdminClient(self.Admins)

       self.Greenhouses=catalog["Greenhouses"]
       self.greenhouse=GreenhouseClient(self.Greenhouses)
       self.Plants=catalog["Plants"]
       self.plant=PlantClient(self.Plants)

       self.Farmers=catalog["Farmers"]
       self.farmer=FarmerClient(self.Farmers)
       self.Users=catalog["Users"]
       self.user=UserClient(self.Users)
       self.Statistics=catalog["Statistics"]
       self.statistic=StatisticClient(self.Statistics)
     
       fp.close()

       

    def GET(self,*uri): #to retrieve information
        output=''
        if len(uri)!=0:
            if uri[0]=='users':
                output=str(self.user.showlist())
		
            if uri[0]=='plants':
                output=str(self.plant.showlist())
                
            if uri[0]=='admins':
                output=str(self.admin.showlist())                
            
            if uri[0]=='plant': 
                if len(uri)==2:
                    output=str(self.plant.search(uri[1],None)) # tutte le informazioni su quella plant http://localhost:8080/plant/84F3EB33DB49
                elif len(uri)==3:
                    output=str(self.plant.search(uri[1],uri[2])) #informazione specifica sulla plant http://localhost:8080/plant/84F3EB33DB49/STATUS_TOPIC
                return str(output)

            if uri[0]=='greenhouses':
                output=str(self.greenhouse.showlist())

            if uri[0]=='greenhouse': #:2000/greenhouse/GreenhouseID
                if len(uri)==2:
                    output=str(self.greenhouse.search(uri[1],None)) 
                elif len(uri)==3:
                    output=str(self.greenhouse.search(uri[1],uri[2])) 
                return str(output)
            if uri[0]=='farmers':
                output=(self.farmer.farmerslist())
                return (output)

            if uri[0]=="farmer":
                output= str(self.farmer.farmerlist(uri[1]))

            if uri[0]=='itemstobuy':
                output=(self.farmer.listforuser())
                return (output)

            if uri[0]=='statistic': 
                if len(uri)==2:
                    output=str(self.statistic.search(uri[1])) # http://localhost:8080/statistic/water_period
                return str(output)
                
        return (output)
            
                
            
          
    def POST(self,*uri):
        output_post=''
        if uri[0]=='plant':
            #aggiungere un device - non inserire nell'url l'ID
            body_p=cherrypy.request.body.read()
            jsonBody_p=json.loads(body_p)
            output_post=str(self.plant.addplant(uri[1],jsonBody_p))

        if uri[0]=='greenhouse':
            body_g=cherrypy.request.body.read()
            jsonBody_g=json.loads(body_g)
            output_post=str(self.greenhouse.addgreenhouse(uri[1],jsonBody_g))

        if uri[0]=="statistic": #serve solo a cambiare il periodo
            output_post=str(self.statistic.modify(uri[1],uri[2]))#http://localhost:8080/statistic/water_period/50
        #####FARMER###### /farmeritem/1234/patate/32/None
        if uri[0]=="uporaddfarmer":
            body_f=cherrypy.request.body.read()
            jsonBody_f=json.loads(body_f)
            output_post=str(self.farmer.addfarmer(uri[1],jsonBody_f))
        if uri[0]=='uporadditem':
            output_post=str(self.farmer.addItem(uri[1],uri[2],uri[3],uri[4]))
        return output_post

    def DELETE(self,*uri):
        output_del=''
        if uri[0]=='plant':
            #rimuovere un device
            output_del=self.plant.removeplant(uri[1])

        if uri[0]=='greenhouse':
            #rimuovere un device
            output_del=self.greenhouse.removegreenhouse(uri[1])
        if uri[0]=='deleteitem':
            output_del=self.farmer.deleteItem(uri[1],uri[2])
        if uri[0]=='buyitem':
            output_del=str(self.user.buyitem(uri[1],uri[2],uri[3]))

        return output_del

        

if __name__=="__main__": 
    conf = {
		'/':{
			'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on':True
		    }
        }
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 2000})
    cherrypy.quickstart(CHERRY_CATALOG(),'/',conf)

   # cherrypy.engine.start()
    #cherrypy.engine.block()
