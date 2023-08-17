from typing import Any, Dict
import requests
from django.shortcuts import render, redirect
from .models import Stock, DayDataStock, User, AbstractUser
from django.views.generic import ListView, View, DetailView, TemplateView, FormView, UpdateView
from datetime import datetime, date
from django.db.models import Q
from django.urls import reverse
from django.http import JsonResponse
from .forms import CreateAccountForm
from django.contrib.auth.mixins import LoginRequiredMixin
from statistics import mean




URL_API = "https://yfapi.net"

# Create your views here.

class HomePage(TemplateView):
    template_name = "homepage.html"

class Dashboard(LoginRequiredMixin, ListView):
    template_name = "dashboard.html"
    model = Stock
    ordering = ['-market_change']

    def get_context_data(self, *args, **kwargs):
        symbols_user = self.request.user.stocks_symbols
        symbols_list = symbols_user.split(',')
        symbols_list_strip = [stock.strip().upper() for stock in symbols_list]
        user_stocks = Stock.objects.filter(symbol__in=symbols_list_strip)
        context = super().get_context_data(*args, **kwargs)
        context["user_stocks"] = user_stocks
        return context

class RefreshStockView(LoginRequiredMixin, View):
    def get_api_data(self, user_symbols):

        url = f"{URL_API}/v6/finance/quote"

        headers = {
    'x-api-key': "F3pqoMA0Df5hjqFbOgnVm6zh9tOOplWP4RwRzF2H",
    "Content-Type": "application/json"
    }


        params = {
        "region": "US",
        "lang": "en",
        "symbols": user_symbols
        }
        print(params)

        response = requests.request("GET", url, headers=headers, params=params)

        if response.ok:
            data = response.json()
            return data["quoteResponse"]["result"]
        else:
            return None


    def post(self, request, *args, **kwargs):
        symbols = request.user.stocks_symbols
        new_symbols = []
        print(symbols)
        user_symbols = symbols.split(",")
        for symbol in user_symbols:
            symbol = symbol.strip().upper()
            new_symbols.append(symbol)
        print(user_symbols)
        new_user_symbols = ",".join(new_symbols)
        print(user_symbols)
        stock_data = self.get_api_data(new_user_symbols)

        for data in stock_data:
            symbol = data['symbol']

            try:
                stock = Stock.objects.get(symbol=symbol)
                stock.company_name = data["longName"]
                stock.current_value = data["regularMarketPrice"]
                stock.symbol = data["symbol"]
                stock.market_change = data["regularMarketChangePercent"]
                stock.growth_indicator = True if stock.market_change > 0 else False
                stock.save()
            except Stock.DoesNotExist:
                Stock.objects.create(
                    company_name = data["longName"],
                    current_value = data["regularMarketPrice"],
                    symbol = data["symbol"],
                    market_change = data["regularMarketChangePercent"]
                )



        return redirect('stock:dashboard')


class StockPage(LoginRequiredMixin, DetailView):
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

class GetDataChart(LoginRequiredMixin, View):

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

class GetBuyRecomendation(View):
    def get_buy_recomendations(self, **kwargs):
        pk = self.kwargs['pk']
        stock = Stock.objects.get(pk=pk)
        data_stocks = DayDataStock.objects.filter(stock_id = stock).order_by('date_value')
        close_values = []
        for value in data_stocks:
            close_values.append(value.close_value)

        return close_values

    def post(self, request, *args, **kwargs):

        close_values_list = self.get_buy_recomendations()

        stock = Stock.objects.get(pk=kwargs['pk'])
        today_value = close_values_list[-1]

        if today_value < mean(close_values_list[-8:-1]):
            if today_value < mean(close_values_list[-31:-1]):
                stock.buy_recomendation = "Buy"
            elif today_value < mean(close_values_list):
                stock.buy_recomendation = "Buy"
            elif today_value > mean(close_values_list[-31:-1]):
                stock.buy_recomendation = "Sell"
        elif today_value > mean(close_values_list[-8:-1]):
            if today_value < mean(close_values_list):
                stock.buy_recomendation = "Buy"
            elif today_value < mean(close_values_list[-31:-1]):
                stock.buy_recomendation = "Buy"
            else:
                stock.buy_recomendation = "Sell"

        stock.save()
        return redirect(reverse('stock:stockpage', kwargs={'pk': kwargs['pk']}))

class CreateAccount(FormView):
    template_name= "createaccount.html"
    form_class = CreateAccountForm

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('stock:login')

class EditProfile(LoginRequiredMixin, UpdateView):
    template_name= "editprofile.html"
    model = User
    fields = ['first_name', 'last_name', 'email', 'stocks_symbols', 'profile_pic',]

    def get_success_url(self):
        return reverse('stock:dashboard')

