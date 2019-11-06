import time, hashlib, traceback

from pyfingerprint.pyfingerprint import PyFingerprint
from employee_helper import Employee

class Fingerprint:

    def __init__(self):
        pass

    def enroll(self):

        outlog = ''

        ## Enrolls new finger
        ##

        ## Tries to initialize the sensor
        try:
            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

            if ( f.verifyPassword() == False ):
                raise ValueError('The given fingerprint sensor password is wrong!')

        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            outlog += ('\nThe fingerprint sensor could not be initialized!\n'+
                'Exception message: ' + str(e))
            exit(1)

        ## Gets some sensor information
        print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
        outlog += ('\nCurrently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

        ## Tries to enroll new finger
        try:
            print('Waiting for finger...')
            outlog += '\nWaiting for finger...'

            scanned = False

            ## Wait that finger is read
            tic = time.clock()
            toc = time.clock()
            while ( f.readImage() == False and (toc - tic < 0.1)):
                toc = time.clock()
            
            scanned = f.readImage()


            ## Converts read image to characteristics and stores it in charbuffer 1
            f.convertImage(0x01)

            ## Checks if finger is already enrolled
            result = f.searchTemplate()
            positionNumber = result[0]

            if ( positionNumber >= 0 ):
                print('Template already exists at position #' + str(positionNumber))
                outlog += '\nTemplate already exists at position #' + str(positionNumber)
                return (self.read()[0], outlog)

            print('Remove finger...')
            outlog += '\nRemove finger...'
            time.sleep(2)

            print('Waiting for same finger again...')
            outlog += '\nWaiting for same finger again...'

            ## Wait that finger is read again
            tic = time.clock()
            toc = time.clock()
            while ( f.readImage() == False and (toc - tic < 0.1)):
                toc = time.clock()
            
            scanned = f.readImage()

            if not scanned:
                print('not scanned')
                return -1

            ## Converts read image to characteristics and stores it in charbuffer 2
            f.convertImage(0x02)

            ## Compares the charbuffers
            if ( f.compareCharacteristics() == 0 ):
                outlog += '\nFingers do not match'
                raise Exception('Fingers do not match')

            ## Creates a template
            f.createTemplate()

            ## Saves template at new position number
            positionNumber = f.storeTemplate()
            print('Finger enrolled successfully!')
            outlog += '\nFinger enrolled successfully!'
            print('New template position #' + str(positionNumber))
            outlog += '\nNew template position #' + str(positionNumber)

        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            outlog += ('\nException message: ' + str(e))
            return (-1, outlog)
            #time.sleep(1)
            #exit(1)

        return (positionNumber, outlog)

    def read(self):

        outlog = ''

        ## Search for a finger
        ##

        ## Tries to initialize the sensor

        try:
            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

            if ( f.verifyPassword() == False ):
                raise ValueError('The given fingerprint sensor password is wrong!')
            

        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            outlog += ('\nThe fingerprint sensor could not be initialized!' + 
            'Exception message: ' + str(e))
            return ('init_error', outlog)
            #exit(1)

        ## Gets some sensor information

        print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
        outlog += ('\nCurrently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

        ## Tries to search the finger and calculate hash
        try:
            print('Waiting for finger...')
            outlog += '\nWaiting for finger...'

            ## Wait that finger is read
            tic = time.clock()
            toc = time.clock()
            while ( f.readImage() == False and (toc - tic < 0.1)):
                toc = time.clock()

            try:
                ## Converts read image to characteristics and stores it in charbuffer 1
                f.convertImage(0x01)
            except:
                print('error converting image')
                outlog += '\nerror converting image'
                return ('convert_error', outlog)
            
            try:
                ## Search template
                result = f.searchTemplate()

                positionNumber = int(result[0])
                accuracyScore = int(result[1])
            except:
                print('could not find template')
                outlog += '\ncould not find template'
                return ('find_error', outlog)

            if ( positionNumber == -1 ):
                print('No match found!')
                outlog += '\nNo match found!'
                return ('no_match', outlog)
                #exit(0)
            else:
                print('Found template at position #' + str(positionNumber))
                print('The accuracy score is: ' + str(accuracyScore))
                outlog += ('\nFound template at position #' + str(positionNumber) + 
                    '\nThe accuracy score is: ' + str(accuracyScore))
        except:
            print('error reading finger')
            outlog += '\nerror reading finger'
            return ('reading_error', outlog)
        
        #delete excess fingerprints
        #self.delete_extra()

        return (positionNumber, outlog)

    def delete(self, uid):
        ## Deletes a finger from sensor
        ##

        employee = Employee()
        ## Tries to initialize the sensor
        try:
            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

            if ( f.verifyPassword() == False ):
                raise ValueError('The given fingerprint sensor password is wrong!')

        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            exit(1)

        ## Gets some sensor information
        print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

        ## Tries to delete the template of the finger
        finger_ids = employee.utof(uid)
        if finger_ids != -1:
            for finger_id in finger_ids:
                try:
                    if ( f.deleteTemplate(finger_id) == True ):
                        print('Template deleted!')

                except Exception as e:
                    print('Operation failed!')
                    print('Exception message: ' + str(e))
                    print(traceback.format_exc())
                    exit(1)

            employee.remove_fingerprint(uid)
        else:
            print('invalid finger id list')

    def delete_fid(self, finger_id):
        try:
            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

            if ( f.verifyPassword() == False ):
                raise ValueError('The given fingerprint sensor password is wrong!')

        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            exit(1)

        try:
            if ( f.deleteTemplate(finger_id) == True ):
                print('Template deleted!')

        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            print(traceback.format_exc())
            exit(1)

    def delete_extra(self):
        employee = Employee()

        finger_ids = []
        for emp in employee.query():
            for finger_id in emp['finger_ids']:
                finger_ids.append(finger_id)
        
        ## Tries to initialize the sensor
        try:
            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

            if ( f.verifyPassword() == False ):
                raise ValueError('The given fingerprint sensor password is wrong!')

        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            exit(1)
        
        index_table = range(f.getTemplateCount())

        for i in index_table:
            if i not in finger_ids:
                print('deleting %s...'%i)
                self.delete_fid(i)

    def delete_all(self):
        ## Tries to initialize the sensor
        try:
            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

            if ( f.verifyPassword() == False ):
                raise ValueError('The given fingerprint sensor password is wrong!')

        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            exit(1)

        ## Gets some sensor information
        print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

        ## Tries to delete the template of the finger
        for finger_id in range(f.getTemplateCount() + 5):
            try:
                if ( f.deleteTemplate(finger_id) == True ):
                    print('Template deleted!')
            except:
                print('could not delete')