import os
import datetime
import pickle
import json

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import Context,Template
from django.template.loader import get_template
from login_db.models import ncc_user,submissions,problems,user_stats
from django.contrib.auth import authenticate, login, logout
from django.utils.timezone import localtime

from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError

# Create your views here.

def logout_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            logout(request)
    return redirect('/ncc/')

        

def login_view(request):
    if request.method == 'POST':
        form = request.POST
        user = authenticate(username = form['uname'],password = form['password'])
        if user is not None:
            if user.is_active:
                login(request,user)
                return redirect('/ncc/main/')
            else:
                output = "banned"
        else:
            output = "Invalid Login Details"
            

    else: output = "lol"
    
    return HttpResponse(output)
    
    
    
def sub_page(request):
    if request.user.is_authenticated():
        t = get_template('main.html')
        c = Context({'username' : request.user.username})
        output = t.render(c)
    else:
        output = "lol"
    return HttpResponse(output)
    
    
    
    
#Submission timeout function, counts down from +90 using datetime of most recent submission by user
def submission_timeout(user):
    if len(submissions.objects.filter(UID=user)):
        submission_timeout = submissions.objects.filter(UID = user).latest('timestamp').timestamp
        submission_timeout = localtime(submission_timeout).replace(tzinfo = None)
        #keeping the timer at 30 seconds for now.
        submission_timeout = submission_timeout + datetime.timedelta(seconds=30)
        curr_time = datetime.datetime.now()
        diff = submission_timeout - curr_time
    else: diff = 0
    return diff

	
def check_current_level(request):
	if submissions.objects.filter(UID = request).exists():
		sub = submissions.objects.filter(UID = request).latest('timestamp')
		level = problems.objects.get(PID = sub.PID).level
	else: level = 1
	
	return HttpResponse(level)
		
"""def calculate_overall_score(user):
	score = 0
	submissions = submissions.objects.filter(UID = user, verdict = 0)
	for subs in submissions:
		problem = problems.objects.get(PID = subs.PID)
		score = score + problem.points
"""

#This view is called whenever you click "Upload" on /lol/submission


def upload_file(request):
    if request.user.is_authenticated():
        ## Create a new submission object and save. Added functionality for the user to submit more than one solution to a problem. 
        if request.method == 'POST':            
            if 'upload_file' in request.FILES:
                diff = submission_timeout(request.user)
                #keeping the timer at 30 seconds for now.
                if diff == 0 or diff.seconds >=30:
                	
                	# verdict = 9 means the submission is in queue
                    new_sub = submissions(UID = request.user,PID = request.POST['PID'], language = request.POST['language'],verdict = 9, source_path = request.FILES['upload_file'])

			
                    print "saved"
                    new_sub.save()		#  save the submission
                    
                    
                    
                    
                    # The following line is commented because it is not used now
                    # verdict = request.POST['verdict']
                    # if(verdict == 0):

                    # call judge, get it's message and verdict and assign the submission result message to the output variable below
                    output = {'message' : "Processing..." , 'value' : request.POST['verdict']}
                    
                    
                    #	The following lines are commented because the points and the level
                    #	updation is happening in the submissions queue
                    
                    '''
                    if int(verdict) == 0:
                        if not prev_submission:
                            stat = user_stats.objects.get(UID=request.user)
                     
                            problem = problems.objects.get(PID=request.POST['PID'])
                        
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
                    '''
                    
                else: return HttpResponse("90 seconds hasn't passed yet!")
            else: output = {'message' : "File not selected. Please select file to upload and try again." , 'value' : "-1"}
        else: output = {'message' : "Invalid request. Did you use the proper page?    " , 'value' : "-3"}
    else: output = {'message' : "Not logged in." , 'value' : "-2"}
    
    return HttpResponse(json.dumps(output), content_type="application/json")

    
    
    

def user_page(request):
    if request.user.is_authenticated():
        output = "Welcome %s, your first name is %s <br> your email is %s" %(request.user.username,request.user.first_name,request.user.email)
    else: output = "rofl"
    return HttpResponse(output)



