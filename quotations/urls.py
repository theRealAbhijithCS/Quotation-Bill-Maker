from django.urls import path
from quotations import views

urlpatterns = [
    path('', views.dashboard_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', views.reset_password_confirm_view, name='reset_password_confirm'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    
    # Bill CRUD
    path('bills/create/', views.bill_create_view, name='bill_create'),
    path('bills/<int:pk>/', views.bill_detail_view, name='bill_detail'),
    path('bills/<int:pk>/edit/', views.bill_edit_view, name='bill_edit'),
    path('bills/<int:pk>/delete/', views.bill_delete_view, name='bill_delete'),
    
    # PDF
    path('bills/<int:pk>/pdf/preview/', views.bill_pdf_preview_view, name='bill_pdf_preview'),
    path('bills/<int:pk>/pdf/download/', views.bill_pdf_download_view, name='bill_pdf_download'),

    # Live Calculation & PDF Modal Preview Endpoints
    path('api/fastapi/calculate', views.fastapi_calculate_view, name='fastapi_calculate'),
    path('api/fastapi/generate-pdf', views.fastapi_generate_pdf_view, name='fastapi_generate_pdf'),
]
