

import sys, atexit
import socket, threading
from tkinter import *
import tkinter as tk
from datetime import datetime
from tkinter import messagebox


#### SERVER ####
SERVER : str = "127.0.0.1"
PORT : int = 7500
ADDRESS : tuple = (SERVER, PORT)
FORMAT : str = "utf-8"
HEADER : int = 1024
LISTEN_LIMIT : int = 5

#### GUI ####
BG_COLOR : str = "#222034"
TXT_COLOR : str = "#5FCDE4"
HELV_14 : str = "Helvetica 14"
HELV_14_B : str = "Helvetica 14 bold"
MSG_BG : str = "#9BADB7"
ET_BG : str = "#25325E"


class Window(tk.Tk):
	def __init__(self) -> None:
		tk.Tk.__init__(self)
		self.resizable(False, False)
		self.iconphoto(False, PhotoImage(file=str("./assets/chat_icon.png")))
		self.wm_attributes("-topmost", 1)
		self._frame = None
		self.switch_frame(Login)

	def switch_frame(self, frameClass) -> None:
		newFrame = frameClass(self)
		if self._frame is not None:
			self._frame.destroy()
			self._frame.destroy()
		self._frame = newFrame
		self.geometry('470x570+'+self.screen()+'+20')
		self._frame.pack()

	def screen(self) -> str:
		screen_width = self.winfo_screenwidth()
		posX = (screen_width //2) - (470//2) 
		return str(posX)


class Login(tk.Frame):
	def __init__(self, master) -> None:
		tk.Frame.__init__(self, master)
		self.tkraise()
		self.master.title("LOGIN")

		self.canvas = tk.Canvas(self, 
            height = 570, width = 470, 
            bd = 0, bg = BG_COLOR,
            highlightthickness = 0)
		self.canvas.pack(side=TOP,padx=0,pady=0)

		self.pls = Label(self.canvas, text="Please login to continue",
			justify=CENTER, font=HELV_14_B, bg=BG_COLOR, fg=TXT_COLOR)
		self.pls.place(x = 130, y = 10)

		self.lblName = Label(self.canvas, text="Name*: ", font=HELV_14,
            bg=BG_COLOR, fg=TXT_COLOR)
		self.lblName.place(x = 20, y = 80)

		self.lblNameInfo = CreateToolTip(self.lblName, \
			"Required information. "
			"No special characters allowed. "
			"Maximum 12 characters !")

		self.entryName = Entry(self.canvas, font=HELV_14, 
            justify='left', width=20)
		self.entryName.place(relwidth=0.7, relheight=0.05, x = 100, y = 76)
		self.entryName.bind("<Return>", lambda x: self.master.switch_frame(ChatBox))
		self.entryName.focus()

		self.btnContinue = Button(self.canvas, text="CONTINUE", font=HELV_14_B,
            background=BG_COLOR, foreground=TXT_COLOR,    
			command = lambda: self.master.switch_frame(ChatBox), width=10)
		self.btnContinue.place(x = 180, y = 150)
		self.btnContinueInfo = CreateToolTip(self.btnContinue, text= \
			"Click to continue to the chatbox!")

		self.btnQuit = Button(text = "QUIT", font=HELV_14_B, 
			background=BG_COLOR, foreground=TXT_COLOR,
			command = self.master.destroy, width=10)
		self.btnQuit.place(x = 180, y = 200)
		self.btnQuitInfo = CreateToolTip(self.btnQuit, text= \
			"Click to quit the application!")


class ChatBox(tk.Frame):
	def __init__(self, master) -> None:
		tk.Frame.__init__(self, master)
		self.tkraise()
		self.master.title("CHATBOX")
		self.usrname : str = str(master._frame.entryName.get())
		self.goAhead(self.usrname)

	def goAhead(self, name:str) -> None:
		self.layout(name)
		self.connect()
		rcv = threading.Thread(target=self.receive)
		rcv.start()

	def layout(self, name:str) -> None:
		self.name : str = name

		## Header zone
		self.menuBtn = tk.Menubutton(self.master, 
				text=(str(self.name)), font=HELV_14_B, 
				bg=BG_COLOR, fg=TXT_COLOR, pady=5)
		self.menu = tk.Menu(self.menuBtn, tearoff=0)
		self.menu.add_command(label="Disconnect              \
                            ", accelerator="Ctrl+D",
            command=self.disconnect, font=("Helvetica 16"), 
            activebackground=BG_COLOR, activeforeground=TXT_COLOR)
		self.menu.add_command(label="Exit", accelerator="Ctrl+Q",
            command=self.stop, font=("Helvetica 16"), 
            activebackground=BG_COLOR, activeforeground=TXT_COLOR)
		self.menuBtn["menu"] = self.menu
		self.menuBtn.place(relwidth=1)
		self.menuBtnInfo = CreateToolTip(self.menuBtn, text= \
      		"Click to see the menu!")
		self.master.bind_all('<Control-d>', lambda x: self.disconnect())
		self.master.bind_all('<Control-D>', lambda x: self.disconnect())
		self.master.bind_all('<Control-q>', lambda x: self.stop())
		self.master.bind_all('<Control-Q>', lambda x: self.stop())

		## Line
		self.line = Label(self.master, width=450, bg=MSG_BG)
		self.line.place(relwidth=1, rely=0.055, relheight=0.012)

		## Text widget
		self.txtCons = Text(self.master, width=20, height=2, bg=BG_COLOR, 
					   fg=TXT_COLOR, font=HELV_14, padx=5, pady=5)
		self.txtCons.place(relheight=0.84, relwidth=1, rely=0.06)
		self.txtConsInfo = CreateToolTip(self.txtCons, text= \
			"Chat messages will be displayed here!")

		## Message zone
		self.lblBottom = Label(self.master, bg=MSG_BG, height=80)
		self.lblBottom.place(relwidth=1, rely=0.89)

		## Entry Messages
		self.entryMsg = Entry(self.lblBottom, bg=ET_BG, justify='left',
						fg=TXT_COLOR, font="Helvetica 13")
		self.entryMsg.place(relwidth=0.8, relheight=0.04, rely=0.002, relx=0.011)
		self.entryMsgInfo = CreateToolTip(self.entryMsg, text= \
			"Type your message here"
            " and press 'Enter' to send it!")
		self.entryMsg.bind("<Return>", lambda x: self.sendButton(self.entryMsg.get()))

		## Send button
		self.btnMsg = Button(self.lblBottom, text="Send", 
				font="Helvetica 10 bold", width=20, bg=MSG_BG, 
				activebackground=BG_COLOR, activeforeground=TXT_COLOR,
				command=lambda: self.sendButton(self.entryMsg.get()))
		self.btnMsg.place(relx=0.815, rely=0.002, 
				relheight=0.04, relwidth=0.18)
		self.btnMsgInfo = CreateToolTip(self.btnMsg, text= \
      			"Press to send your message!")

		## Scrollbar
		self.txtCons.config(cursor="arrow")

		scrollbar = Scrollbar(self.txtCons)
		scrollbar.place(relheight=1, relx=0.974)
		scrollbar.config(command=self.txtCons.yview)

		self.txtCons.config(state=DISABLED)


	def sendButton(self, msg:str) -> None:
		self.txtCons.config(state=DISABLED)
		self.msg : str = msg
		self.entryMsg.delete(0, END)
		snd = threading.Thread(target=self.sendMessage)
		snd.start()

	def receive(self) -> None:
		self.running : bool = True
		while self.running:
			try:
				message : str = client.recv(HEADER).decode(FORMAT)
				if message == 'NAME':
					client.send(self.name.encode(FORMAT))
				else:
					self.txtCons.config(state=NORMAL)
					self.txtCons.insert(END, message+"\n\n")
					self.txtCons.config(state=DISABLED)
					self.txtCons.see(END)
			except ConnectionAbortedError:
				break
			except ConnectionResetError:
				print("The server has disconnected!")
				break
			except:
				print("An error occurred!")
				client.close()
				break

	def sendMessage(self) -> None:
		time : str = datetime.now().strftime("%H:%M:%S")
		self.txtCons.config(state=DISABLED)
		while True:
			message = (f"{self.name} ~ {time} :  {self.msg}")
			client.send(message.encode(FORMAT))
			break

	def connect(self) -> None:
		global client
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			client.connect(ADDRESS)
		except:
			print("Server is not available")
			messagebox.showerror("Unable to connect to server", 
				f"Server is not available at {SERVER}:{PORT}")
			
	def disconnect(self) -> None:
		client.send(f"Le client {self.name} a quitte la discussion! ".encode(FORMAT))
		# client.send(f"Active connections {threading.active_count()-1} ".encode(FORMAT))
		messagebox.showinfo("Disconnected", 
			"You have been disconnected from the server")
		self.closeServer()
		self.master.switch_frame(Login)

	def closeServer(self) -> None:
		self.running = False
		client.close()

	def stop(self) -> None:
		self.closeServer()
		self.master.destroy()


class CreateToolTip(object):
	""" create a tooltip for a given widget """
	def __init__(self, widget, text:str='widget info') -> None:
		self.waittime : int = 500     #miliseconds
		self.wraplength : int = 180   #pixels
		self.widget = widget
		self.text : str = text
		self.widget.bind("<Enter>", self.enter)
		self.widget.bind("<Leave>", self.leave)
		self.widget.bind("<ButtonPress>", self.leave)
		self.id = None
		self.tw = None

	def enter(self, event=None) -> None:
		self.schedule()

	def leave(self, event=None) -> None:
		self.unschedule()
		self.hidetip()

	def schedule(self) -> None:
		self.unschedule()
		self.id = self.widget.after(self.waittime, self.showtip)

	def unschedule(self) -> None:
		id = self.id
		self.id = None
		if id: self.widget.after_cancel(id)

	def showtip(self, event=None) -> None:
		x = y = 0
		x, y, cx, cy = self.widget.bbox("insert")
		x += self.widget.winfo_rootx() + 25
		y += self.widget.winfo_rooty() + 20
		
		# creates a toplevel window
		self.tw = tk.Toplevel(self.widget)
		
		# Leaves only the label and removes the app window
		self.tw.wm_overrideredirect(True)
		self.tw.wm_geometry("+%d+%d" % (x, y))
		label = tk.Label(self.tw, text=self.text, justify='left',
				background="#FFFFE0", relief='solid', borderwidth=1,
				wraplength = self.wraplength)
		label.pack(ipadx=1)

	def hidetip(self) -> None:
		tw = self.tw
		self.tw = None
		if tw: tw.destroy()



def main(args) -> None:
	app = Window()
	app.mainloop()



if __name__ == "__main__":
	main(sys.argv)
	atexit.register(ChatBox.closeServer)


