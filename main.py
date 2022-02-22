import os
import sqlite3
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

if len(key) < 10:
    key = Fernet.generate_key()
    with (".env", "w") as file:
        file.write(key)
        file.close()
else:
    key = os.getenv("KEY").encode()

fernet = Fernet(key)

# Crear Base de datos

connection = sqlite3.connect("passwords.db")

cursor = connection.cursor()

try:
    cursor.execute('''CREATE TABLE account
                (email, servicio, contraseña)''')

    connection.commit()
except sqlite3.OperationalError:
    pass


FONT = "Arial", 25

root = Tk()
root.title("Password Manager")
frm = ttk.Frame(root, padding=10)
frm.grid(column=0, row=0)
frm2 = ttk.Frame(root, padding=10)


def save_password():
    global root, frm
    # Limpiar y crear nuevo Frame
    frm.destroy()
    frm = ttk.Frame(root, padding=10)
    frm.grid(column=0, row=0)
    
    # Crear Layout para guardar contraseñas
    ttk.Label(frm, text="Email: ").pack(pady=10)
    email_entry = ttk.Entry(frm, width=40, justify="center")
    email_entry.pack()

    ttk.Label(frm, text="Servicio: ").pack(pady=10)
    servicio_entry = ttk.Entry(frm, width=40, justify="center")
    servicio_entry.pack()

    ttk.Label(frm, text="Contraseña: ").pack(pady=10)
    password_entry = ttk.Entry(frm, textvariable="password",show="*", width=40, justify="center")
    password_entry.pack()
    
    def save_data():
        email = email_entry.get()
        servicio = servicio_entry.get()
        password = fernet.encrypt(password_entry.get().encode())
        
        # Añadir datos a la base de datos
        cursor.execute("insert into account (email, servicio, contraseña) values (?, ?, ?)", 
                       (email, servicio, password))
        connection.commit()
        email_entry.delete(0, END)
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
    frm.grid(column=0, row=0)
    
    # Crear Layout para ver contraseñas
    ttk.Label(frm, text="Email: ").pack(pady=10)
    email_entry = ttk.Entry(frm, width=40, justify="center")
    email_entry.pack()
        
    
    def get_data():
        """ Extrae la informacion de la base de datos"""
        global root, frm
        
        # Crear otro frame para controlarlo facilmente
        frm2 = ttk.Frame(frm, padding=10)
        frm2.pack()
        
        email = email_entry.get()
        cursor.execute(f"SELECT * FROM account WHERE email=?", (email,))
        rows = cursor.fetchall()
        
        
        def check_button(button_n):
            """Checkea que boton se esta pulsando y llama a la funcion copy"""
            button_password = passwords_list[button_n]
            copy(button_password)
        
        
        def copy(password):
            """Copia la contraseña"""
            pyperclip.copy(password)
            pyperclip.paste()
        
        
        if len(rows) != 0:
            passwords_list = []
            for n in range(0, len(rows)):
                if rows[n][0] == email:
                    servicio = rows[n][1]
                    password = fernet.decrypt(rows[n][2]).decode()
                    ttk.Label(frm2, text=f"Servicio: {servicio}\nPassword: {password}").pack(pady=10, fill=X)
                    button = ttk.Button(frm2, text="Copiar", command=partial(check_button, n))
                    button.pack()
                    passwords_list.append(password)
                    
        else:
            ttk.Label(frm2, text=f"No se ha encontrado el Email en la base de datos.").pack(pady=10)
                
        
        def clear():
            """Limpia el Frame"""
            frm2.destroy()
            email_entry.delete(0, END)
            
            
        clear_button = ttk.Button(frm2, text="Limpiar", command=clear)
        clear_button.pack(pady=10)
        
    ver_button = ttk.Button(frm, text="Ver contraseñas", command=get_data)
    ver_button.pack(pady=10)
    
    guardar_button = ttk.Button(frm, text="Guardar nueva contraseña", command=save_password)
    guardar_button.pack(pady=10)

    

# Crear pantalla principal

ttk.Label(frm, text="Password Manager", font=FONT).grid(column=1, row=0, pady=30, columnspan=2)

get_passwords_button = ttk.Button(frm, text="Ver Contraseñas", command=get_passwords)
get_passwords_button.grid(column=1, row=1, pady=5)

save_password_button = ttk.Button(frm, text="Guardar Contraseña", command=save_password)
save_password_button.grid(column=2, row=1, pady=5)


root.mainloop()
connection.close()
