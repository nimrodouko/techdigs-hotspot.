#!/usr/bin/env python
import datetime
from .models import Payment


def clean_the_database():
    things = Payment.get.all()
    time_in_seconds = 10800
    #set time at creation in models, then take the time and start a countdown
       
    pass