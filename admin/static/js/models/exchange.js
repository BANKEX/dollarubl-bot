"use strict";
define(['backbonekts', 'moment'], function (BackboneKTS, moment) {
    return BackboneKTS.Model.extend({
        url: function () {
            return config.getMethodUrl('exchanges.get');
        },
        get: function (key) {
            var value = BackboneKTS.Model.prototype.get.call(this, key);
            if (key === 'update_date' && value) {
                value = moment(value * 1000).format('DD.MM.YYYY в HH:mm');
            } else if (key === 'geo' && value) {
                var coordinates = value.coordinates;
                value = 'http://static-maps.yandex.ru/1.x/?l=map&pt=' + coordinates[1] + ',' + coordinates[0] + ',pm2rdm&z=15&size=250,250';
            } else if (key === 'lat' || key === 'long') {
                value = BackboneKTS.Model.prototype.get.call(this, 'geo');
                if (value && value.coordinates) {
                    value = value.coordinates;
                } else {
                    value = [55.751574, 37.573856];
                }
                value = (key === 'lat') ? value[0] : value[1];
            }
            return value;
        }
    });
});