from django.urls import include, path
from mail.views import send_email_view, registration, login_view, welcome, view_messages, dashboard, view_sent_messages

urlpatterns = [
    path('', include('mail.urls')),
    path('send_email/', send_email_view, name='send_email'),
    path('registration/', registration, name='registration'),
    path('login/', login_view, name='login'),
    path('welcome/', welcome, name='welcome'),
    path('view_messages/', view_messages, name='view_messages'),
    path('dashboard/', dashboard, name='dashboard'),
    path('view_sent_messages/', view_sent_messages, name='view_sent_messages'),
]
