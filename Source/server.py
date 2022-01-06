import socket
import threading
from apify_client import ApifyClient
import json
import datetime
import os
import pyodbc
import tkinter as tk
from unidecode import unidecode

SERVER_IP = "127.0.0.1"  # localhost, ip loopback: 127.0.0.1
SERVER_PORT = 65000
FORMAT = "utf-8"
N_CLIENT = 0
LOCK = threading.Lock()
USER_LOGGED = []


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("COVID-19 INFO")
        self.geometry("700x450")
        scrollbar = tk.Scrollbar(self, orient="vertical")
        self.list = tk.Listbox(self, width=300, height=400, font=("Times", 12), bg='lightblue', selectmode="extended", yscrollcommand=scrollbar.set)

        container = tk.Frame(self, bg="lightblue")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        background = tk.PhotoImage(file="background.png", width=150, height=115)
        label_background = tk.Label(container, image=background, border=0)
        label_background.image = background
        label_background.place(x=0, y=0)

        scrollbar.pack(side="right", fill="y")
        scrollbar.config(command=self.list.yview)
        self.list.pack(side="left", fill="both", expand=True)
        self.list.config(yscrollcommand=scrollbar.set)
        container.tkraise()

        self.establish_connection(container)

    def abbreviate(self, str: str):
        switcher = {
            'Bà Rịa – Vũng Tàu': 'BV',
            'Bình Thuận': 'BTh',
            'Đà Nẵng': 'ĐNa',
            'Đắc Nông': 'ĐNo',
            'Hà Nam': 'HNa',
            'Hậu Giang': 'HGi',
            'TP. Hồ Chí Minh': 'HCM',
            'Lào Cai': 'LCa',
            'Quảng Nam': 'QNa',
            'Quảng Ngãi': 'QNg',
            'Thái Nguyên': 'TNg'
        }
        return switcher.get(str, ''.join(word[0].upper() for word in str.split()))

    def update_info(self):
        # Initialize the ApifyClient with your API token
        client = ApifyClient("apify_api_aMxfD7gxZdCcQ8KgmULrhN9nmfNn9t2gMj29")
        # Prepare the actor input
        run_input = {}
        # Run the actor and wait for it to finish
        while(not self.stop.is_set()):
            run = client.actor("dtrungtin/covid-vi").call(run_input=run_input)

            # Fetch and write actor results from the run's dataset (if there are any) to file
            file_name = datetime.date.today().strftime("%Y-%m-%d") + '.json'
            os.makedirs('covidinfo', exist_ok=True)
            with open(os.path.join('covidinfo', file_name), 'w', encoding="utf8") as outfile:
                for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                    for location in item['locations']:
                        location['abbr'] = self.abbreviate(location['name'])
                    json.dump(item, outfile, indent=4, ensure_ascii=False)

            self.stop.wait(3600)

    def is_accessible(self, username: str):
        global USER_LOGGED
        for user in USER_LOGGED:
            if(user == username):
                return False
        return True

    def accept_login(self, connect: socket.socket, username: str, password: str):
        try:
            self.cursor.execute("select password from UserAccount where username = ?", username)
            export_password = self.cursor.fetchone()
            if (password == export_password[0]):
                if(self.is_accessible(username)):
                    connect.send("ok".encode(FORMAT))
                    return True
                else:
                    connect.send("User has already logged in".encode(FORMAT))
                    return False
            else:
                connect.send("Wrong password".encode(FORMAT))
                return False
        except:
            connect.send("Username not found".encode(FORMAT))
            return False

    def accept_signup(self, connect: socket.socket, username: str, password: str):
        try:
            self.cursor.execute("select username from UserAccount")
            export_username = self.cursor.fetchone()
            while(export_username != None):
                if(username == export_username[0]):
                    connect.send("Username already exists".encode(FORMAT))
                    return False
                export_username = self.cursor.fetchone()

            self.cursor.execute("insert UserAccount values (?, ?)", username, password)
            self.conx.commit()
            connect.send("Signed up successfully".encode(FORMAT))
            return True
        except:
            connect.send("Sign up failed".encode(FORMAT))
            return False

    def req_prov_info(self, connect: socket.socket, req: str):
        file_name = datetime.date.today().strftime("%Y-%m-%d") + '.json'
        data = json.load(open(os.path.join('covidinfo', file_name), encoding="utf8"))
        flag = "NotFound"
        for location in data['locations']:
            if (len(req) <= 3 and location['abbr'] == req):
                flag = "Found"
                connect.send(json.dumps(location).encode(FORMAT))
                connect.recv(1024).decode(FORMAT)
            elif (req.title() in location['name'] or req.title() in unidecode(location['name'])):
                flag = "Found"
                connect.send(json.dumps(location).encode(FORMAT))
                connect.recv(1024).decode(FORMAT)

        connect.send(flag.encode(FORMAT))

    def req_date_info(self, connect: socket.socket, date: str):
        file_name = date + '.json'
        try:
            data = json.load(open(os.path.join('covidinfo', file_name), encoding="utf8"))
            req = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m")
            for status in data['overview']:
                if status['date'] == req:
                    connect.send(json.dumps(status).encode(FORMAT))
                    return
            connect.send("NotFound".encode(FORMAT))
        except:
            connect.send("NotFound".encode(FORMAT))

    def Handle_client(self, connect: socket.socket, address):
        global N_CLIENT
        self.list.insert(tk.END, "New connection from {}".format(address))
        client_logged = False
        client_name = ""
        while not self.stop.is_set():
            try:
                connect_msg = connect.recv(1024).decode(FORMAT)
                if(connect_msg == "/quit"):
                    try:
                        USER_LOGGED.remove(client_name)
                    except:
                        pass
                    self.list.insert(tk.END, client_name + " " + str(address) + " has disconnected")
                    with LOCK:
                        N_CLIENT -= 1
                    connect.close()
                    return

                elif(not client_logged and connect_msg == "/login"):
                    username = connect.recv(1024).decode(FORMAT)
                    password = connect.recv(1024).decode(FORMAT)
                    client_logged = self.accept_login(connect, username, password)
                    if client_logged:
                        client_name = username
                        USER_LOGGED.append(username)
                        self.list.insert(tk.END, client_name + " " + str(address) + " has loged in")

                elif(not client_logged and connect_msg == "/signup"):
                    username = connect.recv(1024).decode(FORMAT)
                    password = connect.recv(1024).decode(FORMAT)
                    if(self.accept_signup(connect, username, password)):
                        self.list.insert(tk.END, str(address) + " has successfully signed up")

                elif(client_logged and connect_msg == "/logout"):
                    self.list.insert(tk.END, client_name + " " + str(address) + " has loged out")
                    if client_name != "":
                        client_logged = False
                        USER_LOGGED.remove(client_name)

                elif(client_logged and connect_msg == "/req"):
                    connect.send("Please input province you want to get info".encode(FORMAT))
                    req = connect.recv(1024).decode(FORMAT)
                    self.req_prov_info(connect, req)

                elif(client_logged and connect_msg == "/reqdate"):
                    connect.send("Please input date (format dd-mm-yyyy) you want to get info".encode(FORMAT))
                    date = connect.recv(1024).decode(FORMAT)
                    self.req_date_info(connect, date)

            except:
                try:
                    USER_LOGGED.remove(client_name)
                    self.list.insert(tk.END, client_name + " " + str(address) + " has disconnected")
                except:
                    if(client_name == ""):
                        self.list.insert(tk.END, client_name + " " + str(address) + " has disconnected")
                with LOCK:
                    N_CLIENT -= 1
                connect.close()
                return

    def execute(self, server: socket.socket):
        global N_CLIENT
        while N_CLIENT < 200:
            try:
                connect, address = server.accept()
                thread = threading.Thread(target=self.Handle_client, args=(connect, address))
                thread.start()
                N_CLIENT += 1
            except:
                break
        server.close()
        if(self.stop.is_set()):
            return
        else:
            self.stop.wait(60)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((SERVER_IP, SERVER_PORT))
        server.listen()
        self.execute(server)

    def connect_database(self):
        try:
            self.conx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=HOANGGIA;Database=UserAccount;UID=hoanggia;PWD=hoanggia')
            self.cursor = self.conx.cursor()
        except:
            popup = tk.Toplevel(self)
            popup.title("Error")
            popup.geometry("300x100")
            popup.resizable(False, False)
            button_ok = tk.Button(popup, text="OK", font=("Times", 12), bg="blue", fg="white", command=popup.destroy, width=10, height=1)
            label_error = tk.Label(popup, text="Database is not available", font=("Times", 16, "bold"))
            label_error.pack()
            button_ok.pack()
            self.server.close()
            return

    def establish_connection(self, frame):
        popup = tk.Toplevel(self)
        popup.title("Error")
        popup.geometry("300x100")
        popup.resizable(False, False)
        button_ok = tk.Button(popup, text="OK", font=("Times", 12), bg="blue", fg="white", command=popup.destroy, width=10, height=1)
        label_title = tk.Label(frame, text="COVID-19 INFO", font=("Times", 22, "bold"), bg="lightblue")
        label_server = tk.Label(frame, text="Server IP: {}".format(SERVER_IP) + "  PORT: {}".format(SERVER_PORT), font=("Times", 16, "bold"), bg="lightblue", fg="red")
        label_sth = tk.Label(frame, text="", font=("Times", 30, "bold"), bg="lightblue")

        label_title.pack()
        label_sth.pack()
        label_server.pack()
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((SERVER_IP, SERVER_PORT))
            self.server.listen()
            self.stop = threading.Event()

            update_thread = threading.Thread(target=self.update_info)
            update_thread.daemon = True
            update_thread.start()
            popup.destroy()
            execute_thread = threading.Thread(target=self.execute, args=(self.server,))
            execute_thread.daemon = True
            execute_thread.start()

        except:
            label_error = tk.Label(popup, text="Server is not available", font=("Times", 16, "bold"))
            label_error.pack()
            button_ok.pack()
            self.server.close()
            return
        conx_thread = threading.Thread(target=self.connect_database)
        conx_thread.daemon = True
        conx_thread.start()


app = App()
app.mainloop()
if(app.quit):
    try:
        app.stop.set()
        app.server.close()
        app.conx.close()
    except:
        pass
