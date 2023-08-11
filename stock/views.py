from typing import Any, Dict
import requests
from django.shortcuts import render, redirect
from .models import Stock, DayDataStock
from django.views.generic import ListView, View, DetailView, TemplateView, FormView
from datetime import datetime, date
from django.db.models import Q
from django.urls import reverse
from django.http import JsonResponse
from .forms import CreateAccountForm




URL_API = "https://yfapi.net"

# Create your views here.

class HomePage(TemplateView):
    template_name = "homepage.html"

class Dashboard(ListView):
    template_name = "dashboard.html"
    model = Stock
    ordering = ['-market_change']

class RefreshStockView(View):
    def get_api_data(self):
        region = "US"
        lang = "en"
        symbols = "AAPL,MSFT,GOOG,AMZN,NVDA,META,TSLA,JPM,JNJ,WMT"
        url = f"{URL_API}/v6/finance/quote"

        headers = {
    'x-api-key': "F3pqoMA0Df5hjqFbOgnVm6zh9tOOplWP4RwRzF2H",
    "Content-Type": "application/json"
    }

        params = {
        "region": "US",
        "lang": "en",
        "symbols": "AAPL,MSFT,GOOG,AMZN,NVDA,META,TSLA,JPM,JNJ,WMT"
        }

        response = requests.request("GET", url, headers=headers, params=params)

        if response.ok:
            data = response.json()
            return data["quoteResponse"]["result"]
        else:
            return None

    def post(self, request, *args, **kwargs):
        stock_data = self.get_api_data()

        for data in stock_data:
            symbol = data['symbol']

            try:
                stock = Stock.objects.get(symbol=symbol)
                stock.company_name = data["longName"]
                stock.current_value = data["regularMarketPrice"]
                stock.symbol = data["symbol"]
                stock.market_change = data["regularMarketChange"]
                stock.growth_indicator = True if stock.market_change > 0 else False
                stock.save()
            except Stock.DoesNotExist:
                Stock.objects.create(
                    company_name = data["longName"],
                    current_value = data["regularMarketPrice"],
                    symbol = data["symbol"],
                    market_change = data["regularMarketChange"]
                )

        return redirect('stock:dashboard')

class StockPage(DetailView):
    template_name = 'stockpage.html'
    model = Stock

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            pk = self.kwargs['pk']
            stock = Stock.objects.get(pk=pk)
            labels = []
            data = []
            day_data = DayDataStock.objects.filter(stock_id=stock).order_by('date_value')


            context["day_data"] = day_data
            return context

class GetDataChart(View):

    def get_api_day_data(self, *args, **kwargs):
        pk = self.kwargs['pk']
        stock = Stock.objects.get(pk=pk)
        ticker = stock.symbol
        url = f"{URL_API}/v8/finance/chart/{ticker}"


        headers = {
    'x-api-key': "F3pqoMA0Df5hjqFbOgnVm6zh9tOOplWP4RwRzF2H",
    "Content-Type": "application/json"
    }

        params = {
        "range": "6mo",
        "region": "US",
        "interval": "1d",
        "lang": "en",
        }

        response = requests.request("GET", url, headers=headers, params=params)

        if response.ok:
            data = response.json()
            return data["chart"]["result"][0]
        else:
            return None

    def post(self, request, *args, **kwargs):
        day_stock_data = self.get_api_day_data()

        for (stock_date, stock_close) in zip(day_stock_data["timestamp"], day_stock_data["indicators"]["quote"][0]["close"]):
            stock_date_todate = datetime.fromtimestamp(stock_date)
            stock_date_formated = stock_date_todate.date().strftime('%Y-%m-%d')
            stock = Stock.objects.get(pk=kwargs['pk'])
            try:
                daydatastock = DayDataStock.objects.get(date_value = stock_date_formated, stock_id = stock)
                daydatastock.close_value = stock_close
                daydatastock.date_value = stock_date_formated
                daydatastock.save()

            except DayDataStock.DoesNotExist:
                DayDataStock.objects.create(
                close_value = stock_close,
                date_value = stock_date_formated,
                stock = stock,
                )

        return redirect(reverse('stock:stockpage', kwargs={'pk': kwargs['pk']}))

class CreateAccount(FormView):
    template_name= "createaccount.html"
    form_class = CreateAccountForm

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('stock:login')