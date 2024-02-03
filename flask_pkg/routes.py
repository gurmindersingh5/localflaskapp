from datetime import datetime
from time import sleep
from . import app
from flask import render_template, redirect, url_for, request, jsonify
from .form import *
from .models import *
from . import db
from . import bcrypt
from flask import session
from sqlalchemy import extract, and_, desc
from sqlalchemy.exc import SQLAlchemyError
import json
from collections import defaultdict



@app.route('/', methods=['GET','POST'])
def home():
    names = [items.name for items in CEntry.query.join(DEntry).order_by(desc(DEntry.price))]
    prices = [int(items.price) for items in DEntry.query.all()]
    prices = sorted(prices, reverse=True)

    # create string of list of names of highest puchases to send to graph in home page through home.js
    names_str = ""
    price_str = ""
    for name,price in zip(names,prices):
        names_str += name[:15]+','
        price_str += str(price)+','

    # Monthly-sales data extracting from db here:
    Query_time = db.session.query(DEntry.time)
    Query_price = db.session.query(DEntry.price)
    current_year_and_month = [datetime.now().year, datetime.now().month]
    months_for_monthly_sale = []
    list_datetime = []
    list_price = []

    #getting list of datetimes and respective prices of purchase on monthly basis of past 12 months
    for i in range(current_year_and_month[1], current_year_and_month[1]-12, -1):
        if i == 0:
            current_year_and_month[0] -= 1
            current_year_and_month[1] = 12
        list_datetime += [Query_time.filter(
          and_(  
            extract('year', DEntry.time) == current_year_and_month[0],
            extract('month', DEntry.time) == current_year_and_month[1]
              )
            ).all()]
        list_price += [Query_price.filter(
          and_(  
            extract('year', DEntry.time) == current_year_and_month[0],
            extract('month', DEntry.time) == current_year_and_month[1]
              )
            ).all()]
        months_for_monthly_sale += [current_year_and_month[1]]
        current_year_and_month[1] -= 1
    
    # totaling of prices per month
    monthly_sale = []
    monthly_total = 0
    for price in list_price:
    #   price is sublists containing elements prices 
    #   price = [(Decimal('1.00'),), (Decimal('2000.00'),)]  ---> list
    #   sublist/items = (Decimal('1.00'),) ---> tuple
        for items in price:
            monthly_total += int(items[0])
        monthly_sale += [monthly_total]
        monthly_total = 0     
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        if data['key'] == "montlySalesGraph":
            return jsonify({'monthly_sale':monthly_sale, 'months':months_for_monthly_sale})

    return render_template('home.html', data=names_str, price=price_str)


@app.route('/delete_invoice', methods=['GET', 'POST'])
def delete_invoice():
    if request.json['invoiceNo']:    
        entries_to_delete = DEntry.query.filter_by(invoice_no=request.json['invoiceNo']).all()
        for entry in entries_to_delete:
            db.session.delete(entry)
        db.session.commit()
        return jsonify({'success': 'Deleted'}), 200
    



C_ID_FOR_customerdata = None
@app.route('/customerlist', methods=["GET", "POST"])
def customerlist():  
    query = db.session.query(CEntry)
    results = query.order_by(func.lower(CEntry.name)).all()
    
    form_data = search_form()
    NOTE = ""
     
    if request.method == "POST":

       
        # ---------------------------------------------
        try:
            if request.json['custId']:
                global C_ID_FOR_customerdata
                C_ID_FOR_customerdata = request.json['custId']
                return redirect(url_for('customerdata_'))
        except Exception as e:
            print(str(e))
        #---------------------------------------------

        results = []
        if form_data.data['S_name']:
            results += query.filter(CEntry.name.like(f"%{form_data.data['S_name']}%"))
        if form_data.data['S_address']:
            results += query.filter(CEntry.address.like(f"%{form_data.data['S_address']}%"))
        results = set(results)
    if not results:
        NOTE = "Not found in database"
    else:
        NOTE = f"{len(results)} entry/ies"
    return render_template('customerlist.html', form=form_data, results=results, note=NOTE)


