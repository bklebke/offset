from django.urls import path
from . import views

urlpatterns = [
	path('signup/', views.SignUp, name='signup'),
	path('profile/', views.Profile.as_view(), name='profile'),
	path('profile/success', views.Success.as_view(), name='success'),
	path('profile/get_access_token', views.GetAccessToken, name='GetAccessToken'),
	path('profile/account_overview', views.AccountOverview, name='AccountOverview'),
	path('profile/error', views.Error.as_view(), name='error')
]