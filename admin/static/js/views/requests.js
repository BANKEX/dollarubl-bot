"use strict";
define([
    'backbonekts', 'underscore', 'jquery',
    'text!templates/requests/index.html',
    'collections/requests', 'autocomplete', 'x-editable'
], function (BackboneKTS, _, $, indexTemplate, RequestsCollection) {
    return BackboneKTS.View.extend({
        indexTemplate: _.template(indexTemplate),
        events: {
            'click .pagination__item.pagination__item_requests': 'pagination',
            'click .js-request-fail': 'failRequest',
            'submit .js-exchange-respond': 'exchangeRespond',
            'click .js-exchange-confirm': 'updateExchangeConfirm',
            'show.bs.modal #respondModal': function (e) {
                var requestId = $(e.relatedTarget).attr('data-id');
                var form = this.$('.js-exchange-respond');
                form.find('input').val('');
                form.find('[name="request_id"]').val(requestId);
                form.find('.js-submit').prop('disabled', true);
            }
        },
        actionIndex: function (offset) {
            var self = this;
            if (offset === null) {
                offset = 0;
            }
            var currencyCollection = new RequestsCollection();
            currencyCollection.fetch({
                data: {
                    offset: offset
                },
                success: function () {
                    self.$el.html(self.indexTemplate({
                        offset: offset,
                        count: currencyCollection.totalCount,
                        items: currencyCollection
                    }));

                    var respondForm = self.$('.js-exchange-respond');
                    self.$('.js-exchanges-suggest').autocomplete({
                        serviceUrl: '/api/exchanges.suggest',
                        onSelect: function (suggestion) {
                            respondForm.find('.js-submit').prop('disabled', false);
                            respondForm.find('[name="exchange_id"]').val(suggestion.data);
                        }
                    });

                    self.$('.js-set-date').each(function () {
                        var self = $(this);
                        self.editable({
                            type: 'date',

                            title: 'Введите дату',
                            placement: 'left',
                            format: 'dd.mm.yyyy',

                            url: config.getMethodUrl('requests.updateDateCommissionWithdrawal'),
                            pk: self.attr('data-id'),
                            params: function (params) {
                                params.id = self.attr('data-id');
                                return params;
                            }
                        });
                    });
                }
            });
        },
        pagination: function (e) {
            var self = this,
                offset = $(e.currentTarget).attr('data-offset');
            e.preventDefault();
            self.actionIndex(offset);
        },
        failRequest: function (e) {
            e.preventDefault();
            var id = $(e.currentTarget).attr('data-id');
            var self = this;
            if (confirm('Вы уверены? Клиенту будет отправлено сообщение о неудаче')) {
                config.apiCall('requests.setFail', {id: id}, {
                    method: 'post',
                    onSuccess: function (data) {
                        window.location = window.location;
                    },
                    onError: function () {
                        self._showError('Ошибка');
                    }
                });
            }
        },
        exchangeRespond: function (e) {
            e.preventDefault();
            var self = this;
            config.apiCall('requests.respond', this.serializeForm(e.currentTarget), {
                method: 'post',
                onSuccess: function () {
                    window.location = window.location;
                },
                onError: function () {
                    self._showError('Ошибка');
                }
            });
        },
        updateExchangeConfirm: function (e) {
            e.preventDefault();
            var self = $(e.currentTarget);
            config.apiCall('requests.updateExchangeConfirm',
                {
                    id: self.attr('data-id'),
                    value: self.prop('checked')
                },
                {
                    method: 'post',
                    onSuccess: function () {
                        self.prop('checked', !self.prop('checked'));
                    }
                }
            );
        }
    });
});