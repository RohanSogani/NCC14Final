import os
import datetime
import pickle
import json

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import Context,Template
from django.template.loader import get_template
from login_db.models import ncc_user,submissions,problems,user_stats,adminBroadcast,userClarification
from django.contrib.auth import authenticate, login, logout
from django.utils.timezone import localtime
from recaptcha.client import captcha 

from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt

from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from django.core.exceptions import ValidationError

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("/var/log/ncc/submissions_log.log")
logger.addHandler(handler)

# Create your views here.


#Called when logout button is clicked.


def contest_started():
    starting_time = settings.CONTEST_START
    ending_time = settings.CONTEST_END
    if datetime.datetime.now() >= starting_time and datetime.datetime.now() <= ending_time:
        return True
    else:
        return False
    
	
def contest_ended():
    ending_time = settings.CONTEST_END
    if datetime.datetime.now() > ending_time:
        return True
    else:
        return False    


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



def render_with_csrf(request,path,context):
    context.update(csrf(request))
    return render(request,path,context)



def logout_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            logout(request)
    return redirect('/ncc/')

        

#Called when front page is requested.

def test_contest(request):
    if contest_started():
	    if request.user.is_authenticated():
		    return render_with_csrf(request,'site/login/Index.html',{'logged_in' : True, 'username' : request.user.username,'error_login' : False, 'contest_started' : contest_started()})
	    else: return render_with_csrf(request, 'site/login/Index.html',{'logged_in' : False, 'error_login' : False, 'contest_started' : contest_started()})
    else:
            return render_with_csrf(request,'site/login/Index.html',{'logged_in' : False, 'error_login' : False, 'contest_started' : False})


def login_page(request):
    if contest_started():
	    if request.user.is_authenticated():
		    return render_with_csrf(request,'site/login/Index.html',{'logged_in' : True, 'username' : request.user.username,'error_login' : False, 'contest_started' : contest_started()})
	    else: return render_with_csrf(request, 'site/login/Index.html',{'logged_in' : False, 'error_login' : False , 'contest_started' : contest_started(), 'contest_ended' : contest_ended()})
    else:
            return render_with_csrf(request,'site/login/Index.html',{'logged_in' : False, 'error_login' : False, 'contest_started' : contest_started(), 'contest_ended' : contest_ended()})




#Called when signing in.
def login_view(request):
    if contest_started():
        if request.method == 'POST':
            form = request.POST
            user = authenticate(username = form['uname'],password = form['password'])
            if user is not None:
                if user.is_active:
                    login(request,user)
                    return redirect('/ncc/main/')
                else:
                    error = "Your User ID is banned. Please contact us at admin@computingcontest.in, provide your User ID in the subject"
                    return render_with_csrf(request, 'site/login/Index.html',{'logged_in' : False, 'error_login' : True, 'error_text' : error, 'contest_started' : contest_started(), 'contest_ended' : contest_ended()})
            else:
                error = "Invalid User ID/Password. Please try again."
                return render_with_csrf(request, 'site/login/Index.html',{'logged_in' : False, 'error_login' : True, 'error_text' : error, 'contest_started' : contest_started(), 'contest_ended' : contest_ended()})
        
        return render_with_csrf(request, 'site/login/Index.html',{'logged_in' : False, 'error_login' : True, 'error_text' : "I see what you did there ;)", 'contest_started' : contest_started(), 'contest_ended' : contest_ended()})
    else:
        raise Http404


#Called when node page is requested.
    
def rules_view(request):
    return render(request,"site/rules/rules.html") 
    
def team_view(request):
    return render(request,"site/team/team.html")   
    
