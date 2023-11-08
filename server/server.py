import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

# Voy a configurar el servidor
HOST = 'localhost'
PORT = 59420

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = None
        # Aquí voy a ir agregando los usuarios del chat
        self.clients = {}  
        
        # Configuración de la ventana del servidor
        self.window = tk.Tk()
        self.window.title("Servidor Sala de chat")

        self.chat_log = scrolledtext.ScrolledText(self.window)
        self.chat_log.pack(padx=20, pady=5)
        self.chat_log.config(state='disabled')
    

    def accept_incoming_connections(self):
        # Aquí se van a ir manejando o aceptando los nuevos integrantes
        while True:
            client, client_address = self.server.accept()
            self.update_chat_log(f"{client_address} se ha conectado.")

            # Inicio de un nuevo hilo para manejar la conexión con el cliente
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        
        # Se gestiona la conexión con un único cliente
        try:
            # El primer mensaje del cliente será su nombre de usuario
            username = client.recv(1024).decode('utf-8')
            self.clients[username] = client
            self.update_chat_log(f"Usuario {username} conectado.")

            while True:
                message = client.recv(1024).decode('utf-8')
                if message:
                    if message.lower() == "chao":
                        client.send("chao".encode('utf-8'))
                        client.close()
                        del self.clients[username]
                        self.broadcast(f"El usuario {username} abandonó.", username)
                        self.update_chat_log(f"El usuario {username} abandonó.")
                        break
                    else:
                        self.broadcast(f"{username}: {message}", username)
                        self.update_chat_log(f"{username}: {message}")
        except ConnectionResetError:
            client.close()
            del self.clients[username]
            self.broadcast(f"El usuario {username} se ha desconectado inesperadamente.", username)
            self.update_chat_log(f"El usuario {username} se ha desconectado inesperadamente.")
        except Exception as e:
            self.update_chat_log(f"Un error ocurrió con el usuario {username}: {e}")

    

    def broadcast(self, message, sender_username):
        
        # Aquí ajusto para que los mensajes se envíen a todos los clientes menos al que los emite
        for username, client_socket in self.clients.items():
            if username != sender_username:
                try:
                    client_socket.send(message.encode('utf-8'))
                except Exception as e:                    
                    print(f"Error al enviar el mensaje: {e}")

    def update_chat_log(self, message):
        # Aquí se actualiza el chat
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, message + '\n')
        self.chat_log.yview(tk.END)
        self.chat_log.config(state='disabled')

    def stop_server(self):
        # Se detiene el servidor
        for client in self.clients.values():
            client.close()
        self.server.close()
        self.window.quit()

    def run_server(self):
        # Arranca el servidor
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.update_chat_log(f"El servidor está escuchando en {self.host}:{self.port}")
        
        # Iniciar hilo para aceptar conexiones
        accept_thread = threading.Thread(target=self.accept_incoming_connections)
        accept_thread.start()
        
        # Iniciar GUI
        self.window.mainloop()
        
        # Esperar a que el hilo de aceptación de conexiones termine antes de cerrar la aplicación
        accept_thread.join()

# Iniciar el servidor con GUI
if __name__ == "__main__":
    server = Server(HOST, PORT)
    server.run_server()
