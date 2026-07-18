from icalendar import Calendar, Event
from datetime import datetime, timedelta
import uuid
import pytz
import pathlib
import requests
import os
import sys

class UPC_API:
    url = "https://visor-horaris-nest.upc.edu/schedule"
    sfx_carrera = "degrees"
    sfx_asignaturas = "subjects"
    sfx_horarios = "schedule"
    def generic_pub(self):
        ano = None
        mitad = None
        if datetime.now().month >= 7:
            ano = datetime.now().year
            mitad = 1
        else:
            mitad = 2
            ano = datetime.now().year-1
        year = datetime.now().year
        pub= f"{mitad}/{ano}/PUB"
        return pub

class UPC_URL(UPC_API):
    def __init__(self,url:str):
        super().__init__()
        self.url:str=url
        self.splitData()
        self.centro:CentroUPC = CentroUPC(self.dataDict['escola'])
        self.carrera:Carreras = Carreras(self.centro)
        self.asignaturas:Asignaturas = Asignaturas(self.carrera,int(self.dataDict['programa']))
        self.grupos:dict = self.dataDict['groups']
        self.examenes:dict = self.getExamsDict()
        

    
    def splitData(self):
        info=self.url.split("?")[1]
        info=info.split("&")
        self.dataDict={}
        for dato in info:
            
            match dato.split("=")[0]:
                case 'assignaturas':
                    datos=dato.split("=")[1].split(",")
                    self.dataDict.update({dato.split("=")[0]:datos})
                case 'groups':
                    grupos={}
                    datos=dato.split("=")[1].split(",")
                    for data in datos:
                        grup=data.split("of")[0]
                        clase=data.split("of")[1]
                        if int(clase) in grupos:
                            grupos[int(clase)].append(grup)
                        else:
                            grupos.update({int(clase):[grup]})
                    self.dataDict.update({dato.split("=")[0]:grupos})
                case 'lang':
                    self.dataDict.update({dato.split("=")[0]:dato.split("=")[1]})

                case _:
                    self.dataDict.update({dato.split("=")[0]:int(dato.split("=")[1])})

        return self
    def getExamsDict(self):
        exms = {}
        for asignatura in self.grupos.keys():
            exms[asignatura]=Horarios(self.asignaturas.getAsignatura(asignatura)).getExamsList()
        return exms



