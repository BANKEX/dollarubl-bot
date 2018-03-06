"use strict";
define([
    'backbonekts', 'underscore', 'jquery', 'helpers/external',
    'text!templates/exchanges/index.html',
    'text!templates/exchanges/form.html',
    'collections/exchanges', 'models/exchange'
], function (BackboneKTS, _, $, External, indexTemplate, formTemplate, ExchangeCollection, Exchange) {
    return BackboneKTS.View.extend({
        indexTemplate: _.template(indexTemplate),
        formTemplate: _.template(formTemplate),
        events: {
            'click .pagination__item.pagination__item_exchanges': 'pagination',
            'submit .js-exchange-form': 'formSubmit',
            'click .js-exchange-remove': 'removeExchange'
        },
        actionIndex: function (offset) {
            var self = this;
            if (offset === null) {
                offset = 0;
            }
            var exchangeCollection = new ExchangeCollection();
            exchangeCollection.fetch({
                data: {
                    offset: offset
                },
                success: function () {
                    self.$el.html(self.indexTemplate({
                        offset: offset,
                        count: exchangeCollection.totalCount,
                        items: exchangeCollection
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

                External('//api-maps.yandex.ru/2.1/?lang=ru_RU').load(function () {
                    ymaps.ready(function () {
                        var map = new ymaps.Map('map', {
                            center: [item.get('lat'), item.get('long')],
                            zoom: 14,
                            controls: []
                        });
                        var placeMark = new ymaps.Placemark([item.get('lat'), item.get('long')]);

                        map.controls.add(new ymaps.control.SearchControl({
                            options: {
                                noPlacemark: true,
                                noSuggestPanel: true
                            }
                        }));
                        map.geoObjects.add(placeMark);
                        map.controls.add('zoomControl', {left: 5, top: 5});
                        map.events.add('click', function (e) {
                            var coords = e.get('coords');
                            placeMark.geometry.setCoordinates(coords);
                            self.$el.find('[name="lat"]').val(coords[0]);
                            self.$el.find('[name="long"]').val(coords[1]);
                        });
                    });
                });
            }

            if (id !== undefined) {
                var currency = new Exchange({id: id});
                currency.fetch({
                    success: function () {
                        render(currency);
                    }
                });
            } else {
                render(new Exchange());
            }
        },
        formSubmit: function (evt) {
            var self = this,
                data = self.serializeForm(evt.currentTarget);
            evt.preventDefault();

            var currency = new Exchange();
            currency.save(data, {
                url: config.getMethodUrl('exchanges.save'),
                success: function () {
                    if (data.id) {
                        self._showSuccess('Успех', 'Обменник успешно сохранен');
                    }
                    self.redirect('exchanges');
                },
                error: function (object, response) {
                    self._showError(response);
                }
            });
        },
        pagination: function (e) {
            var self = this,
                offset = $(e.currentTarget).attr('data-offset');
            e.preventDefault();
            self.actionIndex(offset);
        },
        removeExchange: function (e) {
            e.preventDefault();
            if (confirm('Вы уверены?')) {
                config.apiCall('exchanges.delete', {id: $(e.currentTarget).attr('data-id')}, {
                    method: 'post',
                    onSuccess: function () {
                        $(e.currentTarget).parents('.js-exchange-row').remove();
                    }
                });
            }
        }
    });
});