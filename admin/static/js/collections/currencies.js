"use strict";
define(['backbonekts', 'models/currency'], function (BackboneKTS, Currency) {
    return BackboneKTS.Collection.extend({
        model: Currency,
        url: function () {
            return config.getMethodUrl('currency.get', {
                offset: this.offset,
                count: this.pageSize
            });
        }
    });
});