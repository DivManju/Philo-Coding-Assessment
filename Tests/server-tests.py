import socket
import unittest
from socket import AF_INET, SOCK_STREAM, socket


class TestStackServer(unittest.TestCase):

    def test_stack_server_accepts_push_request(self):
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect(('localhost', 8080))
        client_socket.send(b'\x08I6jbnLep')
        self.assertEqual(client_socket.recv(1),  b'\x00')
        client_socket.close()

    def test_stack_server_returns_top_value_for_pop_request(self):
        client_1_socket = socket(AF_INET, SOCK_STREAM)
        client_1_socket.connect(('localhost', 8080))
        client_1_socket.send(b'\x08I6jbnLem')
        client_1_socket.close()
        popheader = b'\x80'
        client_2_socket = socket(AF_INET, SOCK_STREAM)
        client_2_socket.connect(('localhost', 8080))
        client_2_socket.send(popheader)
        self.assertEqual(client_2_socket.recv(9).decode(), '\x08I6jbnLem')
        client_2_socket.close()


if __name__ == '__main__':
    unittest.main()
