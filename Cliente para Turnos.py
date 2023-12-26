import csv
import socket
import pickle
import tkinter as tk
from tkinter import ttk
import threading
import os
import time

# Function to check for the existence of the CSV file and wait until it's created
def wait_for_csv_file(filepath):
    while not os.path.exists(filepath):
        time.sleep(1)  # Wait for 1 second before checking again

# Function to read data from CSV file, skipping the header row
def read_csv_data(filepath):
    data = []
    with open(filepath, mode='r') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip the header row
        for row in reader:
            data.append(row)
    return data

# Function to update the table with CSV data
def update_table(table, data):
    for row in table.get_children():
        table.delete(row)
    for row_data in data:
        table.insert('', 'end', values=row_data)

# Function to refresh the data from CSV file
def refresh_data():
    csv_data = read_csv_data(csv_file_path)
    update_table(tabla_turnos_cliente, csv_data)
    ventana_cliente.after(5000, refresh_data)  # Refresh every 5 seconds

# Configuración del cliente
host = '127.0.0.1'
port = 65432

# Crear el socket del cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

# Crear la ventana de la GUI
ventana_cliente = tk.Tk()
ventana_cliente.title("Vista de Turnos")

# Tabla para mostrar los turnos
columnas = ('#1', '#2', '#3', '#4', '#5', '#6')
tabla_turnos_cliente = ttk.Treeview(ventana_cliente, columns=columnas, show='headings')
tabla_turnos_cliente.grid(row=0, column=0, sticky='nsew')

# Wait for the CSV file to be created and then load data
csv_file_path = "D:\\GerenciaV2\\Gerencia\\Datos\\turnos.csv"
wait_for_csv_file(csv_file_path)
csv_data = read_csv_data(csv_file_path)
update_table(tabla_turnos_cliente, csv_data)

# Definir los encabezados de la tabla
labels_texts = ["Número de Turno", "Nombre", "Correo electrónico", "Número de teléfono", "Día de turno", "Hora de turno", "Razón de turno"]
for i, col in enumerate(columnas, start=1):
    tabla_turnos_cliente.heading(f'#{i}', text=labels_texts[i-1])

# Configurar el redimensionamiento de la tabla
ventana_cliente.grid_columnconfigure(0, weight=1)
ventana_cliente.grid_rowconfigure(0, weight=1)

# Función para recibir datos del servidor y actualizar la GUI
def recibir_datos():
    while True:
        try:
            # Recibir datos del servidor
            data = client_socket.recv(4096)
            if not data:
                break
            turnos = pickle.loads(data)

            # Limpiar la tabla y mostrar los nuevos turnos
            tabla_turnos_cliente.delete(*tabla_turnos_cliente.get_children())
            for turno in turnos:
                tabla_turnos_cliente.insert("", "end", values=turno)
        except OSError:
            break

# Iniciar la recepción de datos en un hilo separado para no bloquear la GUI
def iniciar_cliente():
    threading.Thread(target=recibir_datos, daemon=True).start()

# Ejecutar la función iniciar_cliente cuando la GUI esté lista
ventana_cliente.after(100, iniciar_cliente)

# Start the recurring timer to refresh data from CSV
ventana_cliente.after(5000, refresh_data)  # Refresh every 5 seconds

ventana_cliente.mainloop()
