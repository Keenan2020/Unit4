import os
import csv
import datetime
from datetime import date
from collections import OrderedDict

from peewee import *

db = SqliteDatabase('inventory.db')


class Product(Model):
    product_id = AutoField() # primary_key=True is implied
    product_name = CharField(max_length=25, unique=True)
    product_quantity = IntegerField()
    product_price = IntegerField()
    date_updated = DateField()

    class Meta:
        database = db


def add_data(**kwargs):
    # print(kwargs)
    kwargs['product_price'] = clean_price(kwargs['product_price'])
    kwargs['date_updated'] = datetime.datetime.strptime(kwargs['date_updated'], '%m/%d/%Y')
    Product.insert(**kwargs).on_conflict(preserve=[Product.product_id, Product.product_name],conflict_target=[Product.product_name],update={Product.product_quantity : kwargs['product_quantity'], Product.product_price : kwargs['product_price'], Product.date_updated : kwargs['date_updated']}).execute()                


def csv_data():
    with open("inventory.csv") as csvfile:
        product_reader = csv.DictReader(csvfile, delimiter= ',')
        #rows = list(product_reader)
        for row in product_reader:
            add_data(**row)
           
def backup_data(): 
    '''Create Backup File'''
    database_data = Product.select()
    with open("backup_file.csv", 'a') as csvfile:
        writer = csv.writer(csvfile)
        fieldnames = ['product_name','product_price','product_quantity','date_updated']
        header = csv.DictWriter(csvfile, fieldnames = fieldnames)
        header.writeheader()

        for row in database_data:
            writer.writerow([
                row.product_name,
                convert_dollar(row.product_price),
                row.product_quantity,
                row.date_updated
            ])
    print("***Data Saved!***")

#Menu Functions            
def view_entry():
    '''View Item Details'''
    clear()
    query = Product.select().order_by(Product.product_id)
    query = list(query)
    print(query)
    #for row in query:
    #    print(row)
    try:
        select = int(input("What is the product ID: ").strip())
        query = Product.select().where(Product.product_id == select)
        print(list(query)[0].__dict__['__data__'])
    except IndexError:
        print("Product ID number is not here.")
    

def add_entry():
    '''Add An Entry '''
    p_name = input("What is the product name: ").strip()
    p_quantity = input("How many of the product is there: ").strip()
    p_price = input("What does the product cost: ").strip()
    now = datetime.datetime.now()
    p_date = now.strftime('%m/%d/%Y')
    
    add_data(product_name=p_name, product_quantity=p_quantity, product_price=p_price, date_updated=p_date)


#Menu
def menu_loop():
    choice = None   
    while choice != 'q':
        
        print("\nStore Inventory")
        print("=" * 15)
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        print("q) Quit\n")      

        choice = input("Action: ").lower().strip()

        if choice in menu:
            clear()
            menu[choice]()


menu = OrderedDict([
    ('v', view_entry),
    ('a', add_entry),
    ('b', backup_data),
])


#Maintenance
def clean_price(dollars):
    return int(dollars.replace("$","").replace(".",""))

def convert_dollar(cent):
    return float(cent/100)  

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# Start 
def initialize():
    db.connect()
    db.create_tables([Product], safe=True) 

if __name__ == '__main__':
    initialize()
    csv_data() 
    menu_loop()
    #view_entry()