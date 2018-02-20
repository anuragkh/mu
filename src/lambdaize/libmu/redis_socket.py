#!/usr/bin/python

import redis

from libmu.socket_nb import SocketNB


class RedisQueue(object):
    """ Simple message queue with Redis backend.

    Based on http://peter-hoffmann.com/2012/python-simple-queue-redis-queue.html
    """

    maxlen = None

    def __init__(self, name, **redis_kwargs):
        """The default connection parameters are: host='localhost', port=6379, db=0"""
        self.__db = redis.Redis(**redis_kwargs)
        self.key = name

    def __len__(self):
        return self.__db.llen(self.key)

    # TODO: Add Redis cleanup; ideally we would delete the key corresponding to this queue

    def name(self):
        return self.key

    def size(self):
        """Return the size of the queue"""
        return self.__db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.size() == 0

    def append(self, msg):
        """Add msg to the right side of the queue."""
        self.__db.rpush(self.key, msg)

    def appendleft(self, msg):
        """Add msg to the left side of the queue."""
        self.__db.lpush(self.key, msg)

    def clear(self):
        """Remove all msgs from the queue leaving it with length 0."""
        self.__db.ltrim(self.key, 0, -1)

    def count(self, msg):
        """Count the number of queue messages equal to msg."""
        raise NotImplementedError

    def extend(self, iterable):
        """Extend the right side of the queue by appending messages from the iterable argument."""
        raise NotImplementedError

    def extendleft(self, iterable):
        """Extend the left side of the queue by appending messages from the iterable argument. Note, the series of left
        appends results in reversing the order of messages in the iterable argument."""
        raise NotImplementedError

    def pop(self, block=False, timeout=None):
        """Remove and return a msg from the right side of the queue.

        If optional args block is true and timeout is None, block
        if necessary until an msg is available."""
        if block:
            msg = self.__db.brpop(self.key, timeout=timeout)
        else:
            msg = self.__db.rpop(self.key)

        if msg:
            return msg[1]
        else:
            raise IndexError()

    def popleft(self, block=False, timeout=None):
        """Remove and return a msg from the left side of the queue.

        If optional args block is true and timeout is None, block
        if necessary until an msg is available."""
        if block:
            msg = self.__db.blpop(self.key, timeout=timeout)
        else:
            msg = self.__db.lpop(self.key)

        if msg:
            return msg[1]
        else:
            raise IndexError()

    def remove(self, msg):
        """Removed the first occurrence of msg. If not found, raises a ValueError."""
        raise NotImplementedError

    def reverse(self):
        """Reverse the messages in the queue in-place and then return None."""
        raise NotImplementedError

    def rotate(self, n=1):
        """Rotate the deque n steps to the right. If n is negative, rotate to the left.

        When the deque is not empty, rotating one step to the right is equivalent to d.appendleft(d.pop()), and rotating
        one step to the left is equivalent to d.append(d.popleft())."""
        raise NotImplementedError


class RedisSocket(object):
    def __init__(self, src, dst, fd=0):
        self.laddr = src
        self.raddr = dst
        self.fd = fd

    def fileno(self):
        return self.fd

    def getsockname(self):
        return self.laddr

    def getpeername(self):
        return self.raddr

    def close(self):
        pass

    @staticmethod
    def shutdown(*_):
        pass


class RedisSocketNB(SocketNB):
    def __init__(self, src, dst):
        super(RedisSocketNB, self).__init__(RedisSocket(src, dst))
        # Send messages to the specific lambda
        self.send_queue = RedisQueue("%s" % dst)
        # Receive all messages destined to me
        self.recv_queue = RedisQueue("%s" % src)

    def _fill_recv_buf(self):
        pass

    def do_read(self):
        pass

    def _fill_send_buf(self):
        pass

    def _send_raw(self):
        pass

    def do_write(self):
        pass

    def do_handshake(self):
        pass
