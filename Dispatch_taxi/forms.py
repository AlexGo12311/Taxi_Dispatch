from django import forms
from django.core.exceptions import ValidationError
from .models import Driver, DriverInfo, Vehicle, Order, Customer, Tariff, Operator

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['full_name', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван Иванович'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+79991234567'})
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+7'):
            raise ValidationError('Телефон должен начинаться с +7')
        if len(phone) != 12:
            raise ValidationError('Телефон должен содержать 11 цифр после +7')
        return phone

class DriverInfoForm(forms.ModelForm):
    class Meta:
        model = DriverInfo
        exclude = ['driver']
        widgets = {
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            },format='%Y-%m-%d'
            ),
            'driver_license': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234АВ5678'
            }),
            'photo': forms.URLInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'
        widgets = {
            'driver': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Марка'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Модель'
            }),
            'license_plate': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Формат: А123БВ45'
            }),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1960,
                'max': 2025
            }),
            'mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Км'
            }),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ФИО'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+79991234567'
            })
        }
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+7'):
            raise ValidationError('Телефон должен начинаться с +7')
        if len(phone) != 12:
            raise ValidationError('Телефон должен содержать 11 цифр после +7')
        return phone

class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = ['name', 'cost_for_km']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'cost_for_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 0.01,
                'min': 0
            }),
        }

class OperatorForm(forms.ModelForm):
    class Meta:
        model = Operator
        fields = ['full_name', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ФИО'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+79991234567'
            }),
        }
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+7'):
            raise ValidationError('Телефон должен начинаться с +7')
        if len(phone) != 12:
            raise ValidationError('Телефон должен содержать 11 цифр после +7')
        return phone

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['order_time', 'operator']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'tariff': forms.Select(attrs={'class': 'form-control'}),
            'range': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 0.1,
                'min': 0
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
