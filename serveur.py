

import sys
import socket, threading


#### SERVER ####
SERVER : str = "127.0.0.1"
# HOST : str = socket.gethostbyname(socket.gethostname())
PORT : int = 7500
ADDRESS : tuple = (SERVER, PORT)
FORMAT : str = "utf-8"
HEADER : int = 1024
LISTEN_LIMIT : int = 5


active_connections : int = 0
clients, names = [], []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	server.bind(ADDRESS)
except socket.error as e:
	print(str(e))
	print(f"Unable to bind to host {SERVER} and port {PORT}!")


def startChat() -> None:
	global active_connections
	print("server is working on " + SERVER)
	server.listen(LISTEN_LIMIT)
	while True:
		conn, addr = server.accept()
		conn.send("NAME".encode(FORMAT))
		name : str = conn.recv(HEADER).decode(FORMAT)
		names.append(name)
		clients.append(conn)
		active_connections += 1
		print(f"\nName is : {name}")

		send_message_to_client(f"{name} has joined the chat! ".encode(FORMAT))
		# conn.send('Connection successful!'.encode(FORMAT))

		thread = threading.Thread(target=handle, args=(conn, addr, ))
		thread.start()

		print("Active connections: ", active_connections)
		check_active_connections()


def handle(conn, addr) -> None:
	global active_connections
	print(f"new connection {addr}")
	disconnected : bool = False
	while True:
		try:
			message = conn.recv(HEADER)
			if len(message) == 0:
				disconnected = True
				break
			send_message_to_client(message)
			print(message)
		except:
			disconnected = True
			break

	index : int = clients.index(conn)
	clients.remove(conn)
	conn.close()
	name : str = names[index]
	send_message_to_client(f"{name} has left the chat!".encode(FORMAT))
	names.remove(name)
	active_connections -= 1
	check_active_connections()

	if disconnected:
		print(f"\nClient {addr} has disconnected!")
		print(f"Active connections {active_connections}")


def send_message_to_client(message) -> None:
	for client in clients:
		client.send(message)


def check_active_connections() -> None:
	global active_connections
	if active_connections == 0:
		print("ALL clients are disconnected!")
		server.close()
		sys.exit()


def main(args) -> None:
	print("Server is starting...")
	print(f"active connections {threading.active_count()-1}")
	startChat()
	print("Server is closed!...")


if __name__ == "__main__":
	main(sys.argv)






