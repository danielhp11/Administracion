###########################################
    #Aplicacion de escritorio y movil para gestionar las deudas
    #16-Agosto-2021
    #Funciones: puede agregar y eliminar compras, 
                #muestra en una tabla (vista Compra) las compras con nombre,fecha,meses a pagar y el total
                #muestra en una tabla (vista historial) el historial de las compras 
                        # con nombre, cantidad de abonos,total abonado, lo que se debe aun,total de compra
###########################################
from kivy.uix.layout import Layout
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.metrics import dp
import sqlite3
from kivymd.uix import datatables
from kivy.uix.screenmanager import Screen
from kivymd.uix.datatables import MDDataTable
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout

class Historial(Screen):
    layout = None
    btn = None
    def __init__(self, **kwargs):#metodo sobre escrito de la clase padre
        super(Historial,self).__init__(**kwargs)#agrega una cadena de caracteres a la aplicacion para su manipulacion 
        self.tablaHistory()

    def tablaHistory(self):
        from kivy.uix.button import Button
        self.btn = Button(text="Agregar abono",size_hint=[.3,.1])
        layoutB = BoxLayout(orientation="horizontal")
        self.btn.on_press = self.insertAbono
        layoutB.add_widget(self.btn)
        self.layout = AnchorLayout()
        self.layout.anchor_x = "center"
        self.layout.anchor_y = "center"
        con = sqlite3.connect('Deuda.sqlite')
        cur = con.cursor()
        cur.execute('SELECT compra.Nombre,count(abono.id_compra),sum(abono.abono), round( (compra.total-sum(abono.abono)),2 ) as "Debe",compra.total, round( (total/meses)+1, 2 )  FROM abono INNER JOIN compra ON compra.id_compra = abono.id_compra GROUP BY compra.id_compra')
        compra = cur.fetchall()
        data_tables = MDDataTable(#se asigana la tabla a la variable
            size_hint=(0.9, 0.75),#tamañp de la tabla
            use_pagination=True,#la paginacion esta activada
            column_data=[#columnas de titulos
                ("Nombre", dp(25)),
                ("Cantidad \n abonos", dp(20)),
                ("Total \n abonado", dp(25)),
                ("Se \n debe", dp(30)),
                ("Total \n compra", dp(25)),
                ("Abono \n mensual", dp(20))],
            row_data=[ #contenido de la tabla por fila
                (compras) for compras in  compra
            ],
        )
        con.close()
        data_tables.bind(on_row_press=self.on_row_press)
        self.layout.add_widget(data_tables)
        self.layout.add_widget(layoutB)
        self.add_widget(self.layout)

    def tableAbono(self,text):#Crea la tabla para ver el historial de abonos
        from kivy.uix.button import Button
        self.btn = Button(text="Regresar",size_hint=[.3,.1])
        layoutB = BoxLayout(orientation="horizontal")
        self.btn.on_release=self.returnBtn
        layoutB.add_widget(self.btn)
        self.layout = AnchorLayout()
        self.layout.anchor_x = "center"
        self.layout.anchor_y = "center"
        con = sqlite3.connect('Deuda.sqlite')
        cur = con.cursor()
        cur.execute("SELECT compra.Nombre, abono.fecha, abono.abono FROM abono INNER JOIN compra ON compra.id_compra = abono.id_compra WHERE compra.Nombre = '"+text+"'")
        abono = cur.fetchall()
        data_tables = MDDataTable(#se asigana la tabla a la variable
            size_hint=(0.5, 0.75),#tamañp de la tabla
            use_pagination=True,#la paginacion esta activada
            column_data=[#columnas de titulos
                ("Nombre", dp(30)),
                ("Fecha", dp(25)),
                ("Abonado", dp(20))],
            row_data=[ #contenido de la tabla por fila
                (compras) for compras in  abono
            ],
        )
        con.close()
        self.layout.add_widget(data_tables)
        self.layout.add_widget(layoutB)
        self.add_widget(self.layout)
    
    def on_row_press(self, instance_table, instance_row):
        con = sqlite3.connect('Deuda.sqlite')
        cur = con.cursor()
        cur.execute("SELECT compra.Nombre, abono.fecha, abono.abono FROM abono INNER JOIN compra ON compra.id_compra = abono.id_compra WHERE compra.Nombre = '"+instance_row.text+"'")
        abonos = cur.fetchall()
        #print(abonos)
        if(len(abonos)>0):
            #Cuando persionas la fila
            #Se limpia la tabla y el boton de layout
            self.cleanLayout()
            #Se agrega la nueva tabla con los abonos y el boton regresar
            self.tableAbono(instance_row.text)
        else:
            from kivymd.toast import toast
            toast("Selecciona la casilla del nombre")
        
    def cleanLayout(self):
            self.remove_widget(self.layout)
            self.btn = None
            self.layout = None
    
    def returnBtn(self):
        self.cleanLayout()
        self.tablaHistory()
    
    def insertAbono(self):
        from datetime import date
        con = sqlite3.connect('Deuda.sqlite')
        cur = con.cursor()
        cur.execute("SELECT   (total/meses)+1  FROM compra")
        abonos = cur.fetchall()
        cur.execute("SELECT id_compra FROM compra")
        idCompra = cur.fetchall()
        query ="INSERT INTO abono(id_compra,fecha,abono) VALUES"
        today = str(date.today())
        print("Abonos: "+str(abonos)+"\n"+"Id compras: "+str(idCompra))
        for i in range(0,len(abonos)) and range(0,len(idCompra)):
            query += "("+str(idCompra[i][0])+",'"+today+"',"+str(abonos[i][0])+"),"
        query = query.rstrip(query[-1])
        query+=";" 
        cur.execute(query)
        con.commit()
        con.close()
        self.cleanLayout()
        self.tablaHistory()


