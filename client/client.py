import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import simpledialog

HOST = 'localhost'
PORT = 59420

class Client:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        # Solicita al usuario su nombre de usuario
        self.username = simpledialog.askstring("Usuario", "Ingresa tu nombre de usuario", parent=tk.Tk())
        self.sock.sendall(self.username.encode('utf-8'))

        self.root = tk.Tk()
        self.root.title(f"Chat - {self.username}")

        self.chat_area = scrolledtext.ScrolledText(self.root)
        self.chat_area.pack(padx=20, pady=5)
        self.chat_area.tag_config('green', foreground='green')
        self.chat_area.tag_config('red', foreground='red')
        self.chat_area.config(state='disabled')

        self.msg_entry = tk.Entry(self.root)
        self.msg_entry.pack(padx=20, pady=5)

        self.send_button = tk.Button(self.root, text="Enviar", command=self.write)
        self.send_button.pack(padx=20, pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.stop)

        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def write(self):
        message = self.msg_entry.get()
        self.sock.sendall(message.encode('utf-8'))
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"Tú: {message}\n", 'green')
        self.chat_area.config(state='disabled')
        self.msg_entry.delete(0, tk.END)

        if message.lower() == 'chao':
            self.stop()


    def receive(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == 'chao':
                    break
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, message + "\n", 'red')
                self.chat_area.config(state='disabled')
            except ConnectionResetError:
                break
            except OSError:
                break



    def stop(self):
        self.sock.sendall("chao".encode('utf-8'))
        self.sock.close()
        self.root.quit()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    client = Client(HOST, PORT)
    client.run()
