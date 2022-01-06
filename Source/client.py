import json
import socket
import time
import datetime
import tkinter as tk

SERVER_IP = "127.0.0.1"  # default 127.0.0.1
SERVER_PORT = 65000
FORMAT = "utf-8"
LOGGED = False

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class ConnectionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="lightblue")
        label_title = tk.Label(self, text="CONNECT TO SERVER", font=("Times", 20, "bold"), bg="lightblue")
        label_ip = tk.Label(self, text="Server IP:", font=("Times", 16, "bold"), bg="lightblue")
        self.entry_ip = tk.Entry(self, width=20, font=("Times", 16, "bold"), bg="gray", fg="white")

        button_connect = tk.Button(self, text="Connect", font=("Times", 15, "bold"), command=lambda: self.connect(controller), bg="blue", fg="white")

        label_title.pack(side="top", fill="x", pady=10)
        label_ip.place(x=130, y=240)
        self.entry_ip.place(x=240, y=240)
        button_connect.place(x=305, y=300)

    def is_valid_ip(self, IP: str):
        try:
            socket.inet_aton(IP)
            return True
        except:
            return False

    def connect(self, controller):
        global SERVER_IP
        SERVER_IP = self.entry_ip.get()
        popup = tk.Toplevel(controller)
        popup.geometry("200x100")
        popup.resizable(False, False)
        button_ok = tk.Button(popup, text="OK", font=("Times"), bg="blue", fg="white", command=popup.destroy, width=10, height=1)
        if (not self.is_valid_ip(SERVER_IP)):
            popup.title("Error")
            label = tk.Label(popup, text="Invalid IP", font=("Times", 12, "bold"))
            label.pack(side="top", fill="x", pady=10)
            button_ok.pack()
            return
        try:
            popup.geometry("280x100")
            client.connect((SERVER_IP, SERVER_PORT))
            sockname = str(client.getsockname()[0]) + ", " + str(client.getsockname()[1])
            popup.title("Connected")
            label = tk.Label(popup, text=sockname + " has connected", font=("Times", 12, "bold"))
            label.pack(side="top", fill="x", pady=10)
            button_ok.pack()
            controller.show_frame(LoginPage)
        except:
            popup.title("Error")
            label = tk.Label(popup, text="Server has closed the connection", font=("Times", 12, "bold"))
            label.pack(side="top", fill="x", pady=10)
            button_ok.pack()


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="lightblue")
        label_title = tk.Label(self, text="COVID-19 INFO", font=("Times", 20, "bold"), bg="lightblue")
        label_login = tk.Label(self, text="LOGIN TO SERVER", font=("Times", 16, "bold"), bg="lightblue", fg="red")
        label_user = tk.Label(self, text="Username", font=("Times", 16, "bold"), bg="lightblue")
        label_pass = tk.Label(self, text="Password", font=("Times", 16, "bold"), bg="lightblue")
        label_or = tk.Label(self, text="OR", font=("Times", 16, "bold"), bg="lightblue")

        self.entry_user = tk.Entry(self, width=20, font=("Times", 16, "bold"), bg="gray", fg="white")
        self.entry_password = tk.Entry(self, width=20, show="*", font=("Times", 16, "bold"), bg="gray", fg="white")

        button_login = tk.Button(self, text="LOG IN", font=("Times", 16, "bold"), bg="blue", fg="white", command=lambda: self.login(controller))
        button_signup = tk.Button(self, text="SIGN UP", font=("Times", 16, "bold"), bg="blue", fg="white", command=lambda: self.signup_page(controller))

        label_title.pack()
        label_login.place(x=250, y=40)
        label_user.place(x=310, y=80)
        self.entry_user.place(x=250, y=120)
        label_pass.place(x=310, y=160)
        self.entry_password.place(x=250, y=200)
        button_login.place(x=310, y=240)
        label_or.place(x=335, y=285)
        button_signup.place(x=305, y=320)

    def login(self, controller):
        popup = tk.Toplevel(controller)
        button_ok = tk.Button(popup, text="OK", font=("Times"), bg="blue", fg="white", command=popup.destroy, width=10, height=1)
        popup.geometry("300x100")
        popup.resizable(False, False)
        popup.title("Error")
        try:
            username = self.entry_user.get()
            password = self.entry_password.get()
            global LOGGED
            if (LOGGED):
                return
            if(username == "" or password == ""):
                label = tk.Label(popup, text="Username or password cannot be empty!", font=("Times", 12, "bold"))
                label.pack(side="top", fill="x", pady=10)
                button_ok.pack()
                return
            client.send("/login".encode(FORMAT))
            time.sleep(0.05)
            client.send(username.encode(FORMAT))
            time.sleep(0.05)
            client.send(password.encode(FORMAT))
            self.entry_user.delete(0, 'end')
            self.entry_password.delete(0, 'end')
            respone = client.recv(1024).decode(FORMAT)
            if (respone == "ok"):
                LOGGED = True
                popup.destroy()
                controller.show_frame(MainPage)
            else:
                label = tk.Label(popup, text=respone, font=("Times", 12, "bold"))
                label.pack(side="top", fill="x", pady=10)
                button_ok.pack()
        except:
            label = tk.Label(popup, text="Server has closed the connection", font=("Times", 12, "bold"))
            label.pack(side="top", fill="x", pady=10)
            button_ok.pack()

    def signup(self, controller):
        username = self.entry_username.get()
        password = self.entry_passwd.get()
        confirm_password = self.entry_confirm_pass.get()
        popup = tk.Toplevel(controller)
        button_ok = tk.Button(popup, text="OK", font=("Times"), bg="blue", fg="white", command=popup.destroy, width=10, height=1)
        popup.geometry("300x100")
        popup.resizable(False, False)
        popup.title("Error")
        if (username == "" or password == "" or confirm_password == ""):
            label = tk.Label(popup, text="Username or password cannot be empty!", font=("Times", 12, "bold"))
            label.pack(side="top", fill="x", pady=10)
            button_ok.pack()
            return
        if (password != confirm_password):
            label = tk.Label(popup, text="Password does not match!", font=("Times", 12, "bold"))
            label.pack(side="top", fill="x", pady=10)
            button_ok.pack()
            return
        try:
            client.send("/signup".encode(FORMAT))
            time.sleep(0.05)
            client.send(username.encode(FORMAT))
            time.sleep(0.05)
            client.send(password.encode(FORMAT))
            self.entry_username.delete(0, 'end')
            self.entry_passwd.delete(0, 'end')
            self.entry_confirm_pass.delete(0, 'end')
            respone = client.recv(1024).decode(FORMAT)
            popup.title("Notification")
            label = tk.Label(popup, text=respone, font=("Times", 12, "bold"))
            label.pack(side="top", fill="x", pady=10)
            button_ok.pack()
        except:
            label = tk.Label(popup, text="Server has closed the connection", font=("Times", 12, "bold"))
            label.pack(side="top", fill="x", pady=10)
            button_ok.pack()

    def signup_page(self, controller):
        signup_page = tk.Toplevel(controller)
        signup_page.configure(bg="lightblue")
        signup_page.geometry("500x500")
        signup_page.resizable(False, False)
        signup_page.title("Sign Up")

        label_username = tk.Label(signup_page, text="Username", font=("Times", 16, "bold"), bg="lightblue")
        label_password = tk.Label(signup_page, text="Password", font=("Times", 16, "bold"), bg="lightblue")
        label_confirm_password = tk.Label(signup_page, text="Confirm Password", font=("Times", 16, "bold"), bg="lightblue")

        self.entry_username = tk.Entry(signup_page, width=20, font=("Times", 16, "bold"), bg="gray", fg="white")
        self.entry_passwd = tk.Entry(signup_page, width=20, show="*", font=("Times", 16, "bold"), bg="gray", fg="white")
        self.entry_confirm_pass = tk.Entry(signup_page, width=20, show="*", font=("Times", 16, "bold"), bg="gray", fg="white")

        button_signup = tk.Button(signup_page, text="SIGN UP NOW", font=("Times", 16, "bold"), bg="blue", fg="white", command=lambda: self.signup(controller))

        label_username.place(x=200, y=40)
        self.entry_username.place(x=140, y=80)
        label_password.place(x=200, y=120)
        self.entry_passwd.place(x=140, y=160)
        label_confirm_password.place(x=155, y=200)
        self.entry_confirm_pass.place(x=140, y=240)
        button_signup.place(x=170, y=280)


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="lightblue")
        label_title = tk.Label(self, text="COVID-19 INFO", font=("Times", 20, "bold"), bg="lightblue")
        label_notice = tk.Label(self, text="Enter location or date to get the latest information", font=("Times", 16, "bold"), bg="lightblue", fg="red")
        self.entry_province = tk.Entry(self, width=20, font=("Times", 16, "bold"), bg="gray", fg="white")
        self.entry_date = tk.Entry(self, width=20, font=("Times", 16, "bold"), bg="gray", fg="white")

        button_req = tk.Button(self, text="SEARCH BY PROVINCE", font=("Times", 16, "bold"), bg="blue", fg="white", command=lambda: self.search_province(controller))
        button_reqdate = tk.Button(self, text="SEARCH BY DATE", font=("Times", 16, "bold"), bg="blue", fg="white", command=lambda: self.search_date(controller))
        button_logout = tk.Button(self, text="LOG OUT", font=("Times", 16, "bold"), bg="red", fg="white", command=lambda: self.logout(controller))

        label_title.pack()
        label_notice.place(x=125, y=120)
        self.entry_province.place(x=235, y=160)
        button_req.place(x=220, y=200)
        self.entry_date.place(x=235, y=260)
        button_reqdate.place(x=245, y=300)
        button_logout.place(x=290, y=360)

    def search_province(self, controller):
        province = self.entry_province.get()
        popup = tk.Toplevel(controller)
        popup.title("Error")
        scrollbar = tk.Scrollbar(popup, orient="vertical")
        list = tk.Listbox(popup, width=300, height=400, font=("Times", 12), selectmode="extended", yscrollcommand=scrollbar.set)
        button_ok = tk.Button(popup, text="OK", font=("Times"), bg="blue", fg="white", command=popup.destroy, width=10, height=1)
        if (province == ""):
            popup.geometry("280x100")
            label = tk.Label(popup, text="Location cannot be empty!", font=("Times", 12, "bold"))
            label.pack(side="top", fill="x", pady=10)
            button_ok.pack()
            return
        try:
            client.send("/req".encode(FORMAT))
            client.recv(1024).decode(FORMAT)
            client.send(province.encode(FORMAT))
            self.entry_province.delete(0, 'end')
            while True:
                items = client.recv(1024).decode(FORMAT)
                if(items == "Found"):
                    popup.geometry("300x400")
                    popup.title("Search by province")
                    scrollbar.pack(side="right", fill="y")
                    scrollbar.config(command=list.yview)
                    list.pack(side="left", fill="both")
                    list.config(yscrollcommand=scrollbar.set)
                    break
                elif(items == "NotFound"):
                    popup.geometry("280x100")
                    label = tk.Label(popup, text="Province not found", font=("Times", 12, "bold"))
                    label.pack(side="top", fill="x", pady=10)
                    button_ok.pack()
                    break
                location = json.loads(items)
                list.insert(tk.END, "PROVINCE: " + location["name"])
                list.insert(tk.END, "CASES TOTAL: " + str(location["cases"]))
                list.insert(tk.END, "CASES TODAY: " + str(location["casesToday"]))
                list.insert(tk.END, "DEATHS: " + str(location["death"]))
                list.insert(tk.END, "TREATING: " + str(location["treating"]))
                list.insert(tk.END, "RECOVERED: " + str(location["recovered"]))
                list.insert(tk.END, "")
                client.send("ok".encode(FORMAT))
        except:
            popup.geometry("280x100")
            label = tk.Label(popup, text="Server has closed the connection", font=("Times", 12, "bold"))
            label.pack(side="top", fill="x", pady=10)
            button_ok.pack()

    def search_date(self, controller):
        popup = tk.Toplevel(controller)
        scrollbar = tk.Scrollbar(popup, orient="vertical")
        list = tk.Listbox(popup, width=300, height=200, font=("Times", 12), selectmode="extended", yscrollcommand=scrollbar.set)
        button_ok = tk.Button(popup, text="OK", font=("Times"), bg="blue", fg="white", command=popup.destroy, width=10, height=1)
        try:
            date = datetime.datetime.strptime(self.entry_date.get(), "%d-%m-%Y")
            req = date.strftime("%Y-%m-%d")
        except:
            self.entry_date.delete(0, 'end')
            popup.geometry("350x100")
            popup.title("Error")
            label = tk.Label(popup, text="Date format is incorrect, should be dd-mm-yyyy", font=("Times", 12, "bold"))
            label.pack(side="top", fill="x", pady=10)
            button_ok.pack()
            return
        try:
            client.send("/reqdate".encode(FORMAT))
            client.recv(1024).decode(FORMAT)
            client.send(req.encode(FORMAT))
            self.entry_date.delete(0, 'end')
            items = client.recv(1024).decode(FORMAT)
            if(items == "NotFound"):
                popup.geometry("280x100")
                popup.title("Error")
                label = tk.Label(popup, text="Date not found", font=("Times", 12, "bold"))
                label.pack(side="top", fill="x", pady=10)
                button_ok = tk.Button(popup, text="OK", bg="blue", fg="white", command=popup.destroy, width=10, height=1)
                button_ok.pack()
                return
            location = json.loads(items)
            list.insert(tk.END, "DATE: " + date.strftime("%d-%m-%Y"))
            list.insert(tk.END, "CASES: " + str(location["cases"]))
            list.insert(tk.END, "DEATHS: " + str(location["death"]))
            list.insert(tk.END, "TREATING: " + str(location["treating"]))
            list.insert(tk.END, "RECOVERED: " + str(location["recovered"]))
            list.insert(tk.END, "AVG CASES 7-DAY: " + str(location["avgCases7day"]))
            list.insert(tk.END, "AVG DEATHS 7-DAY: " + str(location["avgDeath7day"]))
            list.insert(tk.END, "AVG RECOVERED 7-DAY: " + str(location["avgRecovered7day"]))
            popup.geometry("300x200")
            popup.title("Search by date")
            scrollbar.pack(side="right", fill="y")
            scrollbar.config(command=list.yview)
            list.pack(side="left", fill="both")
            list.config(yscrollcommand=scrollbar.set)
        except:
            popup.geometry("280x100")
            popup.title("Error")
            label = tk.Label(popup, text="Server has closed the connection", font=("Times", 12, "bold"))
            label.pack(side="top", fill="x", pady=10)
            button_ok.pack()

    def logout(self, controller):
        global LOGGED
        if (LOGGED):
            try:
                client.send("/logout".encode(FORMAT))
                LOGGED = False
                controller.show_frame(LoginPage)
            except:
                popup = tk.Toplevel(controller)
                popup.geometry("280x100")
                popup.title("Error")
                label = tk.Label(popup, text="Server has closed the connection", font=("Times", 12, "bold"))
                label.pack(side="top", fill="x", pady=10)
                button_ok = tk.Button(popup, text="OK", font=("Times"), bg="blue", fg="white", command=popup.destroy, width=10, height=1)
                button_ok.pack()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("COVID-19 INFO")
        self.geometry("700x450")
        self.resizable(False, False)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (ConnectionPage, LoginPage, MainPage):
            frame = F(container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[F] = frame

        self.show_frame(ConnectionPage)

    def show_frame(self, cont):
        background = tk.PhotoImage(file="background.png", width=150, height=115)
        frame = self.frames[cont]
        label_background = tk.Label(frame, image=background, border=0)
        label_background.image = background
        label_background.place(x=0, y=0)
        frame.tkraise()


app = App()
app.mainloop()
if (app.quit):
    try:
        client.send("/quit".encode(FORMAT))
    except:
        pass
client.close()
