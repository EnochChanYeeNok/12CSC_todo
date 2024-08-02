#import
import sqlite3
from bottle import route, run, debug, template, redirect, request, static_file, error, response
import hashlib
import json
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = request.get_cookie("account", secret='some-secret-key')
        if not username:
            redirect('/auth?action=login')
        return f(*args, **kwargs)
    return decorated_function

def get_db():
    return sqlite3.connect('todo.db')

@route('/')
@route('/auth', method=['GET', 'POST'])
def auth():
    error = None
    action = request.GET.get('action', 'login')
    
    if request.method == 'POST':
        action = request.forms.get('action')
        username = request.forms.get('username').strip()
        password = request.forms.get('password').strip()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        if action == 'signup':
            try:
                c.execute("INSERT INTO users (username, password, task) VALUES (?, ?, ?)", (username, hashed_password, json.dumps([])))
                conn.commit()
                return redirect('/auth?action=login')
            except sqlite3.IntegrityError:
                return template('auth.html', error="Username already exists.", action='signup')
            finally:
                conn.close()
        elif action == 'login':
            c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed_password))
            user = c.fetchone()
            conn.close()

            if user:
                response.set_cookie("account", str(user[0]), secret='some-secret-key')
                return redirect('/home')
            else:
                return template('auth.html', error="Invalid username or password.", action='login')
    else:
        action = request.query.action or 'login'
    return template('auth.html', action=action, error=error)



    


#home page---------------------------------------------------------------------------------------------------------------
@route('/home')
@login_required
def home():
    return template('home.html')
#------------------------------------------------------------------------------------------------------------------------
#showing items-----------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------


#opened items------------------------------------------------------------------------------------------------------------
@route('/todo')
@login_required
def todo_list():
    user_id = request.get_cookie("account", secret='some-secret-key')
    if not user_id:
        redirect('/auth?action=login')

    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT task FROM users WHERE id = ?", (user_id,))
    user_tasks = c.fetchone()
    conn.close()

    tasks = json.loads(user_tasks['task']) if user_tasks else []
    open_tasks = [task for task in tasks if task['status'] == 1]

    return template('make_table.html', rows=open_tasks)


#closed items-------------------------------------------------------------------------------------------------------------
@route('/closed')
@login_required
def closed_list():
    user_id = request.get_cookie("account", secret='some-secret-key')
    if not user_id:
        redirect('/auth?action=login')

    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT task FROM users WHERE id = ?", (user_id,))
    user_tasks = c.fetchone()
    conn.close()

    tasks = json.loads(user_tasks['task']) if user_tasks else []
    closed_tasks = [task for task in tasks if task['status'] == 0]
    return template('closed_item.html', rows=closed_tasks)


#------------------------------------------------------------------------------------------------------------------------
#new item ----------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
@route('/new', method='GET')
@login_required
def new_item():
    if request.GET.save:
        new_task_content = request.GET.task.strip()
        if not new_task_content:
            return template('new_task.html', error="Task content cannot be empty")
        
        user_id = request.get_cookie("account", secret='some-secret-key')
        if not user_id:
            redirect('/auth?action=login')

        conn = get_db()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT task FROM users WHERE id = ?", (user_id,))
        user_tasks = c.fetchone()
        tasks = json.loads(user_tasks['task']) if user_tasks and user_tasks['task'] else []

        new_task = {"id": len(tasks) + 1, "content": new_task_content, "status": 1}
        tasks.append(new_task)
        print(tasks)
        print(user_id)
        c.execute("UPDATE users SET task = ? WHERE id = ?", (json.dumps(tasks), user_id))
        conn.commit()
        conn.close()
        
        return redirect('/todo')
    else:
        return template('new_task.html')

#------------------------------------------------------------------------------------------------------------------------
# Editing items----------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------ 
@route('/edit/<no:int>', method='GET')
@login_required
def edit_item(no):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if request.GET.save:
        edit_content = request.GET.task.strip()
        status = request.GET.status.strip()
        status = 1 if status == 'open' else 0

        user_id = request.get_cookie("account", secret='some-secret-key')
        if not user_id:
            redirect('/auth?action=login')

        c.execute("SELECT task FROM users WHERE id = ?", (user_id,))
        user_tasks = c.fetchone()
        tasks = json.loads(user_tasks['task']) if user_tasks else []

        for task in tasks:
            if task['id'] == no:
                task['content'] = edit_content
                task['status'] = status
                break

        c.execute("UPDATE users SET task = ? WHERE id = ?", (json.dumps(tasks), user_id))
        conn.commit()
        conn.close()
        return redirect('/todo')
    else:
        user_id = request.get_cookie("account", secret='some-secret-key')
        if not user_id:
            redirect('/auth?action=login')

        c.execute("SELECT task FROM users WHERE id = ?", (user_id,))
        user_tasks = c.fetchone()
        tasks = json.loads(user_tasks['task']) if user_tasks else []

        task_to_edit = next((task for task in tasks if task['id'] == no), None)
        conn.close()
        return template('edit_task.html', old=task_to_edit, no=no)


#-----------------------------------------------------------------------------------------------
#delete item(same page as edit)----------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
@route('/delete/<task_id:int>', method='POST')
@login_required
def delete_item(task_id):
    user_id = request.get_cookie("account", secret='some-secret-key')
    if not user_id:
        redirect('/auth?action=login')

    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT task FROM users WHERE id = ?", (user_id,))
    user_tasks = c.fetchone()
    tasks = json.loads(user_tasks['task']) if user_tasks else []

    tasks = [task for task in tasks if task['id'] != task_id]

    c.execute("UPDATE users SET task = ? WHERE id = ?", (json.dumps(tasks), user_id))
    conn.commit()
    conn.close()
    return redirect('/todo')
#
#connecting to the css file


@route('/logout')
def logout():
    response.delete_cookie("account", secret='some-secret-key')
    return redirect('/auth?action=login')


@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static/')



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