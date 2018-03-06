# coding=utf-8
import locale
import re

import emoji
from mongoengine import Q

from content import awa_client
from content.awa_client import GBR, CHF
from models.awa import User, Request, Currency, Exchange
from models.content import Text, Interval
from roboman.bot import BaseBot
from roboman.keyboard import ReplyKeyboard, ReplyKeyboardHide, KeyboardButton
from tornkts import utils
import logging
from settings import options

logger = logging.getLogger('awa_client')


class AwaClientBot(BaseBot):
    name = 'TestAwaClient'
    key = options.key_awa_client

    @classmethod
    def num_split(cls, num):
        if isinstance(num, float):
            fract = round(num - int(num), 2)
        else:
            fract = False

        s = '%d' % num
        groups = []
        while s and s[-1].isdigit():
            groups.append(s[-3:])
            s = s[:-3]
        return s + ' '.join(reversed(groups)) + ('.' + str(fract)[2:] if fract and fract > 0 else '')

    @classmethod
    def on_hook(cls, data):
        try:
            user = User.objects.get(out_id=data.get('from_id'))
            user.username = data.get('from_username')
            user.save()
        except User.DoesNotExist:
            user = User(
                out_id=data.get('from_id'),
                name=data.get('from_first_name'),
                surname=data.get('from_last_name'),
                username=data.get('from_username')
            )
            user.save()

        if user.current_request is None or Request.objects(pk=user.current_request.id).count() == 0:
            request = Request(user=user)
            request.save()

            user.current_request = request
            user.save()
        else:
            request = Request.objects.get(pk=user.current_request.id)

        request.user = user
        data['user'] = user
        data['request'] = request

        text = data.get('text')

        if repr(text) in [repr(u'Не менял'),
                          repr(emoji.emojize(':star:', True)),
                          repr(emoji.emojize(':star::star:', True)),
                          repr(emoji.emojize(':star::star::star:', True)),
                          repr(emoji.emojize(':star::star::star::star:', True)),
                          repr(emoji.emojize(':star::star::star::star::star:', True))]:
            cls._on_rating(**data)
            return

        if cls.match_command('/start', text) or cls.match_command(Text.format('CL_NEW_EXCHANGE'), text):
            cls._on_start(**data)
        elif request.step == awa_client.STEP_INPUT_OPERATION:
            cls._on_choose_type(**data)
        elif request.step == awa_client.STEP_INPUT_AMOUNT:
            cls._on_enter_amount(**data)
        elif request.step == awa_client.STEP_CONFIRM:
            cls._on_confirm(**data)
        elif request.step in [awa_client.STEP_ENTER_GEO, awa_client.STEP_CONFIRM_NO_TESTING]:
            cls._on_enter_geo(**data)
        else:
            cls._try_get_comment(**data)

    @classmethod
    def _on_start(cls, **kwargs):
        keyboard = []
        currs = {}
        codes = set()

        for item in Currency.objects:
            codes.add(item.code.upper())
            currs[item.code.upper() + '_' + item.direct] = item.value

        codes = sorted(list(codes), key=lambda x: ['USD', 'EUR', 'GBR', 'CHF'].index(x))
        welcome_currencies = []

        for code in codes:
            if code == 'USD':
                keyboard.append([
                    awa_client.CURRENCY_EXCHANGE[Request.TYPE_BUY_USD],
                    awa_client.CURRENCY_EXCHANGE[Request.TYPE_SAIL_USD]
                ])
                welcome_currencies.append('доллар {0}/{1}'.format(currs.get('USD_sale'), currs.get('USD_buy')))
            elif code == 'EUR':
                keyboard.append([
                    awa_client.CURRENCY_EXCHANGE[Request.TYPE_BUY_EUR],
                    awa_client.CURRENCY_EXCHANGE[Request.TYPE_SAIL_EUR]
                ])
                welcome_currencies.append('евро {0}/{1}'.format(currs.get('EUR_sale'), currs.get('EUR_buy')))
            elif code == 'GBR':
                keyboard.append([
                    awa_client.CURRENCY_EXCHANGE[Request.TYPE_BUY_GBR],
                    awa_client.CURRENCY_EXCHANGE[Request.TYPE_SAIL_GBR]
                ])
                welcome_currencies.append('фунт стерлингов {0}/{1}'.format(currs.get('GBR_sale'), currs.get('GBR_buy')))
            elif code == 'CHF':
                keyboard.append([
                    awa_client.CURRENCY_EXCHANGE[Request.TYPE_BUY_CHF],
                    awa_client.CURRENCY_EXCHANGE[Request.TYPE_SAIL_CHF]
                ])
                welcome_currencies.append(
                    'швейцарский франк {0}/{1}'.format(currs.get('CHF_sale'), currs.get('CHF_buy')))

        keyboard = ReplyKeyboard(keyboard=keyboard)

        cls.send(
            chat_id=kwargs.get('chat_id'),
            text=Text.format('CL_MSG_WELCOME', "\n".join(welcome_currencies)),
            reply_markup=keyboard.to_json()
        )

        user = kwargs.get('user')
        request = kwargs.get('request')

        if request.step > awa_client.STEP_ZERO:
            request = Request(user=user)

        request.step = awa_client.STEP_INPUT_OPERATION
        request.save()

        user.current_request = request
        user.save()

    @classmethod
    def _on_choose_type(cls, **kwargs):
        text = kwargs.get('text')
        request = kwargs.get('request')

        currencies = {}
        for item in Currency.objects:
            currencies[item.direct + '_' + item.code.lower()] = item.value

        for k, v in awa_client.CURRENCY_EXCHANGE.items():
            if text == v:
                request.type = k
                request.step = awa_client.STEP_INPUT_AMOUNT
                request.course = currencies.get(k)
                request.save()

                cls.send(
                    chat_id=kwargs.get('chat_id'),
                    text=awa_client.CURRENCY_EXCHANGE_QUESTION.get(k),
                    reply_markup=ReplyKeyboardHide().to_json()
                )

                return
        cls._on_start(**kwargs)

    @classmethod
    def _on_enter_amount(cls, **kwargs):
        text = kwargs.get('text')
        amount = utils.to_int(text, None)
        request = kwargs.get('request')

        if amount is None:
            cls.send(chat_id=kwargs.get('chat_id'), text=u'Введите число')
        else:
            request.amount = amount
            request.step = awa_client.STEP_CONFIRM
            request.save()

            keyboard = ReplyKeyboard(keyboard=[
                [Text.format('CL_CONFIRM_YES'), Text.format('CL_CONFIRM_NO')]
            ])

            currencies = {}
            for item in Currency.objects:
                currencies[item.code.upper() + '_' + item.direct] = float(item.value)

            if request.type == Request.TYPE_BUY_USD:
                course = str(currencies.get('USD_buy', 0)) + u' руб/$'
                operation = [
                    u'покупаете',
                    cls.num_split(request.amount),
                    u'$',
                    course,
                    cls.num_split(request.amount * currencies.get('USD_buy', 0))
                ]
            elif request.type == Request.TYPE_SAIL_USD:
                course = str(currencies.get('USD_sale', 0)) + u' руб/$'
                operation = [
                    u'продаете',
                    cls.num_split(request.amount),
                    u'$',
                    course,
                    cls.num_split(request.amount * currencies.get('USD_sale', 0))
                ]
            elif request.type == Request.TYPE_BUY_EUR:
                course = str(currencies.get('EUR_buy', 0)) + u' руб/€'
                operation = [
                    u'покупаете',
                    cls.num_split(request.amount),
                    u'€',
                    course,
                    cls.num_split(request.amount * currencies.get('EUR_buy', 0))
                ]
            elif request.type == Request.TYPE_SAIL_EUR:
                course = str(currencies.get('EUR_sale', 0)) + u' руб/€'
                operation = [
                    u'продаете',
                    cls.num_split(request.amount),
                    u'€',
                    course,
                    cls.num_split(request.amount * currencies.get('EUR_sale', 0))
                ]
            elif request.type == Request.TYPE_BUY_GBR:
                course = str(currencies.get('GBR_buy', 0)) + u' руб/' + GBR
                operation = [
                    u'покупаете',
                    cls.num_split(request.amount),
                    GBR,
                    course,
                    cls.num_split(request.amount * currencies.get('GBR_buy', 0))
                ]
            elif request.type == Request.TYPE_SAIL_GBR:
                course = str(currencies.get('GBR_sale', 0)) + u' руб/' + GBR
                operation = [
                    u'продаете',
                    cls.num_split(request.amount),
                    GBR,
                    course,
                    cls.num_split(request.amount * currencies.get('GBR_sale', 0))
                ]

            elif request.type == Request.TYPE_BUY_CHF:
                course = str(currencies.get('CHF_buy', 0)) + u' руб/' + CHF
                operation = [
                    u'покупаете',
                    cls.num_split(request.amount),
                    CHF,
                    course,
                    cls.num_split(request.amount * currencies.get('CHF_buy', 0))
                ]
            elif request.type == Request.TYPE_SAIL_CHF:
                course = str(currencies.get('CHF_sale', 0)) + u' руб/' + CHF
                operation = [
                    u'продаете',
                    cls.num_split(request.amount),
                    CHF,
                    course,
                    cls.num_split(request.amount * currencies.get('CHF_sale', 0))
                ]
            else:
                return

            cls.send(
                chat_id=kwargs.get('chat_id'),
                text=Text.format('CL_CONFIRM', *operation),
                reply_markup=keyboard.to_json()
            )

    @classmethod
    def _on_confirm(cls, **kwargs):
        text = kwargs.get('text')
        request = kwargs.get('request')
        user = kwargs.get('user')

        if text == Text.format('CL_CONFIRM_YES'):
            request.step = awa_client.STEP_ENTER_GEO
            request.save()

            cls.send(
                chat_id=kwargs.get('chat_id'),
                text=Text.format('CL_SEND_GEO'),
                reply_markup=ReplyKeyboard(
                    keyboard=[[KeyboardButton(text=u'Отправить гео-позицию', request_location=True)]]
                ).to_json()
            )
        elif text == Text.format('CL_CONFIRM_NO'):
            user.current_request = None
            user.save()
            cls.send(
                chat_id=kwargs.get('chat_id'),
                text=Text.format('CL_OPERATION_CANCEL'),
                reply_markup=cls._start_keyboard()
            )
        else:
            keyboard = ReplyKeyboard(keyboard=[
                [Text.format('CL_CONFIRM_YES'), Text.format('CL_CONFIRM_NO')]
            ])
            cls.send(
                chat_id=kwargs.get('chat_id'),
                text=Text.format('CL_CONFIRM_REPEAT'),
                reply_markup=keyboard.to_json()
            )

    @classmethod
    def _on_enter_geo(cls, **kwargs):
        request = kwargs.get('request')
        location = kwargs.get('location')
        text = kwargs.get('text')
        user = kwargs.get('user')

        if location is None and request.geo is None:
            cls.send(chat_id=kwargs.get('chat_id'), text=Text.format('CL_SEND_GEO'))
        else:
            if location is not None:
                location = [location.get('latitude'), location.get('longitude')]
                request.geo = location
                request.save()

            if options.enable_testing_question:
                keyboard = ReplyKeyboard(keyboard=[
                    [
                        Text.format('CL_YES_REAL_RESERVE'),
                        Text.format('CL_NO_TESTING')
                    ]
                ])

                if request.step == awa_client.STEP_ENTER_GEO:
                    request.step = awa_client.STEP_CONFIRM_NO_TESTING
                    request.save()

                    return cls.send(
                        chat_id=kwargs.get('chat_id'),
                        text=Text.format('CL_CONFIRM_TESTING'),
                        reply_markup=keyboard.to_json()
                    )
                elif request.step == awa_client.STEP_CONFIRM_NO_TESTING:
                    if text == Text.format('CL_YES_REAL_RESERVE'):
                        pass
                    elif text == Text.format('CL_NO_TESTING'):
                        request.step = awa_client.STEP_TEST_REQUEST
                        request.save()

                        user.current_request = None
                        user.save()

                        return cls.send(
                            chat_id=kwargs.get('chat_id'),
                            text=Text.format('CL_CANCEL_REQUEST'),
                            reply_markup=cls._start_keyboard()
                        )
                    else:
                        return cls.send(
                            chat_id=kwargs.get('chat_id'),
                            text=Text.format('CL_CONFIRM_TESTING'),
                            reply_markup=keyboard.to_json()
                        )

            request.step = awa_client.STEP_SEARCH_EXCHANGE
            request.save()

            min_distance = 0
            is_found = False

            logger.info('Location: {0}'.format(repr(location)))
            for max_distance in [Interval.get('max_radius') * 1000.0]:
                exchanges = Exchange.objects(active=True,
                                             geo__near=request.geo,
                                             geo__min_distance=min_distance,
                                             geo__max_distance=max_distance)

                if len(exchanges) > 0:
                    logger.info('Found {0} exchanges in {1} distance'.format(len(exchanges), max_distance))
                    is_found = True
                    for exchange in exchanges:
                        logger.info('Exchange location: {0}'.format(repr(exchange.geo)))

                        from bots.awa_exchange import AwaExchangeBot
                        course = request.course
                        text = Text.format(
                            'EX_EXCHANGE_REQUEST',
                            request.number,
                            request.type,
                            request.amount,
                            '%.2f' % course
                        )
                        AwaExchangeBot.send(chat_id=exchange.out_id, text=text)
                    break
                else:
                    logger.warning('Not found exchanges in {0} distance'.format(max_distance))

                min_distance = max_distance

            if not is_found:
                request.step = awa_client.STEP_SEARCH_FAIL
                request.save()

                user.current_request = None
                user.save()

            cls.send(
                chat_id=kwargs.get('chat_id'),
                text=Text.format('CL_RESERV' if is_found else 'CL_FAIL_RESERV'),
                reply_markup=cls._start_keyboard()
            )

    @classmethod
    def _on_rating(cls, **kwargs):
        q = Q(rating_request_send=True) & Q(step=awa_client.STEP_SEARCH_SUCCESS)

        text = kwargs.get('text')

        request = Request.objects(q).order_by('-update_date').first()
        if not request:
            return

        if repr(text) == repr(u'Не менял'):
            request.rating_value = None
        elif repr(text) == repr(emoji.emojize(':star:', True)):
            request.rating_value = 1
        elif repr(text) == repr(emoji.emojize(':star::star:', True)):
            request.rating_value = 2
        elif repr(text) == repr(emoji.emojize(':star::star::star:', True)):
            request.rating_value = 3
        elif repr(text) == repr(emoji.emojize(':star::star::star::star:', True)):
            request.rating_value = 4
        elif repr(text) == repr(emoji.emojize(':star::star::star::star::star:', True)):
            request.rating_value = 5

        request.user = request.user
        request.save()

        if request.rating_value is not None:
            if request.rating_value < 4:
                AwaClientBot.send(
                    chat_id=kwargs.get('chat_id'),
                    text=Text.format('CL_RATING_COMMENT_REQUEST')
                )
            else:
                AwaClientBot.send(
                    chat_id=kwargs.get('chat_id'),
                    text=Text.format('CL_RATING_COMMENT_GOOD'),
                    reply_markup=cls._start_keyboard()
                )
        else:
            AwaClientBot.send(
                chat_id=kwargs.get('chat_id'),
                text=Text.format('CL_RATING_COMMENT_GOOD_DAY'),
                reply_markup=cls._start_keyboard()
            )

    @classmethod
    def _try_get_comment(cls, **kwargs):
        q = Q(rating_request_send=True) & \
            Q(step=awa_client.STEP_SEARCH_SUCCESS) & \
            Q(rating_value__lt=4) & \
            Q(rating_comment='')
        request = Request.objects(q).order_by('-update_date').first()

        if not request:
            request = kwargs.get('request')
            if request and request.step == awa_client.STEP_SEARCH_SUCCESS:
                cls.send(
                    chat_id=kwargs.get('chat_id'),
                    text=Text.format('CL_ORDER_FORMED'),
                    reply_markup=cls._start_keyboard()
                )
            return

        text = kwargs.get('text')

        request.user = request.user
        request.rating_comment = text
        request.save()

        AwaClientBot.send(
            chat_id=kwargs.get('chat_id'),
            text=Text.format('CL_RATING_COMMENT_GOOD'),
            reply_markup=cls._start_keyboard()
        )

    @classmethod
    def _start_keyboard(cls):
        return ReplyKeyboard(keyboard=[[Text.format('CL_NEW_EXCHANGE')]], one_time_keyboard=False).to_json()
