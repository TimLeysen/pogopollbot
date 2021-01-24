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

import sqlite3



def set_level(user_id : int, user_name : str, level : int):
    conn = sqlite3.connect('pollbot.db')
    c = conn.cursor()
    
    try:
        if c.execute('select * from users where id=?', (user_id,)).fetchone():
            print('update')
            c.execute('update users set name=?, level=? where id=?', (user_name, level, user_id))
        else:
            print('insert')
            c.execute('insert into users values (?,?,?,?)', (user_id, user_name, level, ''))

        conn.commit()
    except sqlite3.Error as e:
        print('database error: {}'.format(e.args[0]))
        
    conn.close()
        
def get_level(user_id : int):
    conn = sqlite3.connect('pollbot.db')
    c = conn.cursor()
    
    try:
        if c.execute('select level from users where id=?', (user_id,)):
            row = c.fetchone()
            return row[0] if row else 0

    except sqlite3.Error as e:
        print('database error: {}'.format(e.args[0]))
        
    conn.close()

def set_remote_id(user_id : int, user_name : str, remote_id : str):
    conn = sqlite3.connect('pollbot.db')
    c = conn.cursor()
    
    try:
        if c.execute('select * from users where id=?', (user_id,)).fetchone():
            print('update')
            c.execute('update users set name=?, remoteid=? where id=?', (user_name, remote_id, user_id))
        else:
            print('insert')
            c.execute('insert into users values (?,?,?,?)', (id, user_name, 0, user_id))

        conn.commit()
    except sqlite3.Error as e:
        print('database error: {}'.format(e.args[0]))
        
    conn.close()

def get_remote_id(user_id : str):
    conn = sqlite3.connect('pollbot.db')
    c = conn.cursor()
    
    try:
        if c.execute('select remoteid from users where id=?', (user_id,)):
            row = c.fetchone()
            return row[0] if row else 0

    except sqlite3.Error as e:
        print('database error: {}'.format(e.args[0]))
        
    conn.close()    