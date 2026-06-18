import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from config import Config

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

db = SQLAlchemy(app)

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    usage_logs = db.relationship('UsageLog', backref='equipment', lazy=True)
    maintenance_logs = db.relationship('MaintenanceLog', backref='equipment', lazy=True)

class UsageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    quantity_used = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(200))
    used_at = db.Column(db.DateTime, default=datetime.utcnow)

class MaintenanceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    maintenance_date = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def home():
    total_items = Equipment.query.count()
    total_quantity = db.session.query(db.func.sum(Equipment.quantity)).scalar() or 0
    return render_template('index.html', total_items=total_items, total_quantity=total_quantity)

@app.route('/dashboard')
def dashboard():
    items = Equipment.query.order_by(Equipment.name).all()
    total_items = len(items)
    total_quantity = sum(item.quantity for item in items)
    recent_usage = UsageLog.query.order_by(UsageLog.used_at.desc()).limit(5).all()
    recent_maintenance = MaintenanceLog.query.order_by(MaintenanceLog.maintenance_date.desc()).limit(5).all()
    return render_template(
        'dashboard.html',
        items=items,
        total_items=total_items,
        total_quantity=total_quantity,
        recent_usage=recent_usage,
        recent_maintenance=recent_maintenance,
    )

@app.route('/add', methods=['GET', 'POST'])
def add_equipment():
    if request.method == 'POST':
        name = request.form['name'].strip()
        category = request.form['category'].strip()
        try:
            quantity = int(request.form['quantity'])
            if quantity < 0:
                raise ValueError()
        except ValueError:
            flash('Quantity must be a positive number.', 'error')
            return redirect(url_for('add_equipment'))

        item = Equipment(name=name, category=category, quantity=quantity)
        db.session.add(item)
        db.session.commit()
        flash(f'Added equipment: {item.name}', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_equipment.html')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_equipment(id):
    item = Equipment.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name'].strip()
        item.category = request.form['category'].strip()
        try:
            quantity = int(request.form['quantity'])
            if quantity < 0:
                raise ValueError()
        except ValueError:
            flash('Quantity must be a positive number.', 'error')
            return redirect(url_for('update_equipment', id=id))

        item.quantity = quantity
        db.session.commit()
        flash(f'Updated equipment: {item.name}', 'success')
        return redirect(url_for('dashboard'))

    return render_template('update_equipment.html', item=item)

@app.route('/delete/<int:id>')
def delete_equipment(id):
    item = Equipment.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash(f'Deleted equipment: {item.name}', 'success')
    return redirect(url_for('dashboard'))

@app.route('/use/<int:id>', methods=['GET', 'POST'])
def log_usage(id):
    item = Equipment.query.get_or_404(id)
    if request.method == 'POST':
        try:
            quantity_used = int(request.form['quantity_used'])
            if quantity_used <= 0 or quantity_used > item.quantity:
                raise ValueError()
        except ValueError:
            flash('Enter a valid quantity that does not exceed current stock.', 'error')
            return redirect(url_for('log_usage', id=id))

        usage = UsageLog(
            equipment_id=item.id,
            quantity_used=quantity_used,
            note=request.form.get('note', '').strip() or None,
        )
        item.quantity -= quantity_used
        db.session.add(usage)
        db.session.commit()
        flash(f'Logged usage for {item.name}.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('log_usage.html', item=item)

@app.route('/maintenance/<int:id>', methods=['GET', 'POST'])
def log_maintenance(id):
    item = Equipment.query.get_or_404(id)
    if request.method == 'POST':
        status = request.form.get('status', '').strip()
        notes = request.form.get('notes', '').strip()
        if not status:
            flash('Please provide a maintenance status.', 'error')
            return redirect(url_for('log_maintenance', id=id))

        maintenance = MaintenanceLog(
            equipment_id=item.id,
            status=status,
            notes=notes or None,
        )
        db.session.add(maintenance)
        db.session.commit()
        flash(f'Saved maintenance log for {item.name}.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('log_maintenance.html', item=item)

@app.route('/history')
def history():
    logs = UsageLog.query.order_by(UsageLog.used_at.desc()).all()
    return render_template('history.html', logs=logs)

@app.route('/maintenance')
def maintenance():
    logs = MaintenanceLog.query.order_by(MaintenanceLog.maintenance_date.desc()).all()
    return render_template('maintenance.html', logs=logs)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
