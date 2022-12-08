import time

import flask
from flask import Blueprint, render_template, request, flash, jsonify, Response, stream_with_context, stream_template
from flask_login import login_required, current_user
from random import uniform
from .generate_serial import generate_serial
from .models import Thermostat, UserLog
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def thermostats():
    if request.method == 'POST':
        thermostat_name = request.form.get('thermostat_name')
        thermostats_list = list()
        for therm in [therm for therm in Thermostat.query.all() if therm.user_id == current_user.id]:
            thermostats_list.append(therm.name.lower())
        if len(thermostat_name) < 1 or thermostat_name.lower() in thermostats_list:
            flash(
                'Имя терморегулятора должно быть уникальным для вашего набора терморегуляторов и длиньше одного символа',
                category='error')
        else:
            new_thermostat = Thermostat(name=thermostat_name, serial_num=generate_serial(23), user_id=current_user.id)
            db.session.add(new_thermostat)
            db.session.add(UserLog(user_id=current_user.id, message='Пользователь ' + str(current_user.first_name) +
                                                                    ' добавил новый терморегулятор ' + str(
                new_thermostat.name) +
                                                                    ' с серийным номером ' + str(
                new_thermostat.serial_num)))
            db.session.commit()
            flash(f'Терморегулятор {thermostat_name} добавлен!', category='success')

    return render_template("thermostats.html", user=current_user)


@views.route('/mock_thermostat/<string:serial>', methods=['GET'])
def mock_thermostat(serial):
    @stream_with_context
    def mocking_cycle():
        while True:
            thermostat = Thermostat.query.get(serial)
            new_temperature = thermostat.current_temp
            if thermostat.mock_mode:
                if thermostat.turn_on:
                    if thermostat.current_temp < thermostat.setpoint and thermostat.mode:
                        thermostat.relay = True
                        new_temperature += 0.2
                    elif thermostat.current_temp > thermostat.setpoint and not thermostat.mode:
                        thermostat.relay = True
                        new_temperature -= 0.2
                    else:
                        thermostat.relay = False
                        new_temperature += round(uniform(-0.1, 0.1), 1)
                else:
                    thermostat.relay = False
                    new_temperature += round(uniform(-0.1, 0.1), 1)
                thermostat.current_temp = round(new_temperature, 2)
            db.session.commit()
            print(thermostat.name, thermostat.current_temp, thermostat.relay)
            yield 'data: {"current_temp":"' + str(round(thermostat.current_temp, 2)) + '","relay":"' + \
                  str(thermostat.relay) + '"}\n\n'
            time.sleep(1.0)
    return Response(mocking_cycle(), mimetype='text/event-stream')


@views.route('/delete-thermostat', methods=['POST'])
def delete_thermostat():
    thermostat = json.loads(request.data)
    serial_num = thermostat['serial_num']
    thermostat = Thermostat.query.get(serial_num)
    if thermostat:
        if thermostat.user_id == current_user.id:
            db.session.delete(thermostat)
            db.session.add(UserLog(user_id=current_user.id,
                                   message='Пользователь ' + str(
                                       current_user.first_name) + ' удалил терморегулятор ' +
                                           str(thermostat.name) + ' с серийным номером ' + str(
                                       thermostat.serial_num)))
            db.session.commit()

    return jsonify({})


@views.route('/increment-setpoint', methods=['POST'])
def increment_setpoint():
    thermostat = json.loads(request.data)
    serial_num = thermostat['serial_num']
    thermostat = Thermostat.query.get(serial_num)
    if thermostat:
        if thermostat.user_id == current_user.id:
            if not thermostat.lock:
                if thermostat.setpoint >= 33:
                    flash('Выбрана опасно высокая температура. Надеюсь вы знаете что делаете.', 'warning')
                thermostat.setpoint += 1
                db.session.add(UserLog(user_id=current_user.id,
                                       message='Пользователь ' + str(current_user.first_name) +
                                               ' увеличил уставку терморегулятор ' + str(
                                           thermostat.name) + ' с серийным номером ' +
                                               str(thermostat.serial_num) + ' на один градус. Теперь его уставка равна ' +
                                               str(thermostat.setpoint)))
                db.session.commit()
            else:
                flash('Возможность изменения параметров через интерфейс заблокирована!','warning')

    return jsonify({})


