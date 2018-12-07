#! /usr/bin/env python

import sys,threading,time,os,subprocess, resource
from subprocess import Popen, PIPE, call
import pwd

"""
::NCC Online Judge::
       Supported Languages: C,C++ and Python.
       Judge calling syntax: "python judge.py <sourcePath> <UID> <PID> <SID>" :: code-file-name must include the file extension
       Code-file must be in ../submissions directory
       Testcase-file must be in ../test_case directory
       Judge will store output and error in /jail/progs/output.txt and /jai/progs/error.txt#
"""
 
'''
0-success
1-wrong answer
2-compile error
3-timeout
4-runtime
6-system calls (review)
'''

results_testcase_thread=[-1,'','']


def clean_up():
        ''' 
        This is the cleanupscript which will be called after the user program is executed, and will free all subuser's
        processes, memory and anything which might be remaining
        '''
        
        ''' deleting all processes belonging to the user subuser '''
        #os.system("kill -9 `ps -aux | grep \"subuser\" | awk '{print $2}'` >& /dev/null")
        pass



#Importing System arguments
argImport = sys.argv
# def onjudge(argImport):
# a=['judge.py', '/home/ncc/user_submissions/1400_123_113312.cpp', '1400', '1', '123']
# argImport=a;
 
#print "here"
 
if len(argImport) != 5:
        #print ":Missing Arguments"
        #print "Try: judge.py <sourcePath> <UID> <PID> <SID>"
        #return "Missing Args Bye"
        quit()
else :
        None
        #print "SourcePath="+argImport[1];
        #print "User ID:"+argImport[2];
        #print "Problem ID:"+argImport[3];    
        #print "Submission ID:"+argImport[4];
 
sourcePath = str(argImport[1])                                                                  #sourcePath (/submission/__/)
UID = str(argImport[2])                                                                         #UID : User ID
PID     = str(argImport[3])                                                                             #PID : Problem ID
SID = str(argImport[4])                                        #SID : Submission ID                                                                            
TcID = "tc"+PID+".txt"                                                                                      #TcID : Test Case ID | TcID is PID.txt
solution = "s"+PID+".txt"
 
 
#Path Variables
 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
 
#print str(BASE_DIR)
 
#codePath = "/home/ncc-14/user_submissions/"
codePath = os.path.join(BASE_DIR,'user_submissions/')
#testCasePath = "/home/ncc-14/problem_data/testcases/"
testCasePath = os.path.join(BASE_DIR, 'problem_data/testcases/')
jail_path = "jail/"
out_file = ""
#originalSolutionPath = "/home/ncc-14/problem_data/solutions/"
originalSolutionPath = os.path.join(BASE_DIR, 'problem_data/solutions/')
#Format Detection
temp = sourcePath.split(".");
file_extension = temp[1];
 
#Changed 28th March 9:00 pm
extensionFlag = 0
endChar = sourcePath[-1]
#print endChar
if endChar == 'c':
        extensionFlag = 1
 
flagToCompare = 0
if int(PID) == 3:
        #print "inside if"
        flagToCompare = 1
 
#Initialize Variables                                  
fExists = 0                                                                                                     #Flag:Existance of Code and TestCase file
ret_flag=-1
       
#print "PWD(codeFile)"+codePath+UID+"_"+SID
#print "codePath="+sourcePath;
#print "UID="+UID
#print "PID="+PID
#print "SID="+SID
#print "TcID="+TcID
#print "solution="+solution
##File Detection
 
#codeFile
#print "File :"+UID+"_"+SID+": found"
fileName = sourcePath.split("/")
lFile = len(fileName);
 
if os.path.exists(sourcePath):
        #print "File :"+fileName[lFile-1]+": found"
        fExists = 1
else :
        #print "File :"+fileName[lFile-1]+": NOT found"
        fExists = 0
        #return "Invalid User code file" #quit();
#testCaseFile
#testCasePath = "/home/ncc-14/problem_data/testcases/"
#print "TestCasePath="+testCasePath
if os.path.exists(testCasePath+TcID):
        #print "File :"+testCasePath+TcID+": found"
        fExists = 1
else :
        #print "File :"+testCasePath+TcID+": NOT found"
        fExists = 0
        #return "Invalid Testcase-file"#quit();
#SolutionFile
if os.path.exists(originalSolutionPath+solution):
        #print "File :"+solution+": found"
        fExists = 1
else :
        #print "File :"+originalSolutionPath+solution+": NOT found"
        fExists = 0
        #return "Invalid SolutionFile"#quit();
 
#Final variables to be used for storing file locations
codeFile = fileName[lFile-1]
testCaseFile = testCasePath+TcID
mainSolutionFile = originalSolutionPath+solution
#jailPath = "/home/ncc-14/judge/jail"
#jailPath = os.path.join(BASE_DIR, 'judge/jail/')
#passWord = "ron@1628"
jailPath = os.path.join(BASE_DIR, '/mnt/abhiraj/asdoc/nishad94/xenny/jammm/RS_18/ashmew2/jail/')
'''
Till now we have successfully checked the existence of test case and code file
'''
# #sudo experiments
# #print "PROCESS ID::"+str(os.getpid())
# password="pop4food"
# command="chroot /home/ncc/judge/jail"
# # p=os.system('echo %s|sudo -S %s' %(password,command))
# os.system("echo %s|sudo -S %s && rm"% (password,command))
 
 
#File read function
def fileRead(filename):
        if fExists == 0: return "";
        f = open(filename,"r"); d = f.read(); f.close(); return d.replace("\r","")
 
