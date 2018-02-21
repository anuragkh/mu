#!/usr/bin/python

import sys
import redis

from libmu.socket_nb import SocketNB


class RedisQueue(object):
    """ Simple message queue with Redis backend.

    Based on http://peter-hoffmann.com/2012/python-simple-queue-redis-queue.html
    """

    def __init__(self, name, db):
        """The default connection parameters are: host='localhost', port=6379, db=0"""
        self.__db = db
        self.key = name

    def __len__(self):
        return self.__db.llen(self.key)

    # TODO: Add Redis cleanup; ideally we would delete the key corresponding to this queue

    def name(self):
        return self.key

    def append(self, msg):
        """Add msg to the right side of the queue."""
        print "RedisQueue: append msg (%s)" % msg
        self.__db.rpush(self.key, msg)

    def appendleft(self, msg):
        """Add msg to the left side of the queue."""
        print "RedisQueue: appendleft msg (%s)" % msg
        self.__db.lpush(self.key, msg)

    def pop(self):
        """Remove and return a msg from the right side of the queue."""
        msg = self.__db.rpop(self.key)
        if msg:
            print "RedisQueue: pop msg (%s)" % msg
            return msg
        else:
            raise IndexError()

    def popleft(self):
        """Remove and return a msg from the left side of the queue."""
        msg = self.__db.lpop(self.key)
        if msg:
            print "RedisQueue: popleft msg (%s)" % msg
            return msg
        else:
            raise IndexError()


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


class RedisSocketNB(SocketNB):
    def __init__(self, src, dst, sockfd, **redis_kwargs):
        super(RedisSocketNB, self).__init__(DummySocket(sockfd))
        db = redis.Redis(**redis_kwargs)
        # Send messages to the specific lambda
        self.send_queue = RedisQueue("%s" % dst, db)
        # Receive all messages destined to me
        self.recv_queue = RedisQueue("%s" % src, db)

    def _fill_recv_buf(self):
        pass

    def do_read(self):
        self.want_handle = len(self.recv_queue) > 0

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
