# coding=utf-8
import logging
import datetime
from content.awa_client import STEP_SEARCH_SUCCESS
from models.awa import Exchange, Request
from models.content import Text, Interval
from roboman.bot import BaseBot
from roboman.keyboard import ReplyKeyboardHide, ReplyKeyboard, KeyboardButton
from geopy.distance import vincenty
from tornkts import utils
from settings import options

logger = logging.getLogger('awa_exchange')


class AwaExchangeBot(BaseBot):
    name = 'awa_exchange'
    key = options.key_awa_exchange

    updating = {}

    @classmethod
    def on_hook(cls, data):
        text = data.get('text')

        try:
            exchange = Exchange.objects.get(out_id=data.get('from_id'))
        except Exchange.DoesNotExist:
            exchange = Exchange(out_id=data.get('from_id'))
            exchange.save()

        if cls.match_command('/start', text):
            if exchange.title and exchange.phone:
                exchange.active = True
                exchange.save()
            cls.send(
                chat_id=data.get('chat_id'),
                text=Text.format('EX_MSG_WELCOME'),
                reply_markup=ReplyKeyboardHide().to_json()
            )
            return

        if cls.match_command('/id', text):
            cls.send(
                chat_id=data.get('chat_id'),
                text=Text.format('EX_TLGRM_ID', data.get('chat_id')),
                reply_markup=ReplyKeyboardHide().to_json()
            )
            return
        elif cls.match_command('/stop', text):
            exchange.active = False
            exchange.save()
            cls.send(
                chat_id=data.get('chat_id'),
                text=Text.format('EX_MSG_STOP'),
                reply_markup=ReplyKeyboardHide().to_json()
            )
            return

        data['exchange'] = exchange
        data['exchange_id'] = exchange.get_id()

        if cls.match_command('/update', text):
            cls.updating[exchange.get_id()] = {'step': 0}
        elif cls.match_command('/confirm', text):
            data['args'] = cls.match_command('/confirm', text).get('args')
            cls._confirm(data)
            return

        if exchange.get_id() in cls.updating:
            cls._updating(data)

    @classmethod
    def _updating(cls, data):
        updating = cls.updating[data.get('exchange_id')]
        step = updating.get('step', 0)
        exchange = data['exchange']
        kwargs = {}
        if step == 0:
            title = str(exchange.title)
            if title != 'None':
                keyboard = ReplyKeyboardHide(keyboard=[[title]])
                kwargs['reply_markup'] = keyboard.to_json()
            cls.send(chat_id=data.get('chat_id'), text=Text.format('EX_MSG_ENTER_TITLE'), **kwargs)
        elif step == 1:
            exchange.title = data.get('text')
            exchange.save()

            phone = str(exchange.phone)
            if phone != 'None':
                keyboard = ReplyKeyboardHide(keyboard=[[phone]])
                kwargs['reply_markup'] = keyboard.to_json()

            cls.send(chat_id=data.get('chat_id'), text=Text.format('EX_MSG_ENTER_PHONE'), **kwargs)
        elif step == 2:
            exchange.phone = data.get('text')
            exchange.save()

            keyboard = ReplyKeyboard(keyboard=[[KeyboardButton(text=u'Отправить гео-позицию', request_location=True)]])
            kwargs['reply_markup'] = keyboard.to_json()

            cls.send(chat_id=data.get('chat_id'), text=Text.format('EX_MSG_ENTER_LOCATION'), **kwargs)
        elif step == 3:
            location = data.get('location')
            if location is None:
                cls.send(chat_id=data.get('chat_id'), text=Text.format('EX_MSG_ENTER_LOCATION'))
                return
            else:
                exchange.geo = [location.get('latitude'), location.get('longitude')]
                exchange.save()

                cls.send(
                    chat_id=data.get('chat_id'),
                    text=Text.format('EX_MSG_ENTER_ADDRESS'),
                    reply_markup=ReplyKeyboardHide().to_json()
                )
        elif step == 4:
            exchange.address = data.get('text')
            exchange.active = True
            exchange.save()
            cls.send(
                chat_id=data.get('chat_id'),
                text=Text.format('EX_MSG_UPDATED'),
                reply_markup=ReplyKeyboardHide().to_json()
            )

            del cls.updating[data.get('exchange_id')]
            return

        updating['step'] = step + 1
        cls.updating[data.get('exchange_id')] = updating

    @classmethod
    def _confirm(cls, data=None, request=None, exchange=None, external_id=None):
        if data is None:
            data = {}
        if exchange is None and request is None and external_id is None:
            number = utils.to_int(data.get('args')[0], -1)
            if number < 0:
                cls.send(
                    chat_id=data.get('chat_id'),
                    text=Text.format('EX_BAD_NUMBER'),
                    reply_markup=ReplyKeyboardHide().to_json()
                )
                return

            try:
                external_id = utils.to_int(data.get('args')[1], -1)
                if external_id < 0:
                    raise Exception
            except:
                cls.send(
                    chat_id=data.get('chat_id'),
                    text=Text.format('EX_BAD_EXTERNAL_ID'),
                    reply_markup=ReplyKeyboardHide().to_json()
                )
                return

            try:
                request = Request.objects(number=number).get()
            except:
                cls.send(
                    chat_id=data.get('chat_id'),
                    text=Text.format('EX_REQUEST_NOT_FOUND'),
                    reply_markup=ReplyKeyboardHide().to_json()
                )
                return
            if request.fail_sended:
                cls.send(
                    chat_id=data.get('chat_id'),
                    text=Text.format('EX_REQUEST_TIMEOUT'),
                    reply_markup=ReplyKeyboardHide().to_json()
                )
                return

            exchange = data['exchange']

        if request.exchange is None:
            request.exchange = exchange
            request.step = STEP_SEARCH_SUCCESS
            request.external_id = external_id
            try:
                request.distance = vincenty(request.geo.get('coordinates'),
                                            exchange.geo.get('coordinates')).meters / 1000.0
            except:
                pass
            request.user = request.user
            request.save()

            cls.send(
                chat_id=exchange.out_id,
                text=Text.format('EX_SUCCESS', external_id),
                reply_markup=ReplyKeyboardHide().to_json()
            )

            from bots.awa_client import AwaClientBot
            AwaClientBot.send(
                chat_id=request.user.out_id,
                text=Text.format('CL_SUCCESS_RESERV', exchange.address, exchange.phone, request.external_id)
            )
            AwaClientBot.sendLocation(
                chat_id=request.user.out_id,
                latitude=exchange.geo.get('coordinates')[0],
                longitude=exchange.geo.get('coordinates')[1]
            )

            time = datetime.datetime.now()
            time += datetime.timedelta(seconds=Interval.seconds('reserve_time'))

            AwaClientBot.send(
                chat_id=request.user.out_id,
                text=Text.format('CL_SUCCESS_WARNING', time.strftime('%d.%m.%Y %H:%M'))
            )
        else:
            cls.send(
                chat_id=data.get('chat_id'),
                text=Text.format('EX_ALREADY_SEND'),
                reply_markup=ReplyKeyboardHide().to_json()
            )
