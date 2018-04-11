#!/usr/bin/python

from elasticmem import ElasticMemClient
from elasticmem import DirectoryServiceException
from libmu.socket_nb import SocketNB


class RedisQueue(object):
    def __init__(self, name, db):
        """The default connection parameters are: host='localhost', port=6379, db=0"""
        self.__db = db
        self.key = name

    def __len__(self):
        return self.__db.llen(self.key)

    def name(self):
        return self.key

    def append(self, msg):
        """Add msg to the right side of the queue."""
        self.__db.rpush(self.key, msg)

    def appendleft(self, msg):
        """Add msg to the left side of the queue."""
        self.__db.lpush(self.key, msg)

    def pop(self):
        """Remove and return a msg from the right side of the queue."""
        return self.__db.rpop(self.key)

    def popleft(self):
        """Remove and return a msg from the left side of the queue."""
        return self.__db.lpop(self.key)


class DummySocket(object):
    def __init__(self, sockfd):
        self.fd = sockfd

    def fileno(self):
        return self.fd

    def close(self):
        pass

    @staticmethod
    def shutdown(*_):
        pass


class EMSocketNB(SocketNB):
    def __init__(self, send_path, recv_path, sockfd, host, port):
        super(EMSocketNB, self).__init__(DummySocket(sockfd))
        print "Connecting to directory server @ %s:%d" % (host, port)
        self.em = ElasticMemClient(host, port)
        self.send_path = send_path
        self.recv_path = recv_path
        try:
            self.kv = self.em.create(self.recv_path, '/tmp')
        except DirectoryServiceException:
            self.kv = self.em.open(self.send_path)
        try:
            self.em.fs.create(self.recv_path, '/tmp')
        except DirectoryServiceException:
            pass
        self.notif = self.em.open_listener(self.recv_path).subscribe(['put'])
        self.want_handle = False
        print "EM socket send %s, recv %s" % (send_path, recv_path)

    def _fill_recv_buf(self):
        pass

    def do_read(self):
        self.want_handle = self.notif.has_notification()

    def enqueue(self, msg):
        self.kv.put(msg, '')

    def dequeue(self):
        self.want_handle = False
        return self.notif.get_notification().data

    def update_flags(self):
        pass

    def _fill_send_buf(self):
        pass

    def _send_raw(self):
        pass

    def do_write(self):
        pass

    def do_handshake(self):
        pass