checkSys = fileRead(sourcePath)
substringSystem = "system(\""
stat = substringSystem in checkSys
if stat == True:
        ret_flag = 6
        print ret_flag
        quit()
 
testCase = fileRead(testCaseFile)
testCase = testCase.split("\n^^--\n")
#print testCase; #print ;
numberOfTestCase = len(testCase)
mainSolution = fileRead(mainSolutionFile)
#print mainSolution
mainSolution = mainSolution.split("\n^^--\n")
#print mainSolution;
realRoot = os.open("/", os.O_RDONLY)
 
os.system("cp "+sourcePath+" "+jailPath+"/submissions/"+fileName[lFile-1] )
 
#Compile
outFile = str(UID+"_"+PID)
os.system("rm -f "+jailPath+"/outputs/*.out")
os.chroot(jailPath)
#Changed today 28th March 10:00pm
if extensionFlag == 1:
        os.system("gcc -lm /submissions/"+codeFile+" -o /outputs/"+outFile+".out 2> /dev/null")
else:
        os.system("g++ -lm /submissions/"+codeFile+" -o /outputs/"+outFile+".out 2> /dev/null")
os.fchdir(realRoot)
os.chroot(".")
#outputFilePath = "/home/ncc-14/judge/jail/outputs/"+outFile+".out"
#outputString = 'judge/jail/outputs/' + outFile + '.out'
outputString = '/mnt/abhiraj/asdoc/nishad94/xenny/jammm/RS_18/ashmew2/jail/outputs/' + outFile + '.out'
outputFilePath = os.path.join(BASE_DIR, outputString)
outputFilePath = '/mnt/abhiraj/asdoc/nishad94/xenny/jammm/RS_18/ashmew2/jail/outputs/' + outFile +'.out'
 
if not os.path.exists(outputFilePath):
        flagCompile = 0; ret_flag=2;
        #print "Compile Error"
        #print "FLAG::"+str(ret_flag)
        print ret_flag
        quit()
else:
        flagCompile = 1
        #print "Compile Successful"
 
#print "iuo"
#Timeopt function

def compare(string1, string2, flag):                                    #string1:User's output   string2:Expected output
        # #print "STRING1="+string1
        # #print "STRING2="+string2
        if flag == 0:
                if string1 != string2:
                        return -1
                elif string1==string2:
                        return 0
                else:
                        return 1
        else:
                #temp = float(abs(float((string1-string2))/float(string2)))
                try :
                        string1 = float(string1)
                        string2 = float(string2)
                        temp = abs((string1-string2)/(string2))
                        #print "temp-->"
                        #print temp
                        if float(temp) <= 0.001:
                                return 0
                        else:
                                return -1
                # ValueError raised when the string is not a number(a string or something else)
                except ValueError as ve :
                        return -1
                       
 
soft , hard = resource.getrlimit(resource.RLIMIT_STACK)
#print "Memory limit before : " + str(soft) + " " + str(hard)
new_soft = 1024*1024*8;
resource.setrlimit(resource.RLIMIT_STACK,(new_soft,hard))
resource.setrlimit(resource.RLIMIT_DATA,(new_soft,hard))
resource.setrlimit(resource.RLIMIT_AS,(1024*1024*500,-1))
soft , hard = resource.getrlimit(resource.RLIMIT_STACK)
#print "Memory limit after : " + str(soft) + " " + str(hard)
 
try:
        pass
except ValueError:
        ret_flag = 5
        print ret_flag
        quit()
       
#for i in range(0, numberOfTestCase -1):
for i in range(0, 2):
        os.chroot(jailPath)
        executablePath = "/outputs/"+outFile+".out"


        '''
        Pass each testcases to a seperate thread, testcases_thread, which executes the program as the user subuser
        '''
        #print os.getpid()
        #os.system("whoami")
        '''
        argument passes to execution_testcase.py is the executablePath
        '''

        open("/testcase_file.txt",'w').write(testCase[i])
        execution_output = os.popen("python /execute_testcase.py "+executablePath).read().split("^^--$$")

        ret_flag = int(execution_output[0])
        output = execution_output[1]
        error = execution_output[2]
        #os.system("whoami")
        os.chroot(".")

        if ret_flag == 4:
                print "4"
                quit()

        #print "rofl"
        #print "Output:\n" + output
        if compare(output, mainSolution[i], flagToCompare) == -1:
                #print "wrong"
                ret_flag=1
                break
                #return "Wrong Solution Found"#quit()
        else:
                ret_flag=0
                #print "correct"
#print os.getcwd()
outputDir = os.path.join(BASE_DIR,'judge/')
os.chdir(outputDir)
 
#print "FLAG::"+str(ret_flag)
print ret_flag
#share.j_postdata(ret_flag)
