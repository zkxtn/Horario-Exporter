from PyQt5 import QtCore, QtGui, QtWidgets
import UI_App as App
from UPC import CentroUPC,UPC_URL,Asignatura,Asignaturas as Clases,Horarios,Carreras
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import uuid
import pytz
import os


def vincular_funciones(ui:App.Ui_Form):
    global select_asignatura, button_remove, button_create,button_add
    global select_carrera, select_uni, select_grupo, selected_classes, sem_end, sem_start
    global url_editor,button_ok,button_remove_exam,select_exam
    global horario_elegido
    global examenes_elegidos

    horario_elegido={}
    examenes_elegidos={}
    
    select_carrera=ui.Grado_Selector
    select_asignatura=ui.Clase_Selector
    select_uni=ui.Uni_Selector
    select_grupo=ui.Grupos_List
    selected_classes=ui.Horario__List
    sem_start=ui.Start_Date
    sem_end=ui.End_Date
    button_remove=ui.Eliminar_Button
    button_add=ui.Anadir_Button
    button_create=ui.Export_Button
    url_editor=ui.Url_Field
    button_ok=ui.Url_Button
    button_remove_exam=ui.Eliminar_Examen_Button
    select_exam=ui.Examen_List


    button_create.clicked.connect(create_ics)
    button_remove.clicked.connect(remove_class)
    button_remove_exam.clicked.connect(remove_exam)
    button_add.clicked.connect(add_class)
    button_ok.clicked.connect(addFromUrl)
    select_asignatura.currentIndexChanged.connect(selected_asignatura)
    select_uni.addItem("Selecciona el centro universitario")
    select_uni.addItems(CentroUPC.getList())
    select_uni.currentIndexChanged.connect(selected_university)
    select_carrera.currentIndexChanged.connect(selected_career)

def selected_university(index):
    if index==0:
        return
    index=index-1
    global centro
    global carrera
    centro=CentroUPC(CentroUPC.getID_fromList(index))
    print(f"Centro Seleccionado:{centro.shortName}")
    carrera=Carreras(centro)
    setCarreras(carrera=carrera)

def setCarreras(carrera:Carreras):
    select_carrera.clear()
    select_carrera.addItem("Selecciona el grado universitario")
    select_carrera.addItems(carrera.getList())

def selected_career(index):
    if index==0:
        return
    index=index-1
    global clases
    clases=Clases(carrera,carrera.getID_fromList(index))
    setAsignaturas(clases)
    print(f"Grado Seleccionado:{carrera.getList()[index]}")

def setAsignaturas(clases:Clases):
    select_asignatura.clear()
    select_asignatura.addItem("Selecciona la assignatura")
    select_asignatura.addItems(clases.getList())


def selected_asignatura(index):
    if index==0:
        return
    index=index-1
    global asignatura
    asignatura=clases.getAsignatura(clases.getID_fromList(index))
    print(f"Asignatura Seleccionada: {asignatura.sigles} - {asignatura.nom_cat}")
    setGrupos(asignatura)

def setGrupos(asignatura:Asignatura):
    global horarios_API
    global grupos
    global examenes
    grupos = Horarios(asignatura=asignatura).getGruposDict()
    examenes = Horarios(asignatura=asignatura).getExamsList()
    horarios_API = Horarios(asignatura)
    select_grupo.clear()
    select_grupo.addItems(horarios_API.getGruposList())


    
def add_class():
    if select_grupo.count() == 0:
        return
    if select_grupo.currentItem() == None:
        return
    if select_grupo.selectedItems():
        grupo_seleccionado=f"{select_asignatura.itemText(select_asignatura.currentIndex())} - {select_grupo.currentItem().text()}"
        examen_seleccionado=select_asignatura.itemText(select_asignatura.currentIndex())
    if grupo_seleccionado not in horario_elegido:
        horario_elegido.update({grupo_seleccionado: grupos[select_grupo.currentItem().text()]})
        selected_classes.addItem(grupo_seleccionado)
    if examen_seleccionado not in examenes_elegidos:
        select_exam.addItem(examen_seleccionado)
        examenes_elegidos[examen_seleccionado] = examenes

    

def remove_class():
    if selected_classes.count() == 0:
        return
    if selected_classes.currentItem() == None:
        return
    grupo_seleccionado = selected_classes.currentItem().text()
    horario_elegido.pop(grupo_seleccionado)
    selected_classes.takeItem(selected_classes.currentRow())

def remove_exam():
    if select_exam.count() == 0 or select_exam.currentItem() == None:
        return
    selected_exam = select_exam.currentItem().text()
    examenes_elegidos.pop(selected_exam)
    select_exam.takeItem(select_exam.currentRow())

def addFromUrl():
    if url_editor.text()=="":
        return
    try:
        datos=UPC_URL(url_editor.text())
        for asignatura in datos.grupos.keys():
            clase=datos.asignaturas.getAsignatura(asignatura)
            horario=Horarios(clase)
            for grupo in datos.grupos[asignatura]:
                grupo_seleccionado=f"{clase.sigles} - {clase.nom_cat} - {grupo}"
                if grupo_seleccionado in horario_elegido:
                    return
                else:
                    horario_elegido.update({grupo_seleccionado: horario.getGruposDict()[grupo]})
                    selected_classes.addItem(grupo_seleccionado)
            if asignatura in datos.examenes.keys():
                examen_seleccionado=f"{clase.sigles} - {clase.nom_cat}"
                if examen_seleccionado not in examenes_elegidos:
                    examenes_elegidos.update({examen_seleccionado: datos.examenes[asignatura]})
                    select_exam.addItem(examen_seleccionado)
    except:
        return
    