class Compra(Screen):
    dialog = None #variable para abrir y cerrar dialogos
    layout = None
    def __init__(self, **kwargs):#metodo sobre escrito de la clase padre
        super(Compra,self).__init__(**kwargs)#agrega una cadena de caracteres a la aplicacion para su manipulacion        
        self.table()                       
        self.add_widget(self.layout)

    def table(self):
        self.layout = AnchorLayout()
        self.layout.anchor_x = "center"
        self.layout.anchor_y = "center"
        con = sqlite3.connect('Deuda.sqlite')
        cur = con.cursor()
        cur.execute('SELECT Nombre,fecha,meses,total as Abono FROM compra')
        compra = cur.fetchall()
        data_tables = MDDataTable(#se asigana la tabla a la variable
            size_hint=(0.7, 0.75),#tamañp de la tabla
            check=True,#casilla para check
            use_pagination=True,#la paginacion esta activada
            column_data=[#columnas de titulos
                ("Nombre", dp(40)),
                ("Fecha compra", dp(30)),
                ("Meses", dp(15)),
                ("Total", dp(20)),             ],
            row_data=[ #contenido de la tabla por fila
                (compras) for compras in  compra
            ],
        )
        con.close()
        data_tables.bind(on_row_press=self.on_row_press)
        self.layout.add_widget(data_tables) 

    def show_confirmation_dialog(self):#metodo que abre el dialogo de nueva compra
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.dialog import MDDialog
        btnCancel = MDFlatButton(text='CANCELAR',on_release=self.closeDialog )
        btnAdd = MDFlatButton(text='Aceptar',on_release=self.addCompra )
        self.dialog = MDDialog(
            title="Nueva compra:",
            type="custom",
            auto_dismiss= False,
            content_cls=ContentNP(),
            buttons=[btnCancel, btnAdd],
        )
        self.dialog.open()
    
    def closeDialog(self,obj):#metodo que cierra el dialogo nueva compra
        self.dialog.dismiss()

    nameDelete=[]
    def on_row_press(self, instance_table, instance_row):
        #funcion para cuando marque check
        if len(self.nameDelete) == 0:
            #la lista esta vacia
            self.nameDelete.append(instance_row.text)#Se cagrega el nombre a la lista
        else:
            #la lista esta llena
            #Como la lista esta llena se busca si el texto del check selecionado esta en la lista
            if(self.nameDelete.count(instance_row.text) == 0 ):#se cuanta las veces que esta el texto en la lista si es mayor a 0 se ecuentra en la lista el texto
                #El texto no se encontro
                self.nameDelete.append(instance_row.text)
            else:
                #El texto se encontro
                self.nameDelete.remove(instance_row.text)
               
    def deleteCompra(self):
        con = sqlite3.connect('Deuda.sqlite')
        cur = con.cursor()
        for row in self.nameDelete:
            cur.execute("DELETE FROM compra WHERE Nombre='"+row+"'")
            con.commit()
        con.close()
        from kivymd.toast import toast
        toast("Se elimino con exito")
        self.remove_widget(self.layout)#se elimna en anchourlayout con la table
        self.table()#se carga la neuva tabla
        self.add_widget(self.layout)#se agrega el layout a l vista
        

    def addCompra(self,obj):#metodo que inserta a la base de datos la neuva compra
        from kivymd.toast import toast
        if(self.dialog.content_cls.ids.Nombre.text == "" or self.dialog.content_cls.ids.Mes.text == "" or self.dialog.content_cls.ids.Total.text == ""):
            #Sentencia para que ningun campo este vacio a la hora de insertar
            toast("Algun campo está vácio")
        else:
            #ningun campo esta vacio y se puede insertar
            from datetime import date
            today = str(date.today())
            query = "INSERT INTO compra(Nombre,Fecha,Meses,Total) VALUES('"+self.dialog.content_cls.ids.Nombre.text+"','"+today+"',"+self.dialog.content_cls.ids.Mes.text+","+self.dialog.content_cls.ids.Total.text+")"
            self.dialog.content_cls.ids.Nombre.text =""
            self.dialog.content_cls.ids.Mes.text =""
            self.dialog.content_cls.ids.Total.text =""
            self.dialog.dismiss()
            con = sqlite3.connect('Deuda.sqlite')
            cur = con.cursor()
            cur.execute(query)
            con.commit()
            toast("Se agrego con exito")
            self.remove_widget(self.layout)#se elimna en anchourlayout con la table
            self.table()#se carga la neuva tabla
            self.add_widget(self.layout)#se agrega el layout a l vista
        

class ContentNP(BoxLayout):#clase de los contenedores de la nueva compra
    pass

class Deuda(MDApp):#Clase principal

    def __init__(self, **kwargs):#metodo sobre escrito de la clase padre
        super(Deuda,self).__init__(**kwargs)#agrega una cadena de caracteres a la aplicacion para su manipulacion        

    def pagos_mes(self):
        con = sqlite3.connect('Deuda.sqlite')
        cur = con.cursor()
        cur.execute('SELECT sum(  round( total/meses+1 ) )  as Abono FROM compra')
        return cur.fetchall().pop()

    def build(self): # metodo principal
        
        return Builder.load_file('kivy/Deuda.kv')#retorna el archivo kvlang llamado Deuda.kv

    
window = Deuda()
window.run()