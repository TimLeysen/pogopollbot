"""
Copyright 2017 Tim Leysen

This file is part of PoGoPollBot.

PoGoPollBot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PoGoPollBot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import datetime
import random

from raidpoll import RaidPoll

poll = RaidPoll('Mega', datetime.datetime.now(), 'location', 'me', False)

def add_vote(id : str, choice : int):
    poll.add_vote(id, 'player{}'.format(id), random.randrange(1,41), 'remote_id{}'.format(i), choice)

print('\n\n5 players choose 0')
for i in range(0, 5):
    add_vote(str(i), 0)
print(poll.message())

print('\n\n3 players choose 0 again')
for i in range(0, 3):
    add_vote(str(i), 0)
print(poll.message())

print('\n\n2 new remote players')
for i in range(5, 7):
    add_vote(str(i), 1)
    add_vote(str(i), 1)  # this shouldn't work
print(poll.message())

print('\n\nall players cancelled')
for i in range(0, 7):
    add_vote(str(i), 2)
print(poll.message())