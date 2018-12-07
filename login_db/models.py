from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import os
from django.utils import timezone
from django.core.validators import RegexValidator
from time import gmtime, strftime

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Create your models here.




class CaseInsensitiveModelBackend(object):

    def authenticate(self, username=None, password=None):
        User = get_user_model()
        try:
            user = User.objects.get(username__iexact=username)
            if user.check_password(password):
                return user
            else:
                return None
        except User.DoesNotExist:
                return None
            
    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class ncc_user(AbstractUser):
    college_org = models.CharField(max_length = 255, null = True)
    phone = models.BigIntegerField(null = True,validators=[
                                                        RegexValidator(
                                                            regex='^[0-9]{10}$',
                                                            message='10 digit numbers only',
                                                            code='invalid_phone'),
                                                        ])

    class Meta:
        verbose_name = "User Details"
        verbose_name_plural = "User Details"

    def __unicode__(self):
        return self.username
    

class problems(models.Model):
    PID = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 255)
    
    p_path = models.FilePathField(path = os.path.join(BASE_DIR,"login_db/templates/site/problems/"))
    tc_path = models.FilePathField(path = os.path.join(BASE_DIR,"problem_data/testcases/"), match = "tc.*\.txt$")
    op_path = models.FilePathField(path = os.path.join(BASE_DIR,"problem_data/solutions/"), match = "s.*\.txt$")

    users_solved_no = models.IntegerField(default = 0)
    users_attempted_no = models.IntegerField(default = 0)
    level = models.IntegerField(default=1)
    points = models.IntegerField(default=0)
    
    def __unicode__(self):
        return unicode(str(self.PID))
    
    class Meta:
        verbose_name = "Problem"
     
      
''' Returns the path where the problem source code submitted by the user should be stored. It is called by the FileField model class. 

Format used: UserId_ProblemId_HourMinSec.Language

This format(especially the time) has been used to facilitate mutiple submissions on problems. The submission ID cannot be used as it is assigned after this field has been saved. So on the first object it is NONE. 
As there is a 90 sec gap between consecutive user submissions, this file name will always be unique.
'''
def user_file(instance,filename):
    path =  "%s_%s_" %(str(instance.UID.id),str(instance.PID)) + strftime("%H%M%S",gmtime()) + ".%s" %(instance.language)
    return path
        

class submissions(models.Model):
    UID = models.ForeignKey(ncc_user)
    PID = models.IntegerField()
    SID = models.AutoField(primary_key = True)
    notified = models.BooleanField(default = False)

    #filefield which stores user's source code.

    source_path = models.FileField(upload_to = user_file, blank = False, null = True)
    timestamp = models.DateTimeField(auto_now_add = True)
    verdict = models.IntegerField(default = 0)
    exec_time = models.FloatField(blank = True,null = True)
    memory = models.IntegerField(blank = True, null = True)
    language = models.CharField(max_length = 10,blank = True,null = True)

    # We don't need to store any test case related info in a submission,
    # Could possibly store which test case went wrong, like on codeforces. Opinion needed?
    #tc_id = models.IntegerField(blank = True,null = True)
    

            

    def __unicode__(self):
        return self.UID.username

    class Meta:
        verbose_name = "Submission Info"
        verbose_name_plural = "Submission Info"
        

#Taken from http://stackoverflow.com/questions/16041232/django-delete-filefield
#The code below is executed whenever a submissions object is deleted. Django doesn't automatically delete the file stored in the filefield.
@receiver(models.signals.post_delete, sender=submissions)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.source_path:
        if os.path.isfile(instance.source_path.path):
            os.remove(instance.source_path.path)
  
        
        
#not used anymore
# @ Jam: How are we gonna know the current score and level of the user? By seperately querrying the submissions table to check if he's solved each problem? I think some of the fields here are necessary. (Opinion?)
class user_stats(models.Model):
    UID = models.ForeignKey(ncc_user)
    score = models.IntegerField(default=0)
    score_level_1 = models.IntegerField(default=0)
    score_level_2 = models.IntegerField(default=0)
    score_level_3 = models.IntegerField(default=0)
    score_level_4 = models.IntegerField(default=0)
    # 1 - solved 0 - wrong 2 - unattempted
    problems_status = models.CharField(max_length = 10,default='2222222222')
    
    current_level = models.IntegerField(default=1)
    submissionTime = models.DateTimeField(default = timezone.now)
    notifs_cnt = models.IntegerField(default=0)
    
    def __unicode__(self):
        return str(self.score)+str(self.score_level_1)


class adminBroadcast(models.Model):
    problem = models.ForeignKey(problems)
    heading = models.CharField('Context',max_length=50)
    clarification = models.TextField(max_length=300)
    timeIssued = models.DateTimeField(default = timezone.now)

    def __unicode__(self):
        return self.heading

class userClarification(models.Model):
    user = models.ForeignKey(ncc_user)
    heading = models.CharField('Context',max_length=500)
    clarification = models.TextField(max_length=300)
    timeIssued = models.DateTimeField(default = timezone.now)
    isClarified = models.BooleanField(default=False)

    def __unicode__(self):
        return self.heading
        



























        
"""class user_reg(models.Model):
    UID = models.AutoField(primary_key = True)
    uname = models.CharField(max_length = 100)
    password = models.CharField(max_length = 60)
    ####required?#####################################
    #date = models.DateTimeField(auto_now_add = True)#
    ##################################################
    def __unicode__(self):
        return self.uname
"""
        

