import socket
import paramiko
import threading
import pymysql.cursors
from typing import Union
from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health_check():
    return 'OK'

class SSHServer(paramiko.ServerInterface):
    def check_auth_password(self, username: str, password: str) -> int:
        # Extract client IP address from self.client_address
        client_ip = self.client_address[0]

        # Extract client operating system from self.client_os
        client_os = self.client_os

        # Print the client details
        print(f"Client IP: {client_ip}")
        print(f"Operating System: {client_os}")

        # Save the client details to MariaDB
        save_to_database(client_ip, client_os)

        return paramiko.AUTH_FAILED

def handle_connection(client_sock: socket.socket) -> None:
    transport = paramiko.Transport(client_sock)
    server_key = paramiko.RSAKey.from_private_key_file('key')
    transport.add_server_key(server_key)
    ssh = SSHServer()

    # Set client IP address and operating system
    ssh.client_address = client_sock.getpeername()[0]
    ssh.client_os = client_sock.recv(2048).decode('utf-8')

    ssh.set_server(transport)
    transport.start_server(server=ssh)

def save_to_database(client_ip: str, client_os: str) -> None:
    connection = pymysql.connect(
        host='localhost',
        user='myhon',
        password='psw123',
        database='honeypot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # Create a table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS client_details (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ip_address VARCHAR(255),
                    operating_system VARCHAR(255)
                )
            """)

            # Insert the client details into the table
            cursor.execute("""
                INSERT INTO client_details (ip_address, operating_system)
                VALUES (%s, %s)
            """, (client_ip, client_os))

        # Commit the transaction
        connection.commit()

        # Display the hacker details
        display_hacker_details(connection)
    finally:
        # Close the connection
        connection.close()

def display_hacker_details(connection) -> None:
    with connection.cursor() as cursor:
        print("Hacker Details:")
        print("----------------")
        cursor.execute("SELECT * FROM client_details")
        for row in cursor.fetchall():
            print(f"ID: {row['id']}")
            print(f"IP Address: {row['ip_address']}")
            print(f"Operating System: {row['operating_system']}")
            print("----------------")

def main() -> None:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('0.0.0.0', 2222))
    server_sock.listen(5)

    while True:
        client_sock, client_addr = server_sock.accept()
        print(f"Connection from {client_addr[0]};{client_addr[1]}")
        t = threading.Thread(target=handle_connection, args=(client_sock,))
        t.start()

if __name__ == "__main__":
    main()
