"use strict";
define(['backbonekts', 'moment'], function (BackboneKTS, moment) {
    return BackboneKTS.Model.extend({
        url: function () {
            return config.getMethodUrl('request.get');
        },
        isPlay: function () {
            var step = this.get('step');
            return step == 5;
        },
        isDeleted: function () {
            var step = this.get('step');
            return step != 6 && step != 100;
        },
        get: function (key) {
            var value = BackboneKTS.Model.prototype.get.call(this, key);
            if (key == 'step_title') {
                value = BackboneKTS.Model.prototype.get.call(this, 'step');
                switch (value) {
                    case 0:
                        return 'Начало';
                    case 1:
                        return 'Вводит операцию';
                    case 2:
                        return 'Вводит кол-во';
                    case 3:
                        return 'Подтвержадет кол-во';
                    case 4:
                        return 'Вводит гео';
                    case 5:
                        return 'Ожидание ответа обменников';
                    case 6:
                        return 'Обменник ответил';
                    case 100:
                        return 'Отправлено сообщение о неудаче';
                    case 101:
                        return 'Поиск не дал результатов';
                    case 102:
                        return 'Тестовый запрос, клиент отказался'
                }
            } else if (key === 'creation_date') {
                value = moment(value * 1000).format('DD.MM.YYYY в HH:mm');
            }
            else if (key === 'update_date') {
                value = moment(value * 1000).format('DD.MM.YYYY в HH:mm');
            } else if (key == 'distance') {
                value = Math.round(value * 1000) / 1000;
                value = !isNaN(value) ? value : '';
            } else if (key === 'user') {
                value = value || {};
            }
            return value;
        },
        getDateCommissionWithdrawal: function () {
            var value = this.get('date_commission_withdrawal');
            if (value) {
                return moment(value * 1000).format('DD.MM.YYYY');
            } else {
                return 'Установить дату';
            }
        }
    });
});