
import daemon
import time
from django.db import models
from login_db.models import ncc_user,submissions,problems,user_stats

with daemon.DaemonContext():
	#	The queue program starts here
	
	# can be changed to " while the contest is running "	
	while True:
		
		
		submission_list  =  user_stats.objects.filter(verdict=9).order_by('timestamp').values()
		
		for submission_dict in submissions_list:
			# TODO call the judge using values in submission_dict
			verdict = 0
			
			# get the executed code's submission entry
			current_submittion = submissions.objects.get(SID=submission_dict['SID'])

		    # boolean storing if submission exists
			prev_submission = submissions.objects.filter(UID = current_submission.UID,PID = current_submission.PID, verdict = 0).exists()
			
			
			# set the verdict and save it
			current_submission.verdict = verdict
			current_submission.save()
			
			
			# updation of points and level
			if verdict == 0:
				if not prev_submission:
					stat = user_stats.objects.get( UID = current_submission.UID )

					problem = problems.objects.get( PID = current_submission.PID )

					stat.score += problem.points

					if problem.level==1:
						stat.score_level_1 += problem.points
					elif problem.level==2:
						stat.score_level_2 += problem.points
					elif problem.level==3:
						stat.score_level_3 += problem.points
					elif problem.level==4:
						stat.score_level_4 += problem.points

					if stat.current_level==1:
						if stat.score_level_1 >= 12:
							stat.current_level=2
					elif stat.current_level==2:
						if stat.score_level_2 >= 30:
							stat.current_level=3
					elif stat.current_level==3:
						if stat.score_level_3 >= 40:
							stat.current_level=4
					stat.save() 

			None
	
	
		# for reducing execution stress of the process if there is no submission in queue
		time.sleep(1)
