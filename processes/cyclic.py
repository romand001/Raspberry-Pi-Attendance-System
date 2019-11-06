#!/usr/bin/python3
print('importing crucial dependancies...')
import sys, os, atexit, time

print('adding helper classes directory to PATH...')
sys.path.append('/home/pi/Desktop/Pontaj Workspace/processes/helper_classes')

print('importing helper classes...')
from helper_classes.fingerprint_helper import Fingerprint
#from helper_classes.sheets_helper import Sheets
from helper_classes.employee_helper import Employee
from helper_classes.persistance import Persistance

print('importing buzzer library...')
from gpiozero import Button, Buzzer, TonalBuzzer
from gpiozero.tones import Tone

print('importing LCD library...')
import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#create pid file to track if running
pid = str(os.getpid())
pidfile = "/tmp/cyclic.pid"

if os.path.isfile(pidfile):
    print("%s already exists, exiting" % pidfile)
    #sys.exit()

with open(pidfile,'w') as f:
        f.write(pid)

def on_crash():
        os.unlink(pidfile)

atexit.register(on_crash)



print('\nrunning cyclic script\n-------------------')

fingerprint = Fingerprint()
employee = Employee()
#sheet = Sheets()
persistance = Persistance()

btn_arrive = Button(2)
btn_leave = Button(3)

buzzer = TonalBuzzer(18)

# Raspberry Pi hardware SPI config:
DC = 23
RST = 24
SPI_PORT = 0
SPI_DEVICE = 0

# Hardware SPI usage:
disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))

# Software SPI usage (defaults to bit-bang SPI interface):
#disp = LCD.PCD8544(DC, RST, SCLK, DIN, CS)

# Initialize library.
disp.begin(contrast=60)

def beep():
        buzzer.play(buzzer.max_tone)
        time.sleep(0.2)
        buzzer.stop()

def success_beeps():
        buzzer.play(buzzer.max_tone)
        time.sleep(0.2)
        buzzer.stop()
        time.sleep(0.2)

        buzzer.play(buzzer.max_tone)
        time.sleep(0.2)
        buzzer.stop()
        time.sleep(0.2)

        buzzer.play(buzzer.max_tone)
        time.sleep(0.2)
        buzzer.stop()

def failure_beeps():
        buzzer.play(buzzer.mid_tone)
        time.sleep(0.5)
        buzzer.stop()

def print_lcd(LCD, text):
        # Clear display.
        disp.clear()
        disp.display()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a white filled box to clear the image.
        draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)

        # Load default font.
        font = ImageFont.load_default()

        draw.text((4,4), text, font=font)

        # Display image.
        disp.image(image)
        disp.display()

print_lcd(LCD, 'Apasa pe\nsosire sau\nplecare')

while True:

        arrive = False
        leave = False
        if btn_arrive.is_active:
                arrive = True
        elif btn_leave.is_active:
                leave = True
        
        if arrive or leave:
                
                beep()

                finished = False
                fail_count = 0
                while not finished and fail_count < 3:

                        if arrive:
                                print_lcd(LCD, 'Scaneaza\namprenta\npentru sosire')
                        elif leave:
                                print_lcd(LCD, 'Scaneaza\namprenta\npentru plecare')

                        finger_id = fingerprint.read()[0]

                        if (finger_id == 'init_error' or finger_id == 'convert_error'
                        or finger_id == 'reading_error'):
                                failure_beeps()
                                print_lcd(LCD, 'Eroare citire\nsau initializare\nsenzor')
                                fail_count += 1
                        elif finger_id == 'find_error' or finger_id == 'no_match':
                                failure_beeps()
                                print_lcd(LCD, 'Nu s-a gasit\namprenta')
                                fail_count += 1
                                #time.sleep(1)
                                #print_lcd(LCD, 'Apasa pe\nsosire sau\nplecare')
                                #finished = True
                        else:
                                uid = employee.ftou(finger_id)
                                print('uid: %s'%uid)
                        
                                if arrive:
                                        arr_status = persistance.arrival(uid)
                                        
                                elif leave:
                                        dep_status = persistance.departure(uid)
                                        
                                        
                                if arrive and arr_status != -1 and arr_status != -2:
                                        print_lcd(LCD, 'Sosire\ninregistrata')
                                        success_beeps()
                                        finished = True
                                elif leave and dep_status != -1:
                                        print_lcd(LCD, 'Plecare\ninregistrata')
                                        success_beeps()
                                        finished = True
                                elif arr_status == -2:
                                        failure_beeps()
                                        print_lcd(LCD, 'Sosire deja\ninregistrata\nastazi')
                                        finished = True
                                else:
                                        failure_beeps()
                                        print_lcd(LCD, 'Amprenta\ninexistenta')
                                        fail_count += 1

                        employee.query()
                        time.sleep(2)
                        print_lcd(LCD, 'Apasa pe\nsosire sau\nplecare')
                
                if fail_count == 3:
                        print('Failed too many times...')
                        print_lcd(LCD, 'Incearca\ndin nou')
                        time.sleep(1.5)
                        print_lcd(LCD, 'Apasa pe\nsosire sau\nplecare')
                                
sys.exit(0)
