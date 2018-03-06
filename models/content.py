# coding=utf-8
from datetime import datetime

from pytz import timezone
from tornkts.base.mongodb import BaseDocument
from mongoengine import StringField, DateTimeField, IntField


class Text(BaseDocument):
    key = StringField(required=True, unique=True)
    value = StringField(required=True)
    comment = StringField()

    update_date = DateTimeField()

    def save(self, *args, **kwargs):
        self.update_date = datetime.now(tz=timezone('UTC'))
        return super(Text, self).save(*args, **kwargs)

    def to_dict_impl(self, **kwargs):
        return {
            'id': self.get_id(),
            'key': self.key,
            'value': self.value,
            'comment': self.comment,
            'update_date': self.update_date
        }

    @staticmethod
    def get(key):
        try:
            return Text.objects.get(key=key)
        except:
            return False

    @classmethod
    def format(cls, key, *args):
        try:
            text = Text.get(key)
            if not text:
                text = cls.defaults().get(key, '')
            else:
                text = text.value
            return text.format(*args)
        except:
            return ''

    @staticmethod
    def defaults():
        return {
            'CL_MSG_WELCOME': u'Здравствуйте!\n\nНаши курсы сейчас:\n{0}\n\nЧто вы хотите поменять?',
            'CL_SEND_GEO': u'Отправьте свою гео-позицию, чтобы мы могли подобрать для вас ближайший обменник',
            'CL_RESERV': u'Спасибо. Мы резервируем для вас курс и сумму в ближайшем обменнике. Это может занять до 15 минут',
            'CL_SUCCESS_RESERV': u"""
Спасибо. Ваш заказ подтвержден пунктом обмена валюты.
Адрес пункта обмена валюты: {0}
Телефон: {1}
Номер вашего заказа: {2}
Сообщите номер заказа в обменнике""",
            'CL_SUCCESS_WARNING': u"Внимание! Чтобы воспользоваться зафиксированным курсом, нужно совершить операцию не позже {0}",
            'CL_FAIL_RESERV': u'К сожалению мы не смогли найти обменник в радиусе 20 км.',
            'CL_FAIL_RESERV_TIMEOUT': u'Извините. Мы не смогли подтвердить ваш курс. Попробуйте, пожалуйста, еще раз ',
            'CL_REQUEST_RATING': u'Оцените, пожалуйста, как вас обслужили',
            'CL_RATING_COMMENT_REQUEST': u'Мы сожалеем и обещаем исправиться. Сообщите, что пошло не так.',
            'CL_RATING_COMMENT_GOOD': u'Спасибо! Хорошего дня!',
            'CL_RATING_COMMENT_GOOD_DAY': u'Хорошего дня!',
            'CL_CONFIRM_YES': u'Да, подтверждаю',
            'CL_CONFIRM_NO': u'Нет, отменить операцию',
            'CL_OPERATION_CANCEL': u'Операция отменена. Введите /start, чтобы начать заново',
            'CL_CONFIRM': u'Хорошо! Вы {0} {1}{2} по курсу {3} за {4} руб. Подвердите.',
            'CL_CONFIRM_REPEAT': u'Подтвердите или отмените операцию',
            'CL_ORDER_FORMED': u'Вы сформировали заказ на обмен валюты в пункте обмена по указанным выше контактным данным',
            'CL_NEW_EXCHANGE': u'Новый обмен',
            'CL_CONFIRM_TESTING': """
Чат-бот ДоллаРубль работает сегодня в бета-режиме.
Вы являетесь тестером сервиса или Вы клиент, и провести реальное бронирование валюты?
            """,
            'CL_YES_REAL_RESERVE': 'Да, бронируйте валюту, еду менять',
            'CL_NO_TESTING': 'Нет, я тестирую',
            'CL_CANCEL_REQUEST': 'Хорошо, заявка отменена',

            'EX_MSG_WELCOME': u'Здравствуйте! Для заполнения информации введите /update',
            'EX_MSG_STOP': u'Прием заявок временно приостановлен',
            'EX_MSG_ENTER_TITLE': u'Введите название',
            'EX_MSG_ENTER_PHONE': u'Введите телефон',
            'EX_MSG_ENTER_LOCATION': u'Отправьте локацию',
            'EX_MSG_ENTER_ADDRESS': u'Введите адрес',
            'EX_MSG_UPDATED': u'Ваш профиль обновлен',
            'EX_EXCHANGE_REQUEST': u"""
Запрос на обмен валюты #{0}:
Валюта: {1}
Курс покупки: {3}
Количество: {2}
Чтобы подтвердить запрос, введите /confirm {0} <номер заказа>""",
            'EX_BAD_NUMBER': u'Вы ввели неверный id заказа',
            'EX_BAD_EXTERNAL_ID': u'Вы ввели неверный номер заказа',
            'EX_REQUEST_NOT_FOUND': u'Запрос не найден',
            'EX_REQUEST_TIMEOUT': u'Превышено время ожидания клиентом',
            'EX_ALREADY_SEND': u'Запрос уже обработан другим обменником',
            'EX_SUCCESS': u'Успешно!',
            'EX_TLGRM_ID': 'Ваш Telegram Id: {0}'
        }


class Interval(BaseDocument):
    key = StringField(required=True, unique=True)
    value = IntField(required=True)
    comment = StringField()

    update_date = DateTimeField()

    def save(self, *args, **kwargs):
        self.update_date = datetime.now(tz=timezone('UTC'))
        return super(Interval, self).save(*args, **kwargs)

    def to_dict_impl(self, **kwargs):
        return {
            'id': self.get_id(),
            'key': self.key,
            'value': self.value,
            'comment': self.comment,
            'update_date': self.update_date
        }

    @classmethod
    def get(cls, key):
        try:
            interval = Interval.objects.get(key=key)
            return interval.value
        except:
            return cls.defaults().get(key, 0)

    @classmethod
    def seconds(cls, key):
        try:
            interval = cls.get(key)
            if not interval:
                return False
            return interval * 60
        except:
            return False

    @classmethod
    def milli(cls, key):
        result = cls.seconds(key)
        return result * 1000 if result else False

    @staticmethod
    def defaults():
        return {
            'fail_timeout': 10,
            'rating_request_timeout': 40,
            'max_radius': 20,
            'reserve_time': 60
        }
