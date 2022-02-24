import os
from tokenize import String
from sqlalchemy import Column, Integer, create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from tkinter import *
from tkinter import ttk
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import pyperclip
from pprint import pprint
from functools import partial

# Crear key para encriptar

load_dotenv()

key = os.getenv("KEY").encode()

fernet = Fernet(key)

# Crear Base de datos
engine = create_engine("sqlite+pysqlite:///passwords.db", echo=True, future=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)
    accounts = relationship("Account", back_populates="user")
    

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    servicio = Column(String)
    password = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="accounts")
    

Base.metadata.create_all(engine)
user = None

FONT = "Arial", 25

root = Tk()
root.title("Password Manager")
frm = ttk.Frame(root, padding=10)
frm.grid(column=0, row=0)
frm2 = ttk.Frame(root, padding=10)


def signup():
    # Limpiar y crear nuevo Frame
    global root, frm
    frm.destroy()
    frm = ttk.Frame(root, padding=10)
    frm.grid(column=0, row=0)
    
    #Crear layout
    ttk.Label(frm, text=f"Email: ").pack(pady=10)
    email_entry = ttk.Entry(frm, width=40, justify="center")
    email_entry.pack()
    
    ttk.Label(frm, text="Contraseña: ").pack(pady=10)
    password_entry = ttk.Entry(frm, textvariable="password",show="*", width=40, justify="center")
    password_entry.pack()
    
    def guardar_datos():
        email = email_entry.get()
        password = fernet.encrypt(password_entry.get().encode())
        
        # Guardar en base de datos
        new_user = User(
            email=email,
            password=password
        )
        session.add(new_user)
        session.commit()
    
    guardar_button = ttk.Button(frm, text="Registrarse", command=guardar_datos)
    guardar_button.pack(pady=10)
    login_button = ttk.Button(frm, text="Iniciar Sesion", command=login)
    login_button.pack(pady=10)


def login():
    # Limpiar y crear nuevo Frame
    global root, frm, user
    frm.destroy()
    frm = ttk.Frame(root, padding=10)
    frm.grid(column=0, row=0)
    
    #Crear layout
    ttk.Label(frm, text="Email: ").pack(pady=10)
    email_entry = ttk.Entry(frm, width=40, justify="center")
    email_entry.pack()
    
    ttk.Label(frm, text="Contraseña: ").pack(pady=10)
    password_entry = ttk.Entry(frm, textvariable="password",show="*", width=40, justify="center")
    password_entry.pack()
    
    
    def iniciar_sesion():
        global user
        email = email_entry.get()
        password = password_entry.get()
        
        def check_user(user, password):
            print(user.password)
            decrypted = fernet.decrypt(user.password).decode()
            if password == decrypted:
                return True
            return False
            
        user = session.query(User).filter(User.email == email).first()
        if check_user(user, password):
            global root, frm
            frm.destroy()
            frm = ttk.Frame(root, padding=10)
            frm.grid(column=0, row=0)

            ttk.Label(frm, text="Password Manager", font=FONT).grid(column=1, row=0, pady=30, columnspan=2)
            ttk.Label(frm, text=f"Usuario actual: {user.email}", font=("Arial 10")).grid(column=1, row=1, pady=5, columnspan=2)


            get_passwords_button = ttk.Button(frm, text="Ver Contraseñas", command=get_passwords)
            get_passwords_button.grid(column=1, row=2, pady=5)

            save_password_button = ttk.Button(frm, text="Guardar Contraseña", command=save_password)
            save_password_button.grid(column=2, row=2, pady=5) 
    login_button = ttk.Button(frm, text="Iniciar Sesion", command=iniciar_sesion)
    login_button.pack(pady=5)

def save_password():
    # Limpiar y crear nuevo Frame
    global root, frm, user
    print(user)
    frm.destroy()
    frm = ttk.Frame(root, padding=10)
    frm.grid(column=0, row=0)

    ttk.Label(frm, text="Servicio: ").pack(pady=10)
    servicio_entry = ttk.Entry(frm, width=40, justify="center")
    servicio_entry.pack()

    ttk.Label(frm, text="Contraseña: ").pack(pady=10)
    password_entry = ttk.Entry(frm, textvariable="password",show="*", width=40, justify="center")
    password_entry.pack()
    
    def save_data():
        global user
        print(user)
        servicio = servicio_entry.get()
        password = fernet.encrypt(password_entry.get().encode())
        
        # Añadir datos a la base de datos
        new_account = Account(
            servicio=servicio,
            password=password,
            user=user
        ) 
        session.add(new_account)
        session.commit()
        servicio_entry.delete(0, END)
        password_entry.delete(0, END)

    guardar_button = ttk.Button(frm, text="Guardar", command=save_data)
    guardar_button.pack(pady=10)
    ver_button = ttk.Button(frm, text="Ver Contraseñas", command=get_passwords)
    ver_button.pack(pady=10)
    
    

def get_passwords():
    # Limpiar y crear nuevo Frame
    global root, frm
    frm.destroy()
    frm = ttk.Frame(root, padding=10)
    frm.pack()
    ttk.Label(frm, text=f"Usuario actual: {user.email}", font=("Arial 15")).pack()    
    n = 0
    def check_button(button_n):
        """Checkea que boton se esta pulsando y llama a la funcion copy"""
        button_password = passwords_list[button_n]
        copy(button_password)
    
    
    def copy(password):
        """Copia la contraseña"""
        pyperclip.copy(fernet.decrypt(password).decode())
        pyperclip.paste()
    
    
    if len(user.accounts) != 0:
        passwords_list = [account.password for account in user.accounts]
        
        for account in user.accounts:
            servicio = account.servicio
            password = fernet.decrypt(account.password).decode()
            ttk.Label(frm, text=f"Servicio: {servicio}\nPassword: {password}").pack(pady=10, fill=X)
            button = ttk.Button(frm, text="Copiar", command=partial(check_button, n))
            button.pack()
            n += 1
                
    else:
        ttk.Label(frm2, text=f"No se ha encontrado el Email en la base de datos.").pack(pady=10)
                
            
            
        clear_button = ttk.Button(frm2, text="Iniciar con otra cuenta", command=login)
        clear_button.pack(pady=10)
        
    
    guardar_button = ttk.Button(frm, text="Guardar nueva contraseña", command=save_password)
    guardar_button.pack(pady=10)

    

# Crear pantalla principal

ttk.Label(frm, text="Password Manager", font=FONT).grid(column=1, row=0, pady=30, columnspan=2)

login_button = ttk.Button(frm, text="Iniciar Sesion", command=login)
login_button.grid(column=1, row=1, pady=5)

register_button = ttk.Button(frm, text="Registrarse", command=signup)
register_button.grid(column=2, row=1, pady=5)

root.mainloop()
