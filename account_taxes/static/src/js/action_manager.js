odoo.define('account_taxes.action_manager', function (require) {
    "use strict";

    var ActionManager = require('web.ActionManager');
    var core = require('web.core');
    var session = require('web.session');

    var _super_execute_report_action = ActionManager.prototype._executeReportAction;

    ActionManager.include({
        /**
         * Executes actions of type 'ir.actions.report'.
         *
         * @private
         * @param {Object} action the description of the action to execute
         * @param {Object} options @see doAction for details
         * @returns {Promise} resolved when the action has been executed
         */
        _executexlsxReportDownloadAction: function (action) {
            core.bus.trigger('rpc_activity_start');
            var def = $.Deferred();
            session.get_file({
                url: '/xlsx_reports',
                data: action.data,
                success: def.resolve.bind(def),
                complete: core.bus.trigger.bind(core.bus, 'rpc_activity_stop'),
            });
            return def;
        },

        /**
         * Overrides to handle the 'ir.actions.report' actions.
         *
         * @override
         * @private
         */
        _executeReportAction: function (action, options) {
            if (action.report_type === 'xlsx') {
                return this._executexlsxReportDownloadAction(action, options);
            }
            return _super_execute_report_action.apply(this, arguments);
        },
    });
});
