odoo.define('kitchen_order_print.DeleteOrderLinesAll', function(require) {
'use strict';
   const { Gui } = require('point_of_sale.Gui');
   const PosComponent = require('point_of_sale.PosComponent');
   const { identifyError } = require('point_of_sale.utils');
   const ProductScreen = require('point_of_sale.ProductScreen');
   const { useListener } = require("@web/core/utils/hooks");
   const Registries = require('point_of_sale.Registries');
   const PaymentScreen = require('point_of_sale.PaymentScreen');
   class OrderLineClearALL extends PosComponent {
       setup() {
           super.setup();
           useListener('click', this.onClick);
       }
      async onClick() {

                var order    = this.env.pos.get_order();
                var lines    = order.get_orderlines();
                var order_lines = [];
                var changes = [];
                if(order.tableId){
                    var tableId = this.env.pos.tables_by_id[order.tableId];
                    var tableName = tableId.name;
                    var floorName = tableId.floor.name
                }else{
                    var tableName = " ";
                    var floorName = "Ground";
                }

                var data = {
                'receipt_number': order.name,
                'table': tableName,
                'session':order.pos_session_id,
                'floor': floorName,
                'employee_name': order.cashier ? order.cashier.name : null,
                'employee_role': order.cashier.role ? order.cashier.role : null,
                'orderlines': [],
              };


                if (typeof order.kot_bill_saved_resume !== 'undefined'){
                    var saved_resume = order.kot_bill_saved_resume

                    order.orderlines.forEach(function(ol) {
                        var savedLine = saved_resume.find(function(saved) {
                            return saved[0] === ol.product.display_name;
                        });

                        if (savedLine) {
                            var savedQuantity = savedLine[1];
                            if (savedQuantity !== ol.quantity) {
                                var difference = ol.quantity - savedQuantity;
                                changes.push([ol.product.display_name, difference, ol.product.categ_id[1], ol.note || '', ol.product.categ_id[0]]);
                            }
                        } else {
                            changes.push([ol.product.display_name, ol.quantity, ol.product.categ_id[1], ol.note || '', ol.product.categ_id[0]]);
                        }
                    });
                }else{
                    order.orderlines.forEach(function(ol) {
                                changes.push([ol.product.display_name, ol.quantity, ol.product.categ_id[1], ol.note || '',ol.product.categ_id[0]]);
                            });
                }
                order.orderlines.forEach(function(ol) {
                                order_lines.push([ol.product.display_name, ol.quantity, ol.product.categ_id[1], ol.note || '',ol.product.categ_id[0]]);
                            });

                var count = 0
                const formattedLines = changes.map(line => {
                    count +=1
                    const product = line[0];
                    const quantity = line[1];
                    const note = line[3];
                    if(note){
                        var kot =`${count}.${product} ---- ${quantity}(${note})`
                        }
                    else{
                        var kot =`${count}.${product} ---- ${quantity}`
                        }
                    return kot;
                    });

                const { confirmed} = await this.showPopup("ConfirmPopup", {
                       title: this.env._t('KOT'),
                       body: formattedLines.join('\n'),
                   });
                if(confirmed){
                            console.log("changes",changes);
                            changes.forEach(function(each_line){
                                data.orderlines.push(each_line)
                            });
                            var result = this.rpc({
                                model: 'pos.printer',
                                method: 'current_kot_print',
                                args: [data],
                            });
                            order.kot_bill_saved_resume = order_lines
                   }

       }

   }

   OrderLineClearALL.template = 'OrderLineClearALL';
   ProductScreen.addControlButton({
       component: OrderLineClearALL,
       condition: function() {
           return this.env.pos;
       },
   });
   Registries.Component.add(OrderLineClearALL);
   return OrderLineClearALL;
});