def node_view(request):
    if not contest_ended():
        if contest_started():
            if request.user.is_authenticated():
                user_stat_id = user_stats.objects.get(UID = request.user)
                problem_data = problems.objects.order_by('PID')
                
                notifs_count =   0    
                notifs_count += adminBroadcast.objects.count()
                notifs_count += userClarification.objects.filter(user=request.user,isClarified=True).count()
                
                return render(request,"site/node/node.html", {'username': request.user.username, 'userStats' :  user_stats.objects.get(UID = request.user), 'problem_data' : problem_data, 'locked' : False , 'contest_ended' : contest_ended(), 'notifs_count' : notifs_count , 'notifs_cnt':user_stats.objects.get(UID=request.user).notifs_cnt })
            else:    
                error = "You are not logged in."
                return render_with_csrf(request, 'site/login/Index.html',{'logged_in' : False, 'error_login' : True, 'error_text' : error, 'contest_started' : contest_started(), 'contest_ended' : contest_ended()})
        else:
            return HttpResponse("<html>You have been successfully registered! <br>Thank you for registering<br><a href=\"../../\">Go back</a></html>")
    else:
        return render_with_csrf(request, 'site/login/Index.html',{'logged_in' : False, 'error_login' : True, 'error_text' : 'The contest has ended', 'contest_started' : contest_started(), 'contest_ended' : contest_ended()})


    
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
    if contest_started():
        if submissions.objects.filter(UID = request).exists():
    	    sub = submissions.objects.filter(UID = request).latest('timestamp')
            level = problems.objects.get(PID = sub.PID).level
        else: level = 1

        return HttpResponse(level)
    else:
        raise Http404
		


#Called whenever username is checked
def username_available(request):
    if request.method == 'POST':
        premature_username = request.POST['uname']
        return HttpResponse(ncc_user.objects.filter(username__iexact = premature_username).exists())
    else: raise Http404



#Restrict the filefield to only accept c/cpp files and max size of 100kB via a custom field which inherits from FileField,
def clean(source_file):
    if contest_started():
        content_type = source_file.content_type
        if content_type in settings.CONTENT_TYPES:
            if source_file.size > int(settings.MAX_UPLOAD_SIZE):
                raise ValidationError('Please upload files less than 100kB!. Current file size is %d bytes' %(source_file.size))
        else: raise ValidationError('Only C/C++ sources allowed.')
    else:
        raise Http404    
    
#This view is called whenever you click "Upload" on /lol/submission    
def upload_file(request):
    if contest_started():
        if request.user.is_authenticated():
            ## Create a new submission object and save. Added functionality for the user to submit more than one solution to a problem. 
            if request.method == 'POST':
            
                if contest_ended():
                    output = {'message' : "Contest has ended" , 'value' : "-1"}
                    return HttpResponse(json.dumps(output), content_type="application/json")
               
                if 'upload_file' in request.FILES:         
                    diff = submission_timeout(request.user)
                    #keeping the timer at 30 seconds for now.
                    if diff == 0 or diff.seconds >=30:
                    
                    #Validate the uploaded file
                        try:
                            clean(request.FILES['upload_file'])
                        except ValidationError as e:
                            output = {'message' : e.messages, 'value' : "-1"}
                            return HttpResponse(json.dumps(output), content_type="application/json")
                                             	
                    	# verdict = 9 means the submission is in queue
                        new_sub = submissions(UID = request.user,PID = request.POST['PID'], language = request.POST['language'],verdict = 9, source_path = request.FILES['upload_file'])
                        new_sub.save()		#  save the submission
                        
                        
                        #get user's public IP address
                        ip = get_client_ip(request)
                        if ip is None:
                            ip = "Not found -.-"
                        logger.info("###" + str(new_sub.timestamp) + "###  " + "SID: " + str(new_sub.SID) + "       ###IP: " + ip + "       ###")
                            
                            
                            
                            
                            

                        output = {'message' : "Processing..." , 'value' : 0}
                        #Increase number of users attempted by one
                        problem = problems.objects.get(PID = request.POST['PID'])
                        problem.users_attempted_no += 1
                        problem.save()
                            
                            

                            
                    else: output = {'message' : "30 seconds haven't passed yet!", 'value' : "-1"}
                else: output = {'message' : "Please select a source file to upload.", 'value' : "-2"}
            else: output = {'message' : "Invalid request. Did you use the proper page?    " , 'value' : "-3"}
        else: output = {'message' : "Not logged in. Please login first before submitting." , 'value' : "-4"}
        
        return HttpResponse(json.dumps(output), content_type="application/json")
    else:
        raise Http404
    
    
    

