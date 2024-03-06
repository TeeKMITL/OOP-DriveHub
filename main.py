from typing import Dict,Any,List,Union
from fastapi import FastAPI,Request,Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import date,timedelta

class WebsiteController:
    def __init__(self):
        self.__user_list = []
        self.__customer_list = []
        self.__lender_list = []
        self.__reservation_list = []
        self.__car_list = []

    @property
    def user_list(self):
        return self.__user_list
    @property
    def customer_list(self):
        return self.__customer_list
    @property
    def lender_list(self):
        return self.__lender_list
    @property
    def reservation_list(self):
        return self.__reservation_list
    @property
    def car_list(self):
        return self.__car_list

    def add_reservation(self,user,car,amount,start_date,end_date):
        temp = start_date.split("/")
        date1 = date(int(float(temp[2])),int(temp[1]),int(temp[0]))
        temp = end_date.split("/")
        date2 = date(int(float(temp[2])),int(temp[1]),int(temp[0]))
        delta = date2-date1
        for i in range(delta.days + 1):
            a = date1 + timedelta(days=i)
            b = str(a)
            splitted = b.split("-")
            r_date = DMY(int(splitted[2]),int(splitted[1]),int(splitted[0]))
            car.unavailable_dates.append(r_date)
        reserve = Reservation(user,car,amount,start_date,end_date)
        self.reservation_list.append(reserve)
        user.add_reservation(reserve)
        return reserve

    def add_user(self,id,name,phone_number,password):
        self.user_list.append(User(id,name,phone_number,password))
    def add_lender(self,id,name,phone_number,password):
        lender_instance = Lender(id,name,phone_number,password)
        self.lender_list.append(lender_instance)
        return lender_instance
    def add_customer(self,id,name,phone_number,password):
        customer_instance = Customer(id,name,phone_number,password)
        self.customer_list.append(customer_instance)
        return customer_instance
    def remove_car(self, car_license):
        for cars in self.car_list:
            if cars.license == car_license:
                for lenders in self.lender_list:
                    if lenders == cars.owner:
                        self.car_list.remove(cars)
    def check_available_car(self, location, start_date, end_date):
        unavailable = False
        available_car = []
        temp = start_date.split("/")
        start = DMY(int(temp[0]),int(temp[1]),int(temp[2]))
        temp = end_date.split("/")
        end = DMY(int(temp[0]),int(temp[1]),int(temp[2]))
        for car in self.car_list:
            if car.location == location:
                if car.status == "AVAILABLE":
                    for date in car.unavailable_dates:
                        if date.year == start.year and date.month == start.month:
                            if date.day >= start.day and date.day <= end.day:
                                unavailable = True
                                break
                    if not unavailable:
                        available_car.append(car)
        return available_car
    
class Reservation:
    def __init__(self,user,car,amount,start_date,end_date):
        self.__user = user
        self.__car = car
        self.__amount = amount
        self.__start_date = start_date
        self.__end_date = end_date
    @property
    def user(self):
        return self.__user
    @property
    def car(self):
        return self.__car
    @property
    def amount(self):
        return self.__amount
    @property
    def start_date(self):
        return self.__start_date
    @property
    def end_date(self):
        return self.__end_date
class User:
    def __init__(self,id,name,phone_number,password):
        self.__id = id
        self.__name = name
        self.__phone_number = phone_number
        self.__password = password
    @property
    def id(self):
        return self.__id
    @property
    def name(self):
        return self.__name
    @property
    def phone_number(self):
        return self.__phone_number
    @property
    def password(self):
        return self.__password
class Customer(User):
    def __init__(self,id,name,phone_number,password):
        super().__init__(id,name,phone_number,password)
        self.__reservations = []
    @property
    def reservations(self):
        return self.__reservations
    def add_reservation(self, reservation):
        self.reservations.append(reservation)

class Lender(User):
    def __init__(self,id,name,phone_number,password):
        super().__init__(id,name,phone_number,password)
        self.__lent_cars = []
    
    @property
    def lent_cars(self):
        return self.__lent_cars
    
    def lend_car(self,status,license,location,price):
        temp = Car(status,license,self,location,price)
        self.lent_cars.append(temp)
        return temp

    def update_car_status(self,updated_status,car_instance):
        if (self == car_instance.owner):
            if updated_status == 0:
                car_instance.change_status("NOT AVAILABLE")
            elif updated_status == 1:
                car_instance.change_status("AVAILABLE")
        
class Car:
    def __init__(self,status,license,owner,location,price):
        self.__status = status
        self.__license = license
        self.__owner = owner
        self.__location = location
        self.__price = price
        self.__unavailable_dates = []

    def reserve_date(self,day,month,year):
        self.unavailable_dates.append(DMY(day,month,year))
    
    def change_status(self,new_status):
        self.__status = new_status

    @property
    def status(self):
        return self.__status
    
    @property
    def license(self):
        return self.__license
    
    @property
    def owner(self):
        return self.__owner

    @property
    def location(self):
        return self.__location
    
    @property
    def price(self):
        return self.__price
    
    @property
    def unavailable_dates(self):
        return self.__unavailable_dates


class DMY:
    def __init__(self,day,month,year):
        self.__day = day
        self.__month = month
        self.__year = year

    @property
    def day(self):
        return self.__day
    @property
    def month(self):
        return self.__month
    @property
    def year(self):
        return self.__year

