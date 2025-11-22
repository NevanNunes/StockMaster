from django.urls import path
from .views import (
    LoginView, LogoutView, UserProfileView, SignupView, 
    login_page_view, signup_page_view, logout_view
)

urlpatterns = [
    # API Endpoints
    path('api/login/', LoginView.as_view(), name='api-login'),
    path('api/logout/', LogoutView.as_view(), name='api-logout'),
    path('api/signup/', SignupView.as_view(), name='api-signup'),
    path('api/me/', UserProfileView.as_view(), name='api-user-profile'),
    
    # UI Pages
    path('login/', login_page_view, name='login'),
    path('signup/', signup_page_view, name='signup'),
    path('logout/', logout_view, name='logout'),
]
