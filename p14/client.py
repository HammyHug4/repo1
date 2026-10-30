import socket, sys
with socket.create_connection(("localhost", 3000)) as s:
    s.sendall((sys.argv[1] + "\n").encode())
    print(s.recv(1024).decode().strip())