def create_ics():
    cal = Calendar()
    cal.add("prodid", "-//Horario//visorhoraris.upc.edu//")
    cal.add("version", "2.0")
    datos=[]
    datos_examenes = []
    tz = pytz.timezone("Europe/Madrid")
    semester_start = datetime(year=sem_start.date().year(), month=sem_start.date().month(), day=sem_start.date().day(), tzinfo=pytz.timezone("Europe/Madrid"))
    semester_end = datetime(year=sem_end.date().year(), month=sem_end.date().month(), day=sem_end.date().day(), tzinfo=pytz.timezone("Europe/Madrid"))
    for group, sesiones in horario_elegido.items():
        grupo_seleccionado = group.split(" - ")[2]
        asignatura_seleccionada = group.split(" - ")[1]
        sigles_asignatura = group.split(" - ")[0]
        for current in sesiones:
            uid = f"{sigles_asignatura}-{grupo_seleccionado}-{str(uuid.uuid4())}@zk.com"
            asignatura = f"{sigles_asignatura} - {asignatura_seleccionada}"
            grupo = grupo_seleccionado
            dia_semana = int(current["dia_setmana"]) - 1  # Convertir a 0=Monday ... 6=Sunday
            hora_inici = current["hora_inici"]
            hora_fi = datetime.strptime(current["hora_inici"], "%H:%M:%S") + timedelta(minutes=int(current["durada"]))
            hora_fi = hora_fi.strftime("%H:%M:%S")
            aula = current["sessions"][0]["recurs"]
            periodicitat = current["periodicitat"]
            tipus = current["tipus"]
            datos.append((uid,asignatura, grupo, dia_semana, hora_inici, hora_fi, aula, periodicitat,tipus))
    for clase, sesiones in examenes_elegidos.items():
        asignatura_seleccionada = clase.split(" - ")[1]
        sigles_asignatura = clase.split(" - ")[0]
        for current in sesiones:
            uid = f"{sigles_asignatura}-Exam-{str(uuid.uuid4())}@zk.com"
            asignatura = f"{sigles_asignatura} - {asignatura_seleccionada}"
            dia = current['dia']
            hora_inici = current['hora_inici']
            hora_fi = current['hora_fi']
            aules = current['aules']
            grupos = current['grups']
            tipo = current['tipus']
            datos_examenes.append((uid,asignatura,dia,hora_inici,hora_fi,aules,grupos,tipo))

        

    for iud,asignatura, grupo, weekday, start_str, end_str, location, periodicitat,tipus in datos:
        first_day = semester_start + timedelta(days=(weekday - semester_start.weekday()) % 7)
        start_hour, start_minute, _ = map(int, start_str.split(":"))
        end_hour, end_minute, _ = map(int, end_str.split(":"))

        event = Event()
        event.add("uid", iud)
        event.add("summary", f"{asignatura} ({grupo})")
        event.add("location", location)

        if periodicitat == "-" or tipus == "T":
          event.add("dtstart", datetime(first_day.year, first_day.month, first_day.day,
                                      start_hour, start_minute, tzinfo=semester_start.tzinfo))
          event.add("rrule", {"freq": "weekly","until": semester_end})
        event.add("dtend", datetime(first_day.year, first_day.month, first_day.day,
                                    end_hour, end_minute, tzinfo=semester_start.tzinfo))
        
        if periodicitat == "A":
            event.add("dtstart", datetime(first_day.year, first_day.month, first_day.day,
                                      start_hour, start_minute, tzinfo=semester_start.tzinfo))
            event.add("rrule", {"freq": "weekly", "interval":2 ,"until": semester_end})
        if periodicitat == "B":
            event.add("dtstart", datetime(first_day.year, first_day.month, first_day.day + 7,
                                      start_hour, start_minute, tzinfo=semester_start.tzinfo))
            event.add("rrule", {"freq": "weekly", "interval":2 ,"until": semester_end})
        
        cal.add_component(event)
    for iud,asignatura,dia,start_str,end_str,location,grupos,tipo in datos_examenes:
        first_day = fecha = datetime.strptime(dia, "%d/%m/%Y")
        start_hour, start_minute= map(int, start_str.split(":"))
        end_hour, end_minute= map(int, end_str.split(":"))

        event = Event()
        event.add("uid", iud)
        event.add("summary", f"{tipo} - {asignatura}")
        event.add("description", f"Grupos: {grupos}")
        event.add("location", location)

        event.add("dtstart", datetime(first_day.year, first_day.month, first_day.day,
                                      start_hour, start_minute, tzinfo=semester_start.tzinfo))
        event.add("dtend", datetime(first_day.year, first_day.month, first_day.day,
                                    end_hour, end_minute, tzinfo=semester_start.tzinfo))
        cal.add_component(event)
    path,_=QtWidgets.QFileDialog.getSaveFileName(filter="*.ics")


    #path=os.getcwd()
    #path=pathlib.Path(__file__).parent.resolve()
    if path != "": open(f"{path}.ics", "wb").write(cal.to_ical())


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = App.Ui_Form()
    ui.setupUi(Form)
    vincular_funciones(ui)
    Form.show()
    sys.exit(app.exec_())
                                    