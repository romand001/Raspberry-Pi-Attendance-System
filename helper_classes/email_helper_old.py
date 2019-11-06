import smtplib, json
from os.path import basename

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

class Email:

    def __init__(self):
        with open('/home/pi/Desktop/Pontaj Workspace/settings/EmailSettings.json') as f:
            fil = json.load(f)

        self.address = fil['address']
        self.password = fil['password']
        self.recipients = fil['recipients']

    def send(self, subject, body, fil):

        msg = MIMEMultipart()
        msg['From'] = self.address
        msg['To'] = self.recipients[0]
        msg['Date'] = formatdate(localtime = True)
        msg['Subject'] = subject
        msg.attach(MIMEText(body))

        #print('created message')

        part = MIMEBase('application', "octet-stream")

        #print(fil)
        reader = open(fil, "rb").read()

        #print('opened file')
        part.set_payload(reader)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'%fil[59:])
        msg.attach(part)

        #print('attached file')


        try:
            smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp.login(self.address, self.password)
            smtp.sendmail(from_addr=self.address, to_addrs=self.recipients[0], msg=msg.as_string())
            smtp.close()
            print('email sent succesfully!')
            return True
        except:
            print('failed to send email')
            return False
