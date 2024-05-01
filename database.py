from sqlite3 import connect

def f1(id, *ar):
    ser = connect("Гавно.db")
    s = ser.cursor()        
    n = []
    k = "UPDATE us SET "
    for i in ar:
        if i == ar[-1]:
            k += i[0] + " = ?"
        else:
            k += i[0] + " = ?, "
        n.append(i[1])
    list(n)
    s.execute(k + f" WHERE user_id = {id};", n)
    ser.commit()
    ser.close()

def f2(id, *ar):
    ser = connect("Гавно.db")
    s = ser.cursor()
    k = "SELECT "
    for i in ar:
        if i == ar[-1]:
            k += i
        else:
            k += i + ", "
    h = s.execute(k + f" FROM us WHERE user_id IS NOT NULL AND user_id = {id};").fetchall()
    ser.commit()
    ser.close()
    return h[0]