@app.route('/customerdata', methods=['GET', 'POST'])
def customerdata_():
    partlist = {}
    total = 0
    invoice_totals = {}
    if C_ID_FOR_customerdata:
        cust_id = C_ID_FOR_customerdata
        cust_data = db.session.query(CEntry).filter_by(cust_id=cust_id).first()
        purchased_data = db.session.query(DEntry).filter_by(cust_id=cust_id).order_by(DEntry.invoice_no.desc()).all()
        
        invoice_items = defaultdict(list)
        for entry in purchased_data:
            invoice_items[entry.invoice_no].append(entry)
        invoice_items = dict(invoice_items)
        
        for invoice_number, items in invoice_items.items():
            total2 = sum(item.price for item in items)
            invoice_totals[invoice_number] = total2

        for item in purchased_data:
            partlist[item.part_id] = db.session.query(PEntry).filter_by(part_id=item.part_id).first().name
            total += item.price
        print('-----------------------------------------------> ', invoice_totals, total)
        return render_template('customerdata.html', cust_data=cust_data, purchased_data=invoice_items, partlist=partlist, total=total, invoice_totals=invoice_totals)
    else:
        return jsonify({'error': 'Pls go back to Customer Inquiry and try again'})


@app.route('/prevbal_for_print', methods=['GET', 'POST'])
def prevbal_for_print():
    if request.json:
        totalbal = 0
        cust_id = request.json
        customer_info = DEntry.query.filter_by(cust_id=cust_id).all()
        for item in customer_info:
            totalbal += item.price

    return jsonify({'prevbal': totalbal}), 200


LASTENTRY = []
e_form_note = ""
PartID_for_e_form = None
next_invoice_number = None
@app.route('/eform', methods=['GET', 'POST'])
def e_form():
    global next_invoice_number

    form_data = DataEntry()
    address_list = CEntry.query.all()
    parts = PEntry.query.all()
    
    err_msg = ""
  
    if request.method == "POST":
        print('='*100, request.form, )
        global LASTENTRY
        global e_form_note
        global PartID_for_e_form
         # setting part price
        

        try:
            customer = request.json['customer']['id']
            order = request.json['order']
            order_cnt = 0
            DEntry_cnt = 0
            order_len = len(order)
            print(' 1 ->'*10,'in try block')
            if customer and order:
                
                next_invoice_number = generate_next_invoice_number()
                new_invoice = Invoice(invoice_number=next_invoice_number)
                
                for item in order:
                    print(' 3 ->'*10,'in for block')

                    part = PEntry.query.filter_by(part_id=item[1]).first()
                    if part.container_qty > 0 or part.pieces_qty > 0:
                        # Update inventory quantities
                        part.container_qty -= item[3]
                        part.pieces_qty -= item[4]
                        # Commit changes to the database
                        db.session.commit()
                        order_cnt += 1
                        print(' 4 ->'*10,'in CTN PCs update block', order_cnt)

                    else:
                        return jsonify({'error': str(e)}), 400
                    
                    data = DEntry(
                        part_id=item[1],
                        container_qty=item[3],
                        pieces_qty=item[4],
                        price=item[6],
                        cust_id=customer,
                        invoice_no=next_invoice_number
                        # time=datetime.strptime(datetime.datetime.now().strftime('%d-%m-%Y ~ %H:%M'), '%d-%m-%Y ~ %H:%M')
                    )
                    db.session.add(data)
                    db.session.commit()
                    DEntry_cnt += 1
                    print(' 5 ->'*10,'in DEntry update block', DEntry_cnt)

                if order_cnt == order_len and DEntry_cnt == order_len:
                    print(' 6 ->'*10,'in CTN PCs update block', ( order_cnt == order_len), (DEntry_cnt == order_len))
                    db.session.add(new_invoice)
                    db.session.commit()
                    
                    return jsonify({'Success': 'Transaction successful'}), 200
                
        except Exception as e:
            print(' 7 ->', 'In exception ', str(e))
            return jsonify({'error': str(e)}), 400
        
    return render_template('eform.html', form=form_data, name_list=address_list, part_list=parts, 
                           address_list=address_list,
                           lastentry=LASTENTRY, e_form_note=e_form_note, err_msg=err_msg)

@app.route('/revieworder', methods=['GET'])
def revieworder():
    return render_template('revieworder.html')

@app.route('/get_capacity', methods=['GET','POST'])
def get_capacity():
    capacity = PEntry.query.all()
    res = {}
    for c in capacity:
        res[c.part_id]=c.container_capacity
    response_data = {'cap' : res}
    return jsonify(response_data)

@app.route('/get_customers', methods=['GET','POST'])
def get_customers():
    # Assuming you have a function to fetch the customer data from your database
    customers = db.session.query(CEntry).order_by(func.lower(CEntry.name)).all()  # Implement this function
    customer_list = [{'id': customer.cust_id, 'name': customer.name, 'address': customer.address, 'contact': customer.contact} for customer in customers]

    print("visited", customer_list)
    response_data = {'cust': customer_list}

    return jsonify(response_data)


@app.route('/test', methods=['GET'])
def test():
    return render_template('test.html')


