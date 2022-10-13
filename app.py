import collections
from struct import pack

# from twisted.internet import epollreactor
#
# epollreactor.install()
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


    def connectionMade(self):
        """
        Invoked by twisted to setup connection object
        """
        pass

    def connectionLost(self, reason):
        """
        Invoked by twisted to tear down connection object
        """
        pass

    def dataReceived(self, data):
        """
        Invoked by twisted to handle streamed request data
        """
        if not self.headerseen:
            header = self.bytesremaining = data[0]
            if header == 128:
                if self.factory.stack:
                    self.pop()
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
            retval = pack('B', 0)
            self.transport.write(retval)
            self.factory.stack.appendleft(self.payload)
            self.transport.loseConnection()

    def pop(self):
        stackval = self.factory.stack.popleft()
        retval = pack('B', len(stackval))
        self.transport.write(retval)
        self.transport.write(stackval)
        self.transport.loseConnection()

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



