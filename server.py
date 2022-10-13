import collections
from struct import pack
from time import time

from twisted.internet import epollreactor
epollreactor.install()

from twisted.internet import reactor

from twisted.internet.protocol import Protocol, Factory

class Stack(Protocol):
    """
    Twisted implements network protocol parsing and handling for TCP servers via
    twisted.internet.protocol.Protocol.

    An instance of the protocol class is instantiated per-connection, on demand,
    and will go away when the connection is finished.This means that persistent
    configuration is not saved in the Protocol

    The protocol responds to events as they arrive from the network and the
    events arrive as calls to methods on the protocol.
    """

    def __init__(self, factory):
        self.factory = factory
        self.headerseen = False
        self.bytesremaining = None
        self.payload = b''
        self.isconnected = False


    def connectionMade(self):
        """
        Invoked by twisted to setup connection object
        """
        self.isconnected = True
        self.factory.open_connections += 1
        now = time()
        if self.factory.open_connections == 101:
            if (int(time() - self.factory.
                    client_connection_timestamp[self.factory.clients[-1]]) > 10):
                self.factory.clients[-1].transport.loseConnection()
                self.factory.client_connection_timestamp[self] = now
                self.factory.clients.insert(0, self)
            else:
                retval = pack('B', 255)
                self.transport.write(retval)
                self.factory.client_connection_timestamp[self] = now
                self.factory.clients.insert(0, self)
                self.transport.loseConnection()
            return
        self.factory.client_connection_timestamp[self] = now
        self.factory.clients.insert(0, self)

    def connectionLost(self, reason):
        """
        Invoked by twisted to tear down connection object
        """
        self.isconnected = False
        self.factory.open_connections -= 1
        self.factory.clients.remove(self)
        del self.factory.client_connection_timestamp[self]

    def dataReceived(self, data):
        """
        Invoked by twisted to handle streamed request data
        """
        if not self.headerseen:
            header = self.bytesremaining = data[0]
            if header == 128:
                if self.factory.stack:
                    self.pop()
                else:
                    self.factory.blocked_pop_requests.appendleft(self)
                self.headerseen = True
                return
            if len(data) > 1:
                self.payload += data[1:]
                self.bytesremaining -= len(data) - 1
            self.headerseen = True
        else:
            self.payload += data
            self.bytesremaining -= len(data)
        if not self.bytesremaining:
            if len(self.factory.stack) < 100:
                self.factory.stack.appendleft(self.payload)
                retval = pack('B', 0)
                self.transport.write(retval)
                self.transport.loseConnection()
            else:
                self.factory.blocked_push_requests.appendleft(self)
            if self.factory.blocked_pop_requests:
                popstackval = self.factory.blocked_pop_requests.pop()
                if not popstackval.isconnected:
                    return
                popstackval.pop()

    def pop(self):
        stackval = self.factory.stack.popleft()
        retval = pack('B', len(stackval))
        self.transport.write(retval)
        self.transport.write(stackval)
        self.transport.loseConnection()
        if self.factory.blocked_push_requests:
            push_request = self.factory.blocked_push_requests.pop()
            if not push_request.isconnected:
                return
            self.factory.stack.appendleft(push_request.payload)
            retval = pack('B', 0)
            push_request.transport.write(retval)
            push_request.transport.loseConnection()

class StackFactory(Factory):
    """
    Factories are state machines to record state of twisted protocol handlers.

    The default implementation of the buildProtocol method calls the protocol
    attribute of the factor to create a Protocol instance, and then sets an attribute
    on it called factory which points to the factory itself.

    This lets every Protocol access, and possibly modify, the persistent configuration.
    """
    def __init__(self):
        self.stack = collections.deque()
        self.blocked_push_requests = collections.deque()
        self.blocked_pop_requests = collections.deque()
        self.clients = []
        self.client_connection_timestamp = {}
        self.open_connections = 0


    def buildProtocol(self, addr):
        return Stack(self)


if __name__ == '__main__':
        """
        The reactor listens for certain events and dispatches them to registered callback 
        functions that have been designed to handle these events
        
        reactor.run() starts the reactor and then waits forever for connections to arrive 
        on the port specified.
        
        The epoll()-based reactor is Twisted’s default on Linux.
        """
        reactor.listenTCP(8080, StackFactory())
        reactor.run()



