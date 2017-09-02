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

from datetime import datetime, timedelta
import random

from common import from_string, to_string, to_time_string
from timepoll import TimePoll

if __name__ == '__main__':
    poll = TimePoll('rhydon', datetime.now(), 'TEST', 'some guy')
    end_times = []
    for i in range(20):
        time = datetime.now() + timedelta(hours=random.randrange(1,2), minutes=random.randrange(0,60))
        end_times.append(time)
    
    for time in end_times:
        start_times = poll.calc_start_times(time)
        print('{} {} => {}'.format(to_time_string(datetime.now()), to_time_string(time), start_times))