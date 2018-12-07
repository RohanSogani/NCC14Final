'''
This file must be present inside the jail folder
'''


'''
Executes one test cases as the user subuser
prints output as a string ret_flag ( default = -1 )^^--$$outputstring^^--$$errorstring
should be called as python execute_testcase.py executablePath
'''

import sys
import os
import threading
import pwd
import getpass
from subprocess import Popen, PIPE, call



ret_flag = -1
output = ''
error = ''



def timeout( p ):
        global ret_flag
        if p.poll() == None:
                try:
                        '''
                        timeout occured
                        '''
                        p.kill()
                        ret_flag=3
                except:
                        pass
 

 
delim = "^^--$$"
executablePath = sys.argv[1]

'''
IMP: TODO clean up to be done for killing all process belonging to subuser
'''

uid_subuser = pwd.getpwnam("subuser")[2]
os.setuid(uid_subuser)


'''
This fragment of code returns "Judgement denied" if the current user is not set to subuser.
'''
if getpass.getuser() != "subuser":
        print getpass.getuser()
        print "NOT SUBUSER"
        print "8^^--$$^^--$$"
        quit()

#os.system("whoami")

try:
        codeExe = Popen(executablePath, stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=False)

        threadExe = threading.Timer( 2.0, timeout, [codeExe])
        threadExe.start()
        output=''
        testCase = open("/testcase_file.txt",'r').read()
        output , error = codeExe.communicate(testCase)
        os.system("exit")
except MemoryError:
        '''
        make ret_flag as runtime error
        '''
        ret_flag=4




if output is '':
        '''
        make ret_flag as runtime error
        '''
        ret_flag=4


if output[-1] == '\n':
        #print "before slice OUTPUT="+output
        output=output[:-1]
        #print "after slice OUTPUT="+output

threadExe.cancel()
'''
print: ret_flag^^--$$output^^--$$error
'''
print str(ret_flag)+delim+output+delim+error