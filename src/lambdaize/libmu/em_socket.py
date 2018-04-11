#!/usr/bin/python

from elasticmem import ElasticMemClient
from elasticmem import DirectoryServiceException
from libmu.socket_nb import SocketNB


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
    def __init__(self, send_path, recv_path, sockfd, host):
        super(EMSocketNB, self).__init__(DummySocket(sockfd))
        self.em = ElasticMemClient(host)
        self.send_path = send_path
        self.recv_path = recv_path

        try:
            self.kv = self.em.create(self.send_path, '/tmp')
        except DirectoryServiceException:
            self.kv = self.em.open(self.send_path)

        try:
            self.em.fs.create(self.recv_path, '/tmp')
        except DirectoryServiceException:
            pass
        self.notif = self.em.open_listener(self.recv_path).subscribe(['put'])
        self.want_handle = False

    def _fill_recv_buf(self):
        pass

    def do_read(self):
        pass

    def enqueue(self, msg):
        self.kv.put(msg, '')

    def dequeue(self):
        return self.notif.get_notification().data

    def has_data(self):
        return self.notif.has_notification()

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
