odoo.define('custom_pos_extension.custom_pos_fields', function(require) {
    "use strict";

        var { Order } = require('point_of_sale.models');
        var Registries = require('point_of_sale.Registries');

        const CustomOrder = (Order) => class CustomOrderline extends Order {
            export_for_printing() {
                var result = super.export_for_printing(...arguments);
                let company = this.pos.company;
                result.fssai_no = company.fssai_no;
                return result;
            }
        }
        Registries.Model.extend(Order, CustomOrder);
});
