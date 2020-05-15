#Código principal del proyecto
from flask import Flask, render_template, request, make_response, session,escape,redirect,url_for,flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  Table, Column, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text
from sqlalchemy.dialects import mysql
from flask_marshmallow import Marshmallow
from flask import json
import json

import sqlite3
import os
from datetime import date
#----- Base de datos (Conectar) -----
dbdir = "sqlite:///" + os.path.abspath(os.getcwd()) + "/database.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
#------------------------------------

global condicion
condicion = ""

#----- Base de datos (Tablas) -------
class Paciente(db.Model):
    __tablename__ = 'paciente'
    cedula = db.Column(db.String(11), primary_key = True)
    nombre = db.Column(db.String(50),nullable =True)
    contraseña = db.Column(db.String(80),nullable =False)
    telefono = db.Column(mysql.BIGINT,nullable = True)
    correo = db.Column(db.String(80),nullable =True)
    direccion = db.Column(db.String(50),nullable =True)
    edad = db.Column(mysql.BIGINT,nullable=True)


    citas_agendadas = db.relationship("AgendarCita",back_populates="paciente")
    citas_agendadas_psicologia = db.relationship("AgendarCita_Psicologo",back_populates="paciente")


class Secretaria(db.Model):
    __tablename__ = 'Secretaria'
    cedula = db.Column(db.String(11), primary_key = True)
    nombre = db.Column(db.String(50),nullable =True)
    contraseña = db.Column(db.String(80),nullable =True)
    telefono = db.Column(mysql.BIGINT,nullable = True)
    correo = db.Column(db.String(80),nullable =True)


class Medico(db.Model):
    __tablename__ = 'medico'
    cedula = db.Column(db.String(11), primary_key = True)
    nombre = db.Column(db.String(50),nullable =True)
    contraseña = db.Column(db.String(80),nullable =True)
    correo = db.Column(db.String(80),nullable =True)

    horario = db.relationship("HorarioMedico", back_populates="medico")
    citas_agendadas = db.relationship("AgendarCita",back_populates="medico")


class Psicologo(db.Model):
    __tablename__ = 'psicologo'
    cedula = db.Column(db.String(11), primary_key = True)
    nombre = db.Column(db.String(50),nullable =True)
    contraseña = db.Column(db.String(80),nullable =True)
    correo = db.Column(db.String(80),nullable =True)

    horarioPsicologo = db.relationship("HorarioPsicologo", back_populates="psicologo")
    citas_agendadas = db.relationship("AgendarCita_Psicologo",back_populates="psicologo")


class AgendarCita(db.Model):
    __tablename__ = "agendarCita"
    codigo = db.Column(db.Integer, primary_key =True)
    diaCalendar = Column(db.Date, index=True)
    diaWeek = db.Column(db.String(15),nullable =False)
    hora = db.Column(db.String(15),nullable =False)
    medico_id = db.Column(db.Integer, ForeignKey('medico.cedula'))
    paciente_id = db.Column(db.Integer, ForeignKey('paciente.cedula'))
    secretaria_id = db.Column(db.String(9), nullable = True)

    medico = db.relationship("Medico",back_populates="citas_agendadas")
    paciente = db.relationship("Paciente",back_populates="citas_agendadas")


class AgendarCita_Psicologo(db.Model):
    __tablename__ = "AgendarCita_Psicologo"
    codigo = db.Column(db.Integer, primary_key =True)
    diaCalendar = Column(db.Date, index=True)
    diaWeek = db.Column(db.String(15),nullable =False)
    hora = db.Column(db.String(15),nullable =False)
    paciente_id = db.Column(db.Integer, ForeignKey('paciente.cedula'))
    psicologo_id = db.Column(db.Integer, ForeignKey('psicologo.cedula'))

    psicologo = db.relationship("Psicologo",back_populates="citas_agendadas")
    paciente = db.relationship("Paciente",back_populates="citas_agendadas_psicologia")


class HorarioMedico(db.Model):
    __tablename__ = "HorarioMedico"
    codigo = db.Column(db.Integer, primary_key = True)
    dias = db.Column(db.String(100),nullable =True)
    horas = db.Column(db.String(100),nullable =True)
    medico_id = db.Column(db.Integer, ForeignKey('medico.cedula'))

    medico = db.relationship("Medico",back_populates="horario")


