from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for
)

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ------------------------------------
# DATABASE CONFIGURATION
# ------------------------------------

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ------------------------------------
# DATABASE MODEL
# ------------------------------------

class Item(db.Model):
    idNum = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )


# Create the database tables
with app.app_context():
    db.create_all()


# ------------------------------------
# READ - DISPLAY ALL ITEMS
# ------------------------------------

@app.route('/')
def index():
    items = Item.query.all()

    return render_template(
        'index.html',
        items=items
    )


# ------------------------------------
# GREETING PAGE
# ------------------------------------

@app.route('/hello')
@app.route('/hello/')
@app.route('/hello/<user_name>')
def hello(user_name=None):
    return render_template(
        'home.html',
        user=user_name
    )


# ------------------------------------
# CREATE - ADD NEW ITEM
# ------------------------------------

@app.route('/create', methods=['GET', 'POST'])
def create():

    if request.method == 'POST':
        name = request.form.get('name', '').strip()

        if not name or len(name) > 100:
            return "Invalid item name", 400

        new_item = Item(name=name)

        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create.html')


# ------------------------------------
# UPDATE - EDIT EXISTING ITEM
# ------------------------------------

@app.route('/update/<int:idNum>', methods=['GET', 'POST'])
def update(idNum):

    item = db.get_or_404(Item, idNum)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()

        if not name or len(name) > 100:
            return "Invalid item name", 400

        item.name = name

        db.session.commit()

        return redirect(url_for('index'))

    return render_template(
        'update.html',
        item=item
    )


# ------------------------------------
# DELETE - REMOVE ITEM
# ------------------------------------

@app.route('/delete/<int:idNum>', methods=['POST'])
def delete(idNum):

    item = db.get_or_404(Item, idNum)

    db.session.delete(item)
    db.session.commit()

    return redirect(url_for('index'))