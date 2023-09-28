odoo.define('pos_discount_manager.ValidateManager', function(require) {
    'use strict';

  const Registries = require('point_of_sale.Registries');
  const PaymentScreen = require('point_of_sale.PaymentScreen');

     const ValidateManagers = (PaymentScreen) =>
        class extends PaymentScreen {
                /**
                *Override the validate button to approve discount limit
                */
            async _finalizeValidation() {
//            const { confirmed, payload } = await this.showPopup('NumberPopup', {
//                    title: this.env._t(employee_name + ', your discount is over the limit. \n Manager pin for Approval'),
//                });
//                const { confirmed, payload } = await this.showPopup('NumberPopup',{
//                title: this.env._t('Discount Percentage'),
//                startingValue: this.env.pos.config.discount_pc,
//                isInputSelected: true
//            });
//            if (confirmed) {
//                const val = Math.round(Math.max(0,Math.min(100,parseFloat(payload))));
//                await self.apply_discount(val);
//            }
             if ((this.currentOrder.is_paid_with_cash() || this.currentOrder.get_change()) && this.env.pos.config.iface_cashdrawer) {
                    this.env.pos.proxy.printer.open_cashbox();
             }

                this.currentOrder.initialize_validation_date();
                let syncedOrderBackendIds = [];
                try {
                    if (this.currentOrder.is_to_invoice()) {
                        syncedOrderBackendIds = await this.env.pos.push_and_invoice_order(
                            this.currentOrder
                        );
                    } else {
                        syncedOrderBackendIds = await this.env.pos.push_single_order(this.currentOrder);
                    }
                } catch (error) {
                    if (error instanceof Error) {
                        throw error;
                    } else {
                        await this._handlePushOrderError(error);
                    }
                }
                if (syncedOrderBackendIds.length && this.currentOrder.wait_for_push_order()) {
                    const result = await this._postPushOrderResolve(
                        this.currentOrder,
                        syncedOrderBackendIds
                    );
                    if (!result) {
                        await this.showPopup('ErrorPopup', {
                            title: 'Error: no internet connection.',
                            body: error,
                        });
                    }
                }

            var order = this.env.pos.get_order();
            var orderlines = this.currentOrder.get_orderlines()
            var employee_dis = this.env.pos.get_cashier()['limited_discount'];
            var employee_name = this.env.pos.get_cashier()['name']
            var manager_id = this.env.pos.employees.filter((obj) => obj.is_manager == true);
            if(manager_id.length == 0){
                            this.showPopup('ErrorPopup', {
                                title: this.env._t(" No Manager"),
                                body: this.env._t("Manager is not set, Please check."),

                            });
                            return false;
                     }
            var res = manager_id.filter((checkPin) => checkPin.pin != false)
            var manager_limit = res[0].limited_discount
            var flag = 1;
            var manager_flag = 1;
             orderlines.forEach((order) => {
               if(order.description){
                var discription = order.description;
                var dis_pct_str = discription.split(',');
                var discount_amt = Number(dis_pct_str[0].replace('%',""))

               }else{
               var discount_amt = 0;
               }
               if(discount_amt > employee_dis){
                    if(discount_amt > manager_limit){
                        manager_flag = 0;
                    }else{
                    flag = 0;
                    }
               }

             });
             if(manager_flag != 1){
                this.showPopup('ErrorPopup', {
                    title: this.env._t("Over the limit"),
                    body: this.env._t("Manager's Discount Is Over The Limit,Discount Can't Be Given"),

                });
                return false;
             }
             if (flag != 1) {
             const {confirmed,payload} = await this.showPopup('NumberPopup', {
                        title: this.env._t(employee_name + ', your discount is over the limit. \n Manager pin for Approval'),
                    });
                    if(confirmed){
                     var output = this.env.pos.employees.filter((obj) => obj.is_manager == true);
                     var res = output.filter((checkPin) => checkPin.pin != false)
//                     var manager_limit = res[0].limited_discount
                     var pin = res[0].pin

                     if (Sha1.hash(payload) == pin) {
                        this.showScreen(this.nextScreen);
                        }
                        else {
                            this.showPopup('ErrorPopup', {
                                title: this.env._t(" Manager Restricted your discount"),
                                body: this.env._t(employee_name + ", Your Manager pin is incorrect."),

                            });
                            return false;
                        }
                    }
                    else {
                        return false;
                    }
                    }
                    this.currentOrder.finalized = true;
                    this.showScreen(this.nextScreen);
                    // If we succeeded in syncing the current order, and
                   // there are still other orders that are left unsynced,
                  // we ask the user if he is willing to wait and sync them.
                  if (syncedOrderBackendIds.length && this.env.pos.db.get_orders().length) {
                    const {
                        confirmed
                    } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Remaining unsynced orders'),
                        body: this.env._t(
                            'There are unsynced orders. Do you want to sync these orders?'
                        ),
                    });
                     if (confirmed) {
                     // Not yet sure if this should be awaited or not.
                        this.env.pos.push_orders();
                     }
                  }
             }
        }
     Registries.Component.extend(PaymentScreen, ValidateManagers);
     return ValidateManagers;
});