from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from login_db import views


from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import django.contrib.staticfiles

urlpatterns = patterns('',
                          #url(r'^register/$', TemplateView.as_view(template_name='index.html'),name="index"),
                          #url(r'^$', TemplateView.as_view(template_name='site/login/login_page.html'),name="login"),
			  url(r'^$', views.login_page,name="login_page"),
			  url(r'^nccgoeslivesoon/', views.test_contest,name="test_page"),
                    	  url(r'^register/out/$',views.register_out,name="after_registration"),
                    	  url(r'^unamechecker/$', views.username_available,name="username_availability_checker"),
                          url(r'^logout/$', views.logout_view,name="logout_page"),
                          url(r'^login/$',views.login_view,name="login_check"),
                          url(r'^rules/$',views.rules_view,name="rules"),
                          url(r'^team/$',views.team_view,name="rules"),
                          url(r'^main/$', views.node_view ,name="nodes_page"),
                          url(r'^main/arena/(?P<probID>\d+)/$', views.arena_view, name='arena_main'),
                          url(r'^main/arena/status/$', views.submissions_check, name='submission_status'),
			  url(r'^main/arena/update/$', views.update_scores, name='update_scores'),
                          #url(r'^main/$',views.user_page,name="user_main_page"),
                          url(r'^submission/upload$',views.upload_file,name="upload"),
                          url(r'^user/(.*)$',views.user),
                          url(r'^notifs/$',views.notifs),
                          url(r'^notifscnt/$',views.notifscnt),
                          #url(r'^clarify/$',views.clarify),
                          url(r'^main/leaderboard/$',views.leaderboard_show,name="leaderboard"),
                          url(r'^timer/fetch/$',views.timer_diff,name="fetch_timer"),
                          url(r'^timer/timeleft/$',views.contest_timeleft,name="time_left"),
                          url(r'^timer/timetocontest/$',views.contest_timetocontest,name="time_left"),
                         #url(r'^problem/(?P<level>\d{1})/(?P<problem>\d{1})/$', views.problem_view, name = "show_prob"),
                            )
                            
urlpatterns += staticfiles_urlpatterns()
