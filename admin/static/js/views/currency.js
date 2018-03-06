"use strict";
define([
    'backbonekts', 'underscore', 'jquery',
    'text!templates/currency/index.html',
    'text!templates/currency/form.html',
    'collections/currencies', 'models/currency'
], function (BackboneKTS, _, $, indexTemplate, formTemplate, CurrenciesCollection, Currency) {
    return BackboneKTS.View.extend({
        indexTemplate: _.template(indexTemplate),
        formTemplate: _.template(formTemplate),
        events: {
            'click .pagination__item.pagination__item_currencies': 'pagination',
            'submit .js-currency-form': 'formSubmit',
            'click .js-currency-remove': 'removeCurrency'
        },
        actionIndex: function (offset) {
            var self = this;
            if (offset === null) {
                offset = 0;
            }
            var currencyCollection = new CurrenciesCollection();
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
                }
            });
        },
        actionAdd: function () {
            this._actionPut();
        },
        actionEdit: function (id) {
            this._actionPut(id);
        },
        _actionPut: function (id) {
            var self = this;

            function render(item) {
                self.$el.html(self.formTemplate({
                    item: item,
                    self: self
                }));
            }

            if (id !== undefined) {
                var currency = new Currency({id: id});
                currency.fetch({
                    success: function () {
                        render(currency);
                    }
                });
            } else {
                render(new Currency());
            }
        },
        formSubmit: function (evt) {
            var self = this,
                data = self.serializeForm(evt.currentTarget);
            evt.preventDefault();

            var currency = new Currency();
            currency.save(data, {
                url: config.getMethodUrl('currency.save'),
                success: function () {
                    if (data.id) {
                        self._showSuccess('Успех', 'Валюта успешно сохранена');
                    }
                    self.redirect('currencies');
                },
                error: function (object, response) {
                    self._showError(response);
                }
            });
        },
        removeCurrency: function (e) {
            e.preventDefault();
            var id = $(e.currentTarget).attr('data-id');
            var self = this;
            if (confirm('Вы уверены?')) {
                $.ajax({
                    method: 'post',
                    url: config.getMethodUrl('currency.delete', {id: id}),
                    success: function () {
                        self._showSuccess('Успех', 'Курс удален');
                        $('.js-currency-row[data-id="' + id + '"]').remove();
                    }
                });
            }
        },
        pagination: function (e) {
            var self = this,
                offset = $(e.currentTarget).attr('data-offset');
            e.preventDefault();
            self.actionIndex(offset);
        }
    });
});