#!/usr/bin/python3
import os, sys, traceback, atexit, gevent.pywsgi
from ctypes import cdll, byref, create_string_buffer

sys.path.append('/home/pi/Desktop/Pontaj Workspace/processes/helper_classes')

#from helper_classes.sheets_helper import Sheets
from helper_classes.email_helper import Email
from helper_classes.employee_helper import Employee
from helper_classes.fingerprint_helper import Fingerprint
from helper_classes.persistance import Persistance

from time import sleep
from datetime import datetime
from flask import Flask, request, render_template
from flask_httpauth import HTTPBasicAuth

#create pid file to track if running
pid = str(os.getpid())
pidfile = "/tmp/server.pid"

if os.path.isfile(pidfile):
    print("%s already exists, exiting" % pidfile)
    #sys.exit()

with open(pidfile,'w') as f:
        f.write(pid)

def on_crash():
        os.unlink(pidfile)

atexit.register(on_crash)

employee = Employee()
#sheetsClient = Sheets()
persist = Persistance()
email = Email()

app = Flask(__name__, 
template_folder='/home/pi/Desktop/Pontaj Workspace/templates', 
static_folder='/home/pi/Desktop/Pontaj Workspace/templates/static')


auth = HTTPBasicAuth()

outlog = ''

def exception_handler(ex):
    global outlog
    if type(ex).__name__ != 'BadRequestKeyError':
            outlog += traceback.format_exc()
            print(traceback.format_exc())

def clear_outlog():
    with open('/home/pi/Desktop/Pontaj Workspace/outlog.txt', 'wt') as outfile:
        outfile.write('')

@auth.verify_password
def verify_password(username, password):
    if username == 'Cristi' and password == 'Eurodac':
        return True
    else:
        return False

@app.route('/index.html')
@auth.login_required
def index():
    templateData = {
        'title': 'HELLO!'
    }

    return render_template('/index.html', **templateData)

@app.route('/setari.html', methods=('GET', 'POST'))
@auth.login_required
def setari():

    if request.method == 'POST':
        #edit working days
        try:
            new_working_days = []
            for i in range(1, 13):
                new_working_days.append(
                    (i, int(request.form[str(i)]))
                )
            persist.set_working_days(new_working_days)
            print('set working days')
        except:
            print('could not set working days')
        
        #add holiday
        try:
            holiday = request.form['holiday']
            date_string = request.form['date']
            coeff = float(request.form['coeff'])

            persist.add_holiday(holiday, date_string, coeff)
            print('added %s holiday on %s'%(holiday, date_string))
        except:
            pass

        #delete holiday
        try:
            index = int(request.form['delete'])

            persist.delete_holiday(index)
            print('deleted holiday at index %s'%index)
        except:
            pass

    working_days = persist.get_working_days()
    holiday_list = persist.get_holidays()

    return render_template('/setari.html', working_days=working_days, holiday_list = holiday_list)