@app.route('/printinvoice', methods=['GET'])
def print_func():
    global next_invoice_number
    return render_template('print.html', invoice=next_invoice_number)


@app.route('/get_parts', methods=['GET','POST'])
def get_parts():
    # Assuming you have a function to fetch the customer data from your database
    parts = db.session.query(PEntry).order_by(func.lower(PEntry.name)).all()  # Implement this function
    parts_list = [{'id': part.part_id, 'name': part.name, 'CTN': part.container_qty, 'PCS': part.pieces_qty, 'price': part.price} for part in parts]

    print("visited", parts_list)
    response_data = {'partlist': parts_list}

    return jsonify(response_data)


NOTE = ""
@app.route('/pform', methods=['GET', 'POST'])
def p_form():
    print('p_form','#'*199, request.args.get('name'), request.args.get('add_p'))
    if not "user_id" in session:
        return redirect(url_for('login_add_p'))
    global NOTE
    form_data = Part()
    print(request.form)
    print(form_data.errors)
    print(form_data.validate_on_submit())
    if form_data.validate_on_submit():
        data = PEntry(name=form_data.name.data.strip(),
                      price=form_data.price.data,
                      container_qty=form_data.container_qty.data,
                      pieces_qty=form_data.pieces_qty.data,
                      container_capacity=form_data.container_capacity.data,
                      )
        existing_product = PEntry.query.filter_by(name=form_data.name.data.strip()).first()
        if existing_product:
            return redirect(url_for('p_form')), 12
        else:
            db.session.add(data)
            db.session.commit()
            NOTE = [data.name, data.price, datetime.now().strftime('%d-%m-%Y ~ %H:%M')]
            return redirect(url_for('p_form'))
    if form_data.errors != {}:
        for err_msg in form_data.errors.values():
            print(f" There was an error {err_msg}")
    return render_template('pform.html', form=form_data, note=NOTE)


success_note = ""


@app.route('/cform', methods=['GET', 'POST'])
def c_form():
    global success_note
    form_data = Customer_Entry()
    if request.method == "POST":
        if form_data.validate_on_submit():
            print(form_data.validate_on_submit())
            data = CEntry(name=form_data.name.data,
                          address=form_data.address.data,
                          contact=form_data.contact.data
                          )
            existing_customer = CEntry.query.filter_by(name=form_data.name.data).first()
            if existing_customer:
                return redirect(url_for('c_form')), 12
            else:
                db.session.add(data)
                db.session.commit()
                success_note = [data.name, data.address, data.contact, datetime.now().strftime('%d-%m-%Y ~ %H:%M')] 

            return redirect(url_for('c_form'))
    if form_data.errors != {}:
        for err_msg in form_data.errors.values():
            print(f" There was an error {err_msg}")
    return render_template('cform.html', form=form_data, success_note=success_note)



@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    print('inventory','#'*199, request.method , request.form.get('redirect_val'))
    Query = db.session.query(PEntry)
    results = Query.order_by(func.lower(PEntry.name)).all()
    # if request.method == "GET":
    #     if request.args.get('sort') == 'name':
    #         results = Query.order_by(func.lower(PEntry.name)).all()
    #     else:
    #         results = Query.all()
    NOTE = ""
    
    print(request.method, request.args, request.args.get('sort'))
    # print([result.container_qty for result in results])
    if request.method == "POST":
        if 'name' in request.form:
            name_query = request.form['name']
            if name_query:
                results = Query.filter(PEntry.name.like(f"%{name_query}%")).all()
                if not results:
                    NOTE = "Not found in database"
                else:
                    NOTE = f"{len(results)} entry/ies found"
        if request.form.get('redirect_val') == 'add_p':
            return redirect(url_for('redirect_p_form'))
        if request.form.get('redirect_val') == 'edit_p':
            return redirect(url_for('redirect_edit_p'))

    return render_template('inventory.html', results=results, note=NOTE)




@app.route('/redirect_pform', methods=['GET', 'POST'])
def redirect_p_form():
    try:
        if not "user_id" in session:
            return redirect(url_for('login_add_p'))
        else:
            return redirect(url_for('p_form'))
    except:
        pass
    return render_template('redirect_pform.html')



@app.route('/redirect_editp', methods=['GET', 'POST'])
def redirect_edit_p():
    try:
        if not "user_id" in session:
            return redirect(url_for('login_edit_p'))
        else:
            return redirect(url_for('edit_p'))
    except:
        pass
    return render_template('redirect_editp.html')


# @app.route('/redirect', methods=['GET', 'POST'])
# def redirect_func():
    
#     print('redirect','#'*199, request.form, request.form.get('redirect_val'))

