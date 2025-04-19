import pytest
import redis
from redis._compat import b, next
from redis.exceptions import ConnectionError

class TestPubSub(object):
    def test_pattern_subscribe(self, r):
        p = r.pubsub()
        # psubscribe doesn't return anything
        assert p.psubscribe('f*') is None
        # send a message
        assert r.publish('foo', 'hello foo') == 1
        # there should be now 2 messages in the buffer, a subscribe and the
        # one we just published
        assert next(p.listen()) == \
            {
                'type': 'psubscribe',
                'pattern': None,
                'channel': 'f*',
                'data': 1
            }
        assert next(p.listen()) == \
            {
                'type': 'pmessage',
                'pattern': 'f*',
                'channel': 'foo',
                'data': b('hello foo')
            }
        # unsubscribe
        assert p.punsubscribe('f*') is None
        # unsubscribe message should be in the buffer
        assert next(p.listen()) == \
            {
                'type': 'punsubscribe',
                'pattern': None,
                'channel': 'f*',
                'data': 0
            }