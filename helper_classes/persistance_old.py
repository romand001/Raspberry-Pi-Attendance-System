import pickle, csv, json
from pprint import pprint
from random import randint, randrange
from math import floor
from decimal import Decimal
from datetime import datetime, date, timedelta
from employee_helper import Employee

class Attendance():

    def __init__(self, uid):

        employee = Employee()

        self.uid = uid
        self.date = datetime.now().date()
        self.month = self.date.month
        

        self.starting = employee.get_starting(uid)
        self.lunch = employee.get_lunch(uid)

        self.arrival = -1
        self.departure = -1
    
    def __str__(self):
        string_rep = 'uid: %s, date: %s, starting: %s, lunch: %s\narrival: %s, departure: %s'%(
                self.uid,
                self.date,
                self.starting,
                self.lunch,
                self.arrival,
                self.departure
            )
        return string_rep

class Persistance():

    def __init__(self):
        self.path = '/home/pi/Desktop/Pontaj Workspace/persistance/attendance.pkl'
        self.settings_path = '/home/pi/Desktop/Pontaj Workspace/settings/WorkSettings.json'
        self.holidays_path = '/home/pi/Desktop/Pontaj Workspace/settings/HolidaySettings.pkl'

        self.TWOPLACES = Decimal(10) ** -2
        self.THREEPLACES = Decimal(10) ** -3

        try:
            emp_file = open(self.path, 'rb')
            pickle.load(emp_file)
            emp_file.close()
        except:
            emp_file = open(self.path, 'wb')
            pickle.dump([], emp_file)
            emp_file.close()
    
    def add_employee(self, uid, name):
        #check attendance file integrity
        try:
            emp_file = open(self.path, 'rb')
            emp_list = pickle.load(emp_file)
            emp_file.close()
        except:
            print('ERROR: failed to load, creating new data structure...')
            emp_file = open(self.path, 'wb')
            pickle.dump([], emp_file)
            emp_file.close()
            emp_list = []

        new_emp = {
            'uid': uid,
            'name': name,
            'attendance': []
        }
        emp_list.append(new_emp)

        att_file = open(self.path, 'wb')
        pickle.dump(emp_list, att_file)
        att_file.close()
    
    def delete_employee(self, uid):
        att_file = open(self.path, 'rb')
        emp_list = pickle.load(att_file)
        att_file.close()

        for emp in emp_list:
            if emp['uid'] == uid:
                emp_list.remove(emp)
        
        att_file = open(self.path, 'wb')
        pickle.dump(emp_list, att_file)
        att_file.close

    def arrival(self, uid):

        #check attendance file integrity
        try:
            emp_file = open(self.path, 'rb')
            emp_list = pickle.load(emp_file)
            emp_file.close()
        except:
            print('ERROR: failed to load, creating new data structure...')
            emp_file = open(self.path, 'wb')
            pickle.dump([], emp_file)
            emp_file.close()
        
        #check for error uid
        if uid == -1:
            print('ERROR: no uid')
            return -1
        
        #check for new employee
        found = False
        for emp in emp_list:
            if emp['uid'] == uid:
                found = True
        
        if not found:
            employee = Employee()
            print('employee not found in attendance file, adding...')
            self.add_employee(uid, employee.get_name(uid))

        emp_file = open(self.path, 'rb')
        emp_list = pickle.load(emp_file)
        emp_file.close()
        

        for emp in emp_list:
            if emp['uid'] == uid:

                for att in emp['attendance']:
                    if att.date == datetime.now().date():
                        print("ERROR: today's entry already exists")
                        return -2

                print('creating new arrival entry...')
                new_att = Attendance(uid)
                new_att.arrival = datetime.now()
                emp['attendance'].append(new_att)
                break
        
        
        #print(emp_list)

        att_file = open(self.path, 'wb')
        pickle.dump(emp_list, att_file)
        att_file.close()
        print('loaded arrival entry')

    def departure(self, uid):
        att_file = open(self.path, 'rb')
        emp_list = pickle.load(att_file)
        att_file.close()

        if uid == -1:
            return -1

        for emp in emp_list:
            if emp['uid'] == uid:
                
                existing = False
                for att in emp['attendance']:
                    if att.date == datetime.now().date():
                        att.departure = datetime.now()
                        existing = True
                        break

                if not existing:
                    new_att = Attendance(uid)
                    new_att.departure = datetime.now()
                    emp['attendance'].append(new_att)

                break
                    

        att_file = open(self.path, 'wb')
        pickle.dump(emp_list, att_file)
        att_file.close()

    def get_data(self, uid, month):

        print('retrieving data...')

        #get holidays
        att_file = open(self.holidays_path, 'rb')
        holiday_list = pickle.load(att_file)
        att_file.close()

        holiday_dates = []
        holiday_coeffs = []
        for holiday in holiday_list:
            holiday_dates.append(holiday['date'])
            holiday_coeffs.append(holiday['coefficient'])

        #open attendance file
        att_file = open(self.path, 'rb')
        emp_list = pickle.load(att_file)
        att_file.close()

        #create csv rows
        rows = [['Data', 'Incepere Program', 'Pauza Masa', 'Ora Ajuns', 'Ora Plecat', 'Factor Sarbatoare']]
        for emp in emp_list:
            if int(emp['uid']) == uid:
                
                #iterate over attendance of chosen month
                for att in emp['attendance']:
                    if att.month == month:
                        
                        #set payment coefficient
                        factor = 0
                        if att.date in holiday_dates:
                            factor = holiday_coeffs[holiday_dates.index(att.date)]

                        #add attendance row
                        try:
                            if att.arrival != -1 and att.departure != -1:
                                #print('entry types: %s, %s'%(type(att.arrival), type(att.departure)))
                                rows.append(
                                    [
                                        att.date, 
                                        str(att.starting.time())[:5],
                                        str(att.lunch.time())[:5],
                                        str(att.arrival.time())[:5],
                                        str(att.departure.time())[:5],
                                        factor
                                    ]
                                )
                            else:
                                print('no arrival or departure entry')
                        except:
                            print('something went wrong with:')
                            print('month: %s, rows: \n%s'%(att.month, rows))

                #write all rows to file
                print('writing to file...')
                with open('/home/pi/Desktop/Pontaj Workspace/persistance/request_temp/%s.csv'%(emp['name'] + ' ' + str(month)), 
                'w',
                newline='') as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerows(rows)
                    print('finished writing temp file')
                break
        
        return rows

    def print_att(self):

        att_file = open(self.path, 'rb')
        emp_list = pickle.load(att_file)
        att_file.close()

        print('\nAttendance Records:\n---------------------')
        for emp in emp_list:
            print('name: %s\nattendance:'%emp['name'])
            for att in emp['attendance']:
                try:
                    print(att)
                except:
                    print('could not print att object')
                    pass
            print('\n')

    def get_summary(self):

        print('getting summary...')

        #load working days file and calculate hours
        with open(self.settings_path, 'rt', encoding='utf-8') as outfile:
            work_days = json.load(outfile)
        
        work_hours = []
        for month in range(1,13):
            work_hours.append(
                (month, int(work_days[str(month)]) * 8)
                )
        
        #get holidays
        att_file = open(self.holidays_path, 'rb')
        holiday_list = pickle.load(att_file)
        att_file.close()

        holiday_dates = []
        holiday_coeffs = []
        for holiday in holiday_list:
            holiday_dates.append(holiday['date'])
            holiday_coeffs.append(holiday['coefficient'])

        #load attendance file
        att_file = open(self.path, 'rb')
        emp_list = pickle.load(att_file)
        att_file.close()

        employee = Employee()
        summary = []

        #iterate over employees to get work hours and skipped days
        for emp in emp_list:

            start = employee.get_starting(emp['uid'])
            lunch = employee.get_lunch(emp['uid'])

            #calculate finishing time
            finish = start + timedelta(hours=lunch.hour+8, minutes=lunch.minute)

            #data structure for each employee summary
            emp_summary = {
                'uid': emp['uid'],
                'name': emp['name'],
                'months': [],
                'average_worked': 0,
                'total_skipped': 0
            }

            for i in range(1, 13):
                emp_summary['months'].append(
                    {
                        'month': i,
                        'hours': 0,
                        'percentage': 0,
                        'skipped': 0
                    }
                )

            
            #iterate over each day of employee to add work hours and skipped days
            i = 1
            for att in emp['attendance']:

                if att.arrival != -1 and att.departure != -1 and (not att.date.weekday() in (5, 6)):

                    #calculate time worked
                    if att.date in holiday_dates:
                        coeff = holiday_coeffs[holiday_dates.index(att.date)]
                        hours_worked = 8 + (att.departure - att.arrival).seconds * coeff / 3600
                    else:
                        hours_worked = (att.departure - att.arrival).seconds / 3600 - lunch.hour - lunch.minute / 60
                    
                    #count skips this day
                    skipped_today = 0

                    #check for late arrival
                    if (att.arrival.hour >= start.hour and att.arrival.minute > start.minute) or att.arrival == -1:
                        skipped_today += 1
                    
                    #check for early departure
                    if (att.departure.hour < finish.hour or 
                    (att.departure.hour <= finish.hour and att.departure.minute < finish.minute)) or att.departure == -1:
                        skipped_today += 1
            
                    #check which month to add hours and skipped days to
                    for month in emp_summary['months']:
                        if month['month'] == att.month:
                            i += 1
                            month['hours'] += hours_worked
                            month['skipped'] += skipped_today


            #calculate percentage after adding all hours
            percentage_sum = 0
            skipped_sum = 0
            for month in emp_summary['months']:
                ideal = work_hours[month['month'] - 1][1]
                month['percentage'] = Decimal(str( (month['hours'] / ideal) * 100 )).quantize(self.THREEPLACES)

                percentage_sum += month['percentage']
                skipped_sum += month['skipped']
            
            emp_summary['average_worked'] = Decimal(str( percentage_sum / 12 )).quantize(self.THREEPLACES)
            emp_summary['total_skipped'] = skipped_sum

            #append employee to summary list after adding all data
            summary.append(emp_summary)


        emp_list = employee.query()
        #create and add csv rows
        rows = []
        for i in range(30):
            row = []

            for j in range(len(emp_list) + 2):
                row.append('')

            rows.append(row)
        
        #populate rows
        month_names = (
            'Ianuarie',
            'Februarie',
            'Martie',
            'Aprilie',
            'Mai',
            'Iunie',
            'Iulie',
            'August',
            'Septembrie',
            'Octombrie',
            'Noiembrie',
            'Decembrie'
        )

        #Average and Total cell names
        rows[14][0] = 'Average'
        rows[28][0] = 'Total'

        #iterate over employees by index number
        for i in range(len(emp_list)):

            #populate names header
            rows[0][i + 1] = summary[i]['name']

            #iterate over months by index number
            for j in range(1, 13):
                
                #populate month column
                if rows[j + 1][0] == '':
                    rows[j + 1][0] = month_names[j - 1]
                    rows[j + 15][0] = month_names[j - 1]
                
                #populate monthly cells
                rows[j + 1][i + 1] = str(summary[i]['months'][j - 1]['percentage']) + '%'
                rows[j + 15][i + 1] = summary[i]['months'][j - 1]['skipped']
            
            #populate averages and totals
            rows[14][i + 1] = str(summary[i]['average_worked']) + '%'
            rows[28][i + 1] = summary[i]['total_skipped']

        #write rows to csv
        print('writing to file...')
        with open('/home/pi/Desktop/Pontaj Workspace/persistance/request_temp/summary %s.csv'%datetime.now().year, 
        'w',
        newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerows(rows)
            print('finished writing temp file')

        return summary
                    
    def print_summary(self, summary):

        print('Attendance Summary:\n-------------------')

        for emp in summary:
            print('\n%s:\n---------------------------'%emp['name'])
            for month in emp['months']:
                print('Month: %s\tPercentage Worked: %s\tSkipped: %s'%(
                    month['month'], month['percentage'], month['skipped']))

    def edit_att(self, gen, uid, date_string, arr_shift, dec_hours):

        hours, minutes = self.htohm(dec_hours)

        #try to parse date string to datetime object
        try:
            date_obj = datetime.strptime(date_string, '%Y/%m/%d').date()
        except:
            print('could not parse date string')
            return -1
        
        #check attendance file integrity
        try:
            emp_file = open(self.path, 'rb')
            emp_list = pickle.load(emp_file)
            emp_file.close()
        except:
            print('ERROR: failed to load, creating new data structure...')
            emp_file = open(self.path, 'wb')
            pickle.dump([], emp_file)
            emp_file.close()
            return -1
        
        #find employee by uid
        for emp in emp_list:
            if emp['uid'] == uid:
                #find attendance date by datetime.date
                found = False
                for att in emp['attendance']:
                    if att.date == date_obj:
                        found = True
                        #set arrival and departure by hours
                        att.arrival = att.starting

                        att.departure = att.arrival + timedelta(hours=hours, minutes=minutes) + timedelta(
                            hours=att.lunch.hour,
                            minutes=att.lunch.minute
                            )
                        
                        break

                if not found:

                    new_att = Attendance(uid)
                    new_att.date = date_obj
                    new_att.month = date_obj.month

                    if gen:
                        if arr_shift < 0:
                            new_att.arrival = new_att.starting - timedelta(minutes=abs(arr_shift))
                        else:
                            new_att.arrival = new_att.starting + timedelta(minutes=arr_shift) 

                        new_att.departure = new_att.arrival + timedelta(hours=hours, minutes=minutes) + timedelta(
                                hours=new_att.lunch.hour,
                                minutes=new_att.lunch.minute
                                )
                    else:
                        new_att.arrival = new_att.starting
                        new_att.departure = new_att.arrival + timedelta(hours=hours, minutes=minutes) + timedelta(
                                hours=new_att.lunch.hour,
                                minutes=new_att.lunch.minute
                                )
                    emp['attendance'].append(new_att)
                    #print('added new attendance entry to employee record')

                break
    
        #dump records to file
        att_file = open(self.path, 'wb')
        pickle.dump(emp_list, att_file)
        att_file.close()
        #print('successfully modified attendance')

    def clear_att(self):
        print('clearing attendance file...')

        att_file = open(self.path, 'wb')
        pickle.dump([], att_file)
        att_file.close()

        print('finished clearing attendance file')

    def random_att(self, num_employees):

        self.clear_att()

        employee = Employee()
        for uid in range(40):
            employee.delete(uid)

        starting_strings = (
            '7:00',
            '7:30',
            '9:00',
            '10:00'
        )

        lunch_strings = (
            '0:30',
            '0:45',
            '1:00'
        )

        employee = Employee()

        for emp in range(1, num_employees + 1):

            employee.add(
                'Angajat %s'%emp,
                starting_strings[randint(0, 3)],
                lunch_strings[randint(0, 2)]
            )
            self.add_employee(emp, 'Angajat %s'%emp)

            for month in range(1,13):
                print(
                    'generating month: %s, for employee: %s'%(
                        month, emp
                    )
                )
                for day in range(1,31):
                    date_string = '2019/%s/%s'%(month, day)
                    #try to parse date string to datetime object
                    try:
                        date_obj = datetime.strptime(date_string, '%Y/%m/%d').date()

                        if not date_obj.weekday() in (5, 6):
                            self.edit_att(
                                True,
                                emp,
                                date_string,
                                randrange(-15, 15),
                                randrange(78, 82) / 10
                            )
                    except:
                        print('could not parse date string')

    def htohm(self, dec_hours):
        hours = floor(dec_hours)
        minutes = floor( (dec_hours-hours) * 60 )
        return hours, minutes

    def get_working_days(self):

        with open(self.settings_path, 'rt', encoding='utf-8') as outfile:
            work_days = json.load(outfile)
        
        work_days_list = []
        for month, days in work_days.items():
            work_days_list.append(
                (int(month), int(days))
            )
        
        return work_days_list

    def set_working_days(self, working_days):

        working_days_dict = {}

        for month in working_days:
            working_days_dict[str(month[0])] = str(month[1])

        with open(self.settings_path, 'w') as outfile:
            json.dump(working_days_dict, outfile)

    def get_holidays(self):
        #check holidays file integrity
        try:
            hol_file = open(self.holidays_path, 'rb')
            hol_list = pickle.load(hol_file)
            hol_file.close()
        except:
            print('ERROR: failed to load, creating new data structure...')
            hol_file = open(self.holidays_path, 'wb')
            pickle.dump([], hol_file)
            hol_file.close()
            hol_list = []
        
        return hol_list
    
    def add_holiday(self, holiday, date_string, coeff):
        #try to parse date string to datetime object
        try:
            date_obj = datetime.strptime(date_string, '%Y/%m/%d').date()
        except:
            print('could not parse date string')
            return -1
        
        #check holidays file integrity
        try:
            hol_file = open(self.holidays_path, 'rb')
            hol_list = pickle.load(hol_file)
            hol_file.close()
        except:
            print('ERROR: failed to load, creating new data structure...')
            hol_file = open(self.holidays_path, 'wb')
            pickle.dump([], hol_file)
            hol_file.close()
            hol_list = []
        
        hol_list.append(
            {
                'holiday': holiday,
                'date': date_obj,
                'coefficient': coeff
            }
        )

        hol_file = open(self.holidays_path, 'wb')
        pickle.dump(hol_list, hol_file)
        hol_file.close()
        
    def delete_holiday(self, index):
        #check holidays file integrity
        try:
            hol_file = open(self.holidays_path, 'rb')
            hol_list = pickle.load(hol_file)
            hol_file.close()
        except:
            print('ERROR: failed to load, creating new data structure...')
            hol_file = open(self.holidays_path, 'wb')
            pickle.dump([], hol_file)
            hol_file.close()
            hol_list = []
        
        del hol_list[int(index)]

        hol_file = open(self.holidays_path, 'wb')
        pickle.dump(hol_list, hol_file)
        hol_file.close()
