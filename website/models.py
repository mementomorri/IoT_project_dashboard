from . import db
from flask_login import UserMixin
from .generate_serial import generate_serial
from sqlalchemy.sql import func


class Thermostat(db.Model):
    name = db.Column(db.String(150))
    serial_num = db.Column(db.String(30), primary_key=True, default=generate_serial(23))  # Случайный серийник
    turn_on = db.Column(db.Boolean, default=True)  # True - вкл, Flase - выкл
    wifi = db.Column(db.Boolean, default=True)  # True - есть wifi подключение, False - подключения нет
    current_temp = db.Column(db.Float(precision=2),
                             default=0.0)  # Текущая температура в °C, точность до одного символа после запятой
    setpoint = db.Column(db.Integer, default=22)  # Уставка в °C, точность до целых символов
    brightness = db.Column(db.Integer, default=15)  # Яркость с точностью до целых, %
    mode = db.Column(db.Boolean, default=True)  # True - обогрев, False - охлаждение
    lock = db.Column(db.Boolean, default=False)  # True - кнопки заблокированы, False - разблокированы
    relay = db.Column(db.Boolean, default=True) # True - реле включено, Flase - реле выключено
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    thermostats = db.relationship('Thermostat')
    logs = db.relationship('UserLog')


class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(255))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
