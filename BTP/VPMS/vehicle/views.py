from django.db.models import Q
from django.shortcuts import render,redirect, get_object_or_404
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.http import JsonResponse

from datetime import date
from datetime import datetime, timedelta, time
import random
import json
import os
import json
from django.conf import settings
import traceback



# Create your views here.


# import datetime

def get_monthly_costs(parking_data):
    monthly_costs = {}
    # L1=[]

    for transaction in parking_data:
        in_datetime = datetime.strptime(str(transaction["indate"]) + " " + str(transaction["intime"]), "%Y-%m-%d %H:%M")
        out_datetime = datetime.strptime(str(transaction["outdate"]) + " " + str(transaction["outtime"]), "%Y-%m-%d %H:%M")
        total_time = (out_datetime - in_datetime).total_seconds() / 3600.0
        total_cost = transaction['cost']

        transaction_month = out_datetime.strftime("%Y-%m")

        if transaction_month not in monthly_costs:
            monthly_costs[transaction_month] = 0.0
        # L1.append(total_cost)
        monthly_costs[transaction_month] += float(total_cost)
    # print(L1)
    # print(monthly_costs)
    return monthly_costs
def calc_cost(startdate, enddate, starttime, endtime, cost_rate):
    start = datetime.strptime(str(startdate) + ' ' + str(starttime), '%Y-%m-%d %H:%M')
    end = datetime.strptime(str(enddate) + ' ' + str(endtime), '%Y-%m-%d %H:%M')
    duration = end - start
    hours = duration.total_seconds() / 3600
    # print(cost_rate)
    cost = round(hours * float(cost_rate), 2)
    print((start,end,cost,hours))
    return cost


def register(request):
    er = 'yes'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username is already taken'})
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email is already taken'})
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        # return render(request, 'index.html', {'errorsucc':"Successfully registered"})
        er = 'no'
        u = username
        p = password
        user = authenticate(username=u, password=p)
        try:
            if user.is_staff:
                login(request,user)
                error = "no"
            else:
                login(request,user)
                error = "no"
        except:
            error = "yes"
        # return redirect('')
    d = {'er': er}
    return render(request, 'register.html',d)
def Index(request):
    if request.user.is_authenticated:
        # return redirect('logout')
        return redirect('admin_home')
    error = ""
    if request.method == 'POST':
        u = request.POST['username']
        p = request.POST['password']
        user = authenticate(username=u, password=p)
        try:
            if user.is_staff:
                login(request,user)
                error = "no"
            else:
                login(request,user)
                error = "no"
        except:
            error = "yes"
    d = {'error': error}
    return render(request, 'index.html', d)





def admin_home(request):
    if not request.user.is_authenticated:
        return redirect('index')
    today = datetime.now().date()
    yesterday = today - timedelta(1)
    lasts = today - timedelta(7)

    tv = Vehicle.objects.filter(pdate=today).count()
    iv = Vehicle.objects.filter(status='In').count()
    yv = Vehicle.objects.filter(pdate=yesterday).count()
    ls = Vehicle.objects.filter(pdate__gte=lasts,pdate__lte=today).count()
    totalv = Vehicle.objects.all().count()

    d = {'tv':tv,'yv':yv,'ls':ls,'totalv':totalv,'Instatus':iv}
    return render(request,'admin_home.html',d)



def Logout(request):
    logout(request)
    return redirect('index')


def changepassword(request):
    if not request.user.is_authenticated:
        return redirect('index')
    error = ""
    if request.method=="POST":
        o = request.POST['currentpassword']
        n = request.POST['newpassword']
        c = request.POST['confirmpassword']
        if c == n:
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(n)
            u.save()
            error = "yes"
        else:
            error = "not"
    d = {'error':error}
    return render(request,'changepassword.html',d)


def search(request):
    q = request.GET.get('searchdata')

    try:
        vehicle = Vehicle.objects.filter(Q(parkingnumber=q))
        vehiclecount = Vehicle.objects.filter(Q(parkingnumber=q)).count()

    except:
        vehicle = ""
    d = {'vehicle': vehicle,'q':q,'vehiclecount':vehiclecount}
    return render(request, 'search.html',d)