def register_out(request):
    if request.method == 'POST':
        form = request.POST
        try:
            user = ncc_user.objects.create_user(form['uname'],form['email'],form['password'])
            user.first_name = form['firstname']
            user.last_name = form['lastname']
            user.college_org = form['college']
            user.phone = form['phone']
            user.save()

            user_stat = user_stats(UID = user)
            user_stat.save()
        except IntegrityError:
            return HttpResponse("That User ID/Email is already taken! Try another one.")
        user = authenticate(username = form['uname'],password = form['password'])
        login(request,user)
        output = "Successfully registered user %s. Please login." %(form['uname'])
    else: output = "lol"
    return HttpResponse(output)
    

def leaderboard_show(request):
    #TODO 
    leaderboard_list  =  user_stats.objects.order_by('-score_level_4','-score_level_3','-score_level_2','-score_level_1').values()
    
    to_ret=""
    
    for i in leaderboard_list:
        to_ret+="<br>"
        user = ncc_user.objects.get(id=i['UID_id'])
        to_ret+=user.username
        to_ret+=": "
        to_ret+=str(i)
    
    return HttpResponse(to_ret)
    # display learder board
    None

# Direct user to arena if logged in, else redirect to index page for login
def arena_view(request, probID):
    if request.user.is_authenticated():
        probLevel = problems.objects.get(PID=probID).level
        currentUser = user_stats.objects.get(UID=request.user)
        # Allow user to view problem based on his current level
        if(currentUser.current_level >= probLevel):      
            path = settings.BASE_DIR + "/login_db/templates//site/problems/p%d.html" %(probLevel)
            problem_template_path = get_template(path)
            problem_html = open(path,'r').read()
            problem_context = Context({'problem': problem_html,'pid':probID})
            problem_template = get_template('site/login/Arena.html')
            output = problem_template.render(problem_context)
            return HttpResponse(output)
    return redirect('/ncc/')

def submission_status(request,probID):
	if request.user.is_authenticated():
		if submissions.objects.filter(UID = request.user,PID = probID).exists():
			
			#return HttpResponse (str(submissions.objects.filter(UID = request.user,PID = probID).order_by('timestamp').values()))
			verdict = prev_submission = submissions.objects.filter(UID = request.user,PID = probID).order_by('-timestamp').values()[0]['verdict']
			
			message = ""
			if verdict == 9:
				message = "In queue"
			elif verdict == 0:
				message = "correct"
			else:
				message = "wrong"
		
			return HttpResponse(message)


















#View called by jQuery requests

def submissions_check(request):
	
	output = {'message' : 'lol' , 'value' : '-1'}
	if request.method == 'POST':
		sub = submissions.objects.filter(UID = request.user, notified = False).latest('timestamp')

		verdict = sub.verdict
		problem = problems.objects.get(PID = sub.PID)
		sub.notified = True
		if verdict == 0:
			output = {'message' : 'Problem %s submission was correct! %d points awarded.' %(problem.PID,problem.points), 'value' : '0'}
		elif verdict == 1:
			output = {'message' : 'Wrong answer in submission of problem %s.' %(problem.PID), 'value' : '1'}
		elif verdict == 2:
			output = {'message' : 'Compile-time error in problem %s!' %(problem.PID), 'value' : '2'}
		elif verdict == 3:
			output = {'message' : 'Problem %s submission timed out!' %(problem.PID), 'value' : '3'}
		elif verdict == 4:
			output = {'message' : 'Runtime error in submission of problem %s.' %(problem.PID), 'value' : '4'}
		else: sub.notified=False
		sub.save()
		
		
	else: output = {'message' : 'kaus' , 'value' : '-1'}
	
	return HttpResponse(json.dumps(output), content_type="application/json")
	
	













#Timer URL, returns difference between user's most recent submission timestamp (+90 secs) and the current server time

def timer_diff(request):

    diff = submission_timeout(request.user)
    if diff != 0:
        if diff.seconds<=90:
            output = str(diff.seconds)
        else: output = '0'
    else: output = '0'
    
    
        
    return HttpResponse(output)
