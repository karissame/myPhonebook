import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import mysql.connector


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
#define connection
app = Flask("MyApp")
app.config['UPLOAD_FOLDER'] = "/Users/DSS-Mac/htdocs/myPhonebook/static/profilepics/"
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
home_dir = os.path.join(app.config['UPLOAD_FOLDER'],"")

conn = mysql.connector.connect(
         user='root',
         password='',
         host='127.0.0.1',
         database='demo')
#opens connection
cur = conn.cursor()
activeTab={"home":"","addEntries":"","updateEntry":""}

def allowed_file(filename):
    return '.' in filename and \
           filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
def listings():
    query = ("SELECT id,name,email,phone,photo_ext FROM phonebook")
    cur.execute(query)
    l = []
    for each in cur.fetchall():

        l.append(list(each))
    print l
    for i in l:
        print i
        if i[4]:
            print i[0]
            print i[4]
            i[4]= str(i[0]) + "." +i[4]
            print i[4]
        else:
            i[4]= "placeholder.jpg"
    setActiveTab("home")
    return render_template("listings.html", contact_list=l, title="My Phonebook",activeTab=activeTab)

@app.route("/update_entry")
def updateEntry(methods = ['GET']):
    id = request.args.get('id')
    query = ("SELECT id,name,email,phone,photo_ext FROM phonebook WHERE id = '%s'" % id)
    cur.execute(query)
    list = cur.fetchone()
    setActiveTab("updateEntry")
    return render_template("update_entry.html", phonebook=list, title="My Phonebook",activeTab=activeTab)

#set all active tab dictionaries value to "" then make the indicated tab from the flask route function active. This make class="active" for css styling dynamically.
def setActiveTab(tabName):
    global activeTab
    for tab in activeTab:
        activeTab[tab] = ""
    if activeTab.has_key(tabName):
        activeTab[tabName] = "active"
    print activeTab

@app.route("/new_entry")
def new_entry():
    setActiveTab("addEntries")
    return render_template("new_entry.html", title="My Phonebook",activeTab=activeTab)

@app.route("/submit_new_entry", methods=['POST'])
def submit_new_student():
    setActiveTab("addEntries")
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print filename
            ext = filename.lower().rsplit('.', 1)[1]
        else:
            ext = ""
        print ext
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        query = "insert into phonebook (name,email,phone,photo_ext) values ('%s','%s','%s','%s')" % (name,email,phone,ext)
        cur.execute(query)
        conn.commit()
        lastId=cur.lastrowid
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(lastId)+"."+ext))

    # return render_template("submit_new_entry.html", name=name,email=email,phone=phone, activeTab=activeTab)
    return redirect("/")

@app.route("/submit_update_contact", methods=['POST'])
def submit_update_contact():
    id = request.form.get('id')
    setActiveTab("updateEntry")
    name=request.form.get('name')
    email=request.form.get('email')
    phone=request.form.get('phone')
    if request.form['submit'] == 'update':
        query = "UPDATE phonebook SET name = '%s', email = '%s', phone = '%s' WHERE id = '%s'" % (name,email,phone, id)
        cur.execute(query)
        conn.commit()
    if request.form['submit'] == 'delete':
        query = "DELETE FROM phonebook WHERE id = '%s'" % id
        cur.execute(query)
        conn.commit()
    return redirect("/")




if __name__=="__main__":
    app.run(debug=True)

cur.close()
conn.close()
