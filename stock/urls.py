from django.urls import path
from .views import Dashboard, RefreshStockView, StockPage, GetDataChart
from django.contrib.auth import views as auth_view
from . import views


app_name = 'stock'

urlpatterns = [
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('refresh-stock/', RefreshStockView.as_view(), name='refresh-stock'),
    path('stockpage/<int:pk>/', StockPage.as_view(), name='stockpage'),
    path('day-data-stock/<int:pk>/', GetDataChart.as_view(), name='get-data-stock'),
    path('linechart/<int:pk>/', views.lineChart, name='linechart'),
]