@views.route('/decrement-setpoint', methods=['POST'])
def decrement_setpoint():
    thermostat = json.loads(request.data)
    serial_num = thermostat['serial_num']
    thermostat = Thermostat.query.get(serial_num)
    if thermostat:
        if thermostat.user_id == current_user.id:
            if not thermostat.lock:
                if thermostat.setpoint <= 5:
                    flash('Выбрана опасно низкая температура. Надеюсь вы знаете что делаете.', 'warning')
                thermostat.setpoint -= 1
                db.session.add(UserLog(user_id=current_user.id,
                                       message='Пользователь ' + str(current_user.first_name) +
                                               ' снизил уставку терморегулятор ' + str(
                                           thermostat.name) + ' с серийным номером ' +
                                               str(thermostat.serial_num) + ' на один градус. Теперь его уставка равна ' +
                                               str(thermostat.setpoint)))
                db.session.commit()
            else:
                flash('Возможность изменения параметров через интерфейс заблокирована!', 'warning')

    return jsonify({})


@views.route('/increment-brightness', methods=['POST'])
def increment_brightness():
    thermostat = json.loads(request.data)
    serial_num = thermostat['serial_num']
    thermostat = Thermostat.query.get(serial_num)
    if thermostat:
        if thermostat.user_id == current_user.id:
            if not thermostat.lock:
                if thermostat.brightness < 100:
                    thermostat.brightness += 1
                    db.session.add(UserLog(user_id=current_user.id,
                                           message='Пользователь ' + str(current_user.first_name) +
                                                   ' увеличил яркость терморегулятора ' + str(thermostat.name) +
                                                   ' с серийным номером ' + str(thermostat.serial_num) +
                                                   ' на один процент. Теперь его яркость равна ' +
                                                   str(thermostat.brightness)))
                    db.session.commit()
                else:
                    flash('Яркость не может быть выше 100%', category='error')
            else:
                flash('Возможность изменения параметров через интерфейс заблокирована!', 'warning')

    return jsonify({})


@views.route('/decrement-brightness', methods=['POST'])
def decrement_brightness():
    thermostat = json.loads(request.data)
    serial_num = thermostat['serial_num']
    thermostat = Thermostat.query.get(serial_num)
    if thermostat:
        if thermostat.user_id == current_user.id:
            if not thermostat.lock:
                if thermostat.brightness > 1:
                    thermostat.brightness -= 1
                    db.session.add(UserLog(user_id=current_user.id,
                                           message='Пользователь ' + str(current_user.first_name) +
                                                   ' снизил яркость терморегулятора ' + str(thermostat.name) +
                                                   ' с серийным номером ' + str(thermostat.serial_num) +
                                                   ' на один процент. Теперь его яркость равна ' +
                                                   str(thermostat.brightness)))
                    db.session.commit()
                else:
                    flash('Яркость не может быть ниже 1%', category='error')
            else:
                flash('Возможность изменения параметров через интерфейс заблокирована!', 'warning')

    return jsonify({})


@views.route('/switch-power', methods=['POST'])
def switch_power():
    thermostat = json.loads(request.data)
    serial_num = thermostat['serial_num']
    thermostat = Thermostat.query.get(serial_num)
    if thermostat:
        if thermostat.user_id == current_user.id:
            if not thermostat.lock:
                thermostat.turn_on = not thermostat.turn_on
                if thermostat.turn_on:
                    db.session.add(UserLog(user_id=current_user.id,
                                           message='Пользователь ' + str(current_user.first_name) +
                                                   ' включил терморегулятор ' + str(thermostat.name) +
                                                   ' с серийным номером ' + str(thermostat.serial_num)))
                else:
                    db.session.add(UserLog(user_id=current_user.id,
                                           message='Пользователь ' + str(current_user.first_name) +
                                                   ' выключил терморегулятор ' + str(thermostat.name) +
                                                   ' с серийным номером ' + str(thermostat.serial_num)))
                db.session.commit()
            else:
                flash('Возможность изменения параметров через интерфейс заблокирована!', 'warning')

    return jsonify({})


