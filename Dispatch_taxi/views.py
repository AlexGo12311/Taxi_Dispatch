from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import models
from django.db.models import Q

from .models import Driver, Vehicle, Order, Customer, Tariff, Operator
from .forms import DriverForm, DriverInfoForm, VehicleForm, OrderForm, CustomerForm, TariffForm, OperatorForm

def index(request):
    stats = {
        'total_drivers': Driver.objects.count(),
        'total_vehicles': Vehicle.objects.count(),
        'active_orders': Order.objects.filter(status='in_progress').count(),
        'total_orders': Order.objects.count(),
        'total_customers' : Customer.objects.count(),
        'total_tariffs' : Tariff.objects.count()
    }
    return render(request, 'index.html', {
        'stats': stats,
    })

def driver_list(request):
    drivers_list = Driver.objects.all()
    search = request.GET.get('search', '')
    if search:
        drivers_list = drivers_list.filter(
            Q(full_name__icontains=search)
        )

    return render(request, 'driver_list.html', {
        'search': search,
        'drivers_list': drivers_list
    })

def driver_detail(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    try:
        driver_info = driver.info
    except:
        driver_info = None

    return render(request, 'driver_detail.html', {
        'driver': driver,
        'driver_info': driver_info,
    })


def driver_create(request):
    if request.method == 'POST':
        driver_form = DriverForm(request.POST)
        info_form = DriverInfoForm(request.POST, request.FILES)

        if driver_form.is_valid() and info_form.is_valid():
            driver = driver_form.save()
            info = info_form.save(commit=False)
            info.driver = driver
            info.save()
            messages.success(request, 'Водитель успешно добавлен!')
            return redirect('driver_detail', pk=driver.pk)
    else:
        driver_form = DriverForm()
        info_form = DriverInfoForm()
    return render(request, 'driver_form.html', {
        'driver_form': driver_form,
        'info_form': info_form,
        'title': 'Добавить водителя'
    })


def driver_edit(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    try:
        driver_info = driver.info
    except:
        driver_info = None

    if request.method == 'POST':
        driver_form = DriverForm(request.POST, instance=driver)

        if driver_info:
            info_form = DriverInfoForm(request.POST, instance=driver_info)
        else:
            info_form = DriverInfoForm(request.POST)

        if driver_form.is_valid() and info_form.is_valid():
            driver = driver_form.save()

            info = info_form.save(commit=False)
            info.driver = driver
            info.save()

            messages.success(request, 'Данные водителя обновлены!')
            return redirect('driver_detail', pk=driver.pk)
    else:
        driver_form = DriverForm(instance=driver)

        if driver_info:
            initial_data = {}
            if driver_info.birth_date:
                initial_data['birth_date'] = driver_info.birth_date.strftime('%Y-%m-%d')
            info_form = DriverInfoForm(instance=driver_info)
        else:
            info_form = DriverInfoForm()

    return render(request, 'driver_form.html', {
        'driver_form': driver_form,
        'info_form': info_form,
        'title': 'Редактировать водителя',
        'driver': driver
    })


def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        driver.delete()
        messages.success(request, 'Водитель удален!')
        return redirect('driver_list')
    return render(request, 'driver_confirm_delete.html', {'driver': driver })

def vehicle_list(request):
    vehicles_list = Vehicle.objects.all()
    search = request.GET.get('search', '')

    return render(request, 'vehicle_list.html', {
        'search': search,
        'vehicles_list': vehicles_list,
        'colors': Vehicle.COLORS
    })


def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    return render(request, 'vehicle_detail.html', {
        'vehicle': vehicle,
    })

def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)

        if form.is_valid():
            vehicle = form.save()
            messages.success(request, 'Автомобиль успешно добавлен!')
            return redirect('vehicle_detail', pk=vehicle.pk)
    else:
        form = VehicleForm()

    return render(request, 'vehicle_form.html', {
        'form': form,
        'title': 'Добавить автомобиль'
    })


def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)

        if form.is_valid():
            vehicle = form.save()
            messages.success(request, 'Данные автомобиля обновлены!')
            return redirect('vehicle_detail', pk=vehicle.pk)
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'vehicle_form.html', {
        'form': form,
        'title': 'Редактировать автомобиль',
        'vehicle': vehicle
    })