def user_page(request):
    if contest_started():
        if request.user.is_authenticated():
            output = "Welcome %s, your first name is %s <br> your email is %s" %(request.user.username,request.user.first_name,request.user.email)
        else: output = "rofl"
        return HttpResponse(output)
    else:
        raise Http404



def register_out(request):
    if not contest_ended():
        if request.method == 'POST':
            response = captcha.submit(  
                request.POST.get('recaptcha_challenge_field'),  
                request.POST.get('recaptcha_response_field'),  
                '6LeuffASAAAAAKsnz48k5ofStznS1R4tL1gzFx3a',  
                request.META['REMOTE_ADDR'],)
            if not response.is_valid:
                output = {'message': "The captcha you entered is incorrect, Please try again.", 'value':"-2"}
                return HttpResponse(json.dumps(output), content_type="application/json") 
        

            form = request.POST
            if ncc_user.objects.filter(username__iexact = form['uname']).exists():
                output = {'message': "The User ID %s already exists! Please try another one." %(form['uname']), 'value':"-1"}
                return HttpResponse(json.dumps(output), content_type="application/json")
            try:
                user = ncc_user.objects.create_user(form['uname'],form['email'],form['password'])
            except IntegrityError:
                output = {'message': "The User ID %s already exists! Please try another one." %(form['uname']), 'value':"-1"}
                return HttpResponse(json.dumps(output), content_type="application/json")
            except (ValidationError,ValueError):
                output = {'message': "What?", 'value':"-1"}
                return HttpResponse(json.dumps(output), content_type="application/json")
            #Save the rest of the user details     
            
            user.first_name = form['firstname']
            user.last_name = form['lastname']
            user.college_org = form['college']
            user.phone = form['phone']
            
            try:
                user.full_clean()
            except ValidationError as e:
                user.delete()
                msg = ""
                for i in e.messages: msg += i
                output = {'message': "What? " + msg, 'value':"-1"}
                return HttpResponse(json.dumps(output), content_type="application/json")   
            
            #if no erros, finally save the rest of the details
            user.save()
            #generate the default user stats for this user.
            user_stat = user_stats(UID = user)
            user_stat.save()
            
            if contest_started():
                user = authenticate(username = form['uname'],password = form['password'])
                login(request,user)
                output = {'message': "Successfully registered user %s." %(form['uname']), 'value':"0"}
            else: output = {'message': "Successfully registered user ID %s. Stay tuned for NCC! We will notify you soon." %(form['uname']), 'value':"1"}
        else: raise Http404
        return HttpResponse(json.dumps(output), content_type="application/json")
    else:
        output = {'message' : "The contest has ended", 'value' : "1"}
        return HttpResponse(json.dumps(output), content_type="application/json")

def leaderboard_show(request):
    if contest_started():
        if request.user.is_authenticated():
        	leaderboard_list  =  user_stats.objects.order_by('-score_level_4','-score_level_3','-score_level_2','-score_level_1','submissionTime')
        	leaderboard_template = get_template('site/leaderboard/leaderboard.html')
        	leaderboard_context = Context({'users' : leaderboard_list, 'loggedInUser': request.user.username})
        	httpOutput = leaderboard_template.render(leaderboard_context)
        	return HttpResponse(httpOutput)
        else:
        	raise Http404
    else:
        raise Http404

