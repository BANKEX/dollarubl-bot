"use strict";
define(['backbonekts', 'models/content_manager'], function (BackboneKTS, ContentManager) {
    return BackboneKTS.Collection.extend({
        model: ContentManager,
        url: function () {
            return config.getMethodUrl('content_manager.get', {
                offset: this.offset,
                count: this.pageSize
            });
        }
    });
});