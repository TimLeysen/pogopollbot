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

poll = RaidPoll('Tyranitar', datetime.datetime.now(), 'location', 'me')
for i in range(0,20):
    poll.add_vote(str(i), random.randrange(1,41), 0)

print(poll.message())
poll.all_voters[0].sort_by_level()
print(poll.message())