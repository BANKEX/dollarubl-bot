"use strict";
define([
    'backbonekts', 'underscore', 'jquery',
    'text!templates/intervals/index.html',
    'text!templates/intervals/form.html',
    'collections/intervals', 'models/interval'
], function (BackboneKTS, _, $, indexTemplate, formTemplate, IntervalsCollection, Interval) {
    return BackboneKTS.View.extend({
        indexTemplate: _.template(indexTemplate),
        formTemplate: _.template(formTemplate),
        events: {
            'submit .js-interval-form': 'formSubmit',
            'click .js-remove': 'remove'
        },
        actionIndex: function (offset) {
            var self = this;
            if (offset === null) {
                offset = 0;
            }
            var intervalsCollection = new IntervalsCollection();
            intervalsCollection.fetch({
                data: {
                    offset: offset,
                    limit: 100500
                },
                success: function () {
                    self.$el.html(self.indexTemplate({
                        offset: offset,
                        count: intervalsCollection.totalCount,
                        items: intervalsCollection
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

                config.apiCall('intervals.keys', {}, {
                    onSuccess: function (data) {
                        var keys = $('.js-keys');
                        for (var i in data.data) {
                            var item = data.data[i];
                            var option = $('<option/>', {
                                html: item,
                                value: item
                            });
                            if (keys.attr('data-value') == item) {
                                option.prop('selected', true)
                            }
                            keys.append(option);
                        }
                    }
                });
            }

            if (id !== undefined) {
                var currency = new Interval({id: id});
                currency.fetch({
                    success: function () {
                        render(currency);
                    }
                });
            } else {
                render(new Interval());
            }
        },
        formSubmit: function (evt) {
            var self = this,
                data = self.serializeForm(evt.currentTarget);

            evt.preventDefault();
            var currency = new Interval();
            currency.save(data, {
                url: config.getMethodUrl('intervals.save'),
                success: function () {
                    if (data.id) {
                        self._showSuccess('Успех', 'Интервал успешно сохранен');
                    }
                    self.redirect('intervals');
                },
                error: function (object, response) {
                    if (response.responseJSON.status === 'internal_error') {
                        self._showError(undefined, 'Запись уже существует');
                    } else if (response.responseJSON.status === 'invalid_param') {
                        self._showError(undefined, 'Неверное значение');
                    } else {
                        self._showError(undefined, response.responseJSON.message);
                    }
                }
            });
        },
        remove: function (e) {
            e.preventDefault();
            var id = $(e.currentTarget).attr('data-id');
            var self = this;
            if (confirm('Вы уверены?')) {
                $.ajax({
                    method: 'post',
                    url: config.getMethodUrl('intervals.delete', {id: id}),
                    success: function () {
                        self._showSuccess('Успех', 'Текст удален');
                        $('.js-row[data-id="' + id + '"]').remove();
                    }
                });
            }
        }
    });
});