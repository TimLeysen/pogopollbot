import sqlite3



def set_level(id : int, name : str, level : int):
    conn = sqlite3.connect('pollbot.db')
    c = conn.cursor()
    
    try:
        if c.execute('select * from users where id=?', (id,)).fetchone():
            print('update')
            c.execute('update users set name=?, level=? where id=?', (name, level, id))
        else:
            print('insert')
            c.execute('insert into users values (?,?,?)', (id, name, level))

        conn.commit()
    except sqlite3.Error as e:
        print('database error: {}'.format(e.args[0]))
        
    conn.close()
        
def get_level(id : str):
    conn = sqlite3.connect('pollbot.db')
    c = conn.cursor()
    
    try:
        if c.execute('select level from users where id=?', (id,)):
            row = c.fetchone()
            return row[0] if row else 0

    except sqlite3.Error as e:
        print('database error: {}'.format(e.args[0]))
        
    conn.close()