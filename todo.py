#import
import sqlite3
from bottle import route, run, debug,template, redirect, request,static_file, error
#------------------------------------------------------------------------------------------------------------------------
#showing items-----------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------


#opened items------------------------------------------------------------------------------------------------------------
@route('/todo')
def todo_list():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT id, task FROM todo WHERE status LIKE '1'")
    result = c.fetchall()
    c.close
    return template('make_table', rows=result)


#closed items-------------------------------------------------------------------------------------------------------------
@route('/closed')
def closed_list():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT id, task FROM todo WHERE status LIKE '0'")
    result = c.fetchall()
    c.close()
    return template('closed_item', rows=result)


#------------------------------------------------------------------------------------------------------------------------
#new item----------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
@route('/new', method='GET')
def new_item():

    if request.GET.save:

        new = request.GET.task.strip()
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()

        c.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new,1))
        new_id = c.lastrowid

        conn.commit()
        c.close()

        return redirect('/todo')
    else:
        return template('new_task.tpl')
#------------------------------------------------------------------------------------------------------------------------
# Editing items----------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------ 
@route('/edit/<no:int>', method='GET')
def edit_item(no):

    if request.GET.save:
        edit = request.GET.task.strip()
        status = request.GET.status.strip()

        if status == 'open':
            status = 1
        else:
            status = 0

        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("UPDATE todo SET task = ?, status = ? WHERE id LIKE ?", (edit, status, no))
        conn.commit()

        return redirect('/todo')
    else:
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", (str(no),))
        cur_data = c.fetchone()

        return template('edit_task', old=cur_data, no=no)

#-----------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------

#
#
@route('/help')
def help():
    return static_file('help.html',root='/path/to/file')
#
#
#
#
#
#
@error(404)
def mistake404(code):
    return 'Sorry, this page does not exist'
@error(403)
def mistake403(code):
    return 'The parameter you passed has the wrong format'
#-------------------------------------------------------------------------------------------------
#Main
#-------------------------------------------------------------------------------------------------
debug(True)#only for dev
run(reloader= True)#reloader only for dev