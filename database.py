import sqlite3



def set_level(name : str, level : int):
    conn = sqlite3.connect('pollbot.db')
    c = conn.cursor()
    
    try:
        if c.execute('select * from users where name=?', (name,)).fetchone():
            print('update')
            c.execute('update users set level=? where name=?', (level, name))
        else:
            print('insert')
            c.execute('insert into users values (?,?)', (name, level))

        conn.commit()
    except sqlite3.Error as e:
        print('database error: {}'.format(e.args[0]))
        
    conn.close()
        
def get_level(name : str):
    conn = sqlite3.connect('pollbot.db')
    c = conn.cursor()
    
    try:
        if c.execute('select level from users where name=?', (name,)):
            row = c.fetchone()
            return row[0] if row else 0

    except sqlite3.Error as e:
        print('database error: {}'.format(e.args[0]))
        
    conn.close()