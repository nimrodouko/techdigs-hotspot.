from django.shortcuts import render
import random


# Create your views here.

# deliverables::
        
        #create code generating code
        #create the m-pesa bridge
      
        #create the mikrotic router - site connection.
          


def generete_code():
    alphabets = ['A','B', 'C', 'D', 'E', 'F', 'G', 'H','I','J','K','L','M','N','O', 'P','Q', 'R', 'S', 'T','U', 'V', 'W', 'X', 'Y','Z']
    nambas = [0,1,2,3,4,5,6,7,8,9]
    code = random.choice(alphabets)+str(random.randint(0,9))+random.choice(alphabets)+str(random.randint(0,9))+random.choice(alphabets)+str(random.randint(0,9))
    print(code)
    return code


#page main ya site
def index(request):
    #after confirmation of m-pesa payment
    code = generete_code()
    return render(request, 'index.html', {'code': code})