#     boolean = "user_id" in session
#     print('in the redirect func',boolean, request.method, request.args.get('name'))
#     # if request.method == "GET":
#     #     try:
#     #         redirect_to = ''
#     #         print('In try req.args[val]:', redirect_to)
#     #     except:
#     #         redirect_to = ''
#     #         print('REDIRECT_TO: in else: ')
 
#     #     if boolean == True and redirect_to == 'add_p': 
#     #         return redirect(url_for('p_form'))
#     #     elif boolean == True and redirect_to == 'edit_p': 
#     #         return redirect(url_for('edit_p'))
#     #     elif boolean == True and redirect_to == 'inventory':
#     #         return redirect(url_for(redirect_to))
#     #     else:
#     #         return redirect(url_for('login'))
#     if request.method == "POST" and boolean == False:

#         return redirect('login.html', redirect_val=request.form.get('redirect_val'))


PartID = None  
@app.route('/edit', methods=['GET', 'POST'])
def edit_p():
    if not "user_id" in session:
        return redirect(url_for('login_edit_p'))
    Query = db.session.query(PEntry)
    results = Query.order_by(func.lower(PEntry.name)).all()
    NOTE = ""

    if request.method == "POST":
        try:
            if request.get_json:
                global PartID
                PartID = request.get_json()['part_id']
                return redirect(url_for('detailed_edit_p'))
        except:
            pass
        
        try:
            if 'name' in request.form:
                name_query = request.form['name']
                print('name_query: ', name_query)
                if name_query:
                    results = Query.filter(PEntry.name.like(f"%{name_query}%")).all()
                    if not results:
                        NOTE = "Not found in database"
                    else:
                        NOTE = f"{len(results)} entry/ies found"
                       

        except Exception as e:
            # Handle specific exceptions if needed or log the exception for debugging
            print(f"An error occurred: {e}")
        print('request.get_json: ', request.get_json, 'request.form[name]: ',  request.form, '0'*10)
    
    return render_template('edit.html', results=results, note=NOTE)


@app.route('/detailed', methods=['GET', 'POST'])
def detailed_edit_p():
    global PartID
    data = db.session.query(PEntry).filter_by(part_id=PartID).first()
    if request.method == 'POST':
        
        try:
            if request.json['updated_data']:
                recieve_updated_data = request.json['updated_data']
                data_to_be_edited = db.session.query(PEntry).filter_by(part_id=recieve_updated_data[0]).first()
                if data_to_be_edited and len(recieve_updated_data) == 6:
                    data_to_be_edited.name = str(recieve_updated_data[1])
                    data_to_be_edited.container_qty = int(recieve_updated_data[2])
                    data_to_be_edited.pieces_qty = int(recieve_updated_data[3])
                    data_to_be_edited.price = float(recieve_updated_data[4])
                    data_to_be_edited.container_capacity = int(recieve_updated_data[5])
                    try:
                        db.session.commit()
                        print('succesfully committed----')
                        return 'committed', 200
                    except SQLAlchemyError as e:
                        db.session.rollback()  # Rollback changes if an error occurs
                        error_message = str(e)  # Get the error message
                        print(error_message, 'error')
                        return render_template('detailed.html', error_message=error_message, data=data)
                    finally:
                        db.session.close()  # Close the session
        except:
            pass        
        # if statement to delete the data to be deleted
        try:
            if request.get_json()['delete'] == "true":
                entry_to_delete = PEntry.query.filter_by(part_id=PartID).first()
                if entry_to_delete:
                    db.session.delete(entry_to_delete)
                    db.session.commit()
                    return 'Deletion committed', 200
                else:
                    return jsonify({'error':'Row not found'})
        except Exception as e:
            print('error', str(e))        
    return render_template('detailed.html', data=data)




@app.route('/login_p_form', methods=['GET', 'POST'])
def login_add_p():

    form_data = login_form()
    form_data.Username.default = "Admin"

    login_note = ""
    if not "user_id" in session:
        login_note = "Session timed out.! Please login again"
    try:
        if loginModel.query.filter_by(username = 'Admin').first().password:
            pass
    except: 
        return redirect(url_for('set_password_func'))
    if request.method == 'POST':
        # redirect_val = request.form.get('redirect_val')
        entered_password = form_data.Password.data
        stored_password_hash = loginModel.query.filter_by(username = 'Admin').first().password
        if bcrypt.check_password_hash(stored_password_hash, entered_password):
            session['user_id'] = "Admin"
            login_note = "Login successful-loginnote"
            return redirect(url_for('p_form'))
        else:
            login_note = "Incorrect Password!"
    return render_template('login_p_form.html', form=form_data, failed_login=login_note)