@views.route('/switch-wifi', methods=['POST'])
def switch_wifi():
    thermostat = json.loads(request.data)
    serial_num = thermostat['serial_num']
    thermostat = Thermostat.query.get(serial_num)
    if thermostat:
        if thermostat.user_id == current_user.id:
            if not thermostat.lock:
                thermostat.wifi = not thermostat.wifi
                if thermostat.wifi:
                    db.session.add(UserLog(user_id=current_user.id,
                                           message='Пользователь ' + str(current_user.first_name) +
                                                   ' включил wifi модуль терморегулятора ' + str(thermostat.name) +
                                                   ' с серийным номером ' + str(thermostat.serial_num)))
                else:
                    db.session.add(UserLog(user_id=current_user.id,
                                           message='Пользователь ' + str(current_user.first_name) +
                                                   ' выключил wifi модуль терморегулятора ' + str(thermostat.name) +
                                                   ' с серийным номером ' + str(thermostat.serial_num)))
                db.session.commit()
            else:
                flash('Возможность изменения параметров через интерфейс заблокирована!', 'warning')

    return jsonify({})


@views.route('/switch-mode', methods=['POST'])
def switch_mode():
    thermostat = json.loads(request.data)
    serial_num = thermostat['serial_num']
    thermostat = Thermostat.query.get(serial_num)
    if thermostat:
        if thermostat.user_id == current_user.id:
            if not thermostat.lock:
                thermostat.mode = not thermostat.mode
                if thermostat.mode:
                    db.session.add(UserLog(user_id=current_user.id,
                                           message='Пользователь ' + str(current_user.first_name) +
                                                   ' переключил режим терморегулятора ' + str(thermostat.name) +
                                                   ' с серийным номером ' + str(thermostat.serial_num) + ' на нагрев'))
                else:
                    db.session.add(UserLog(user_id=current_user.id,
                                           message='Пользователь ' + str(current_user.first_name) +
                                                   ' переключил режим терморегулятора ' + str(thermostat.name) +
                                                   ' с серийным номером ' + str(thermostat.serial_num) + ' на охлаждение'))
                db.session.commit()
            else:
                flash('Возможность изменения параметров через интерфейс заблокирована!', 'warning')

    return jsonify({})


@views.route('/switch-lock', methods=['POST'])
def switch_lock():
    thermostat = json.loads(request.data)
    serial_num = thermostat['serial_num']
    thermostat = Thermostat.query.get(serial_num)
    if thermostat:
        if thermostat.user_id == current_user.id:
            thermostat.lock = not thermostat.lock
            if thermostat.lock:
                db.session.add(UserLog(user_id=current_user.id,
                                       message='Пользователь ' + str(current_user.first_name) +
                                               ' переключил блокировку клавиатуры терморегулятора ' + str(
                                           thermostat.name) +
                                               ' с серийным номером ' + str(thermostat.serial_num) + ' на блокировку'))
            else:
                db.session.add(UserLog(user_id=current_user.id,
                                       message='Пользователь ' + str(current_user.first_name) +
                                               ' переключил блокировку клавиатуры терморегулятора ' + str(
                                           thermostat.name) +
                                               ' с серийным номером ' + str(
                                           thermostat.serial_num) + ' на разблокировку'))
            db.session.commit()

    return jsonify({})


@views.route('/switch-relay', methods=['POST'])
def switch_relay():
    thermostat = json.loads(request.data)
    serial_num = thermostat['serial_num']
    thermostat = Thermostat.query.get(serial_num)
    if thermostat:
        if thermostat.user_id == current_user.id:
            if not thermostat.lock:
                thermostat.relay = not thermostat.relay
                if thermostat.relay:
                    db.session.add(UserLog(user_id=current_user.id,
                                           message='Пользователь ' + str(current_user.first_name) +
                                                   ' включил реле терморегулятора ' + str(thermostat.name) +
                                                   ' с серийным номером ' + str(thermostat.serial_num)))
                else:
                    db.session.add(UserLog(user_id=current_user.id,
                                           message='Пользователь ' + str(current_user.first_name) +
                                                   ' выключил реле терморегулятора ' + str(thermostat.name) +
                                                   ' с серийным номером ' + str(thermostat.serial_num)))
                db.session.commit()
            else:
                flash('Возможность изменения параметров через интерфейс заблокирована!', 'warning')

    return jsonify({})
