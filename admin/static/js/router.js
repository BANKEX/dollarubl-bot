"use strict";
define([
    'config', 'backbonekts', 'backbone', 'jquery', 'underscore',
    'models/admin',
    'views/login',
    'views/main',
    'views/toolbar',
    'views/admins',
    'views/currency',
    'views/requests',
    'views/exchanges',
    'views/texts',
    'views/intervals',
    'views/users'
], function (Config, BackboneKTS, Backbone, $, _, Admin,
             LoginView, MainView, ToolbarView, AdminsView,
             CurrencyView, RequestsView, ExchangesView, TextsView,
             IntervalsView, UsersView) {
    return BackboneKTS.Router.extend({
        routes: {
            "requests": "requestsPage",
            "users": "usersPage",

            "currencies/(:action)/(:id)": "currencyPage",
            "currencies/(:action)": "currencyPage",
            "currencies": "currencyPage",

            "exchanges/(:action)/(:id)": "exchangesPage",
            "exchanges/(:action)": "exchangesPage",
            "exchanges": "exchangesPage",

            "texts": "textsPage",
            "texts/(:action)/(:id)": "textsPage",
            "texts/(:action)": "textsPage",

            "intervals": "intervalsPage",
            "intervals/(:action)/(:id)": "intervalsPage",
            "intervals/(:action)": "intervalsPage",

            "admins/(:action)/(:id)": "adminsPage",
            "admins/(:action)": "adminsPage",
            "admins": "adminsPage",

            "login": "loginPage",
            "": "mainPage",
            '*default': 'mainPage'
        },
        views: {
            'login': LoginView,
            'main': MainView,
            'toolbar': ToolbarView,
            'admins': AdminsView,
            'currency': CurrencyView,
            'requests': RequestsView,
            'exchanges': ExchangesView,
            'texts': TextsView,
            'intervals': IntervalsView,
            'users': UsersView
        },
        initialize: function () {
            window.config = Config;
            config.user = false;
        },
        start: function () {
            var self = this;
            $(document).delegate("a", "click", function (evt) {
                var event = evt.originalEvent;
                if (event.metaKey || event.ctrlKey) {
                    return true;
                }

                var href = $(this).attr("href");
                if ($(evt.currentTarget).prop('target') === '_blank') {
                    return true;
                }

                if (href === undefined) {
                    href = '';
                }

                if (href === '/logout') {
                    $.ajax({
                        method: 'post',
                        url: config.getMethodUrl('logout'),
                        complete: function () {
                            window.location.pathname = '/login';
                        }
                    });
                    return false;
                }
                var protocol = document.location.protocol + "//";
                if (href.slice(0, protocol.length) !== protocol && href.substring(0, 1) !== '#') {
                    evt.preventDefault();
                    Backbone.history.navigate(href, true);
                }
            });

            var initHistory = function () {
                Backbone.history.start({pushState: true, root: '/'});
                Backbone.history.on("all", function () {
                    if (config.user !== false && self._getViewByName('toolbar').rendered === false) {
                        self._getViewByName('toolbar').render();
                    }
                });
            };

            var admin = new Admin();
            admin.fetch({
                url: config.getMethodUrl('admin.info'),
                success: function () {
                    config.user = admin;
                    initHistory();
                    if (Backbone.history.fragment === 'login') {
                        self.redirect('');
                    }
                    self._getViewByName('toolbar').render();
                },
                error: function () {
                    initHistory();
                    self.redirect('login');
                }
            });
        },
        mainPage: function () {
            if (config.user === false) {
                return false;
            }
            this.redirect('requests');
        },
        loginPage: function (action) {
            this._getViewByName('login').render(action);
        },
        adminsPage: function (action, id) {
            if (config.user === false) {
                return false;
            }
            this._getViewByName('admins').render(action, id);
        },
        currencyPage: function (action, id) {
            if (config.user === false) {
                return false;
            }
            this._getViewByName('currency').render(action, id);
        },
        requestsPage: function (action, id) {
            if (config.user === false) {
                return false;
            }
            this._getViewByName('requests').render(action, id);
        },
        usersPage: function (action, id) {
            if (config.user === false) {
                return false;
            }
            this._getViewByName('users').render(action, id);
        },
        exchangesPage: function (action, id) {
            if (config.user === false) {
                return false;
            }
            this._getViewByName('exchanges').render(action, id);
        },
        textsPage: function (action, id) {
            if (config.user === false) {
                return false;
            }
            this._getViewByName('texts').render(action, id);
        },
        intervalsPage: function (action, id) {
            if (config.user === false) {
                return false;
            }
            this._getViewByName('intervals').render(action, id);
        }
    });
});