class CentroUPC(UPC_API):
    all=[{
          "idSchool": 205,
          "enName": "Terrassa School of Industrial, Aerospace and Audiovisual Engineering",
          "caName": "Escola Superior d'Enginyeries Industrial, Aeroespacial i Audiovisual de Terrassa",
          "esName": "Escuela Superior de Ingenier\xedas Industrial, Aeroespacial y Audiovisual de Terrassa",
          "shortName": "ESEIAAT"
        },
        {
          "idSchool": 295,
          "enName": "Barcelona East School of Engineering",
          "caName": "Escola d'Enginyeria de Barcelona Est",
          "esName": "Escuela de Ingenier\xeda de Barcelona Este",
          "shortName": "EEBE"
        },
        {
          "idSchool": 250,
          "enName": "Barcelona School of Civil Engineering",
          "caName": "Escola T\xe8cnica Superior d'Enginyeria de Camins, Canals i Ports de Barcelona",
          "esName": "Escuela T\xe9cnica Superior de Ingenier\xeda de Caminos, Canales y Puertos de Barcelona",
          "shortName": "ETSECCPB"
        },
        {
          "idSchool": 200,
          "enName": "Maths and Statistics faculty",
          "caName": "Facultat de Matem\xe0tiques i Estad\xed\xadstica",
          "esName": "Facultad de Matem\xe1ticas y Estadistica",
          "shortName": "FME"
        },
        {
          "idSchool": 240,
          "enName": "Barcelona School of Industrial Engineering",
          "caName": "Escola T\xe8cnica Superior d'Enginyeria Industrial de Barcelona",
          "esName": "Escuela T\xe9cnica Superior de Ingenier\xeda Industrial de Barcelona",
          "shortName": "ETSEIB"
        },
        {
          "idSchool": 230,
          "enName": "Barcelona School of Telecommunications Engineering",
          "caName": "Escola T\xe8cnica Superior d'Enginyeria de Telecomunicaci\xf3 de Barcelona",
          "esName": "Escuela T\xe9cnica Superior de Ingenier\xeda de Telecomunicaci\xf3n de Barcelona",
          "shortName": "ETSETB"
        },
        {
          "idSchool": 370,
          "enName": "Terrassa School of Optics and Optometry",
          "caName": "Facultat d'\xd2ptica i Optometria de Terrassa",
          "esName": "Facultad de \xd3ptica y Optometr\xeda de Terrassa",
          "shortName": "FOOT"
        },
        {
          "idSchool": 290,
          "enName": "Vall\xe8s School of Architecture",
          "caName": "Escola T\xe8cnica Superior d'Arquitectura del Vall\xe8s",
          "esName": "Escuela T\xe9cnica Superior de Arquitectura del Vall\xe8s",
          "shortName": "ETSAV"
        },
        {
          "idSchool": 310,
          "enName": "Barcelona School of Building Construction",
          "caName": "Escola Polit\xe8cnica Superior d'Edificaci\xf3 de Barcelona",
          "esName": "Escuela Polit\xe9cnica Superior de Edificaci\xf3n de Barcelona",
          "shortName": "EPSEB"
        },
        {
          "idSchool": 330,
          "enName": "Manresa School of Engineering",
          "caName": "Escola Polit\xe8cnica Superior d'Enginyeria de Manresa",
          "esName": "Escuela Polit\xe9cnica Superior de Ingenier\xeda de Manresa",
          "shortName": "EPSEM"
        },
        {
          "idSchool": 340,
          "enName": "Polytechnic School of Engineering of Vilanova i la Geltr\xfa",
          "caName": "Escola Polit\xe8cnica Superior d'Enginyeria de Vilanova i la Geltr\xfa",
          "esName": "Escuela Polit\xe9cnica Superior de Ingenier\xeda de Vilanova i la Geltr\xfa",
          "shortName": "EPSEVG"
        }
      ]
    def __init__(self,id:int):
        self.id:int
        self.enName:str
        self.caName:str
        self.esName:str
        self.shortName:str
        self.setInfo(id)
        super().__init__()


    @classmethod
    def setInfo(cls,id):
        for centro in cls.all:
            if centro["idSchool"]==id :
                cls.enName=centro["enName"]
                cls.caName=centro["caName"]
                cls.shortName=centro["shortName"]
                cls.id=id
                cls.url_carrera=f"{cls.url}/{cls.sfx_carrera}/{id}"
                return cls
        print("[ERROR]: No se ha encontrado el centro elegido")
        return cls
    
    def getUrl(self):
        return self.url_carrera
    
    @classmethod
    def getDict(cls):
        universidades={}
        for centro in cls.all:
          universidades[f"{centro["shortName"]} - {centro["caName"]}"] = centro["idSchool"]
        return universidades
    
    @classmethod
    def getList(cls):
        universidades=[]
        for uni in cls.getDict():
            universidades.append(uni)
        return universidades
    
    @classmethod
    def getID_fromDict(cls,centro:str):
      return cls.getDict()[centro]
    
    @classmethod
    def getID_fromList(cls,posicion:int):
      return cls.getID_fromDict(cls.getList()[posicion])
    
    @classmethod
    def setID_fromDict(cls,centro:str):
      return cls(cls.getID_fromDict(centro))
    
    @classmethod
    def setID_fromList(cls,posicion:int):
      return cls(cls.getID_fromList(posicion))
        
    
class Carreras(UPC_API):

  def __init__(self,centro:CentroUPC):
      self.centro:CentroUPC = centro
      self.url_carrera:str = centro.getUrl()
      super().__init__()

  
  def getDict(self):
      grados={}
      carreras = requests.get(self.url_carrera)
      carreras = carreras.json()
      for carrera in carreras:
          grados[carrera['nom_cat']]=carrera['codi_programa']
      return grados
  
  def getList(self):
      grados=[]
      for grado in self.getDict().keys():
          grados.append(grado)
      return grados
  
  def getID_fromDict(self,carrera:str):
      return self.getDict()[carrera]
  
  def getID_fromList(self,posicion:int):
      return self.getID_fromDict(self.getList()[posicion])
      

  @classmethod
  def from_ID_School(cls,id):
      return cls(CentroUPC(id))
  
  @classmethod
  def from_url(cls,url_carrera:str):
      centro=int(url_carrera.split("/")[-1])
      return cls(CentroUPC(centro))

