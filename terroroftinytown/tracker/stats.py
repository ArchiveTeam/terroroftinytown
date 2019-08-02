# encoding=utf-8
'''Stats information'''
import json

from terroroftinytown.event import Bus

__all__ = ['Stats', 'stats_bus']

stats_bus = Bus()

class Stats:
    def __init__(self, redis, redis_prefix, count=30):
        global stats

        self.redis = redis
        self.prefix = redis_prefix
        self.count = count

        Stats.instance = self

    def update(self, stats):
        # live stats
        key = self.get_key()
        self.redis.lpush(key, json.dumps(stats))
        self.redis.ltrim(key, 0, self.count)

        # users lifetime stat
        self.redis.hincrby(key+':s', stats['username'], stats['scanned'])
        self.redis.hincrby(key+':f', stats['username'], stats['found'])

        # total stats
        self.redis.incrby(key+':ts', stats['scanned'])
        self.redis.incrby(key+':tf', stats['found'])

        # project stats
        self.redis.hincrby(key+':pf', stats['project'], stats['found'])
        self.redis.hincrby(key+':ps', stats['project'], stats['scanned'])

        stats_bus.fire(**stats)

    def get_live(self):
        '''Return live item results, for format of output see model.checkin_item'''
        return [json.loads(item.decode('utf-8')) for item in self.redis.lrange(self.get_key(), 0, self.count)]

    def get_lifetime(self):
        '''
        Return lifetime stats for all users.
        Output:
        {
            'username': [found, scanned],
            ...
        }
        '''
        key = self.get_key()
        scanned = self.redis.hgetall(key+':s')
        found = self.redis.hgetall(key+':f')
        out = {}

        for user, count in scanned.items():
            out[user.decode('utf-8')] = [int(found[user]), int(count)]

        return out

    def get_user_lifetime(self, user):
        '''Return user lifetime stats as array of [found, scanned]'''
        key = self.get_key()
        scanned = self.redis.hget(key+':s', user) or 0
        found = self.redis.hget(key+':f', user) or 0
        return [int(found), int(scanned)]

    def get_global(self):
        '''Return total stats as array of [found, scanned]'''
        found = self.redis.get(self.get_key()+':tf')
        scanned = self.redis.get(self.get_key()+':ts')

        return [
            int(found) if found else 0,
            int(scanned) if scanned else 0
        ]

    def get_project(self):
        key = self.get_key()
        scanned = self.redis.hgetall(key+':ps')
        found = self.redis.hgetall(key+':pf')
        out = {}

        for project, count in scanned.items():
            out[project.decode('utf-8')] = [int(found[project]), int(count)]

        return out

    def get_key(self):
        return self.prefix + 'stats'

    def clear(self):
        key = self.get_key()
        self.redis.delete(
            key, key + ':s', key + ':f', key + ':ts', key + ':tf',
            key + ':pf', key + ':ps'
        )

Stats.instance = None