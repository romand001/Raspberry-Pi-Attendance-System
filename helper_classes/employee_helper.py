import pickle
from datetime import datetime
import json

class Employee:

    def __init__(self):
        self.path = '/home/pi/Desktop/Pontaj Workspace/settings/Angajati.json'
        self.employee_list = []

    def add(self, name, starting_string, lunch_string):

        #try to parse starting time string to datetime object
        try:
            starting = datetime.strptime(starting_string, '%-H:%M')
        except:
            try:
                starting = datetime.strptime(starting_string, '%H:%M')
            except:
                print("couldn't parse starting time")
                return -1

        #try to parse lunch break string to datetime object
        try:
            lunch = datetime.strptime(lunch_string, '%-H:%M')
        except:
            try:
                lunch = datetime.strptime(lunch_string, '%H:%M')
            except:
                print("couldn't parse lunch time")
                return -1

        try:
            emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
            emp_list = pickle.load(emp_file)
            emp_file.close()
        except:
            emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
            pickle.dump([], emp_file)
            emp_file.close()

        max_uid = 0
        for emp in emp_list:
            uid = emp['uid']
            if uid > max_uid:
                max_uid = uid

        new_emp = {
            'uid': max_uid + 1,
            'name': name,
            'starting': starting,
            'lunch': lunch,
            'finger_ids': []
        }

        emp_list.append(new_emp)

        emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'wb')
        pickle.dump(emp_list, emp_file)
        emp_file.close()

        return max_uid + 1

        # with open(self.path, 'rt', encoding='utf-8') as outfile:
        #     data = json.load(outfile)



        # data.append(
        #     {
        #         "uid": str(max_uid + 1),
        #         "name": name,
        #         "starting": starting,
        #         "lunch": lunch,
        #         "finger_id": -1
        #     }
        # )

        # with open(self.path, 'wt', encoding='utf-8') as outfile:
        #     json.dump(data, outfile, ensure_ascii=False, indent=2)
        #     #print('New JSON:\n' + str(data))

    def delete(self, uid):

        emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
        emp_list = pickle.load(emp_file)
        emp_file.close()

        for emp in emp_list:
            if emp['uid'] == uid:
                print('removed from employee list')
                emp_list.remove(emp)

        emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'wb')
        pickle.dump(emp_list, emp_file)
        emp_file.close()

        # with open(self.path, 'rt', encoding='utf-8') as outfile:
        #     data = json.load(outfile)

        # to_delete = -1
        # for employee in data:
        #     if employee['uid'] == str(uid):
        #         to_delete = employee
        #         break

        # data.remove(to_delete)

        # with open(self.path, 'wt', encoding='utf-8') as outfile:
        #     json.dump(data, outfile, ensure_ascii=False, indent=2)

    def query(self):
        print('querying employee list...')

        try:
            emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
            emp_list = pickle.load(emp_file)
            emp_file.close()
        except:
            emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
            pickle.dump([], emp_file)
            emp_file.close()

        return emp_list

    def get_name(self, uid):
        try:
            emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
            emp_list = pickle.load(emp_file)
            emp_file.close()
        except:
            emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
            pickle.dump([], emp_file)
            emp_file.close()
        
        for emp in emp_list:
            if emp['uid'] == uid:
                return emp['name']
        
        return ''

    def get_starting(self, uid):

        emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
        emp_list = pickle.load(emp_file)
        emp_file.close()

        for emp in emp_list:
            if emp['uid'] == uid:
                return emp['starting']

        # with open(self.path, 'rt', encoding='utf-8') as outfile:
        #     data = json.load(outfile)

        # for emp in data:
        #     if int(emp['uid']) == int(uid):
        #         return emp['starting']

        # return -1

    def get_lunch(self, uid):

        emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
        emp_list = pickle.load(emp_file)
        emp_file.close()

        for emp in emp_list:
            if emp['uid'] == uid:
                return emp['lunch']

        # with open(self.path, 'rt', encoding='utf-8') as outfile:
        #     data = json.load(outfile)

        # for emp in data:
        #     if int(emp['uid']) == int(uid):
        #         return emp['lunch']

        # return -1

    def set_employee_prefs(self, uid, starting_string, lunch_string):
        #try to parse starting time string to datetime object
        try:
            starting = datetime.strptime(starting_string, '%-H:%M')
        except:
            try:
                starting = datetime.strptime(starting_string, '%H:%M')
            except:
                print("couldn't parse starting time")
                return -1

        #try to parse lunch break string to datetime object
        try:
            lunch = datetime.strptime(lunch_string, '%-H:%M')
        except:
            try:
                lunch = datetime.strptime(lunch_string, '%H:%M')
            except:
                print("couldn't parse lunch time")
                return -1

        try:
            emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
            emp_list = pickle.load(emp_file)
            emp_file.close()
        except:
            emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
            pickle.dump([], emp_file)
            emp_file.close()

        for emp in emp_list:
            if emp['uid'] == uid:
                emp['starting'] = starting
                emp['lunch'] = lunch
                print('successfully changed prefs\n',
                    'starting: %s, lunch: %s'%(
                        starting, lunch
                    ))
        
        emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'wb')
        pickle.dump(emp_list, emp_file)
        emp_file.close()

    def enroll_fingerprint(self, uid, finger_id):

        emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
        emp_list = pickle.load(emp_file)
        emp_file.close()

        for emp in emp_list:
            if emp['uid'] == uid:
                emp['finger_ids'].append(finger_id)
                emp['finger_ids'] = list(set(emp['finger_ids']))

        emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'wb')
        pickle.dump(emp_list, emp_file)
        emp_file.close()

        # with open(self.path, 'rt', encoding='utf-8') as outfile:
        #     data = json.load(outfile)

        # for employee in data:
        #     #print(employee['uid'])
        #     if int(employee['uid']) == int(uid):
        #         employee['finger_id'] = str(finger_id)
        #         print('enrolled id %s to employee named %s'%(finger_id, employee['name']))

        # with open(self.path, 'wt', encoding='utf-8') as outfile:
        #     json.dump(data, outfile, ensure_ascii=False, indent=2)

    def remove_fingerprint(self, uid):

        emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
        emp_list = pickle.load(emp_file)
        emp_file.close()

        for emp in emp_list:
            if emp['uid'] == uid:
                emp['finger_ids'] = []

        emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'wb')
        pickle.dump(emp_list, emp_file)
        emp_file.close()

        # for emp in self.query():
        #     if int(emp['uid']) == uid:
        #         emp["finger_id"] = "-1"

    def utof(self, uid):

        if uid == -1:
            print('invalid uid')
            return -1

        emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
        emp_list = pickle.load(emp_file)
        emp_file.close()

        for emp in emp_list:
            #print(emp)
            if emp['uid'] == int(uid):
                return emp['finger_ids']
        
        print('could not find employee')
        return -1

        # with open(self.path, 'rt', encoding='utf-8') as outfile:
        #     data = json.load(outfile)

        # for employee in data:
        #     if employee['uid'] == uid:
        #         return employee['finger_id']

    def ftou(self, finger_id):

        if finger_id == -1:
            return -1

        emp_file = open(r'/home/pi/Desktop/Pontaj Workspace/persistance/employees.pkl', 'rb')
        emp_list = pickle.load(emp_file)
        emp_file.close()

        for emp in emp_list:
            if finger_id in emp['finger_ids']:
                return int(emp['uid'])

        # with open(self.path, 'rt', encoding='utf-8') as outfile:
        #     data = json.load(outfile)

        # if finger_id == -1:
        #     return -1

        # for employee in data:
        #     if int(employee['finger_id']) == finger_id:
        #         return int(employee['uid'])