class Asignaturas(UPC_API):
  def __init__(self,carrera:Carreras,id_carrera):
      self.carrera:Carreras =carrera
      self.id_carrera:int=id_carrera
      self.url_asignatura:str = f"{self.url}/{self.sfx_asignaturas}/{self.id_carrera}/{self.generic_pub()}"
      super().__init__()

  def getDict(self):
      asignaturas = requests.get(self.url_asignatura)
      asignaturas = asignaturas.json()
      print(asignaturas)
      clases={}
      for asignatura in asignaturas:
          clases[f"{asignatura['sigles']} - {asignatura['nom_cat']}"] = asignatura['codi_upc_ud']
      return clases

  def getList(self):
      grados=[]
      for grado in self.getDict().keys():
          grados.append(grado)
      return grados
  
  def getID_fromDict(self,asignatura:str):
      return self.getDict()[asignatura]
  
  def getID_fromList(self,posicion:int):
      return self.getID_fromDict(self.getList()[posicion])
  
  def getAsignatura(self,ID):
      asignaturas = requests.get(self.url_asignatura)
      asignaturas = asignaturas.json()
      for asignatura in asignaturas:
          if asignatura['codi_upc_ud']==str(ID):
              nombre=asignatura['nom_cat']
              siglas=asignatura['sigles']
              codi=asignatura['codi_upc_ud']
              return Asignatura(nombre=nombre,sigla=siglas,codi_upc=codi,carrera=self)


class Asignatura(UPC_API):
    def __init__(self,carrera:Asignaturas,sigla:str,nombre:str,codi_upc:int):
        self.carrera:Asignaturas=carrera
        self.sigles:str = sigla
        self.nom_cat:str = nombre
        self.codi_upc:int = codi_upc
        super().__init__()


class Horarios(UPC_API):
    def __init__(self,asignatura:Asignatura):
        self.asignatura:Asignatura = asignatura
        self.url_horarios:str = f"{self.url}/{self.sfx_horarios}/{asignatura.carrera.id_carrera}/{self.generic_pub()}"
        self.horarios_json= requests.get(self.url_horarios)
        self.examenes_json= self.horarios_json.json()["response_examens"]
        self.horarios_json= self.horarios_json.json()["response"]
    def getGruposDict(self):
        grupos = {}
        for horario in self.horarios_json:
            for grupo in horario:
                if grupo["codi_upc_ud"] == self.asignatura.codi_upc:
                    if grupo["grup"] in grupos:
                        grupos[grupo["grup"]].append(grupo)
                    else:
                        grupos[grupo["grup"]] = [grupo]
        return grupos
    def getExamsList(self):
        examenes = []
        for clase in self.examenes_json:
            for examen in clase:
                if examen["codi_upc_ud"] == self.asignatura.codi_upc:
                    datos_examen = examen
                    datos_examen['sigles'] = self.asignatura.sigles
                    examenes.append(datos_examen)
        return examenes


    def getGruposList(self):
        grupos = []
        for grupo in self.getGruposDict().keys():
            grupos.append(grupo)
        return grupos

if __name__ == "__main__":
    print("by Zk")
    print(UPC_API().generic_pub())
    var = "https://visorhoraris.upc.edu/horaris?escola=295&quad=2&curs=2025&programa=1264&assignaturas=820094,820430,820425,295906,820428,820426&groups=M1of820428,M1of820426,M1of820425,M15of820425,M11of820426,M12of820426,M1of820430,M13of820426,M13of820428,M13of820430,M12of820428,M11of820428&lang=cahttps://visorhoraris.upc.edu/horaris?escola=295&quad=2&curs=2025&programa=1264&assignaturas=820094,820430,820425,295906,820428,820426&groups=M1of820428,M1of820426,M1of820425,M15of820425,M11of820426,M12of820426,M1of820430,M13of820426,M13of820428,M13of820430,M12of820428,M11of820428&lang=ca"
    info_URL=UPC_URL(var)
    print(info_URL.grupos)
    print(info_URL.asignaturas.getAsignatura(list(info_URL.grupos.keys())[0]).sigles)
    patata=info_URL.asignaturas.getAsignatura(list(info_URL.grupos.keys())[0])
    #print(info_URL.examenes)


