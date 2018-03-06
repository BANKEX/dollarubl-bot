# coding=utf-8
from models.awa import Request

GBR = '£'
CHF = '₣'

CURRENCY_EXCHANGE = {
    Request.TYPE_BUY_USD: 'Купить $',
    Request.TYPE_SAIL_USD: 'Продать $',
    Request.TYPE_BUY_EUR: 'Купить €',
    Request.TYPE_SAIL_EUR: 'Продать €',
    Request.TYPE_BUY_GBR: 'Купить £',
    Request.TYPE_SAIL_GBR: 'Продать £',
    Request.TYPE_BUY_CHF: 'Купить ₣',
    Request.TYPE_SAIL_CHF: 'Продать ₣',
}

CURRENCY_EXCHANGE_QUESTION = {
    Request.TYPE_BUY_USD: 'Сколько $ вы хотите купить?',
    Request.TYPE_SAIL_USD: 'Сколько $ вы хотите продать?',
    Request.TYPE_BUY_EUR: 'Сколько € вы хотите купить?',
    Request.TYPE_SAIL_EUR: 'Сколько € вы хотите продать?',
    Request.TYPE_BUY_GBR: 'Сколько £ вы хотите купить?',
    Request.TYPE_SAIL_GBR: 'Сколько £ вы хотите продать?',
    Request.TYPE_BUY_CHF: 'Сколько ₣ вы хотите купить?',
    Request.TYPE_SAIL_CHF: 'Сколько ₣ вы хотите продать?',
}

STEP_ZERO = 0
STEP_INPUT_OPERATION = 1
STEP_INPUT_AMOUNT = 2
STEP_CONFIRM = 3
STEP_ENTER_GEO = 4
STEP_CONFIRM_NO_TESTING = 8
STEP_SEARCH_EXCHANGE = 5
STEP_SEARCH_SUCCESS = 6
STEP_SUCCESS_RESPONSE = 7

STEP_NO_RESPONSE = 100
STEP_SEARCH_FAIL = 101
STEP_TEST_REQUEST = 102
