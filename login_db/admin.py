from django.contrib import admin
from login_db.models import ncc_user,submissions, problems, adminBroadcast, userClarification, user_stats


class problemsAdmin(admin.ModelAdmin):
    readonly_fields = ('users_solved_no', 'PID', 'users_attempted_no')

    # Divides the admin page into sections
    fieldsets = [
        (None, {'fields' : ('PID', 'name')}),
        ('Scoring Details', {'fields' : (('level', 'points'),)}),
        ('Problem Stats',{'fields' : (('users_attempted_no', 'users_solved_no'),)}),
        ('Problem data path: ', {'fields' : ('p_path', 'tc_path', 'op_path')}),
    ]
    
    # Fields enlisted in the change page
    list_display = ('name', 'level', 'points', 'users_attempted_no', 'users_solved_no')
    # Filter options
    list_filter = ['level', 'points', 'users_attempted_no', 'users_solved_no']
    # Default search fields
    search_fields = ['name', 'PID']

admin.site.register(problems, problemsAdmin)

class ncc_userAdmin(admin.ModelAdmin):
    readonly_fields = ('password', 'last_login', 'date_joined')

    fieldsets = [
        ('User Details', {'fields' : ('username', 'first_name', 'last_name', 'email', 'college_org', 'phone' )}),

        ('Status/Permissions', {'fields' : ('password', 'last_login', 'is_staff', 'is_active', 'is_superuser', 'date_joined', 'groups')}),
    ]

    list_display = ('username', 'date_joined')
    list_filter = ['username', 'first_name']
    search_fields = ['username', 'first_name', 'college_org', 'phone']

admin.site.register(ncc_user, ncc_userAdmin)

class submissionsAdmin(admin.ModelAdmin):
    readonly_fields = ('UID', 'PID', 'SID', 'timestamp', 'verdict', 'exec_time', 'memory', 'language','notified')
    list_display = ('UID' , 'PID', 'verdict')

admin.site.register(submissions, submissionsAdmin)


class adminBroadcastAdmin(admin.ModelAdmin):  
    def Problem_Name(self, obj):
        return obj.problem.name

   
    list_display = ('heading','Problem_Name','timeIssued')
    list_filter = ['timeIssued']
    search_fields = ['Problem_Name', 'heading']


admin.site.register(adminBroadcast, adminBroadcastAdmin)

class userClarificationAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Username',{'fields' : ['user']}),
        ('Clarification',{'fields' : ['heading', 'clarification','isClarified']}),
        ('Time of issue',{'fields' : ['timeIssued'], 'classes' : ['collapse']}),
    ]
    
    list_display = ('heading', 'get_user_username', 'timeIssued')

    def get_user_username(self, obj):
        return obj.user.username
    get_user_username.short_description  ='Username'

admin.site.register(userClarification, userClarificationAdmin)

admin.site.register(user_stats)
