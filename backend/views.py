from django.shortcuts import render, get_object_or_404, redirect
import random
import routeros_api
from routeros_api import RouterOsApiPool

import requests
from .models import Amount, Payment
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse, HttpResponse
import base64
from datetime import datetime
from django.conf import settings


# Create your views here.

# deliverables::
        
        #create code generating code
        #create the m-pesa bridge - lipa na m-sape
      
        #create the mikrotic router - site connection.
        #page main ya site
        # 

                                                                                                                                                                              

def index(request):
    
    code = generete_code()
    internet_packages ={'packages':Amount.objects.all()}
   
    return render(request, 'index.html',internet_packages)

def confirms(request, package_id):
    package = get_object_or_404(Amount, id = package_id)
    return render(request,'mpesa.html', {'package':package})




@csrf_exempt
def mpesa_payment(request, package_id):
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    passkey = settings.MPESA_PASSKEY 
    print(consumer_key)

    encoded = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
            #daraja 2.o 
    if request.method == 'POST':
        access = requests.get(
                        'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
            headers={
                            'Authorization':  f'Basic {encoded}'}
                    )


        if access.status_code != 200:
            print("Failed to get access token:", access.status_code, access.text)
            return HttpResponse("Access token failure", status=500)

        access_token = access.json().get('access_token')
        print("Access token:", access_token)

        headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
        package = get_object_or_404(Amount, id = package_id)
        amount = package.amount
        phonenumber= request.POST.get('reciever')
          
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
         
        shortcode = "174379"
        data = shortcode + passkey + timestamp
        password = base64.b64encode(data.encode()).decode()
        

        payload = {
                        
                            "BusinessShortCode": "174379",    
                            "Password": password,    
                            "Timestamp":timestamp,    
                            "TransactionType": "CustomerPayBillOnline",    
                            "Amount": amount,    
                            "PartyA":phonenumber,    
                            "PartyB":shortcode,    
                            "PhoneNumber": phonenumber,    
                            "CallBackURL": "https://5796e7f0cb56.ngrok-free.app/callback/",  #kumbuka kutumia ngrok url  
                            "AccountReference":"Test",    
                            "TransactionDesc":"Test"
                            }
                    
        api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        response = requests.request("POST", api_url, headers = headers, json = payload)
        print(response.text.encode('utf8'))
        safaricom_response = response.json()
        checkout_id = safaricom_response.get('CheckoutRequestID')

        Payment.objects.create(phonenumber = phonenumber,checkoutrequestid = checkout_id, amountpaid = amount)
        return JsonResponse({"message": "STK push initiated", "safaricom_response": response.json()})
      
       
        
    else:
        return HttpResponse("Only POST requests allowed", status=405)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        mpesa_response = json.loads(request.body)
        checkout_id =  mpesa_response['Body']['stkCallback']['CheckoutRequestID']
        result_code = mpesa_response['Body']['stkCallback']['ResultCode']
        try:
            truepayment = Payment.objects.get(checkoutrequestid=checkout_id)
            print("truepayment",truepayment)
           
        except Payment.DoesNotExist:
            return HttpResponse("Payment not found", status=404)
        if result_code != 0:
            print("payment failed")
            return render(request,'index.html')
        else:
            
            return render(request,"paymentsuccess")

          
def mikrotic_router_connection():
    try:
        api_pool = RouterOsApiPool(
                host='192.168.88.1',  # MikroTik IP
                username='admin',
                password='yourpassword',
                port=8728,  # API port
                plaintext_login=True
                )
        users = api('ip/hotspot/user/print') #hii ni ya kutest
        for user in users:
            print(user)
        return api
    except Exception as e:
        print(f"failed to cnnect because of {e}")
        return None


def generete_code():
    alphabets = ['A','B', 'C', 'D', 'E', 'F', 'G', 'H','I','J','K','L','M','N','O', 'P','Q', 'R', 'S', 'T','U', 'V', 'W', 'X', 'Y','Z']
    #nambas = [0,1,2,3,4,5,6,7,8,9]
    code = random.choice(alphabets)+str(random.randint(0,9))+random.choice(alphabets)+str(random.randint(0,9))+random.choice(alphabets)+str(random.randint(0,9))
    print(code)
    return code








