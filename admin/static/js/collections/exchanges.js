"use strict";
define(['backbonekts', 'models/exchange'], function (BackboneKTS, Exchange) {
    return BackboneKTS.Collection.extend({
        model: Exchange,
        url: function () {
            return config.getMethodUrl('exchanges.get', {
                offset: this.offset,
                count: this.pageSize
            });
        }
    });
});