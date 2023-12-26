from asyncio import start_server
import pickle
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import openpyxl
import re
from tkcalendar import Calendar
from datetime import datetime
import socket
import threading
import csv

archivo_csv = r'D:\GerenciaV2\Gerencia\Datos\turnos.csv'
host = '127.0.0.1'
port = 65432

def __init__(self, root):
        self.root = root
        self.root.title("Queue Management System - Client")

        self.frame = ttk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.tree = ttk.Treeview(self.frame, columns=("Nombre", "Apellidos", "Correo", "Número Estudiante", "Teléfono", "Referido", "Razón", "Fecha", "Hora"), show='headings')
        self.tree.pack(side="left", fill="both", expand=True)

        # Configurando las columnas
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)

        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Iniciar el proceso de actualización
        self.update_data()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))  # Asegúrate de que el puerto coincida con el del servidor

        # Iniciar hilo para escuchar mensajes del servidor
        threading.Thread(target=self.listen_for_updates, daemon=True).start()

# Función para cargar los turnos desde un archivo CSV
def cargar_turnos():
    try:
        with open(archivo_csv, newline='') as file:
            reader = csv.reader(archivo_csv)
            return [tuple(row) for row in reader]
    except FileNotFoundError:
        return []
    
# Función para guardar los turnos en un archivo CSV
def guardar_turnos(turnos):
    with open(archivo_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(turnos)    
    
    # Cargar turnos al inicio
turnos = cargar_turnos()

def listen_for_updates(self):
        while True:
            try:
                message = self.client_socket.recv(1024)
                if message:
                    self.update_data()  # Actualizar datos cuando se recibe un mensaje
            except:
                break

# Función para manejar al cliente
def client_handler(conn):
    global turnos
    while True:
        try:
            # Esperar a recibir una solicitud del cliente
            data = conn.recv(1024)
            if not data:
                break

            # Procesar la solicitud
            solicitud = pickle.loads(data)
            if solicitud['accion'] == 'obtener':
                conn.sendall(pickle.dumps(turnos))
        except ConnectionResetError:
            break
    conn.close()

print(f"Servidor escuchando en {host}:{port}")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen()

# Aceptar una conexión de cliente
conn, addr = server_socket.accept()
print(f"Conectado a {addr}")

# Iniciar un nuevo hilo para manejar al cliente
client_thread = threading.Thread(target=client_handler, args=(conn,))
client_thread.daemon = True
client_thread.start()

# GUI del servidor
#ventana = tk.Tk()
#ventana.title("Administración de Turnos")

# Function to validate user entries in the form
def validate_entries():
    # Get values from user input fields
    firstname = first_name_entry.get()
    lastname = last_name_entry.get()
    email = email_entry.get()
    student_num = student_num_entry.get()
    telephone_num = telephone_num_entry.get()

    # Get values from appointment-related input fields
    referall = referall_var.get()
    appointment_reason = appointment_reason_entry.get()
    appointment_date = appointment_date_entry.get()
    appointment_time_hour = appointment_time_hour_combobox.get()
    appointment_time_minute = appointment_minute_combobox.get()
    appointment_am_pm = appointment_am_pm_combobox.get()

    # Check if any field is empty
    if not all([firstname, lastname, email, student_num, telephone_num, referall, appointment_reason, appointment_date, appointment_time_hour, appointment_time_minute, appointment_am_pm]):
        return {"error": "Please fill in all fields."}

    # Check if email is valid
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return {"error": "Please enter a valid email address."}

    # Check if student number is valid (assuming it's a number)
    if not student_num.isdigit():
        return {"error": "Please enter a valid student number."}

    # Check if telephone number is valid (assuming it's a number)
    if not telephone_num.isdigit():
        return {"error": "Please enter a valid telephone number."}

    # If everything is valid, return success and user data
    return {"success": True,
            "data": {"firstname": firstname,
                     "lastname": lastname,
                     "email": email,
                     "student_num": student_num,
                     "telephone_num": telephone_num,
                     "referall": referall,
                     "appointment_reason": appointment_reason,
                     "appointment_date": appointment_date,
                     "appointment_time_hour": appointment_time_hour,
                     "appointment_time_minute": appointment_time_minute,
                     "appointment_am_pm": appointment_am_pm}}

# Function to submit validated data to an Excel file
def submit_data():
    # Validate entries and get the data
    validation_result = validate_entries()

    # If the data is valid, append it to the Excel document
    if "success" in validation_result:
        try:
        # Open the CSV file in append mode, create it if it doesn't exist
            with open("D:\\GerenciaV2\\Gerencia\\Datos\\turnos.csv", mode='a', newline='') as file:
                writer = csv.writer(file)

            # Write headers if the file is new/empty
                if file.tell() == 0:
                    headers = list(validation_result["data"].keys())
                    writer.writerow(headers)

            # Write data to the CSV file
                data_values = list(validation_result["data"].values())
            # Concatenate time components for the time column
                time_str = f"{data_values[-3]}:{data_values[-2]} {data_values[-1]}"
                data_values[-3] = time_str
                # Remove individual time components from the list
                data_values.pop(-2)
                data_values.pop(-1)
                writer.writerow(data_values)

        # Show a success message
            messagebox.showinfo("Submission Result", "Data submitted and saved to turnos.csv")
        except Exception as e:
        # Show an error message if there are issues with file handling
         messagebox.showerror("File Error", f"An error occurred: {e}")
        else:
            # Show an error message if the data is not valid
            messagebox.showerror("Validation Error", validation_result["error"])

# Function to update date entry field when a date is selected in the calendar
def on_date_select(date):
    selected_date_str = cal.get_date()
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

    formatted_date = selected_date.strftime('%Y-%m-%d')
    appointment_date_entry.delete(0, tk.END)
    appointment_date_entry.insert(0, formatted_date)
    appointment_time_hour_combobox.focus_set()

# Create the main window
window = tk.Tk()
window.title("Data Entry Form")

# Create a frame for organizing widgets
frame = tk.Frame(window)
frame.pack()

# Create a frame for user information
user_info_frame = tk.LabelFrame(frame, text="Información de Usuario")
user_info_frame.grid(row=0, column=0, padx=20, pady=10)

# Create labels and entry fields for personal information
first_name_label = tk.Label(user_info_frame, text="Nombre")
first_name_label.grid(row=0, column=0)
first_name_entry = tk.Entry(user_info_frame)
first_name_entry.grid(row=1, column=0)

last_name_label = tk.Label(user_info_frame, text="Apellidos")
last_name_label.grid(row=0, column=1)
last_name_entry = tk.Entry(user_info_frame)
last_name_entry.grid(row=1, column=1)

email_label = tk.Label(user_info_frame, text="Correo Electrónico")
email_label.grid(row=2, column=0)
email_entry = tk.Entry(user_info_frame)
email_entry.grid(row=3, column=0)

student_num_label = tk.Label(user_info_frame, text="Número de Estudiante")
student_num_label.grid(row=2, column=1)
student_num_entry = tk.Entry(user_info_frame)
student_num_entry.grid(row=3, column=1)

telephone_num_label = tk.Label(user_info_frame, text="Número de Teléfono")
telephone_num_label.grid(row=2, column=2)
telephone_num_entry = tk.Entry(user_info_frame)
telephone_num_entry.grid(row=3, column=2)

# Apply padding and alignment configurations for user information frame
for widget in user_info_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)

