from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

# 🗄️ MODEL
class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# 🏠 HOME
@app.route('/')
def home():
    return render_template("index.html")

# 📊 DASHBOARD
@app.route('/dashboard')
def dashboard():
    items = Equipment.query.all()
    return render_template("dashboard.html", items=items)

# ➕ ADD
@app.route('/add', methods=['GET', 'POST'])
def add_equipment():
    if request.method == 'POST':
        item = Equipment(
            name=request.form['name'],
            category=request.form['category'],
            quantity=request.form['quantity']
        )
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template("add_equipment.html")

# ✏️ UPDATE
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_equipment(id):
    item = Equipment.query.get_or_404(id)

    if request.method == 'POST':
        item.name = request.form['name']
        item.category = request.form['category']
        item.quantity = request.form['quantity']
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template("update_equipment.html", item=item)

# 🗑️ DELETE
@app.route('/delete/<int:id>')
def delete_equipment(id):
    item = Equipment.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('dashboard'))

# ⚙️ OTHER PAGES
@app.route('/history')
def history():
    return render_template("history.html")

@app.route('/maintenance')
def maintenance():
    return render_template("maintenance.html")

# RUN
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)