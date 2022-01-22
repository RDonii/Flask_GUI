from datetime import datetime, timedelta, date
from flask import Flask, redirect, render_template, request, flash, url_for
from modules import Imports, Sales, Items, create_db
from auth import get_loged
from sqlalchemy import desc
from flaskwebgui import FlaskUI

app = Flask(__name__)
app.config["SECRET_KEY"] = '038be6dc-c709-47ef-ae3a-2240dca288c1'
ui = FlaskUI(app, maximized=True, close_server_on_exit=False)

create_db(app)

def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

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
        
        if len(count)==0:
            count = 0
        else:
            count = int(count)
        
        in_time = datetime.now().replace(microsecond=0)

        while name[0]==' ':
            name = name.replace(" ", '')

        try:
            new_import = Imports(name=name.lower().capitalize(), count=count, in_price=in_price, in_time=in_time)
            new_import.insert()

            item_check = Items.query.filter(Items.name==name.lower().capitalize(), Items.in_price==in_price).one_or_none()
            if item_check:
                item_check.in_time = in_time
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

@app.route('/items')
def items():

    items_query = Items.query.all()
    items = [item.format() for item in items_query]

    return render_template('items.html', items=items)

@app.route('/items/<int:id>', methods=['GET', 'POST'])
def items_id(id):
    item_query = Items.query.filter(Items.id==id).first()
    item = item_query.format()

    if request.method == 'POST':
        s_count = request.form.get("count")
        out_price = request.form.get("out_price")

        if not s_count or not out_price or len(s_count)==0 or len(out_price)==0 :
            flash('Narx va Sonini kiriting!')
            return redirect(url_for('items_id', id=id), code=302)
        else:
            s_count = int(s_count)
            out_price = int(out_price)        

        if item_query.count < s_count:
            flash('Buncha tavar mavjud emas!')
            return redirect(url_for('items_id', id=id), code=302)
        
        out_time = datetime.now().replace(microsecond=0)

        try:
            new_sale = Sales(name=item["name"], count=s_count, in_time=item["in_time"], in_price=item["in_price"], out_time=out_time, out_price=out_price)
            new_sale.insert()

            item_query.count -= s_count
            if item_query.count == 0:
                item_query.delete()
            else:
                item_query.update()
        except:
                flash('Xatolik yuzberdi.')
                return redirect(url_for('items_id', id=id), code=301)
        
        return redirect(url_for('items'), code=301)

    return render_template('saling.html', item=item)

@app.route('/sales/<int:days>')
def sales(days):
    start = date.today() - timedelta(days=days)
    sales_query = Sales.query.filter(Sales.out_time>start).all()
    sales = [sale.format() for sale in sales_query]

    in_total = 0
    out_total = 0

    for item in sales_query:
        in_total += (item.in_price * item.count)
        out_total += (item.out_price * item.count)
    
    benefit = out_total - in_total

    return render_template('sales.html', days=str(days), sales=sales, in_total=in_total, out_total=out_total, benefit=benefit)

@app.route('/imports/<int:days>')
def imports(days):
    start = date.today() - timedelta(days=days)
    imports_query = Imports.query.filter(Imports.in_time>start).all()
    imports = [imp.format() for imp in imports_query]
    
    return render_template('imports.html', days=str(days), imports=imports)

@app.route('/stop')
def shutdown():
    shutdown_server()
    return render_template('exit.html')

if __name__=='__main__':
    app.run(debug=True)