class HorarioPsicologo(db.Model):
    __tablename__ = "HorarioPsicologo"
    codigo = db.Column(db.Integer, primary_key = True)
    dias = db.Column(db.String(100),nullable =True)
    horas = db.Column(db.String(100),nullable =True)
    psicologo_id = db.Column(db.Integer, ForeignKey('psicologo.cedula'))

    psicologo = db.relationship("Psicologo",back_populates="horarioPsicologo")

#------------------------------------





#--------- Todas la rutas -----------
@app.route("/",methods=['GET','POST'])
def incio():

    paciente = Paciente.query.all()
    medico = Medico.query.all()
    secretaria = Secretaria.query.all()

    for i in session:
        for k in paciente:
            if session[i] == k.cedula:
                print("paciente")
                h = Paciente.query.filter_by(cedula = session["cedula_paciente"]).first()
                citas_agendadas_paciente = AgendarCita.query.filter_by(paciente_id = session["cedula_paciente"]).all()
                return render_template("perfil_paciente.html", paciente = h, citas = citas_agendadas_paciente)
        
    for i in session:
        for k in secretaria:
            if session[i] == k.cedula:
                print("secretaria")
                h = Secretaria.query.filter_by(cedula = session["cedula_secretaria"]).first()
                return render_template("perfil_secretaria.html")

    for i in session:
        for k in medico:
            if session[i] == k.cedula:
                print("medico")
                h = Medico.query.filter_by(cedula = session["cedula_medico"]).first()
                return 'Perfil médico'

    return 'Inicio de la página'

@app.route("/logout",methods=['GET','POST'])
def logout():
    if request.method == 'POST':
        session.pop("cedula_paciente",None)
        session.pop("cedula_secretaria",None)
        session.pop("cedula_medico",None)
        print("Cerrar")
        return redirect("/")

@app.route("/login",methods=['GET','POST'])
def login():

    if request.method == "POST":
        paciente = Paciente.query.filter_by(cedula=request.form["cedula"]).first()
        secretaria = Secretaria.query.filter_by(cedula=request.form["cedula"]).first()
        medico = Medico.query.filter_by(cedula=request.form["cedula"]).first()

        if paciente and paciente.contraseña == request.form["password"]:
            print("Entró un paciente")
            session["cedula_paciente"] = paciente.cedula


        elif secretaria and secretaria.contraseña == request.form["password"]:
            print("Entró un secretaria")
            session["cedula_secretaria"] = secretaria.cedula

        elif medico and medico.contraseña == request.form["password"]:
            print("Entró un médico")
            session["cedula_medico"] = medico.cedula
        
        return redirect("/")    

    return render_template("loguearse.html")

@app.route("/registroPaciente",methods=['GET','POST'])
def registroPaciente():
    if request.method == 'POST':
        new_paciente = Paciente(nombre = request.form["nombre"], 
                                cedula = request.form["cedula"], 
                                contraseña = request.form["password"], 
                                telefono = request.form["telefono"], 
                                correo = request.form["correo"], 
                                direccion = request.form["direccion"], 
                                edad = request.form["edad"])
        db.session.add(new_paciente)
        db.session.commit()
        
        return '200'

    return render_template("registrar_paciente.html")

@app.route("/registroSecretaria",methods=['GET','POST'])
def registroSecretaria():
    if request.method == 'POST':
        new_secretaria = Secretaria(nombre = request.form["nombre"],
                                    cedula = request.form["cedula"],
                                    contraseña = request.form["password"],
                                    correo = request.form["correo"],
                                    telefono = request.form["telefono"])

        db.session.add(new_secretaria)
        db.session.commit()

        return '200'

    return render_template("registrar_secretaria.html")

@app.route("/registroMedico",methods=['GET','POST'])
def registroMedico():
    if request.method == 'POST':

        new_medico = Medico(nombre = request.form["nombre"],
                        cedula = request.form["cedula"],
                        contraseña = request.form["contraseña"],
                        correo = request.form["correo"])
        db.session.add(new_medico)
        db.session.commit()

        dias = request.form["dias"]
        horas = request.form["horas"]

        new_horario_medico = HorarioMedico(dias = dias,
                                            horas = horas,
                                            medico = new_medico)
        db.session.add(new_horario_medico)
        db.session.commit()

        return '200'

    return render_template("registro_medico.html")