def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if request.method == 'POST':
        if Order.objects.filter(vehicle=vehicle).exists():
            messages.error(request, 'Нельзя удалить автомобиль, у которого есть заказы!')
            return redirect('vehicle_detail', pk=vehicle.pk)

        vehicle.delete()
        messages.success(request, 'Автомобиль удален!')
        return redirect('vehicle_list')
    return render(request, 'vehicle_confirm_delete.html', { 'vehicle': vehicle })


def customer_list(request):
    customers_list = Customer.objects.all().order_by('full_name')
    search = request.GET.get('search', '')
    if search:
        customers_list = customers_list.filter(
            Q(full_name__icontains=search)
        )

    return render(request, 'customer_list.html', {
        'customers_list': customers_list,
        'search': search,
    })

def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = Order.objects.filter(customer=customer).order_by('-order_time')

    return render(request, 'customer_detail.html', {
        'customer': customer,
        'orders': orders,
    })

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, 'Клиент успешно добавлен!')
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()

    return render(request, 'customer_form.html', {
        'form': form,
        'title': 'Добавить клиента'
    })


def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            messages.success(request, 'Данные клиента обновлены!')
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'customer_form.html', {
        'form': form,
        'title': 'Редактировать клиента',
        'customer': customer
    })


def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        if Order.objects.filter(customer=customer).exists():
            messages.error(request, 'Нельзя удалить клиента, у которого есть заказы!')
            return redirect('customer_detail', pk=customer.pk)

        customer.delete()
        messages.success(request, 'Клиент удален!')
        return redirect('customer_list')

    return render(request, 'customer_confirm_delete.html', {'customer': customer})


def tariff_list(request):
    tariffs_list = Tariff.objects.all().order_by('name')
    search = request.GET.get('search', '')

    return render(request, 'tariff_list.html', {
        'tariffs_list': tariffs_list,
        'search': search,
    })

def tariff_create(request):
    if request.method == 'POST':
        form = TariffForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тариф успешно добавлен!')
            return redirect('tariff_list')
    else:
        form = TariffForm()

    return render(request, 'tariff_form.html', {
        'form': form,
        'title': 'Добавить тариф'
    })

def tariff_edit(request, pk):
    tariff = get_object_or_404(Tariff, pk=pk)

    if request.method == 'POST':
        form = TariffForm(request.POST, instance=tariff)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные тарифа обновлены!')
            return redirect('tariff_list')
    else:
        form = TariffForm(instance=tariff)

    return render(request, 'tariff_form.html', {
        'form': form,
        'title': 'Редактировать тариф',
        'tariff': tariff
    })


def tariff_delete(request, pk):
    tariff = get_object_or_404(Tariff, pk=pk)

    if request.method == 'POST':

        tariff.delete()
        messages.success(request, 'Тариф удален!')
        return redirect('tariff_list')

    return render(request, 'tariff_confirm_delete.html', {'tariff': tariff})


def operator_detail(request):
    operators = Operator.objects.all()

    return render(request, 'operator_detail.html', {
        'operators': operators,
    })

def operator_create(request):
    if request.method == 'POST':
        form = OperatorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Оператор создан!')
            return redirect('operator_detail')
    else:
        form = OperatorForm()

    return render(request, 'operator_form.html', {
        'form': form,
        'title': 'Создать оператора'
    })

def operator_edit(request, pk):
    operator = get_object_or_404(Operator, pk=pk)

    if request.method == 'POST':
        form = OperatorForm(request.POST, instance=operator)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные оператора обновлены!')
            return redirect('operator_detail')
    else:
        form = OperatorForm(instance=operator)

    return render(request, 'operator_form.html', {
        'form': form,
        'title': 'Редактировать оператора',
        'operator': operator
    })

