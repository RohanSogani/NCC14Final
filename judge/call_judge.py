import os
BASE_DIR = os.path.dirname(__file__)
MASTER_JUDGE_PATH = os.path.join(BASE_DIR,'server.py')

def call1(sourcepath,UID,PID,SID):
	password = "ncclol"
	#os.system("../")
	#os.system("pwd")
	#os.system("../judge/")	
	#a=os.system("echo $password | sudo -S python master_judge.py "+sourcepath+" "+UID+" "+PID+" "+SID)
	a=os.popen("echo $password | sudo -S python " + MASTER_JUDGE_PATH + " " + sourcepath + " " + str(UID) + " " + str(PID) + " " + str(SID)).read()
	#print 'yoyoyoyyoyoy'
	print a

	# We need to catch memory exceeded error, which basically is: Fatal Python error: Couldn't create autoTLSkey mapping... so if a isnt a number, we return verdict 4(runtime error)
	try :
		float(a)
		return int(a[0])
	except ValueError:
		return 8
	#return int(a[0])
		
