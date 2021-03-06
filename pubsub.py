import socket
import selectors
from array import array
from datetime import datetime

SUBSCRIPTION_TIMEOUT = 10  # send subscription every 10 minutes
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 200

FOREX_ADDRESS = 'localhost'
FOREX_PORT = 50404


class ForexSubscriber(object):
    """
    Accept subscriptions for a new instance of a given publisher class.
    """

    def __init__(self, request_address, forex_provider_address):
        """
        :param request_address:
        :param request_port:
        """
        self.forex_provider_address = forex_provider_address
        self.selector = selectors.DefaultSelector()
        self.last_renew_timestamp = 0
        self.listener, self.listener_address = self.start_a_server(request_address)

    def run_forever(self):
        next_timeout = 0.2  # FIXME
        while True:
            events = self.selector.select(next_timeout)
            for key, mask in events:
                if key.fileobj == self.listener:
                    self.on_accept(key.fileobj)
                elif mask & selectors.EVENT_READ:
                    # if data is callable method then call the method
                    if key.data and callable(key.data):
                        key.data(key.fileobj)
                    # else:
                    #     self.receive_message(key.fileobj)
                elif mask & selectors.EVENT_WRITE:
                    handler = key.data
                    # if the callable method then call the method
                    # other wise call send message
                    if callable(handler):
                        handler(key.fileobj)

            self.ready_to_renew()


    def on_accept(self, sock: socket):
        print("getting data from {0}".format(sock.fileno()))
        conn, addr = sock.accept()
        print('accepted connection from {0}'.format(addr))
        conn.setblocking(False)
        # set it state for Any in coming message
        # register this new conn to read event
        self.selector.register(fileobj=conn, events=selectors.EVENT_READ)

    def start_a_server(self, address):
        """
        Start a socket bound to given address.

        :returns: listening socket
        """
        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener.bind(address)
        listener.setblocking(False)
        #listener.settimeout(0.2)  # FIXME
        self.selector.register(listener, selectors.EVENT_READ)
        return listener, listener.getsockname()

    def ready_to_renew(self):
        current_timestamp = datetime.utcnow().timestamp()
        if (self.last_renew_timestamp == 0) \
            or (current_timestamp - self.last_renew_timestamp) > SUBSCRIPTION_TIMEOUT:
            self.last_renew_timestamp = current_timestamp
            conn = self.get_connection(self.forex_provider_address)
            self.selector.register(conn, selectors.EVENT_WRITE, self.renew_subscription)
        # create a new connection for "member"

    def serialize_ip(self, b: str) -> bytes:
        ip = '168.108.114.22'

        #b_out = bytes(map(int, b.split('.'))).swapcase()
        b_out = bytes(map(int, b.split('.')))
        return b_out

    def serialize_port(self, b: int) -> bytes:
        a = array('H', [b])  # array of 8-byte floating-point numbers
        a.byteswap()
        return a.tobytes()

    def serialize_address(self, b: str) -> bytes:
        message = bytes()
        message += self.serialize_ip(b[0])
        message += self.serialize_port(b[1])
        print(message)
        #self.deserialize_address(message)
        return message

    def get_connection(self, member):
        new_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("get Connection {0}".format(member))
        new_conn.connect(member)
        new_conn.setblocking(False)
        return new_conn

    def renew_subscription(self, conn):
        # renew subscription to provider
        print('Renew Subscription')
        message = '{}'.format(self.listener_address).encode()
        conn.sendall(b'')
        self.selector.unregister(conn)
        conn.close()

if __name__ == '__main__':
    fsubs = ForexSubscriber((SERVER_ADDRESS, SERVER_PORT), (FOREX_ADDRESS, FOREX_PORT))
    fsubs.ready_to_renew()
    fsubs.run_forever()