def add_vehicle(request):
    if not request.user.is_authenticated:
        return redirect('index')
    error = ""
    category1 = Category.objects.all()
    if request.method=="POST":
        pn = str(random.randint(10000000, 99999999))
        ct = request.POST['category']
        vc = request.POST['username']
        rn = request.POST['regno']
        on = request.POST['ownername']
        oc = request.POST['ownercontact']
        pd = request.POST['pdate']
        it = request.POST['intime']
        status = "In"
        category = Category.objects.get(categoryname=ct)
        try:
            u = User.objects.get(username__exact=vc)

            try:
                Vehicle.objects.create(parkingnumber=pn,category=category,vehiclecompany=vc,regno=rn,ownername=on,ownercontact=oc,pdate=pd,intime=it,outtime='',parkingcharge='',remark='',status=status)
                error = "no"
                return redirect('view_parking_map', vechicleID=rn)
            except:
                error = "yes"
                traceback.print_exc()
        except:
            error = "no_user"
    d = {'error':error,'category1':category1}
    return render(request, 'add_vehicle.html', d)


def manage_incomingvehicle(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.is_staff:
        vehicle = Vehicle.objects.filter(status="In").exclude(slotID='')
        d = {'vehicle':vehicle}
    else:
        vehicle = Vehicle.objects.filter(status="In",vehiclecompany=request.user.username).exclude(slotID='')
        d = {'vehicle':vehicle}
    return render(request, 'manage_incomingvehicle.html', d)

def manage_outgoingvehicle(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.is_staff:
        vehicle = Vehicle.objects.filter(status="Out").exclude(slotID='')
        d = {'vehicle':vehicle}
    else:
        vehicle = Vehicle.objects.filter(status="Out",vehiclecompany=request.user.username).exclude(slotID='')
        d = {'vehicle':vehicle}
    return render(request, 'manage_outgoingvehicle.html', d)


def view_incomingdetail(request,pid):
    if not request.user.is_authenticated:
        return redirect('index')
    error = ""
    vehicle = Vehicle.objects.get(id=pid)
    if request.method == 'POST':
        rm = request.POST['remark']
        ot = request.POST['outtime']
        pc = request.POST['parkingcharge']
        
        od = request.POST['outdate']
        pc = calc_cost(vehicle.pdate,od,vehicle.intime,ot,pc)
        status = "Out"
        try:
            vehicle.remark = rm
            vehicle.outtime = ot
            vehicle.parkingcharge = pc
            vehicle.status = status
            vehicle.outdate = od
            vehicle.save()
            error = "no"
        except:
            error = "yes"

    d = {'vehicle': vehicle,'error':error}
    return render(request,'view_incomingdetail.html', d)



def view_outgoingdetail(request,pid):
    if not request.user.is_authenticated:
        return redirect('index')
    vehicle = Vehicle.objects.get(id=pid)

    d = {'vehicle': vehicle}
    return render(request,'view_outgoingdetail.html', d)


def print_detail(request,pid):
    if not request.user.is_authenticated:
        return redirect('index')
    vehicle = Vehicle.objects.get(id=pid)

    d = {'vehicle': vehicle}
    return render(request,'print.html', d)


def delete_detail(request, pid):
    if not request.user.is_authenticated:
        return redirect('index')
    vehicle = Vehicle.objects.get(id=pid)
    vehicle.delete()
    return redirect('manage_outgoingvehicle')

def view_parking_map(request,vechicleID):
    if not request.user.is_authenticated:
        return redirect('index')
    slottemp = Vehicle.objects.all()
    L=[]
    for i in slottemp:
            if i.status=="In":
                if i.slotID!="":
                    if int(i.slotID) not in L:
                    
                        L.append(int(i.slotID))
    print(L)
    with open(settings.BASE_DIR +'/'+'vehicle'+'/'+ 'parking.json') as f:
        parking_data = json.load(f)
    
    
    # vechicleID = 11
    vehicletemp = Vehicle.objects.filter(regno=vechicleID).order_by('-id')
    # vehicletemp = Vehicle.objects.get(regno=vechicleID)
    vehicletemp = vehicletemp.first()
    vechicleID = vehicletemp.id
    vehicle_instance = get_object_or_404(Vehicle, id=vechicleID)
    vehicle = {'id':vehicle_instance.id, 'slotID':vehicle_instance.slotID,'regno':vehicle_instance.regno}
    # vehicle = Vehicle.objects.get(id=vechicleID)
    # parking_data["spaces"] = [s.replace('"', '') for s in parking_data["spaces"]]
    # parking_data["size"] = [s.replace('"', '') for s in parking_data["size"]]
    # print(json.dumps(L))
    print(vehicle["slotID"])
    temp_slot = -1
    if vehicle["slotID"]!='':
        temp_slot = int(vehicle["slotID"])
    d = {'vehicle': json.dumps(vehicle),'slots_filled':json.dumps(L),'current':temp_slot,'parking_data':json.dumps(parking_data)}
    print(vehicle_instance)
    print(vehicle)
    return render(request,'parking_map.html', d)

def booked_parking_map(request,vechicleID,slotID):
    if not request.user.is_authenticated:
        return redirect('index')
    vehicle = Vehicle.objects.get(id=vechicleID)
    vehicle_instance = get_object_or_404(Vehicle, id=vechicleID)
    vehicle = vehicle_instance
    d = {'vehicle': vehicle_instance}
    return render(request,'parking_map_booked.html', d)

def update_slot(request,vechicleID,slotID):
    #1.get vehicle object based on vehicle id
    if not request.user.is_authenticated:
        return redirect('index')
    try:
        result=Vehicle.objects.filter(id=vechicleID).update(slotID=slotID)
        my_dict = {'result': 'slot changed'}
        status_code = 200 # Replace with your desired status code
        return JsonResponse(my_dict, status=status_code)
    finally:
        my_dict = {'result': 'slot changed'}
        status_code = 200 # Replace with your desired status code
    return JsonResponse(my_dict, status=status_code)


def show_slot_url(request,parking_number):
    
    if not request.user.is_authenticated:
        return redirect('index')
    with open(settings.BASE_DIR +'/'+'vehicle'+'/'+ 'parking.json') as f:
        parking_data = json.load(f)
    if request.user.is_staff:
        try:
            result = Vehicle.objects.get(parkingnumber=parking_number,status="In")
            
            # result = result.first()
            if result.slotID=="":
                d = {'error':"no_active"}
                return render(request, 'admin_home.html', d)
            else:
                d = {'slotID':[int(result.slotID)],'noerr':'yes','parking_data':json.dumps(parking_data),"slots_filled":[int(result.slotID)]}
                return render(request, 'show_url.html', d)
        except Vehicle.DoesNotExist:
            print(parking_number)
            # print(result)
            d = {'error':"no_active"}
            return render(request, 'admin_home.html', d)
        else:
            d = {'error':"exception"}
            return render(request, 'admin_home.html', d)
    else:
        try:
            result = Vehicle.objects.get(parkingnumber=parking_number,status="In",vehiclecompany=request.user.username)
            
            # result = result.first()
            if result.slotID=="":
                d = {'error':"no_active"}
                return render(request, 'admin_home.html', d)
            else:
                d = {'slotID':[int(result.slotID)],'noerr':'yes','parking_data':json.dumps(parking_data),"slots_filled":[int(result.slotID)]}
                return render(request, 'show_url.html', d)
        except Vehicle.DoesNotExist:
            print(parking_number)
            # print(result)
            d = {'error':"no_active"}
            return render(request, 'admin_home.html', d)
        else:
            d = {'error':"exception"}
            return render(request, 'admin_home.html', d)
        
def monthly_bills(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.last_name!='visitor':

        L1=[]
        try:
            objec = Vehicle.objects.filter(vehiclecompany=request.user.username,status='Out').order_by('pdate')
            L=[]
            for i in objec:
                L.append({'cost':i.parkingcharge,'intime':i.intime,'outtime':i.outtime,'indate':i.pdate,'outdate':i.outdate})
            bills = get_monthly_costs(L)
            for i in bills:
                L1.append((i,bills[i]))
            
            
            
            return render(request,'monthly.html',{'bills':L1,'error':'no'})


        except Vehicle.DoesNotExist:
            
            return render(request,'monthly.html',{'bills':[],'error':'yes'})
    else:
        return redirect('admin_home')
    
def view_monthly_bills(request,month):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.last_name!='visitor':
        L=[]
        try:
            objec = Vehicle.objects.filter(vehiclecompany=request.user.username,status='Out').order_by('outdate')
            for i in objec:
                if str(i.outdate)[:7]==month:
                    L.append(i)
        except Vehicle.DoesNotExist:
            L=[]
        

        return render(request,'view_monthly_bills.html',{'vehicle':L,'month':month})
    else:
        return redirect('admin_home')
    
def changegrid(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if not request.user.is_staff:
        return redirect('admin_home')
    with open(settings.BASE_DIR +'/'+'vehicle'+'/'+ 'gridselect.json') as f:
        parking_data = json.load(f)
    with open(settings.BASE_DIR +'/'+'vehicle'+'/'+ 'parking.json') as f:
        parking_data_live = json.load(f)
    max_height = 400
    data_live = parking_data_live["spaces"]
    data = parking_data["spaces"]
    dicto ={}
    L=[]
    
    for i in data_live:
        dicto[i["id"]]=1
    for i in data:
        try:
            dicto[i["id"]]
            i["inc"]=1
            L.append(i["id"])
            try:
                tempo = Vehicle.objects.get(status='In',slotID=str(i["id"]))
                
                i["inc"]=2
            except Vehicle.DoesNotExist:
                i["inc"]=1
            # print(i)
        except:
            pass

    
    return render(request,'changegrid.html',{'parking_data':json.dumps(parking_data),'already_live':L})

def enable_disable(request,opcode):
    if not request.user.is_authenticated:
        return redirect('index')
    if not request.user.is_staff:
        return redirect('admin_home')
    with open(settings.BASE_DIR +'/'+'vehicle'+'/'+ 'gridselect.json') as f:
        parking_data = json.load(f)
    with open(settings.BASE_DIR +'/'+'vehicle'+'/'+ 'parking.json') as f:
        parking_data_live = json.load(f)
    # max_height = 400
    data_live = parking_data_live["spaces"]
    data = parking_data["spaces"]
    dicto={}
    for i in data_live:
        dicto[i["id"]]=1
        # print(type(i["id"]))
    remove=[]
    add=[]



    stro = ''
    L1=[]
    for i in opcode:
        if i!='-':
            stro+=i
        else:
            if stro!='':
                L1.append(int(stro))
            stro = ''
    print(L1)
    for i in L1:
        try:
            dicto[i]
            remove.append(i)

        except:
            add.append(i)
    maxx=-1
    maxy=-1
    L3=[]
    for i in range(len(data_live)):
        if data_live[i]["id"] not in remove:
            L3.append(data_live[i])
            maxx = max(maxx,data_live[i]["x"])
            maxy = max(maxy,data_live[i]["y"])
    for i in add:
        templ = data[i-1]
        L3.append({"x":templ["x"],"y":templ["y"],"width":templ["width"],"height":templ["height"],"id":templ["id"]})
        maxx = max(maxx,templ["x"])
        maxy = max(maxy,templ["y"])
    # parking_data_live["size"] = {"width":maxx+150,"height":maxy+150}
    print((maxx,maxy))
    parking_data_live["spaces"] = L3
    with open(settings.BASE_DIR +'/'+'vehicle'+'/'+ 'parking.json', "w") as outfile:
        json.dump(parking_data_live, outfile)
    print(parking_data_live)



    return redirect('changegrid')

def increase(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if not request.user.is_staff:
        return redirect('admin_home')
    with open(settings.BASE_DIR +'/'+'vehicle'+'/'+ 'gridselect.json') as f:
        parking_data = json.load(f)
    data = parking_data["spaces"]
    # print(len(data))
    data1 = data[len(data)-12:].copy()
    # print(len(data))
    for i in range(len(data1)):
        data1[i]['y']+=80
        data1[i]['id']+=12
    # print(len(data))
    # data = data[:len(data)-12]
    with open(settings.BASE_DIR +'/'+'vehicle'+'/'+ 'gridselect.json') as f:
        parking_data = json.load(f)
    data = parking_data["spaces"]
    maxy = data1[0]["y"]+150
    for i in data1:
        data.append(i)
    # print(len(data))
    parking_data["spaces"] = data
    parking_data["size"]["height"] = maxy
    with open(settings.BASE_DIR +'/'+'vehicle'+'/'+ 'gridselect.json', "w") as outfile:
        json.dump(parking_data, outfile)
    # for i in data1:

    # print(len(data))
    return redirect('changegrid')

def decrease(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if not request.user.is_staff:
        return redirect('admin_home')
    with open(settings.BASE_DIR +'/'+'vehicle'+'/'+ 'gridselect.json') as f:
        parking_data = json.load(f)
    data = parking_data["spaces"]
    if len(data)==12:
        err = "dont"
        return render(request,'admin_home.html',{"err":err})
    # print(len(data))
    with open(settings.BASE_DIR +'/'+'vehicle'+'/'+ 'parking.json') as f:
        parking_data_live = json.load(f)
    # max_height = 400
    data_live = parking_data_live["spaces"]
    L=[]
    count = 0
    for i in data[len(data)-12:]:
        objec = Vehicle.objects.filter(status="In",slotID=i["id"]).count()
        for j in data_live:
            if int(j["id"])==int(i["id"]):
                count+=1

        if objec!=0:
            count+=1
    
    err="no"
    if count==0:
        data = data[:len(data)-12]
        # print(len(data))
        maxy = data[len(data)-2]["y"]+150
        parking_data["spaces"] = data
        parking_data["size"]["height"] = maxy
        with open(settings.BASE_DIR +'/'+'vehicle'+'/'+ 'gridselect.json', "w") as outfile:
            json.dump(parking_data, outfile)
    else:
        err="yes"
    return render(request,'admin_home.html',{"err":err})