@app.route("/registroPsicologo",methods=['GET','POST'])
def registroPsicologo():
    if request.method == 'POST':
        
        new_psicologo = Psicologo(nombre = request.form["nombre"],
                        cedula = request.form["cedula"],
                        contraseña = request.form["contraseña"],
                        correo = request.form["correo"])
        db.session.add(new_psicologo)
        db.session.commit()
        
        dias = request.form["dias"]
        horas = request.form["horas"]

        print(dias)
        print(horas)

        new_horario_psicologo = HorarioPsicologo(dias = dias,
                                            horas = horas,
                                            psicologo = new_psicologo)
        db.session.add(new_horario_psicologo)
        db.session.commit()

        return '200'

    return render_template("registro_psicologo.html")

@app.route("/agendarCita",methods=['GET','POST'])
def agendarCita():
    if request.method == 'POST':

        dia = request.form["dia"]
        hora = request.form["hora"]
        cedula_medico = request.form["cedula_medico"]

        print("Dia = ",dia)
        print("Hora = ",hora)

        u = dia.split(",")
        print(u[0],u[1],u[2],u[3])

        if u[2] == " Jan":
            u[2] = 1
        elif u[2] == " Feb":
            u[2] = 2
        elif u[2] == " Mar":
            u[2] = 3
        elif u[2] == " Apr":
            print(4)
            u[2] = 4
        elif u[2] == " May":
            u[2] = 5
        elif u[2] == " Jun":
            u[2] = 6
        elif u[2] == " Jul":
            u[2] = 7
        elif u[2] == " Aug":
            u[2] = 8
        elif u[2] == " Sep":
            u[2] = 9
        elif u[2] == " Oct":
            u[2] = 10
        elif u[2] == " Nov":
            u[2] = 11
        elif u[2] == " Dec":
            u[2] = 12

        o = date(int(u[3]),u[2],int(u[1]))
        medico = Medico.query.filter_by(cedula = cedula_medico).first()
        print(o)
        print(medico)

        if request.form["condicion"] == "secretaria":
            secretaria = Secretaria.query.filter_by(cedula = session["cedula_secretaria"]).first()
            paciente = Paciente.query.filter_by(cedula = request.form["cedula_paciente"]).first()
            new_cita = AgendarCita(paciente = paciente, 
                                medico = medico, 
                                diaCalendar = o,
                                diaWeek = u[0],
                                hora = hora,
                                secretaria_id = secretaria.cedula)
            db.session.add(new_cita)
            db.session.commit()
                
 
        elif request.form["condicion"] == "paciente":
            paciente = Paciente.query.filter_by(cedula = session["cedula_paciente"]).first()
            new_cita = AgendarCita(paciente = paciente, 
                                    medico = medico, 
                                    diaCalendar = o,
                                    diaWeek = u[0],
                                    hora = hora)
            db.session.add(new_cita)
            db.session.commit()

        return redirect("/")


    horarios_medicos = HorarioMedico.query.all()
    array_horarios_medicos = []
    for i in range(len(horarios_medicos)):
        array_horarios_medicos.append({"dias":horarios_medicos[i].dias,
                                        "horas":horarios_medicos[i].horas,
                                        "nombre_medico":horarios_medicos[i].medico.nombre,
                                        "cedula_medico":horarios_medicos[i].medico.cedula})

    
    citas_agendadas = AgendarCita.query.all()
    array_citas_agendadas = []
    for i in range(len(citas_agendadas)):
        array_citas_agendadas.append({"diaCalendar":citas_agendadas[i].diaCalendar,
                                        "diaWeek":citas_agendadas[i].diaWeek,
                                        "hora":citas_agendadas[i].hora,
                                        "nombre_medico":citas_agendadas[i].medico.nombre,
                                        "cedula_medico":citas_agendadas[i].medico.cedula,
                                        "paciente":citas_agendadas[i].paciente.nombre})

    
    paciente = Paciente.query.all()
    array_pacientes = []
    for i in range(len(paciente)):
        array_pacientes.append({"nombre_paciente":paciente[i].nombre,
                                "cedula_paciente":paciente[i].cedula
        })


    secretaria = Secretaria.query.all()
    for i in session:
        for k in paciente:
            if session[i] == k.cedula:
                print("paciente")
                condicion = "paciente"
        
    
    for i in session:
        for k in secretaria:
            if session[i] == k.cedula:
                print("secretaria")
                condicion = "secretaria"

    return render_template("agendar_cita.html",horarios_medicos = array_horarios_medicos,citas_agendadas = array_citas_agendadas, session = condicion, pacientes = array_pacientes)

@app.route("/COVID",methods=['GET','POST'])
def COVID():
    return render_template("covid.html")

