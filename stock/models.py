from django.db import models
from django.contrib.auth.models import AbstractUser

# Stock model
class Stock(models.Model):
    company_name = models.CharField(max_length=100, default='')
    logo = models.ImageField(upload_to="stock_logos", default=None)
    current_value = models.FloatField(default=0)
    company_description = models.TextField(max_length=1000, default='')
    founders_name = models.CharField(max_length=100, default='')
    foundation_year = models.IntegerField(default=0)
    company_website = models.CharField(max_length=100, default='')
    symbol = models.CharField(max_length=10, default='')
    growth_indicator = models.BooleanField(default=True)
    market_change = models.FloatField(default=0)
    buy_recomendation = models.CharField(default="Refresh Data")

    def get_pk(self):
         return self.pk

    def __str__(self):
        return self.company_name


class DayDataStock(models.Model):
      stock = models.ForeignKey(Stock, related_name="day_data_id", on_delete=models.CASCADE)
      date_value = models.DateField()
      close_value = models.FloatField(default=0)

#user
class User(AbstractUser):
    stocks_symbols = models.CharField(default="AAPL,MSFT,GOOG,AMZN,NVDA,META,TSLA,JPM,JNJ,WMT")
    profile_pic = models.ImageField(upload_to="profile_pic", blank=True)