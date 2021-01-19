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

import json
import string


class Pokedex:
    def __init__(self):
        with open('pokemon_types.json', 'r') as f:
            data = f.read()
        pokemon_types = json.loads(data)
        self.data = { t['pokemon_id'] : {'name': t['pokemon_name'].lower(), "types": [x.lower() for x in t['type']]} for t in pokemon_types}

        with open('pokemon_strengths_and_weaknesses.json', 'r') as f:
            data = f.read()        
        strenghts_and_weaknesses = json.loads(data)
        self.types = { t['type']: {
            'strenghts': [x.lower() for x in t['strenghts']], 
            'weaknesses': [x.lower() for x in t['weaknesses']]}
            for t in strenghts_and_weaknesses}

    def get_strengths(self, id : int):
        result = []
        for key in self.get_types(id):
            if key in self.types.keys():
                result += self.types[key]['strenghts']
        
        return sorted(result)

    def get_weaknesses(self, id : int):
        result = []
        for key in self.get_types(id):
            if key in self.types.keys():
                result += self.types[key]['weaknesses']
        
        return sorted(result)

    # get weaknesses as distinct strings with suffix x<count>
    def get_distinct_weaknesses(self, id : int):
        result = []
        counts = {}
        for w in self.get_weaknesses(id):
            if w in counts.keys():
                counts[w] += 1
            else:
                counts[w] = 1

        for s in self.get_strengths(id):
            if s in counts.keys():
                counts[s] -= 1
        
        return ['{}{}'.format(k, 'x{}'.format(v) if v > 1 else '')
            for (k, v) in counts.items()
            if v > 0]

    def get_name(self, id : int):
        if id in self.data.keys():
            return self.data[id]['name']
            return None

    def get_names(self, ids : [int]):
        return [get_name(id) for id in ids]
        
    def get_id(self, name : str):
        name = name.lower()
        for k,v in self.data.items():
            if v['name'].lower() == name:
                return k
        return None
        
    def get_ids(self, names : [str]):
        return [get_id(name) for name in names]

    def get_types(self, id : int):
        if id in self.data.keys():
            return self.data[id]['types']
        return []
        
    def id_exists(self, id : int):
        return id in self.data.keys()
        
    def name_exists(self, name : str):
        return name.lower() in [v['name'] for v in self.data.values()]

    def is_raid_boss(self, name : str):
        return name.lower() in list(raid_bosses.keys())
        
    def is_exclusive_raid_boss(self, name : str):
        return name.lower() in exclusive_raid_bosses
        
    def capwords(s : str):
        return '-'.join([x.capitalize() for x in s.split('-')])

    def sprite_url(self, name : str):
        return 'http://floatzel.net/pokemon/black-white/sprites/images/{0}.png'.format(get_id(name))