site = WebsiteController()
me = site.add_lender(123,"Tee","0649494466","1234")
me1 = site.add_customer(124,"Eet","012345678","1234")
# mycar = me.lend_car("AVAILABLE","AB123","HOME",100)
# site.car_list.append(mycar)
# site.add_reservation(me1,mycar,100,"1/1/1","5/1/1")
# print(site.check_available_car("HOME","1/1/1","2/2/2"))

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/api/customer", tags=["API"])
def get_all_customer():
    return {"Customers": {index: str(obj) for index, obj in enumerate(site.customer_list)}}

@app.get("/api/lender", tags=["API"])
def get_all_lender():
    return {"Lenders": {index: str(obj) for index, obj in enumerate(site.lender_list)}}

@app.get("/customer/{customer_id}/home", tags =["Customer"])
def customer_home_page(request: Request, customer_id:int):
    return templates.TemplateResponse("customer_home.html", {"request": request, "customer_id": customer_id})

@app.get("/customer/{customer_id}/reservations", tags=["Customer"])
def get_all_reservations_page(customer_id:int) -> dict:
    for customers in site.customer_list:
        if customers.id == customer_id:
            temp = customers.reservations
            return {"Reservations": {index: str(obj) for index, obj in enumerate(temp)}}
    return {"Error":"Error"}

@app.get("/customer/{customer_id}/find_car", tags = ["Customer"])
def find_car_page(request:Request,customer_id: int):
    return templates.TemplateResponse("find_car.html", {"request":request, "customer_id": customer_id})

@app.get("/customer/{customer_id}/make_reservation", tags = ["Customer"])
def make_reservation_page(request: Request,customer_id:int):
    return templates.TemplateResponse("make_reservation.html", {"request": request, "customer_id": customer_id})

@app.post("/find_car")
async def find_car_post(request:Request, customer_id:int = Form(...), location:str = Form(...), start_date:date = Form(...), end_date:date = Form(...)):
    start = str(start_date).split("-")
    end = str(end_date).split("-")
    new_start = f"{start[2]}/{start[1]}/{start[0]}"
    new_end = f"{end[2]}/{end[1]}/{end[0]}"
    temp = site.check_available_car(location,new_start,new_end)
    return {"Available Car(s)" : {index: {"Car License": obj.license, "Price": obj.price} for index, obj in enumerate(temp)}}

@app.post("/make_reservation")
async def make_reservation_post(request: Request, customer_id:int = Form(...), license:str = Form(...), amount:int=Form(...),start_date:date = Form(...), end_date:date = Form(...)):
    for customers in site.customer_list:
        if customers.id == customer_id:
            for cars in site.car_list:
                if cars.license == license:
                    start = str(start_date).split("-")
                    end = str(end_date).split("-")
                    new_start = f"{start[2]}/{start[1]}/{start[0]}"
                    new_end = f"{end[2]}/{end[1]}/{end[0]}"
                    site.add_reservation(customers,cars,amount,new_start,new_end)
                    return {"Successful Reservation":{"From" : new_start, "To": new_end}}

@app.get("/lender/{lender_id}/home", tags =["Lender"])
def lender_home_page(request: Request, lender_id:int):
    return templates.TemplateResponse("lender_home.html", {"request": request, "lender_id": lender_id})

@app.get('/lender/{lender_id}/update_car', tags =["Lender"])
def update_car_page(request: Request, lender_id:int):
    return templates.TemplateResponse("update_car.html", {"request": request, "lender_id": lender_id})

@app.get("/lender/{lender_id}/add_car", tags =["Lender"])
def add_car_page(request:Request, lender_id:int):
    return templates.TemplateResponse("add_car.html", {"request": request, "lender_id": lender_id})

@app.get("/lender/{lender_id}/get_car_unavailable_dates", tags =["Lender"])
def get_car_unavailable_dates_page(request:Request, lender_id:int):
    return templates.TemplateResponse("get_car_unavailable_dates.html", {"request": request, "lender_id": lender_id})

@app.get("/lender/{lender_id}/car_list", tags=["Lender"])
def car_list(lender_id:int) -> dict:
    for lenders in site.lender_list:
        if lenders.id == lender_id:
            temp = lenders.lent_cars
            return {"Lent Cars": {index: {"license": obj.license, "status": obj.status, "price":obj.price, "location":obj.location} for index, obj in enumerate(temp)}}
    return {"Error"}

@app.post("/get_car_unavailable_dates", tags = ["Lender"])
async def get_car_unavailable_dates_post(request: Request,lender_id:int = Form(...), license: str = Form(...)):
    for cars in site.car_list:
        if cars.license == license:
            if cars.owner.id == lender_id:
                return {"Car Unavailable Dates" : {index: {"DAY" : obj.day, "MONTH": obj.month, "YEAR": obj.year} for index, obj in enumerate(cars.unavailable_dates)}}
    return {"Error"}

@app.post("/add_car", tags =["API"])
async def add_car_post(request: Request, lender_id: int = Form(...),license:str=Form(...), location: str = Form(...), price: int = Form(...)):
    for lenders in site.lender_list:
        if lenders.id == lender_id:
            temp = lenders.lend_car("AVAILABLE",license,location,price)
            site.car_list.append(temp)
            return {"Successful"}
    return {"Not Successful"}

@app.post("/update_car", tags =["API"])
async def update_car_post(request: Request, lender_id: int = Form(...), new_status: int = Form(...), license: str = Form(...)):
    if lender_id is None:
        return {"error": "Lender ID not provided"}
    if new_status != 1 and new_status != 0:
        return {"Not Successful"}
    for Lenders in site.lender_list:
        if(Lenders.id == lender_id):
            for Cars in Lenders.lent_cars:
                if (Cars.license == license):
                    Lenders.update_car_status(new_status,Cars)
                    return {"Car Status Changed to":Cars.status}
    return{"Not Successful"}

if __name__=="__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")