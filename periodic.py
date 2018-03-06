# coding=utf-8
import datetime

import emoji
from mongoengine import Q
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornkts.utils import json_loads

from bots.awa_client import AwaClientBot
from content import awa_client
from content.awa_client import STEP_NO_RESPONSE
from models.content import Text, Interval
from roboman.keyboard import ReplyKeyboard
from models.awa import Currency, Request
import logging
from pytz import timezone

logger = logging.getLogger('periodic')


def currency_updater(call=False):
    client = AsyncHTTPClient()

    @gen.coroutine
    def wrapper():
        logger.info('Update currency')

        req = HTTPRequest('http://example.com/api/exchange.current')
        res = yield client.fetch(req)
        data = json_loads(res.body)

        for currency, item in data.get('data', {}).items():
            currency = currency.upper()
            value = item.get('purchasing_rate')
            try:
                logger.info('try find {0}, {1}'.format(currency, Currency.DIRECT_SALE))
                object = Currency.objects.get(code=currency, direct=Currency.DIRECT_SALE)
                logger.info('Success find')
                if object.use_api:
                    logger.info('Update')
                    object.value = value
                    object.save()
                else:
                    logger.info('use_api=False, skip')
            except Currency.DoesNotExist:
                logger.info('Create {0}, {1}'.format(currency, Currency.DIRECT_SALE))
                Currency(code=currency, direct=Currency.DIRECT_SALE, value=value).save()

            value = item.get('selling_rate')
            try:
                logger.info('try find {0}, {1}'.format(currency, Currency.DIRECT_BUY))
                object = Currency.objects.get(code=currency, direct=Currency.DIRECT_BUY)
                logger.info('Success find')
                if object.use_api:
                    logger.info('Update')
                    object.value = value
                    object.save()
                else:
                    logger.info('use_api=False, skip')
            except Currency.DoesNotExist:
                logger.info('Create {0}, {1}'.format(currency, Currency.DIRECT_BUY))
                Currency(code=currency, direct=Currency.DIRECT_SALE, value=value).save()

    if call:
        wrapper()
    return wrapper


def send_fails(requests=None):
    if requests is None:
        date = datetime.datetime.now(tz=timezone('UTC'))
        date -= datetime.timedelta(seconds=Interval.seconds('fail_timeout'))

        q = (
                Q(exchange__exists=False) |
                Q(exchange=None)
            ) & \
            Q(fail_sended=False) & \
            Q(update_date__lt=date) & \
            Q(step=awa_client.STEP_SEARCH_EXCHANGE)

        requests = Request.objects(q)
        if len(requests) > 0:
            logger.info('Found fails')
        else:
            logger.debug('No fails')
            return

    for request in requests:
        request.fail_sended = True
        request.step = STEP_NO_RESPONSE
        request.user = request.user
        request.save()

        logger.info('Send fail: {0}'.format(request.user.out_id))
        AwaClientBot.send(chat_id=request.user.out_id, text=Text.format('CL_FAIL_RESERV_TIMEOUT'))


def rating_request_send():
    date = datetime.datetime.now(tz=timezone('UTC'))
    date -= datetime.timedelta(seconds=Interval.seconds('rating_request_timeout'))

    q = Q(rating_request_send=False) & \
        Q(update_date__lte=date) & \
        Q(step=awa_client.STEP_SEARCH_SUCCESS)

    requests = Request.objects(q).order_by('-update_date')

    users = set()
    for request in requests:
        if request.user.get_id() not in users:
            request.rating_request_send = True
            request.user = request.user
            request.save()

            keyboard = ReplyKeyboard(keyboard=[
                [u'Не менял', emoji.emojize(':star:', True)],
                [emoji.emojize(':star::star:', True), emoji.emojize(':star::star::star:', True)],
                [emoji.emojize(':star::star::star::star:', True), emoji.emojize(':star::star::star::star::star:', True)]
            ])

            AwaClientBot.send(chat_id=request.user.out_id, text=Text.format('CL_REQUEST_RATING'),
                              reply_markup=keyboard.to_json())
            users.add(request.user.get_id())