def operator_delete(request, pk):
    operator = get_object_or_404(Operator, pk=pk)

    if request.method == 'POST':
        if Order.objects.filter(operator=operator).exists():
            messages.error(request, 'Нельзя удалить оператора, который обслуживает заказы!')
            return redirect('operator_detail')
        operator.delete()
        messages.success(request, 'Оператор удален!')
        return redirect('operator_detail')

    return render(request, 'operator_confirm_delete.html', {'operator': operator})

def get_busy_vehicles():
    return Order.objects.filter(
        status__in=['assigned', 'in_progress']
    ).values_list('vehicle_id', flat=True)

def order_list(request):
    orders_list = Order.objects.all().select_related('customer', 'vehicle', 'tariff')
    search = request.GET.get('search', '')
    if search:
        orders_list = orders_list.filter(customer__full_name__icontains=search)
    status = request.GET.get('status', '')
    if status:
        orders_list = orders_list.filter(status=status)
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        try:
            orders_list = orders_list.annotate(
                calculated_price=models.F('range') * models.F('tariff__cost_for_km')
            ).filter(calculated_price__gte=float(min_price))
        except:
            pass
    if max_price:
        try:
            orders_list = orders_list.annotate(
                calculated_price=models.F('range') * models.F('tariff__cost_for_km')
            ).filter(calculated_price__lte=float(max_price))
        except:
            pass
    sort = request.GET.get('sort', '-order_time')
    if sort in ['order_time', '-order_time', 'total_cost', '-total_cost']:
        if sort in ['total_cost', '-total_cost']:
            orders_list = orders_list.annotate(
                calculated_price=models.F('range') * models.F('tariff__cost_for_km')
            ).order_by(sort.replace('total_cost', 'calculated_price'))
        else:
            orders_list = orders_list.order_by(sort)

    return render(request, 'order_list.html', {
        'orders_list': orders_list,
        'search': search,
        'status': status,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
        'status_choices': Order.STATUS_CHOICES,
    })


def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'order_detail.html', {
        'order': order
    })

def order_create(request):
    customer_id = request.GET.get('customer')
    operator_id = request.GET.get('operator')
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.operator=Operator.objects.first()
            order.save()
            messages.success(request, 'Заказ успешно создан!')
            return redirect('order_detail', pk=order.pk)
    else:
        initial_data = {}
        if customer_id:
            try:
                customer = Customer.objects.get(pk=customer_id)
                initial_data['customer'] = customer
            except:
                pass
        if operator_id:
            try:
                operator = Operator.objects.get(pk=operator_id)
                initial_data['operator'] = operator
            except:
                messages.warning(request, 'Оператор не найден!')
        form = OrderForm(initial=initial_data)
        busy_vehicles = get_busy_vehicles()
        form.fields['vehicle'].queryset = Vehicle.objects.exclude(
            id__in=busy_vehicles
        ).order_by('license_plate')

    return render(request, 'order_form.html', {
        'form': form,
        'title': 'Создать заказ'
    })


def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)

        if form.is_valid():
            order = form.save()
            order.save()
            messages.success(request, 'Заказ обновлен!')
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)
        busy_vehicles = get_busy_vehicles()
        available_vehicles = Vehicle.objects.exclude(id__in=busy_vehicles)
        if order.vehicle:
            available_vehicles = available_vehicles | Vehicle.objects.filter(id=order.vehicle.id)

        form.fields['vehicle'].queryset = available_vehicles.distinct().order_by('license_plate')

    return render(request, 'order_form.html', {
        'form': form,
        'title': 'Редактировать заказ',
        'order': order
    })

def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Заказ удален!')
        return redirect('order_list')
    return render(request, 'order_confirm_delete.html', {
        'order': order
    })



