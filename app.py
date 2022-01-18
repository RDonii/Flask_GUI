from flask import Flask, redirect, render_template, request, url_for
from modules import create_db, Item
from flaskwebgui import FlaskUI

def create_app():
    app = Flask(__name__)
    create_db(app)

    ui = FlaskUI(app, maximized=True)

    @app.route('/')
    def home():
        return redirect(url_for('get_items'), code=301)

    @app.route('/items')
    def get_items():
        items = Item.query.all()
        items_list = [item.format() for item in items]

        return render_template('items.html', items=items_list)

    @app.route('/items', methods=['POST'])
    def add_items():
        name = request.form.get('name')

        new_item = Item(name)
        new_item.insert()

        return redirect(url_for('get_items'), code=301)
    return ui

ui = create_app()

if __name__=='__main__':
    ui.run()

        