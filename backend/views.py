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
                            "CallBackURL": "https://0e6892e0ad3b.ngrok-free.app/callback/",  #kumbuka kutumia ngrok url  
                            "AccountReference":"Test",    
                            "TransactionDesc":"Test"
                            }
                    
        api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        response = requests.request("POST", api_url, headers = headers, json = payload)
        print(response.text.encode('utf8'))
        safaricom_response = response.json()
        the_response = JsonResponse({"message": "STK push initiated", "safaricom_response": response.json()})
        
    else:
        return HttpResponse("Only POST requests allowed", status=405)

@csrf_exempt
def callback(request):
    if request.method == "POST":
        mpesa_response = json.loads(request.body.decode("utf-8"))

        stk_callback = mpesa_response.get("Body", {}).get("stkCallback", {})
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")

        if result_code == 0:
            metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            metadict = {item["Name"]: item.get("Value") for item in metadata}

            receipt = metadict.get("MpesaReceiptNumber")
            amount = metadict.get("Amount")
            phone_number = metadict.get("PhoneNumber")

            if receipt:
                payment, created = Payment.objects.get_or_create(mpesareciept=receipt)
            
          
                mikrotic_router_connection(receipt, receipt)

                return JsonResponse({"ResultCode": 0,"ResultDesc": "Callback processed successfully"})
            

        else:
            return JsonResponse({"ResultCode": 1,"ResultDesc": "Payment failed"})
            
    
          
def mikrotic_router_connection(username, password):
    
    routerip = settings.IP
    routerusername = settings.USERNAME
    routerpassword = settings.PASSWORD
    port = settings.PORT

    connection = routeros_api.RouterOsApiPool(routerip,routerusername,routerpassword,port,plaintext_login=True,use_ssl=False,ssl_verify=True,ssl_verify_hostname=True,ssl_context=None,)
    api = connection.get_api()
    users = api.get_resource('/ip/hotspot/user')
    users.add(name=username, password=password, profile='default', limit_uptime ="3hrs")



def reconnection(request):
    if request.method == "POST":
        value = request.POST.get("reconnection")
        
        try:
            payment = Payment.objects.get(mpesareciept = value)
            if payment.is_expired:
                return HttpResponse("the voucher has expired please recharge")
            mikrotic_router_connection(payment.mpesareciept, payment.mpesareciept)
            return HttpResponse("Reconnection successful")
        
        except Payment.DoesNotExist:
            return HttpResponse("No such code retry or contact management")
        
def payment_success(request):
    return render(request, "success.html")

def payment_failure(request):
    return render(request, "failure.html")

                                                                                                                                                                              

def index(request):
    
 
    internet_packages ={'packages':Amount.objects.all()}
   
    return render(request, 'index.html',internet_packages)

def confirms(request, package_id):
    package = get_object_or_404(Amount, id = package_id)
    return render(request,'mpesa.html', {'package':package})










