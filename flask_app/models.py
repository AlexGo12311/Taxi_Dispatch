from datetime import datetime
from extentions import db

class Driver(db.Model):
    __tablename__ = 'Dispatch_taxi_driver'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    vehicles = db.relationship('Vehicle', back_populates='driver', lazy='dynamic')
    info = db.relationship('DriverInfo', back_populates='driver', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'vehicles_count': self.vehicles.count()
        }

class DriverInfo(db.Model):
    __tablename__ = 'Dispatch_taxi_driverinfo'

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('Dispatch_taxi_driver.id'), unique=True)
    birth_date = db.Column(db.Date, nullable=True)
    driver_license = db.Column(db.String(10), unique=True, nullable=False)
    photo = db.Column(db.String(500), nullable=True)
    experience_years = db.Column(db.Integer, default=0)
    gender = db.Column(db.String(7))

    driver = db.relationship('Driver', back_populates='info')

    def to_dict(self):
        return {
            'driver_id': self.driver_id,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'driver_license': self.driver_license,
            'experience_years': self.experience_years,
            'gender': self.gender,
            'has_photo': bool(self.photo)
        }


class Vehicle(db.Model):
    __tablename__ = 'Dispatch_taxi_vehicle'

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('Dispatch_taxi_driver.id'), nullable=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    license_plate = db.Column(db.String(15), unique=True, nullable=False)
    color = db.Column(db.String(20))
    year = db.Column(db.Integer)
    mileage = db.Column(db.Integer)

    driver = db.relationship('Driver', back_populates='vehicles')
    orders = db.relationship('Order', back_populates='vehicle', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'brand': self.brand,
            'model': self.model,
            'license_plate': self.license_plate,
            'color': self.color,
            'year': self.year,
            'mileage': self.mileage,
            'driver_name': self.driver.full_name if self.driver else None,
            'orders_count': self.orders.count()
        }


class Customer(db.Model):
    __tablename__ = 'Dispatch_taxi_customer'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(12), nullable=False)

    # Связи
    orders = db.relationship('Order', back_populates='customer', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'orders_count': self.orders.count()
        }


class Tariff(db.Model):
    __tablename__ = 'Dispatch_taxi_tariff'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost_for_km = db.Column(db.Numeric(8, 2), nullable=False)

    orders = db.relationship('Order', back_populates='tariff', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cost_for_km': float(self.cost_for_km) if self.cost_for_km else 0
        }


class Operator(db.Model):
    __tablename__ = 'Dispatch_taxi_operator'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(12), nullable=False)

    orders = db.relationship('Order', back_populates='operator', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'orders_count': self.orders.count()
        }


class Order(db.Model):
    __tablename__ = 'Dispatch_taxi_order'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Dispatch_taxi_customer.id'), nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('Dispatch_taxi_vehicle.id'), nullable=True)
    tariff_id = db.Column(db.Integer, db.ForeignKey('Dispatch_taxi_tariff.id'), nullable=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('Dispatch_taxi_operator.id'), nullable=False)
    order_time = db.Column(db.DateTime, default=datetime.utcnow)
    range = db.Column(db.Numeric(3, 1))
    status = db.Column(db.String(15))

    customer = db.relationship('Customer', back_populates='orders')
    vehicle = db.relationship('Vehicle', back_populates='orders')
    tariff = db.relationship('Tariff', back_populates='orders')
    operator = db.relationship('Operator', back_populates='orders')

    def to_dict(self):
        total_cost = None
        if self.tariff and self.range:
            total_cost = float(self.tariff.cost_for_km) * float(self.range)

        return {
            'id': self.id,
            'customer': self.customer.full_name if self.customer else None,
            'customer_id': self.customer_id,
            'vehicle': f"{self.vehicle.brand} {self.vehicle.model}" if self.vehicle else None,
            'vehicle_id': self.vehicle_id,
            'tariff': self.tariff.name if self.tariff else None,
            'tariff_id': self.tariff_id,
            'operator': self.operator.full_name if self.operator else None,
            'operator_id': self.operator_id,
            'order_time': self.order_time.isoformat() if self.order_time else None,
            'distance': float(self.range) if self.range else 0,
            'status': self.status,
            'total_cost': total_cost,
            'status_display': self.get_status_display()
        }

    def get_status_display(self):
        status_map = {
            'in_progress': 'В процессе',
            'completed': 'Завершен',
            'cancelled': 'Отменен'
        }
        return status_map.get(self.status, self.status)