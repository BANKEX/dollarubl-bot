"use strict";
define(['backbonekts', 'models/interval'], function (BackboneKTS, Interval) {
    return BackboneKTS.Collection.extend({
        model: Interval,
        url: function () {
            return config.getMethodUrl('intervals.get', {
                offset: this.offset,
                count: 100500
            });
        }
    });
});