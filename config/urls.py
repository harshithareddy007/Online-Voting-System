from django.contrib import admin
from django.urls import path, include
from voting import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # Public routes
    path('', views.home, name="home"),
    path('login/', views.user_login, name="login"),
    path('admin-login/', views.admin_login, name="admin_login"),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    # Admin system
    path('admin/', include('voting.urls')),
]

# ✅ THIS MUST BE OUTSIDE THE LIST
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)