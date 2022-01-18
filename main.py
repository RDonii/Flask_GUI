import os
from datetime import datetime
from tabnanny import check
from flask import Flask, redirect, render_template, request, flash, url_for
from modules import Imports, Sales, Items, create_db
from auth import get_loged
from sqlalchemy import desc

app = Flask(__name__)
app.config["SECRET_KEY"] = '038be6dc-c709-47ef-ae3a-2240dca288c1'

create_db(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    if not password:
        flash('Parolni kiriting!')
        return redirect(url_for('home'), code=302)
    elif get_loged(password):
        return redirect(url_for('dashboard'), code=302)
    else:
        flash('Qayta urunib ko`ring.')
        return redirect(url_for('home'), code=302)
    
@app.route('/dashboard')
def dashboard():
    items = Items.query.all()
    count_items = 0
    names = []
    for item in items:
        count_items += item.count
        if item.name not in names:
            names.append(item.name)
    newest_item = Imports.query.order_by(desc(Imports.in_time)).first()
    newest_sale = Sales.query.order_by(desc(Sales.out_time)).first()

    if newest_item:
        last_in_name = newest_item.name
        last_in_date = newest_item.in_time
    else:
        last_in_name = ''
        last_in_date = ''

    if newest_sale:
        last_out_name = newest_item.name
        last_out_date = newest_item.in_time
    else:
        last_out_name = ''
        last_out_date = ''

    response = {
        "count_items": count_items,
        "names": names,
        "last_in_name": last_in_name,
        "last_in_date": last_in_date,
        "last_out_name": last_out_name,
        "last_out_date": last_out_date
    }

    return render_template('dashboard.html', response=response)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form.get("name")
        count = request.form.get("count", 0)
        in_price = request.form.get("in_price")
        
        if not in_price:
            flash('Mahsulotning sotib olingan narxini kiriting!')
            return redirect(url_for('add_item'), code=302)
        check = name
        if check:
            N = check.count(' ')
            for i in range(N):
                check = check.replace(' ', '')

        if not name or len(check)==0:
            flash('Mahsulotga nom bering!')
            return redirect(url_for('add_item'), code=302)
        
        in_time = datetime.now()

        while name[0]==' ':
            name = name.replace(" ", '')

        try:
            new_import = Imports(name=name.lower().capitalize(), count=count, in_price=in_price, in_time=in_time)
            new_import.insert()

            item_check = Items.query.filter(Items.name==name, Items.in_price==in_price).one_or_none()
            if item_check:
                item_check.count += count
                item_check.update()
            else:
                new_item = Items(name=name.lower().capitalize(), count=count, in_price=in_price, in_time=in_time)
                new_item.insert()

            flash('Mahsulot omborga qo`shildi.')
            return redirect(url_for('add_item'), code=301)
        except:
            flash('Xatolik yuzberdi.')
            return redirect(url_for('add_item'), code=301)

    items = Items.query.all()
    names = []
    for item in items:
        if item.name not in names:
            names.append(item.name)
    
    return render_template('add.html', names=names)

if __name__=='__main__':
    app.run(debug=True)