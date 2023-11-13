import socket


class HTTPResponseHandler:
    HTTP_RESPONSE_200 = b"HTTP/1.1 200 OK\r\n\r\n"
    HTTP_RESPONSE_400 = b"HTTP/1.1 404 Not Found\r\n\r\n"
    HTTP_200 = "HTTP/1.1 200 OK"
    TEXT_PLAIN = "Content-Type: text/plain"

    @staticmethod
    def get_response(request_path, user_input):
        print(request_path, user_input)
        match request_path:
            case "/":
                return HTTPResponseHandler.HTTP_RESPONSE_200
            case "/echo/":
                return HTTPResponseHandler.response_200_builder(user_input)
            case _:
                return HTTPResponseHandler.HTTP_RESPONSE_400

    @staticmethod
    def response_200_builder(user_input):
        response_headers = [
            HTTPResponseHandler.HTTP_200,
            HTTPResponseHandler.TEXT_PLAIN,
            f"Content-Length: {len(user_input)}",
            "",
            "",
        ]
        response = "\r\n".join(response_headers) + user_input
        return response.encode()


class HTTPRequestDecoder:
    @staticmethod
    def decode_request(request):
        decoded_request = request.decode("utf-8")
        split_request = decoded_request.splitlines()
        http_method, request_path, http_version = split_request[0].split(" ")
        return http_method, request_path, http_version

    @staticmethod
    def get_user_line(request_path):
        final_user_input = ""
        string_list = request_path.split("/")
        if len(string_list) < 4:
            return ""
        for iterator_number in range(len(string_list)):
            if iterator_number > 1:
                user_input = string_list[iterator_number]
                final_user_input += user_input
                final_user_input += "/"
        return final_user_input[:-1]

    @staticmethod
    def extract_request(request_path):
        interaction_flag = False
        user_input = ""
        for char in request_path:
            if char == "/":
                user_input += char
                if interaction_flag is True:
                    return user_input
                interaction_flag = True
            elif interaction_flag is True:
                user_input += char
        return user_input


class EchoServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        server_socket = socket.create_server((self.host, self.port), reuse_port=True)
        while True:
            client_socket, address = server_socket.accept()
            print(f"A request received from {address}")
            request = client_socket.recv(4096)
            http_method, request_path, http_version = HTTPRequestDecoder.decode_request(
                request
            )
            print(
                f"Method: {http_method}\nPath: {request_path}\nVersion: {http_version}"
            )
            user_input = HTTPRequestDecoder.get_user_line(request_path)
            client_socket.send(
                HTTPResponseHandler.get_response(
                    HTTPRequestDecoder.extract_request(request_path), user_input
                )
            )
            client_socket.close()


if __name__ == "__main__":
    server = EchoServer("localhost", 4221)
    server.start()
