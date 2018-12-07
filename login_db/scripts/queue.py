def run():
    import daemon
    import time
    import datetime
    import logging
    from django.utils.timezone import utc
    from django.db import models
    from login_db.models import ncc_user,submissions,problems,user_stats
    import sys
    import os
    # Relative paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    JUDGE_DIR = os.path.join(BASE_DIR,'judge/')
    USER_SUB_DIR = os.path.join(BASE_DIR, 'user_submissions/')

    sys.path.append(JUDGE_DIR)
    import call_judge
    logger = logging.getLogger("DaemonLog")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler("queue_log.log")
    logger.addHandler(handler)
    #logging.basicConfig(filename='queue_log.log',level=logging.DEBUG)
    logger.info("###Queue started at " + str(datetime.datetime.now()) + "###")

    verdict_dict = {0 : 'Correct' , 1 : 'Wrong Answer', 2 : 'Compile Error', 3 : 'Timeout', 4 : 'Runtime Error', 6 : 'System Calls Error', 9 : ' In queue' }

    with daemon.DaemonContext(stdout=sys.stdout,stderr=sys.stderr,files_preserve=[handler.stream]):

		#	The queue program starts here
	
		# can be changed to " while the contest is running "	
        while True:
		
            
            submission_list  =  submissions.objects.filter(verdict=9).order_by('timestamp').values()
            
            for submission_dict in submission_list:
				
				# TODO call the judge using values in submission_dict
				#path_topass = "/home/ncc-14/user_submissions/"+submission_dict['source_path']
				path_topass = USER_SUB_DIR + submission_dict['source_path']
				verdict = call_judge.call1(path_topass,submission_dict['UID_id'],submission_dict['PID'],submission_dict['SID'])
				

				info = "Executed UID: "+str(submission_dict['UID_id'])+" PID: "+str(submission_dict['PID']) + " SID: " + str(submission_dict['SID']) + " verdict: "+str(verdict) + " " + verdict_dict[verdict]
				print info
				logger.info(info)
				# boolean storing if submission exists
				prev_submission = submissions.objects.filter(UID = submission_dict['UID_id'],PID = submission_dict['PID'], verdict = 0).exists()
			
				# get the executed code's submission entry
				current_submission = submissions.objects.get(SID=submission_dict['SID'])
			
				# set the verdict and save it
				current_submission.verdict = verdict
				current_submission.save()
			
				stat = user_stats.objects.get( UID = current_submission.UID )
				problem = problems.objects.get( PID = current_submission.PID )

				problem.users_attempted_no += 1
				# Get array(stored as a string) and convert to list due to string immutability
				probStatus = stat.problems_status
				probStatus = list(probStatus)
				
				# Change problem status(3-val array) to wrong(0) from unsolved(2), change to right(1) if verdict == 0
				# updation of points and level
				if verdict == 0:
					# increase count of correct submissions by 1 (does not have to be a unique submission)
					 problem.users_solved_no += 1
					 problem.save()
				
					 # Update problem status boolean string
					 probStatus[current_submission.PID - 1] = '1'
					 probStatus = "".join(probStatus)
					 stat.problems_status = probStatus
					 stat.save()
					 problem.save()
					 
					 
					 # if correct submission was not there for the currently submitted problem
					 if not prev_submission:
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
						 stat.submissionTime = datetime.datetime.utcnow().replace(tzinfo=utc)
						 stat.save() 

				else :
					# If previous submissions wern't correct, update to wrong
					if not probStatus[current_submission.PID - 1] == '1' :
						probStatus[current_submission.PID - 1] = '0'
						probStatus = "".join(probStatus)
						stat.problems_status = probStatus
						stat.save()
	
	
			# for reducing execution stress of the process if there is no submission in queue
            time.sleep(1)
