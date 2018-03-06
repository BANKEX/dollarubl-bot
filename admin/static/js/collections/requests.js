"use strict";
define(['backbonekts', 'models/request'], function (BackboneKTS, Request) {
    return BackboneKTS.Collection.extend({
        model: Request,
        url: function () {
            return config.getMethodUrl('requests.get', {
                offset: this.offset,
                count: this.pageSize
            });
        }
    });
});