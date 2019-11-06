from helper_classes.employee_helper import Employee
import gspread, pprint, time, datetime
from oauth2client.service_account import ServiceAccountCredentials

class Sheets:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            "/home/pi/Desktop/Pontaj Workspace/helper_classes/Sistem Pontaj-2131cbe042a0.json", scope)
        client = gspread.authorize(self.creds)

        self.sheet1 = client.open('Pontaj Test').sheet1
    
    def authenticate(self):
        client = gspread.authorize(self.creds)
        self.sheet1 = client.open('Pontaj Test').sheet1

    def read(self):
        self.authenticate()
        data = self.sheet1.get_all_records()
        pp = pprint.PrettyPrinter()
        pp.pprint(data)
        return data

    def write(self, uid, action):
        self.authenticate()
        employeeClient = Employee()

        employee_list = employeeClient.query()

        num_employees = len(employee_list)
        cell_list1  = self.sheet1.range('A2:A%s'%(num_employees + 1))
        cell_list2 = self.sheet1.range('B2:B%s'%(num_employees + 1))
        cell_list3 = self.sheet1.range('C2:C%s'%(num_employees + 1))


        for i in range(num_employees):
            cell_list1[i].value = employee_list[i]['name']

        if action != 'null':

            index = -1
            for employee in employee_list:
                #print('%s %s'%(employee[0], uid))
                if int(employee['uid']) == uid:
                    index = employee_list.index(employee)
            
            if index == -1:
                return -1

            time_string = str(datetime.datetime.now().time())[:8]

            if action == 'arrive':
                cell_list2[index].value = time_string
            elif action == 'leave':
                cell_list3[index].value = time_string
            elif action == 'delete':
                cell_list2[index].value = ''
                cell_list3[index].value = ''


        clear_cells_list = self.sheet1.range('A2:C40')
        for cell in clear_cells_list:
            cell.value = ''

        finished_writing = False
        while not finished_writing:
            try:
                self.sheet1.update_cells(clear_cells_list)
                self.sheet1.update_cells(cell_list1)
                self.sheet1.update_cells(cell_list2)
                self.sheet1.update_cells(cell_list3)
                finished_writing = True
            except:
                print('API timed out, waiting 100 seconds...')
                time.sleep(100)