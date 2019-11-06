print('loading processing modules...')
from subprocess import call
from sys import executable, path
import os
print('loading cyclic task...')
#from processes import cyclic
print('loading server task...')
#from processes import server
print('loading fingerprint module...')
import helper_classes.fingerprint_helper as fingerprint
path.append('/home/pi/Desktop/Pontaj Workspace/processes/helper_classes')

def run_process(process):
    print(process)
    if process == 'cyclic.py':
        #cyclic.run()
        pass
    elif process == 'server.py':
        #server.run()
        pass


if __name__ == "__main__":

    print('running processes...')

    call(['gnome-terminal', '-x', 'python', '/home/pi/Desktop/Pontaj Workspace/processes/cyclic.py'])
    call(['gnome-terminal', '-x', 'python', '/home/pi/Desktop/Pontaj Workspace/processes/server.py'])

    