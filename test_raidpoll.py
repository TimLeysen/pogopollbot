import datetime
import random

from raidpoll import RaidPoll

poll = RaidPoll('Tyranitar', datetime.datetime.now(), 'location', 'me')
for i in range(0,20):
    poll.add_vote(str(i), random.randrange(1,41), 0)

print(poll.message())
poll.all_voters[0].sort_by_level()
print(poll.message())