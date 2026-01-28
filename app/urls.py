from django.contrib import admin
from django.urls import path,include
from .views import test
from .API.dashboard import display_count
from .utils import validate_signup_token
from .API.user_management import view_all_users,view_user_details,add_user,delete_user,personal_detail_test,create_password

from .API.test_views import verify_token,admin_dashboard,user_profile

from .API.auth import login_view

urlpatterns = [
    # ========== Admin =============
    path('test/', test),
    path('view_all_users/', view_all_users),
    path('view_user_details/<uuid:id>', view_user_details),
    path('add_user', add_user),
    path('delete_user/<str:id>', delete_user),

    #=============== Dashboard =================
    path('display_count',display_count),

    # =============== Sign Up =================
    path("auth/validate-signup-token/", validate_signup_token),
    path("auth/create_password/", create_password),

    # ================== Login ==================
    path("auth/login",login_view),

    # ============= Testing ============
    path('personal_detail_test',personal_detail_test),

    path("token/verify/", verify_token),

    path("test/dashboard/", admin_dashboard),
    path("user/profile/", user_profile),

]