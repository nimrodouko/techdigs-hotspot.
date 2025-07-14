from django.shortcuts import render, redirect
import random
from librouteros import connect





# Create your views here.

# deliverables::
        
        #create code generating code
        #create the m-pesa bridge - django rest framework
      
        #create the mikrotic router - site connection.

def check_mpesa_payment():
    pass
          
def mikrotic_router_connection():
    try:
        api =connect(
            host ='#', #routerip
            username = '#',#your mikrtic username
            password = '#',
            port = 8728 #default APi port
        )
        users = api('ip/hotspot/user/print') #hii ni ya kutest
        for user in users:
            print(user)
        return api
    except Exception as e:
        print(f"failed to cnnect because of {e}")
        return None

def confirms(request):
    return render(request,'mpesa.html')

def generete_code():
    alphabets = ['A','B', 'C', 'D', 'E', 'F', 'G', 'H','I','J','K','L','M','N','O', 'P','Q', 'R', 'S', 'T','U', 'V', 'W', 'X', 'Y','Z']
    #nambas = [0,1,2,3,4,5,6,7,8,9]
    code = random.choice(alphabets)+str(random.randint(0,9))+random.choice(alphabets)+str(random.randint(0,9))+random.choice(alphabets)+str(random.randint(0,9))
    print(code)
    return code





#page main ya site                                                                                                                                                                            
def index(request):
    #after confirmation of m-pesa payment
    code = generete_code()
    return render(request, 'index.html', {'code': code})