# Direct user to arena if logged in, else redirect to index page for login
def arena_view(request, probID):
    if not contest_ended():
        if contest_started():
            if(int(probID) > 10): raise Http404
            if request.user.is_authenticated():
                probLevel = problems.objects.get(PID=probID).level
                user_score = user_stats.objects.get(UID=request.user)
                problem_data = problems.objects.order_by('PID')
                if int(probID) >= 1 and int(probID) <= 4:
                    current_level = 1
                elif int(probID) >= 5 and int(probID) <= 7:
                    current_level = 2
                elif int(probID) >= 8 and int(probID) <= 9:
                    current_level = 3
                else :
                    current_level = 4
                # Allow user to view problem based on his current level
                if(user_score.current_level >= probLevel):
                    path = settings.BASE_DIR + "/login_db/templates/site/problems/p%d.html" %int	(probID)
                    problem_template_path = get_template(path)
                    problem_html = open(path,'r').read()
                    
                    
                    notifs_count = 0
                    
                    notifs_count += adminBroadcast.objects.count()
                    notifs_count += userClarification.objects.filter(user=request.user,isClarified=True).count()
                    
                    
                    problem_context = Context({'username' : request.user.username, 'problem': problem_html,'pid':probID, 'score' : user_score, 'notifs_count':notifs_count, 'notifs_cnt':user_stats.objects.get(UID=request.user).notifs_cnt , 'loggedInUser':request.user.username, 'contest_ended' : contest_ended(), 'current_level' : current_level, 'problem_data' : problem_data, 'problems_status' : user_score.problems_status})
                    return render_with_csrf(request,'site/login/Arena.html',problem_context)
                    
                else: return render(request,"site/node/node.html", {'username': request.user.username, 'userStats' :  user_stats.objects.get(UID = request.user), 'problem_data' : problems.objects.all() , 'locked' : True, 'contest_ended' : contest_ended(), 'notifs_cnt':user_stats.objects.get(UID=request.user).notifs_cnt })
            error = "You are not logged in."
            return render_with_csrf(request, 'site/login/Index.html',{'logged_in' : False, 'error_login' : True, 'error_text' : error, 'contest_started' : contest_started(), 'contest_ended' : contest_ended()})
        else:
            raise Http404
    else:
        return render_with_csrf(request, 'site/login/Index.html',{'logged_in' : False, 'error_login' : True, 'error_text' : 'The contest has ended', 'contest_started' : contest_started(), 'contest_ended' : contest_ended()})


#called everytime a correct solution is submitted.

def update_scores(request):
    if contest_started():
	    if request.method == 'POST':
		    score = user_stats.objects.get(UID = request.user)
		    output = {'l1':score.score_level_1,'l2':score.score_level_2,'l3':score.score_level_3,'l4':score.score_level_4,'total':score.score}
		    return HttpResponse(json.dumps(output), content_type="application/json")
	    else: raise Http404
    else:
        raise Http404








def notifs(request):
    if contest_started():
        op = ""
        if request.method == 'POST':
		
            if userClarification.objects.filter(user = request.user).count() >= 30:
                return HttpResponse("1")
            new_clarification = userClarification(user=request.user,heading=request.POST['heading'])
            new_clarification.save()
            return HttpResponse("0")


        broadcasts = adminBroadcast.objects.all().values()
        clarifications = userClarification.objects.filter(user = request.user).values()


        if adminBroadcast.objects.all().count() != 0:
            op += "<h2 align = 'center'>Messages</h2>"

        for i in broadcasts:
            op += "<br><b>"+i['heading']+"</b>"
            op += "<br> "+i['clarification']+"<br>"


        cnt_notifs = adminBroadcast.objects.all().count()
        cnt_notifs += userClarification.objects.filter(user = request.user, isClarified=True).count()
        to_save = user_stats.objects.get(UID = request.user)
        to_save.notifs_cnt = cnt_notifs
        to_save.save()
        
        if userClarification.objects.filter(user = request.user).exists():
            op += "<br><h2 align = 'center'>Clarifications</h2>"
    	elif userClarification.objects.filter(user = request.user).count()==0 and adminBroadcast.objects.all().count() == 0: op += "<br><h2>No messages to display.</h2>"

        for i in clarifications:
            op += "<br><b>Query: "+i['heading']+"</b>"
            if i['clarification'] == "":
                op += "<br>Yet to be clarified<br>"
            else:
                op += "<br>Clarification: "+i['clarification']+"<br>"

        return HttpResponse("<html><title align = 'center'>Messages</title>"+op+"</body></html>")
    else: raise Http404




def notifscnt(request):
    if contest_started():
        op = ""
        if request.method == 'POST':
            return HttpResponse("-1")


        to_ret = adminBroadcast.objects.all().count()
        to_ret += userClarification.objects.filter(user = request.user, isClarified=True).count()
        return HttpResponse(str(to_ret))
    else: raise Http404