@app.route('/login_edit_p', methods=['GET', 'POST'])
def login_edit_p():

    form_data = login_form()
    form_data.Username.default = "Admin"

    login_note = ""
    if not "user_id" in session:
        login_note = "Session timed out.! Please login again"
    try:
        if loginModel.query.filter_by(username = 'Admin').first().password:
            pass
    except: 
        return redirect(url_for('set_password_func'))
    if request.method == 'POST':
        # redirect_val = request.form.get('redirect_val')
        entered_password = form_data.Password.data
        stored_password_hash = loginModel.query.filter_by(username = 'Admin').first().password
        if bcrypt.check_password_hash(stored_password_hash, entered_password):
            session['user_id'] = "Admin"
            login_note = "Login successful-loginnote"
            return redirect(url_for('edit_p'))
        else:
            login_note = "Incorrect Password!"
    return render_template('login_edit_p.html', form=form_data, failed_login=login_note)



@app.route('/register-password', methods=['GET', 'POST'])
def set_password_func():

    redirect_val = 'home'

    form_data = set_password()
    form_data.Username.default = "Admin"

    # if not loginModel.query.filter_by(username = 'Admin').first().password:  
        # <--- to add a password if there is none--->


    if request.method == "POST":
        password = bcrypt.generate_password_hash(password=form_data.Password.data).decode('utf-8')
        data = loginModel(
            username = "Admin",
        password = password)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for(redirect_val))

    return render_template('register-password.html', form=form_data)


 # Function to generate the next invoice number
def generate_next_invoice_number():
    last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
    if last_invoice:
        last_invoice_number = int(last_invoice.invoice_number[3:])  # Extract the numeric part
        next_invoice_number = last_invoice_number + 1
    else:
        next_invoice_number = 1
    return f"INV{next_invoice_number:06d}"  # Format the next invoice number with leading zeros


# @app.route('/delete', methods=['GET', 'POST'])
# def delete():
#     Query = db.session.query(PEntry)

#     if request.method == "GET":
#         if request.args.get('sort') and request.args.get('sort') == 'name':
#             results = Query.order_by(PEntry.name).all()
#         else:
#             results = Query.all()
#         if request.args.get('delete_btn'):
#             Query.filter_by(part_id=request.args.get('delete_btn')).delete()
#             db.session.commit()
#             return redirect(url_for('delete'))
#         if request.args.get('edit'):
#             item = Query.filter_by(part_id=request.args.get('edit')).first()
#             return render_template('edit.html', item=item)
#         if request.args.get('newval'):
#             Query.filter_by(part_id=request.args.get('hid')).first().qty = request.args.get('newval')
#             db.session.commit()
#             return redirect(url_for('delete'))
#     NOTE = ""
#     print(request.method, request.args, request.form)
#     if request.method == "POST":
#         results = []
#         if request.form['name']:
#             results += Query.filter(PEntry.name.like(f"%{request.form['name']}%"))
#             print(results, Query)
#             if not results:
#                 NOTE = "Not found in database"
#             else:
#                 NOTE = f"{len(results)} entry/ies found"
#     # print(results)
#     return render_template('delete.html', results=results, note=NOTE)

# old versio of edit_p
# PartID = ''
# @app.route('/edit', methods=['GET', 'POST'])
# def edit_p():
#     Query = db.session.query(PEntry)
#     results = Query.order_by(func.lower(PEntry.name)).all()
#     # if request.method == "GET":
#     #     if request.args.get('sort') == 'name':
#     #         results = Query.order_by(func.lower(PEntry.name)).all()
#     #     else:
#     #         results = Query.all()

#     # request to search by name from database PEntry
        
#     NOTE = ""
#     print(request.method, request.args, request.args.get('sort'))
#     # print([result.container_qty for result in results])
#     if request.method == "POST":
#         print(':D' * 10, 'in the if', request.json, request.form['name'])

#         results = []
#         try:
                
#             print(request.form['name'], '='*10)
#             # if request.form['name']:
#             #     results += Query.filter(PEntry.name.like(f"%{request.form['name']}%"))
#             #     print(results, Query)
#             #     if not results:
#             #         NOTE = "Not found in database"
#             #     else:
#             #         NOTE = f"{len(results)} entry/ies found"
#         except:
#             pass
#         # Part_id being sent from js to get the detailed page from the list of items
#         if request.get_json:
#             global PartID
#             PartID = request.get_json()['part_id']
#             return redirect(url_for('detailed_edit_p'))  # Correct route name 'detailed_edit_p'

#     return render_template('edit.html', results=results, note=NOTE)
