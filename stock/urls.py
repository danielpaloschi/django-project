from django.urls import path
from .views import Dashboard, RefreshStockView, StockPage, GetDataChart, HomePage, CreateAccount
from django.contrib.auth import views as auth_view
from . import views

app_name = 'stock'

urlpatterns = [
    path('', HomePage.as_view(), name='homepage'),
    path('login/', auth_view.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_view.LogoutView.as_view(), name='logout'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('refresh-stock/', RefreshStockView.as_view(), name='refresh-stock'),
    path('stockpage/<int:pk>/', StockPage.as_view(), name='stockpage'),
    path('day-data-stock/<int:pk>/', GetDataChart.as_view(), name='day-data-stock'),
    path('createaccount/', CreateAccount.as_view(), name='createaccount')
]