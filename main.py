
import kivy
import os
import sqlite3
from kivy.config import Config
Config.set("graphics","width","350")
Config.set("graphics","height","660")
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen

def conect_to_database(path):
    try:
        con = sqlite3.connect(path)
        cursor = con.cursor()
        create_table_productos(cursor)
        con.commit()
        con.close()
    except Exception as e:
        print(e)
def create_table_productos(cursor):
    cursor.execute(
        """
        CREATE TABLE Productos(
        ID      INT PRIMARY KEY NOT NULL,
        Nombre  TEXT            NOT NULL,
        Color   TEXT            NOT NULL,
        Talla   TEXT            NOT NULL,
        Costo   INT            NOT NULL,
        Almacen INT             NOT NULL,
        Estado  TEXT            NOT NULL)
        """
    )
class MessagePopup(Popup):
    pass
class MainWid(ScreenManager):
    def __init__(self, **kwarg):
        super(MainWid, self).__init__()
        self.APP_PATH = os.getcwd()
        self.DB_PATH = self.APP_PATH+"/my_database.db"

        self.StartWid = StartWid(self)
        self.DataBaseWid = DataBaseWid(self)
        self.InsertDataWid = BoxLayout()
        self.UpdateDataWid = BoxLayout()
        self.Popup = MessagePopup()
        wid = Screen(name='start')
        wid.add_widget(self.StartWid)
        self.add_widget(wid)

        wid = Screen(name='database')
        wid.add_widget(self.DataBaseWid)
        self.add_widget(wid)

        wid = Screen(name='insertdata')
        wid.add_widget(self.InsertDataWid)
        self.add_widget(wid)

        wid = Screen(name='updatedata')
        wid.add_widget(self.UpdateDataWid)
        self.add_widget(wid)

        self.goto_start()

    def goto_start(self):
        self.current = 'start'

    def goto_database(self):
        self.DataBaseWid.check_memory()
        self.current = 'database'

    def goto_insertdata(self):
        self.InsertDataWid.clear_widgets()
        wid = InsertDataWid(self)
        self.InsertDataWid.add_widget(wid)
        self.current = 'insertdata'

    def goto_updatedata(self, data_id):
        self.UpdateDataWid.clear_widgets()
        wid = UpdateDataWid(self, data_id)
        self.UpdateDataWid.add_widget(wid)
        self.current = 'updatedata'

class StartWid(BoxLayout):
    def __init__(self,mainwid, **kwargs):
        super(StartWid, self).__init__()
        self.mainwid = mainwid

    def create_database(self):
        conect_to_database(self.mainwid.DB_PATH)
        self.mainwid.goto_database()
class DataBaseWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super(DataBaseWid, self).__init__()
        self.mainwid = mainwid

    def check_memory(self):
        self.ids.contenedor.clear_widgets()
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        cursor.execute('select ID, Nombre, Color, Talla, Costo, Estado from Productos')
        for i in cursor:
            wid = DataWid(self.mainwid)
            r1 = 'ID: ' +str(10000 + i[0])[1:5]+'\n'
            r2 = i[1]+ ',   '+i[2]+ ',  '+i[3]+'\n'
            r3 = 'Precio: Bs' +str(i[4])+ '  est: '+ i[5]+ '\n'
            wid.data_id =str(i[0])
            wid.data = r1 + r2 + r3
            self.ids.contenedor.add_widget(wid)
        wid = NewDataButton(self.mainwid)
        self.ids.contenedor.add_widget(wid)
        con.close()

class InsertDataWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super(InsertDataWid, self).__init__()
        self.mainwid = mainwid

    def insert_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        d1 = self.ids.ti_id.text
        d2 = self.ids.ti_nombre.text
        d3 = self.ids.ti_color.text
        d4 = self.ids.ti_talla.text
        d5 = self.ids.ti_costo.text
        d6 = self.ids.ti_almacen.text
        d7 = self.ids.ti_estado.text
        a1 = (d1, d2, d3, d4, d5, d6, d7)
        s1 = 'INSERT INTO Productos(ID, Nombre, Color, Talla, Costo, Almacen, Estado)'
        s2 = 'VALUES(%s,"%s","%s","%s","%s",%s,"%s")' % a1
        try:
            cursor.execute(s1+' '+s2)
            con.commit()
            con.close()
            self.mainwid.goto_database()
        except Exception as e:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Database error"
            if '' in a1:
                message.text = 'Uno o mas campos estan vacios'
            else:
                message.text = str(e)
            con.close()
    def back_to_dbw(self):
        self.mainwid.goto_database()

class UpdateDataWid(BoxLayout):
    def __init__(self, mainwid, data_id, **kwargs):
        super(UpdateDataWid, self).__init__()
        self.mainwid = mainwid
        self.data_id =data_id
        self.check_memory()
    def check_memory(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        s = 'select  Nombre, Color, Talla, Costo, Almacen, Estado from Productos where ID='
        cursor.execute(s+self.data_id)
        for i in cursor:
            self.ids.ti_nombre.text = i[0]
            self.ids.ti_color.text = i[1]
            self.ids.ti_talla.text = i[2]
            self.ids.ti_costo.text = str(i[3])
            self.ids.ti_almacen.text = str(i[4])
            self.ids.ti_estado.text = i[5]
        con.close()

    def update_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        d1 = self.ids.ti_nombre.text
        d2 = self.ids.ti_color.text
        d3 = self.ids.ti_talla.text
        d4 = self.ids.ti_costo.text
        d5 = self.ids.ti_almacen.text
        d6 = self.ids.ti_estado.text
        a1 = (d1, d2, d3, d4, d5, d6)
        s1 ='UPDATE Productos SET'
        s2 = 'Nombre="%s", Color="%s", Talla="%s", Costo=%s, Almacen=%s, Estado="%s"'% a1
        s3 = 'WHERE ID=%s' % self.data_id
        try:
            cursor.execute(s1 +' ' + s2+ ' '+ s3)
            con.commit()
            con.close()
            self.mainwid.goto_database()
        except Exception as e:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Database error"
            if '' in a1:
                message.text = 'Uno o mas campos estan vacios'
            else:
                message.text = str(e)
            con.close()
    def delete_data(sef):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        s = 'delete from Productos where ID='+self.data_id
        cursor.execute(s)
        con.commit()
        con.close()
        self.mainwid.goto_database()
    def back_to_dbw(self):
        self.mainwid.goto_database()
class DataWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super(DataWid, self).__init__()
        self.mainwid = mainwid
    def update_data(self, data_id):
        if __name__ == '__main__':
            self.mainwid.goto_updatedata(data_id)

class NewDataButton(Button):
    def __init__(self, mainwid, **kwargs):
        super(NewDataButton, self).__init__()
        self.mainwid = mainwid
    def create_new_product(self):
        self.mainwid.goto_insertdata()

class MainApp (App):
    title = 'Inventario Simple'
    def build(self):
        return MainWid()

if __name__ == '__main__':
    MainApp().run()