#View called by jQuery requests
def submissions_check(request):
    if not contest_ended():
        if contest_started():
            if request.user.is_authenticated():
                output = {'message' : 'lol' , 'value' : '-1'}
                if request.method == 'POST' and submissions.objects.filter(UID = request.user, notified = False).exists():
                    sub = submissions.objects.filter(UID = request.user, notified = False).latest('timestamp')
                    problem = problems.objects.get(PID = sub.PID)

                    verdict = sub.verdict
                    sub.notified = True
                    
                    if verdict == 0:
                        output = {'message' : 'Problem %s submission was correct! %d points awarded. (Click me to close)' %(problem.PID,problem.points), 'value' : '0'}                    
                    elif verdict == 1:
                        output = {'message' : 'Wrong answer in submission of problem %s. (Click me to close)' %(problem.PID), 'value' : '1'}
                    elif verdict == 2:
                         output = {'message' : 'Compile-time error in problem %s! (Click me to close)' %(problem.PID), 'value' : '2'}
                    elif verdict == 3:
                         output = {'message' : 'Problem %s submission timed out! (Click me to close)' %(problem.PID), 'value' : '3'}
                    elif verdict == 4:
                         output = {'message' : 'Runtime error in submission of problem %s. (Click me to close)' %(problem.PID), 'value' : '4'}
                    else: sub.notified=False
                    sub.save()
                    problem.save()
		
                else: output = {'message' : 'kaus' , 'value' : '-1'}
            else: raise Http404

            return HttpResponse(json.dumps(output), content_type="application/json")
        else: raise Http404
    else:
	    return HttpResponse(json.dumps("The contest has ended"), content_type="application/json")
	





def user(request,user_name):
    if contest_started():
        '''
        subs = submissions.objects.filter( UID = ncc_user.objects.get(username = user_name) ).order_by('timestamp')
        op = ""
        for i in subs:
            op += user_name+"<br>Problem: "+str(i['PID'])+"<br>State: "+str(i['verdict'])+"<br><br>"    
        return HttpResponse("<html> <title>"+user_name+"</title> <body overflow=\"auto\">"+op+"</body>")
       '''
        if request.user.is_authenticated():
            if ncc_user.objects.filter( username = user_name ).exists():
                submission_list  =  submissions.objects.filter( UID = ncc_user.objects.get(username = user_name) ).order_by('timestamp')
                Problems = problems.objects.all()
                user_template = get_template('site/user/user.html')
                leaderboard_list  =  user_stats.objects.order_by('-score_level_4','-score_level_3','-score_level_2','-score_level_1','submissionTime')
                current_user = ncc_user.objects.get(username = user_name)
                rank = -1
                total_users = len(leaderboard_list)
                for i,user in enumerate(leaderboard_list) :
                    if user.UID == ncc_user.objects.get(username = user_name) :
                        rank = i + 1
                user_context = Context({'submissions' : submission_list, 'currentUser': user_name, 'points':user_stats.objects.get(UID = current_user).score, 'Rank' : rank , 'total_users':total_users, 'Problems' : Problems})
                httpOutput = user_template.render(user_context)
                return HttpResponse(httpOutput)
            else: raise Http404
        else:
            raise Http404
    else: raise Http404







#Timer URL, returns difference between user's most recent submission timestamp (+90 secs) and the current server time


def timer_diff(request):
    if contest_started():
        diff = submission_timeout(request.user)
        if diff != 0:
            if diff.seconds<=30:
                output = str(diff.seconds)
            else: output = '0'
        else: output = '0'
        
        
            
        return HttpResponse(output)
    else: raise Http404
    

def contest_timeleft(request):
    if contest_started():
        curr_time = datetime.datetime.now()
        ending_time = settings.CONTEST_END
        time_diff = ending_time - curr_time
        if(time_diff.days < 0): output = "0"
        else: output = time_diff.seconds
        return HttpResponse(output)
    else: raise Http404
        
def contest_timetocontest(request):
    curr_time = datetime.datetime.now()
    ending_time = settings.CONTEST_END
    time_diff = ending_time - curr_time
    if(time_diff.days < 0): output = "0"
    else: output = time_diff.seconds
    return HttpResponse(output)
        
        
        
