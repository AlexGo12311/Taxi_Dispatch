from flask import Blueprint, request, jsonify
from models import *
from sqlalchemy import func, or_
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__, url_prefix='/api/taxi')

@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    try:
        total_orders = Order.query.count()
        active_orders = Order.query.filter(Order.status == 'in_progress').count()
        total_drivers = Driver.query.count()
        total_customers = Customer.query.count()
        total_vehicles = Vehicle.query.count()
        total_tariffs = Tariff.query.count()
        total_operators = Operator.query.count()

        # Расчет выручки
        revenue_result = db.session.query(
            func.sum(Order.range * Tariff.cost_for_km)
        ).join(Tariff).filter(
            Order.tariff_id == Tariff.id,
            Order.status.in_(['completed', 'in_progress'])
        ).first()

        total_revenue = float(revenue_result[0]) if revenue_result[0] else 0.0

        week_ago = datetime.utcnow() - timedelta(days=7)
        daily_stats = db.session.query(
            func.date(Order.order_time).label('date'),
            func.count(Order.id).label('count'),
            func.sum(Order.range * Tariff.cost_for_km).label('revenue')
        ).join(Tariff).filter(
            Order.order_time >= week_ago,
            Order.tariff_id == Tariff.id
        ).group_by(
            func.date(Order.order_time)
        ).order_by(
            func.date(Order.order_time).desc()
        ).all()

        daily_data = [
            {
                'date': stat.date.isoformat(),
                'orders': stat.count,
                'revenue': float(stat.revenue) if stat.revenue else 0.0
            }
            for stat in daily_stats
        ]

        response_data = {
            'success': True,
            'statistics': {
                'total_orders': total_orders,
                'active_orders': active_orders,
                'total_drivers': total_drivers,
                'total_customers': total_customers,
                'total_vehicles': total_vehicles,
                'total_tariffs': total_tariffs,
                'total_operators': total_operators,
                'revenue': round(total_revenue, 2),
                'avg_order_value': round(total_revenue / total_orders, 2) if total_orders > 0 else 0
            },
            'daily_stats': daily_data,
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(response_data)

    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        return jsonify(error_response), 500

@api_bp.route('/orders', methods=['GET'])
def get_orders():
    try:
        status = request.args.get('status')
        customer_id = request.args.get('customer_id')
        vehicle_id = request.args.get('vehicle_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        query = Order.query

        if status:
            query = query.filter(Order.status == status)
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        if vehicle_id:
            query = query.filter(Order.vehicle_id == vehicle_id)
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Order.order_time >= start_dt)
            except:
                pass
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Order.order_time <= end_dt)
            except:
                pass

        total = query.count()
        orders = query.order_by(Order.order_time.desc()).offset(offset).limit(limit).all()

        response_data = {
            'success': True,
            'total': total,
            'count': len(orders),
            'filters': {
                'status': status,
                'customer_id': customer_id,
                'vehicle_id': vehicle_id,
                'start_date': start_date,
                'end_date': end_date
            },
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + len(orders) < total
            },
            'orders': [order.to_dict() for order in orders]
        }


        return jsonify(response_data)

    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        return jsonify(error_response), 500

@api_bp.route('/drivers', methods=['GET'])
def get_drivers():
    try:
        search = request.args.get('search', '')
        with_vehicles = request.args.get('with_vehicles', 'false').lower() == 'true'
        limit = request.args.get('limit', 50, type=int)

        query = Driver.query

        if search:
            query = query.filter(
                or_(
                    Driver.full_name.ilike(f'%{search}%'),
                    Driver.phone.ilike(f'%{search}%')
                )
            )

        drivers = query.limit(limit).all()

        driver_data = []
        for driver in drivers:
            data = driver.to_dict()
            if with_vehicles:
                data['vehicles'] = [v.to_dict() for v in driver.vehicles]
            driver_data.append(data)

        response = {
            'success': True,
            'count': len(driver_data),
            'drivers': driver_data
        }

        return jsonify(response)

    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        return jsonify(error_response), 500

@api_bp.route('/customers', methods=['GET'])
def get_customers():
    try:
        search = request.args.get('search', '')
        with_orders = request.args.get('with_orders', 'false').lower() == 'true'
        limit = request.args.get('limit', 50, type=int)

        query = Customer.query

        if search:
            query = query.filter(
                or_(
                    Customer.full_name.ilike(f'%{search}%'),
                    Customer.phone.ilike(f'%{search}%')
                )
            )

        customers = query.limit(limit).all()

        customer_data = []
        for customer in customers:
            data = customer.to_dict()
            if with_orders:
                data['orders'] = [o.to_dict() for o in customer.orders.limit(10)]
            customer_data.append(data)

        response = {
            'success': True,
            'count': len(customer_data),
            'customers': customer_data
        }

        return jsonify(response)

    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        return jsonify(error_response), 500

@api_bp.route('/vehicles', methods=['GET'])
def get_vehicles():
    try:
        search = request.args.get('search', '')
        color = request.args.get('color')
        available_only = request.args.get('available_only', 'false').lower() == 'true'
        limit = request.args.get('limit', 50, type=int)

        query = Vehicle.query

        if search:
            query = query.filter(
                or_(
                    Vehicle.brand.ilike(f'%{search}%'),
                    Vehicle.model.ilike(f'%{search}%'),
                    Vehicle.license_plate.ilike(f'%{search}%')
                )
            )

        if color:
            query = query.filter(Vehicle.color == color)

        if available_only:
            busy_vehicle_ids = db.session.query(Order.vehicle_id).filter(
                Order.status == 'in_progress'
            ).distinct().subquery()

            query = query.filter(~Vehicle.id.in_(busy_vehicle_ids))

        vehicles = query.limit(limit).all()

        response = {
            'success': True,
            'count': len(vehicles),
            'vehicles': [v.to_dict() for v in vehicles]
        }

        return jsonify(response)

    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        return jsonify(error_response), 500

@api_bp.route('/tariffs', methods=['GET'])
def get_tariffs():
    try:
        tariffs = Tariff.query.all()

        response = {
            'success': True,
            'count': len(tariffs),
            'tariffs': [t.to_dict() for t in tariffs]
        }

        return jsonify(response)

    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        return jsonify(error_response), 500

@api_bp.route('/operators', methods=['GET'])
def get_operators():
    try:
        operators = Operator.query.all()

        response = {
            'success': True,
            'count': len(operators),
            'operators': [o.to_dict() for o in operators]
        }

        return jsonify(response)

    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        return jsonify(error_response), 500

@api_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    try:
        order = Order.query.get_or_404(order_id)

        response = {
            'success': True,
            'order': order.to_dict(),
            'customer': order.customer.to_dict() if order.customer else None,
            'vehicle': order.vehicle.to_dict() if order.vehicle else None,
            'tariff': order.tariff.to_dict() if order.tariff else None,
            'operator': order.operator.to_dict() if order.operator else None
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/drivers/<int:driver_id>', methods=['GET'])
def get_driver_detail(driver_id):
    try:
        driver = Driver.query.get_or_404(driver_id)

        response = {
            'success': True,
            'driver': driver.to_dict(),
            'info': driver.info.to_dict() if driver.info else None,
            'vehicles': [v.to_dict() for v in driver.vehicles],
            'orders': [o.to_dict() for o in Order.query.filter(
                Order.vehicle_id.in_([v.id for v in driver.vehicles])
            ).limit(20)]
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500