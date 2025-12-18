from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from urllib.parse import urlparse


def validate_phone(value):
    if not value.startswith('+7') or len(value) != 12:
        raise ValidationError(
            _('Номер телефона должен начинаться с +7 и содержать 11 цифр')
        )

def validate_license_plate(value):
    import re
    pattern = r'^[АБВЕКМНОПРИСТУХ]\d{3}[АБВЕКМНОПРИСТУХ]{2}\d{2,3}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Номерной знак должен быть в формате: А123БВ45')
        )

def validate_driver_license(value):
    if len(value) != 10 or not value[:4].isdigit() or not value[4:6].isalpha() or not value[6:].isdigit():
        raise ValidationError(
            _('Водительское удостоверение должно быть в формате: 1234АВ5678')
        )

def validate_url(value):
    if value:
        parsed = urlparse(value)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValidationError(_('Введите корректный URL (например: https://example.com/image.jpg)'))

class Driver(models.Model):
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    phone = models.CharField(max_length=12,verbose_name='Телефон',validators=[validate_phone])

    objects = models.Manager()
    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'

    def __str__(self):
        return f"{self.full_name}"

class DriverInfo(models.Model):
    GENDER_CHOICES = [
        ('male', 'Мужской'),
        ('female', 'Женский')
    ]
    driver = models.OneToOneField(Driver,on_delete=models.CASCADE,related_name='info',verbose_name='Водитель')
    birth_date = models.DateField(verbose_name='Дата рождения',null=True,blank=True)
    driver_license = models.CharField(max_length=10,verbose_name='Водительское удостоверение',
                                      unique=True,validators=[validate_driver_license])
    photo = models.URLField(max_length=500,verbose_name='Фото водителя',null=True,blank=True, validators=[validate_url])
    experience_years = models.PositiveIntegerField(verbose_name='Стаж вождения (лет)',default=0)
    gender=models.CharField(max_length=7,choices=GENDER_CHOICES,verbose_name='Пол водителя')

    objects = models.Manager()

    class Meta:
        verbose_name = 'Дополнительная информация о водителе'
        verbose_name_plural = 'Дополнительная информация о водителях'

    def get_photo_url(self):
        if self.photo:
            return self.photo

    @property
    def has_photo(self):
        return bool(self.photo)

class Vehicle(models.Model):

    COLORS = [
        ('white', 'Белый'),
        ('black', 'Черный'),
        ('silver', 'Серебристый'),
        ('gray', 'Серый'),
        ('blue', 'Синий'),
        ('red', 'Красный'),
        ('yellow', 'Жёлтый'),
    ]
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True,
                               related_name='vehicles', blank=True, verbose_name='Водитель')
    brand = models.CharField(max_length=50, verbose_name='Марка')
    model = models.CharField(max_length=50, verbose_name='Модель')
    license_plate = models.CharField(max_length=15,verbose_name='Номерной знак',unique=True,validators=[validate_license_plate])
    color = models.CharField(max_length=20,choices=COLORS,verbose_name='Цвет')
    year = models.PositiveIntegerField(verbose_name='Год выпуска')
    mileage = models.PositiveIntegerField(verbose_name='Пробег')

    objects = models.Manager()

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'

    def __str__(self):
        return f"{self.brand} {self.model} ({self.license_plate})"

class Customer(models.Model):
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    phone = models.CharField(max_length=12,verbose_name='Телефон',validators=[validate_phone])

    objects = models.Manager()
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f"{self.full_name}"

class Tariff(models.Model):
    name = models.CharField(max_length=100, verbose_name='ФИО')
    cost_for_km = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Стоимость за км')

    objects = models.Manager()
    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'

    def __str__(self):
        return f"{self.name} - {self.cost_for_km} руб/км"

class Operator (models.Model):
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    phone = models.CharField(max_length=12,verbose_name='Телефон',validators=[validate_phone])

    objects = models.Manager()
    class Meta:
        verbose_name = 'Оператор'
        verbose_name_plural = 'Операторы'

    def __str__(self):
        return f"{self.full_name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'В процессе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE, related_name='orders',
                                 null=True,blank=True,verbose_name='Клиент')
    vehicle = models.ForeignKey(Vehicle,on_delete=models.CASCADE, related_name='orders',
                                null=True, blank=True,verbose_name='Автомобиль')
    tariff = models.ForeignKey(Tariff,on_delete=models.CASCADE, related_name='orders',
                               null=True, blank=True,verbose_name='Тарифы')
    order_time = models.DateTimeField(verbose_name='Время заказа', auto_now_add=True)
    range = models.DecimalField(max_digits=3, decimal_places=1,verbose_name='Дистанция поездки')
    status = models.CharField(max_length=15,choices=STATUS_CHOICES,verbose_name='Статус')
    operator = models.ForeignKey(Operator,on_delete=models.CASCADE,related_name='operator_order',verbose_name='Водитель')

    @property
    def total_cost(self):
        if self.tariff and self.range:
            return Decimal(str(self.range)) * self.tariff.cost_for_km

    objects = models.Manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-order_time']