@app.route('/angajati.html', methods=('GET', 'POST'))
@auth.login_required
def angajati():

    global outlog

    if request.method == 'POST':
        #enroll employee fingerprint
        try:
            uid = int(request.form['enroll'])
            print('starting enrollment')
            finger = Fingerprint()

            try:
                finger.delete_extra()
            except Exception as ex:
                print(traceback.format_exc())

            finger_id, outlog = finger.enroll()

            print(finger_id)

            tries = 0
            while finger_id == -1 or (not isinstance(finger_id, int)):

                finger_id, outlog = finger.enroll()

                tries += 1
                if tries >= 3:
                    break

            if finger_id != -1:
                print('enrolling with uid %s and finger_id %s'%(uid, finger_id))
                employee.enroll_fingerprint(uid, finger_id)
            else:
                print('could not enroll')
        except Exception as ex:
            exception_handler(ex)

        #delete employee
        try:
            uid = int(request.form['delete'])
            
            fingerprint = Fingerprint()
            fingerprint.delete(uid)
            employee.delete(uid)
            persist.delete_employee(uid)
            #fingerprint.delete_all()
        except Exception as ex:
            exception_handler(ex)

        #add employee
        try:
            name = request.form['name']
            starting = request.form['starting']
            lunch = request.form['lunch']

            if not (name == '' or starting == '' or lunch == ''):
                uid = employee.add(name, starting, lunch)
                persist.add_employee(uid, name)

        except Exception as ex:
            exception_handler(ex)
        
        #modify employee
        try:
            uid = int(request.form['uid'])
            new_starting = request.form['new_starting']
            new_lunch = request.form['new_lunch']

            employee.set_employee_prefs(uid, new_starting, new_lunch)
        except Exception as ex:
            exception_handler(ex)
        
        #modify attendance
        try:
            uid = int(request.form['uid'])
            date_string = request.form['date']
            hours = float(request.form['hours'])

            persist.edit_att(False, uid, date_string, 0, hours)
        except Exception as ex:
            exception_handler(ex)

        #request data
        try:
            uid = int(request.form['uid'])
            month = int(request.form['month'])
            name = employee.get_name(uid)

            if month == -1:
                #persist.clear_att()
                pass
            
            else:

                print('received request for employee %s and month %s...'%(name, month))
                persist.get_data(uid, month)

                #persist.get_summary()
                
                sent = False
                while not sent:
                    print('sending email...')
                    sent = email.send(
                        'Angajat: %s, Luna: %s'%(name, month),
                        'Salut Cristi,\n\nRaportul este atasat si poate fi deschis in excel.\n\nSloppy Toppy',
                        '/home/pi/Desktop/Pontaj Workspace/persistance/request_temp/%s.csv'%(name + ' ' + str(month))
                    )
                    if not sent:
                        sleep(2)  
        except Exception as ex:
            exception_handler(ex)
        
        #request summary
        try:
            request.form['summary']

            clear_outlog()

            try:
                summary = persist.get_summary()
                persist.print_summary(summary)

                year = datetime.now().year

                sent = False
                while not sent:
                    print('sending email...')
                    sent = email.send(
                        'Summar for: %s'%str(year),
                        'Salut Cristi,\n\nRaportul este atasat si poate fi deschis in excel.\n\nSloppy Toppy',
                        '/home/pi/Desktop/Pontaj Workspace/persistance/request_temp/%s.csv'%('summary ' + str(year))
                    )
                    if not sent:
                        sleep(2)  

            except Exception as ex:
                exception_handler(ex)
        except Exception as ex:
            exception_handler(ex)

        #generate data
        try:
            request.form['generate_data']
            num_employees = request.form['num_employees']
            try:
                persist.random_att(int(num_employees))
            except Exception as ex:
                print(traceback.format_exc())
                exception_handler(ex)
        except Exception as ex:
            exception_handler(ex)
        
        #delete data
        try:
            request.form['delete_data']
            try:
                persist.clear_att()
            except Exception as ex:
                print(traceback.format_exc())
                exception_handler(ex)
        except Exception as ex:
            exception_handler(ex)
        
    employee_list = employee.query()

    return render_template('/angajati.html', employee_list=employee_list, outlog=outlog)

@app.route('/popups/numardezilelucratoare.html')
def numardezilelucratoare():
    return render_template('/popups/numardezilelucratoare.html')

@app.route('/popups/ziledesarbatoare.html')
def ziledesarbatoare():
    return render_template('/popups/ziledesarbatoare.html')

@app.route('/popups/adaugazidesarbatoare.html')
def adaugazidesarbatoare():
    return render_template('/popups/adaugazidesarbatoare.html')

@app.route('/popups/listadeangajati.html')
def listadeangajati():
    return render_template('/popups/listadeangajati.html')

@app.route('/popups/introduceunnouangajat.html')
def introduceunnouangajat():
    return render_template('/popups/introduceunnouangajat.html')

@app.route('/popups/modificaunangajat.html')
def modificaunangajat():
    return render_template('/popups/modificaunangajat.html')

@app.route('/popups/solicitaredate.html')
def solicitaredate():
    return render_template('/popups/solicitaredate.html')

@app.route('/popups/modificarepontaj.html')
def modificarepontaj():
    return render_template('/popups/modificarepontaj.html')

@app.route('/popups/solicitaresumar.html')
def solicitaresumar():
    return render_template('/popups/solicitaresumar.html')

@app.route('/popups/programoutput.html')
def programoutput():
    return render_template('/popups/programoutput.html')


def run():
    try:
        print('running server')
        app.run(debug=True, port=8080, host='0.0.0.0')
    except Exception as ex:
        exception_handler(ex)
        print('failed to initialize')
        

run()
