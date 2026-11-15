from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import config
# Email:    admin@gmail.com  
# Password: admin123
app = Flask(__name__)
app.secret_key = 'secret'

# DB CONFIG
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['MYSQL_PORT'] = config.MYSQL_PORT

mysql = MySQL(app)

# ================= HOME =================
@app.route('/')
def index():
    return render_template('index.html')

# ================= REGISTER =================
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO employees(employee_name,email,department,password)
            VALUES(%s,%s,%s,%s)
        """, (
            request.form['name'],
            request.form['email'],
            request.form['dept'],
            request.form['password']
        ))
        mysql.connection.commit()
        return redirect('/login')
    return render_template('register.html')

# ================= LOGIN =================
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employees WHERE email=%s AND password=%s",
                    (request.form['email'], request.form['password']))
        user = cur.fetchone()

        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')

    return render_template('login.html')

# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

# ================= APPLY LEAVE =================
@app.route('/apply_leave', methods=['GET','POST'])
def apply_leave():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO leave_requests(employee_id,leave_type,start_date,end_date,reason)
            VALUES(%s,%s,%s,%s,%s)
        """, (
            session['user_id'],
            request.form['type'],
            request.form['start'],
            request.form['end'],
            request.form['reason']
        ))
        mysql.connection.commit()
        return redirect('/leave_history')

    return render_template('apply_leave.html')

# ================= LEAVE HISTORY =================
@app.route('/leave_history')
def leave_history():
    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM leave_requests WHERE employee_id=%s",
                (session['user_id'],))
    data = cur.fetchall()

    return render_template('leave_history.html', leaves=data)

# ================= ADMIN LOGIN =================
@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        if request.form['email'] == 'admin@gmail.com' and request.form['password'] == 'admin123':
            session['admin'] = True
            return redirect('/admin/dashboard')
    return render_template('admin_login.html')

# ================= ADMIN DASHBOARD =================
@app.route('/admin/dashboard')
def admin_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT leave_requests.id,
               leave_requests.leave_type,
               leave_requests.start_date,
               leave_requests.end_date,
               leave_requests.reason,
               leave_requests.status,
               employees.employee_name
        FROM leave_requests
        JOIN employees ON leave_requests.employee_id = employees.id
    """)
    data = cur.fetchall()
    return render_template('admin_dashboard.html', leaves=data)


# ================= APPROVE / REJECT =================
"""@app.route('/update_leave/<int:id>/<action>')
def update_leave(id, action):
    cur = mysql.connection.cursor()

    if action == "approve":
        cur.execute("UPDATE leave_requests SET status='Approved' WHERE id=%s", (id,))
    elif action == "reject":
        cur.execute("UPDATE leave_requests SET status='Rejected' WHERE id=%s", (id,))

    mysql.connection.commit()
    return redirect('/admin/dashboard')
@app.route('/approve/<int:id>')
def approve(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE leave_requests SET status='Approved' WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect('/admin/dashboard')

@app.route('/reject/<int:id>')
def reject(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE leave_requests SET status='Rejected' WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect('/admin/dashboard')"""



@app.route('/approve/<int:id>')
def approve(id):
    cur = mysql.connection.cursor()

    # Check current status
    cur.execute("SELECT status FROM leave_requests WHERE id=%s", (id,))
    leave = cur.fetchone()

    if leave and leave[0] == 'Pending':
        cur.execute(
            "UPDATE leave_requests SET status='Approved' WHERE id=%s",
            (id,)
        )
        mysql.connection.commit()

    return redirect('/admin/dashboard')


@app.route('/reject/<int:id>')
def reject(id):
    cur = mysql.connection.cursor()

    # Check current status
    cur.execute("SELECT status FROM leave_requests WHERE id=%s", (id,))
    leave = cur.fetchone()

    if leave and leave[0] == 'Pending':
        cur.execute(
            "UPDATE leave_requests SET status='Rejected' WHERE id=%s",
            (id,)
        )
        mysql.connection.commit()

    return redirect('/admin/dashboard')
# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(__import__('os').environ.get('PORT', 5000)), debug=False)