@app.route("/agendarCitaPsicologo",methods=['GET','POST'])
def agendarCitaPsicologo():
    if request.method == 'POST':

        dia = request.form["dia"]
        hora = request.form["hora"]
        cedula_psicologo = request.form["cedula_psicologo"]

        u = dia.split(",")

        if u[2] == " Jan":
            u[2] = 1
        elif u[2] == " Feb":
            u[2] = 2
        elif u[2] == " Mar":
            u[2] = 3
        elif u[2] == " Apr":
            print(4)
            u[2] = 4
        elif u[2] == " May":
            u[2] = 5
        elif u[2] == " Jun":
            u[2] = 6
        elif u[2] == " Jul":
            u[2] = 7
        elif u[2] == " Aug":
            u[2] = 8
        elif u[2] == " Sep":
            u[2] = 9
        elif u[2] == " Oct":
            u[2] = 10
        elif u[2] == " Nov":
            u[2] = 11
        elif u[2] == " Dec":
            u[2] = 12

        o = date(int(u[3]),u[2],int(u[1]))
        psicologo = Psicologo.query.filter_by(cedula = cedula_psicologo).first()
        paciente = Paciente.query.filter_by(cedula = session["cedula_paciente"]).first()

        new_cita = AgendarCita_Psicologo(paciente = paciente, 
                                psicologo = psicologo, 
                                diaCalendar = o,
                                diaWeek = u[0],
                                hora = hora)
        db.session.add(new_cita)
        db.session.commit()

        return redirect("/")

    horarios_psicologos = HorarioPsicologo.query.all()
    array_horarios_psicologos = []
    for i in range(len(horarios_psicologos)):
        array_horarios_psicologos.append({"dias":horarios_psicologos[i].dias,
                                        "horas":horarios_psicologos[i].horas,
                                        "nombre_psicologo":horarios_psicologos[i].psicologo.nombre,
                                        "cedula_psicologo":horarios_psicologos[i].psicologo.cedula})

    
    citas_agendadas = AgendarCita_Psicologo.query.all()
    array_citas_agendadas = []
    for i in range(len(citas_agendadas)):
        array_citas_agendadas.append({"diaCalendar":citas_agendadas[i].diaCalendar,
                                        "diaWeek":citas_agendadas[i].diaWeek,
                                        "hora":citas_agendadas[i].hora,
                                        "nombre_psicologo":citas_agendadas[i].psicologo.nombre,
                                        "cedula_psicologo":citas_agendadas[i].psicologo.cedula,
                                        "paciente":citas_agendadas[i].paciente.nombre})


    paciente = Paciente.query.filter_by(cedula = session["cedula_paciente"]).first()
    paciente = {"nombre":paciente.nombre}

    return render_template("agendar_cita_psicologo.html",horarios_psicologos = array_horarios_psicologos,citas_agendadas = array_citas_agendadas, paciente = paciente)


















@app.route("/pruebas",methods=["GET","POST"])
def pruebas():  
    citas_agendadas = AgendarCita.query.filter_by(paciente_id = session["cedula_paciente"]).all()

    for i in range(len(citas_agendadas)):
        print(citas_agendadas[i].paciente_id)

    return '200'    

@app.route("/pruebasDos",methods=["GET","POST"])
def pruebasDos():  
    if request.method == 'POST':
        print("POST", request.form["saludo"])
        return render_template("perfil_secretaria.html")
    elif request.method == 'GET':
        print("GET")
        return render_template("perfil_secretaria.html")
#------------------------------------




#--------- Redirecciones -----------

@app.route("/irLogin",methods=["GET","POST"])
def irLogin():
    if request.method == "POST":
        return redirect("/login")

@app.route("/irInicio",methods=["GET","POST"])
def irInicio():
    if request.method == "POST":
        return redirect("/")

@app.route("/iragendarCita",methods=["GET","POST"])
def iragendarCita():
    if request.method == "POST":
        return redirect("/agendarCita")

@app.route("/iragendarCitaPsicologo",methods=["GET","POST"])
def iragendarCitaPsicologo():
    if request.method == "POST":
        return redirect("/agendarCitaPsicologo")

@app.route("/irCovid",methods=["GET","POST"])
def irCovid():
    if request.method == "POST":
        return redirect("/COVID")

#------------------------------------

























app.secret_key = "12345"

if __name__=="__main__":
    db.create_all()
    app.run(debug=True)