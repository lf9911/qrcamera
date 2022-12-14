#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tkinter import *
import tkinter.scrolledtext as scrolledtext
from tkinter import messagebox, filedialog
from pyzbar.pyzbar import decode, ZBarSymbol
import webbrowser as wbr
from urllib.parse import urlparse
import webbrowser
import cv2
import pyautogui
import numpy as np
import threading
from PIL import Image, ImageTk, ImageDraw
import os
 
class App:
    def __init__(self,font_video=0):
        self.active_camera = False
        self.info = []
        self.codelist = []
        self.appName = 'QR Code Reader'
        self.ventana = Tk()
        self.ventana.title(self.appName)
        self.ventana['bg']='black'
        self.font_video=font_video
        self.label=Label(self.ventana,text=self.appName,font=15,bg='blue',
                         fg='white').pack(side=TOP,fill=BOTH)
        self.btnAcces = Button(self.ventana,text="ACCEDER A PAGINA",bg='light blue',height=1,width=90,state='disabled',command=self.connect)
        self.btnAcces.pack(side=BOTTOM)
        self.btnSave = Button(self.ventana,text="GUARDAR INFO",bg='light blue',height=1,width=90,command=self.guardar)
        self.btnSave.pack(side=BOTTOM)
 
        self.display=scrolledtext.ScrolledText(self.ventana,width=86,background='snow3'
                                        ,height=4,padx=10, pady=10,font=('Arial', 10))
        self.display.pack(side=BOTTOM)
 
        self.canvas=Canvas(self.ventana,bg='black',width=640,height=0)
        self.canvas.pack()
        self.btnLoad = Button(self.ventana,text="CARGAR ARCHIVO",width=29,bg='goldenrod2',
                    activebackground='red',command=self.abrir)
        self.btnLoad.pack(side=LEFT)
        self.btnCamera = Button(self.ventana,text="INICIAR LECTURA POR CAMARA",width=30,bg='goldenrod2',
                                activebackground='red',command=self.active_cam)
        self.btnCamera.pack(side=LEFT)
        self.btnScreen = Button(self.ventana,text="DETECTAR EN PANTALLA",width=29,bg='goldenrod2',
                                activebackground='red',command=self.screen_shot)
        self.btnScreen.pack(side=RIGHT)     
 
        self.ventana.mainloop()
 
    def guardar(self):
        if len(self.display.get('1.0',END))>1:
            documento = filedialog.asksaveasfilename(initialdir="/",
                        title="Guardar en",defaultextension='.txt')
            if documento != "":
                archivo_guardar = open(documento,"w",encoding="utf-8")
                linea=""
                for c in str(self.display.get('1.0',END)):
                    linea=linea+c
                archivo_guardar.write(linea)
                archivo_guardar.close()
                messagebox.showinfo("GUARDADO","INFORMACI??N GUARDADA EN \'{}\'".format(documento))
 
    def abrir(self):
        ruta = filedialog.askopenfilename(initialdir="/",title="SELECCIONAR ARCHIVO",
                    filetypes =(("png files","*.png") ,("jpg files","*.jpg")))
        if ruta != "":
            archivo = cv2.imread(ruta)
            self.info = decode(archivo)
            if self.info != []:
                self.display.delete('1.0',END)
                for i in self.info:
                    self.display.insert(END,(i[0].decode('utf-8'))+'\n')
                if i[0].decode('utf-8').startswith("https://"):##############################
                    try:
                        question = messagebox.askquestion("ACCEDER","Desea acceder a {}?".format(i[0].decode('utf-8')))
                        if question == "yes":
                            wbr.open(i[0].decode('utf-8'))
                    except:
                        messagebox.showwarning("ERROR","No se pudo acceder a {}.".format(i[0].decode('utf-8')))
                        pass
            else:
                messagebox.showwarning("ARCHIVO NO V??LIDO","NO SE DETECT?? C??DIGO QR.")
 
    def screen_shot(self):
        self.web_list = []
        pyautogui.screenshot("QRsearch_screenshoot.jpg")
        archivo = cv2.imread("QRsearch_screenshoot.jpg")
        self.info = decode(archivo)
        print("INFO: ",self.info)
        if self.info != []:
            self.display.delete('1.0',END)
            for i in self.info:
                cont = i[0].decode('utf-8')
                self.display.insert(END,cont+'\n')
                if "https:" in str(cont):
                    self.web_list.append(cont)
        else:
            messagebox.showwarning("QR NO ENCONTRADO","NO SE DETECT?? C??DIGO")
        os.remove("QRsearch_screenshoot.jpg")
 
    def visor(self):
        ret, frame=self.get_frame()
        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0,0,image=self.photo,anchor=NW)
            self.ventana.after(15,self.visor)
 
    def active_cam(self):
        if self.active_camera == False:
            self.active_camera = True
            self.VideoCaptura()
            self.visor()
        else:
            self.active_camera = False
            self.codelist = []
            self.btnCamera.configure(text="INICIAR LECTURA POR CAMARA")
            self.vid.release()
            self.canvas.delete('all')
            self.canvas.configure(height=0)

    def is_url(self,content):
        try:
            result = urlparse(content)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def connect(self):
        question = messagebox.askquestion("??CONECTAR?","??Desea conectarse con {}?".format(self.the_info))
        if question == "yes":
            webbrowser.open(self.the_info)
 
    def capta(self,frm):
        self.info = decode(frm)
        cv2.putText(frm, "Muestre el codigo delante de la camara para su lectura", (84, 37), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        if self.info != []:
            self.display.delete('1.0',END)
            for code in self.info:
                self.codelist.append(code)
                self.the_info = code[0].decode('utf-8')
                if self.is_url(self.the_info) == True:
                    self.btnAcces.configure(state="normal")
                self.display.insert(END,self.the_info+'\n')
                
            self.draw_rectangle(frm)
 
    def get_frame(self):
        if self.vid.isOpened():
            verif,frame=self.vid.read()
            if verif:
                self.btnCamera.configure(text="CERRAR CAMARA")
                self.capta(frame)
                return(verif,cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                messagebox.showwarning("CAMARA NO DISPONIBLE","""La c??mara est?? siendo utilizada por otra aplicaci??n.
                Cierrela e intentelo de nuevo.""")
                self.active_cam()
                return(verif,None)
        else:
            verif=False
            return(verif,None)
 
    def draw_rectangle(self,frm):
        codes = decode(frm)
        for code in codes:
            data = code.data.decode('ascii')
            x, y, w, h = code.rect.left, code.rect.top, \
                        code.rect.width, code.rect.height
            cv2.rectangle(frm, (x,y),(x+w, y+h),(255, 0, 0), 6)
            cv2.putText(frm, code.type, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 50, 255), 2)
 
    def VideoCaptura(self):
        self.vid = cv2.VideoCapture(self.font_video)
        if self.vid.isOpened():
            self.width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.canvas.configure(width=self.width,height=self.height)
        else:
            messagebox.showwarning("CAMARA NO DISPONIBLE","El dispositivo est?? desactivado o no disponible")
            self.display.delete('1.0',END)
            self.active_camera = False
 
    def __del__(self):
        if self.active_camera == True:
            self.vid.release()
 
if __name__=="__main__":
    App()
