from django.shortcuts import render, get_object_or_404, redirect
import random
import routeros_api
from routeros_api import RouterOsApiPool

import requests
from .models import Amount, Payment, Voucher
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

        def format_phone_number(phone):
            if phone.startswith('07'):
                return '254' + phone[1:]
            elif phone.startswith('+254'):
                return phone[1:]
            return phone
        

        payload = {
                        
                            "BusinessShortCode": "174379",    
                            "Password": password,    
                            "Timestamp":timestamp,    
                            "TransactionType": "CustomerPayBillOnline",    
                            "Amount": amount,    
                            "PartyA":format_phone_number(phonenumber),    
                            "PartyB":shortcode,    
                            "PhoneNumber": format_phone_number(phonenumber),    
                            "CallBackURL": "https://0e6892e0ad3b.ngrok-free.app/callback/{package_id}",  #kumbuka kutumia ngrok url  
                            "AccountReference":"Test",    
                            "TransactionDesc":"Test"
                            }
                    
        api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        response = requests.request("POST", api_url, headers = headers, json = payload)
        print(response.text.encode('utf8'))
        safaricom_response = response.json()
        checkout_id = safaricom_response.get('CheckoutRequestID')

        Payment.objects.create(phonenumber = phonenumber,checkoutrequestid = checkout_id, amountpaid = amount)
        the_response = JsonResponse({"message": "STK push initiated", "safaricom_response": response.json()})
        return render(request, "waiting.html", {"checkout_id": checkout_id})
      
       
        
    else:
        return HttpResponse("Only POST requests allowed", status=405)

@csrf_exempt
def callback(request,package_id):
    if request.method == 'POST':
        mpesa_response = json.loads(request.body)
        checkout_id =  mpesa_response['Body']['stkCallback']['CheckoutRequestID']
        result_code = mpesa_response['Body']['stkCallback']['ResultCode']
        try:
            truepayment = Payment.objects.get(checkoutrequestid=checkout_id)
            truepayment.confirmed = True
            truepayment.save()
            print("truepayment:",truepayment)
           
        except Payment.DoesNotExist:
            return HttpResponse("Payment not found", status=404)
        if result_code != 0:
            print("payment failed")
            return render(request,'index.html')
        else:
            codeuse = generete_code()
            duration = get_object_or_404(Amount, id= package_id)
            voucher = Voucher.objects.create(code=codeuse, duration=duration)
            mikrotic_router_connection(codeuse,voucher.duration)

            

            
            return render(request,"paymentsuccess")

          
def mikrotic_router_connection(username, duration):
    
    ip = settings.IP
    username = settings.USERNAME
    password = settings.PASSWORD
    port = settings.PORT

    connection = routeros_api.RouterOsApiPool(ip,username,password,port,plaintext_login=True,use_ssl=False,ssl_verify=True,ssl_verify_hostname=True,ssl_context=None,)
    api = connection.get_api()
    users = api.get_resource('/ip/hotspot/user')
    users.add(name=username, password=username, profile='default', limit_uptime =duration)

def reconnection():
    
    pass    


def generete_code():
    alphabets = ['A','B', 'C', 'D', 'E', 'F', 'G', 'H','I','J','K','L','M','N','O', 'P','Q', 'R', 'S', 'T','U', 'V', 'W', 'X', 'Y','Z']
    #nambas = [0,1,2,3,4,5,6,7,8,9]
    code = random.choice(alphabets)+str(random.randint(0,9))+random.choice(alphabets)+str(random.randint(0,9))+random.choice(alphabets)+str(random.randint(0,9))
  
    return code

def check_payment_status(request, checkout_id):
    try:
        payment = Payment.objects.get(checkoutrequestid=checkout_id)
        if payment.confirmed:
            return JsonResponse({"status":"confirmed"})
        else:
            return JsonResponse({"status":"waiting"})
    except Payment.DoesNotExist:
        return JsonResponse({"status":"not found"})
    
def payment_success(request):
    return render(request, "success.html")