# Create a frame for appointment information
appointment_frame = tk.LabelFrame(frame, text="Información para Cita")
appointment_frame.grid(row=1, column=0, sticky="news", padx=20, pady=20)

# Create a checkbutton for referral information
referall_label = tk.Label(appointment_frame, text="Cita por Referido")
referall_var = tk.StringVar(value="Sin Referido")
referall_check = tk.Checkbutton(appointment_frame, text="Referido",
                                variable=referall_var, onvalue="Con Referido", offvalue="Sin Referido")
referall_label.grid(row=0, column=0)
referall_check.grid(row=1, column=0)

# Create labels and entry fields for appointment information
appointment_reason_label = tk.Label(appointment_frame, text="Razón de Cita")
appointment_reason_label.grid(row=0, column=1)
appointment_reason_entry = tk.Entry(appointment_frame)
appointment_reason_entry.grid(row=1, column=1)

appointment_date_label = tk.Label(appointment_frame, text="Fecha de Cita")
appointment_date_label.grid(row=2, column=0)

# Create a calendar widget for date selection
cal = Calendar(appointment_frame, selectmode='day', year=2023, month=11, day=19, date_pattern='yyyy-mm-dd',
               foreground='black', background='white', bordercolor='black', headersbackground='gray',
               normalbackground='white', normalforeground='black', weekendbackground='white',
               weekendforeground='black', selectbackground='#a6a6a6', selectforeground='black', showweeknumbers=False,
               locale='es_ES', disabledbackground='white', disabledforeground='gray')
cal.grid(row=4, column=0)

# Create an entry field for displaying selected date
appointment_date_entry = tk.Entry(appointment_frame)
appointment_date_entry.grid(row=3, column=0)

# Bind the on_date_select function to the calendar selection event
cal.bind("<<CalendarSelected>>", lambda e: on_date_select(cal.get_date()))

appointment_time_label = tk.Label(appointment_frame, text="Fecha y Hora de la Cita")
appointment_time_label.grid(row=2, column=1)

# Create ttk.Combobox widgets for time selection
time_hour_options = [f"{hour:02d}" for hour in range(1, 13)]
appointment_time_hour_var = tk.StringVar(value=time_hour_options[0])
appointment_time_hour_combobox = ttk.Combobox(appointment_frame, textvariable=appointment_time_hour_var, values=time_hour_options)
appointment_time_hour_combobox.grid(row=3, column=1)

minute_options = [f"{minute:02d}" for minute in range(0, 60, 5)]
appointment_minute_var = tk.StringVar(value=minute_options[0])
appointment_minute_combobox = ttk.Combobox(appointment_frame, textvariable=appointment_minute_var, values=minute_options)
appointment_minute_combobox.grid(row=3, column=2)

am_pm_options = ["AM", "PM"]
appointment_am_pm_var = tk.StringVar(value=am_pm_options[0])
appointment_am_pm_combobox = ttk.Combobox(appointment_frame, textvariable=appointment_am_pm_var, values=am_pm_options)
appointment_am_pm_combobox.grid(row=3, column=3)

# Create a button for submitting data
button = tk.Button(frame, text="Enter data", command=submit_data)
button.grid(row=3, column=0, sticky="news", padx=30, pady=20)

# Apply padding and alignment configurations for appointment frame
for widget in appointment_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)

# Start the main event loop
window.mainloop()

# Al final del script del servidor
if __name__ == "__main__":
    start_server()

