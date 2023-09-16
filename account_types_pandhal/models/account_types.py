from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountAccount(models.Model):
    _inherit = 'account.account'

    account_type = fields.Selection(
        selection_add=[('equity_capital', 'Partner Capital Account'),
                       ('equity_current', 'Partner Current Account'),
                       ('equity_share_capital', 'Equity Share Capital'),
                       ('equity_retained_earnings', 'Retained Earnings - prior years'),
                       ('equity_year_profit_loss', 'Year Profit/Loss'),
                       ('liability_secured_loan', 'Secured Loan'),
                       ('asset_inventories', 'Inventories'),
                       ('expense_purchases', 'Purchases'),
                       ('expense_inventory_adjustment_account', 'INVENTORY ADJUSTMENT ACCOUNT'),
                       ('expense_sales_and_distribution_expenses', 'SALES AND DISTRIBUTION EXPENSES'),
                       ('expense_house_keeping', 'House Keeping Charge'),
                       ('expense_insurance', 'Insurance'),
                       ('expense_legal_professional', 'Legal & Professional Charges'),
                       ('expense_marketing_expenses', 'Marketing Expenses'),
                       ('expense_miscellaneous_expenses', 'Miscellaneous Expenses'),
                       ('expense_office_expenses', 'Office Expenses'),
                       ('expense_postage_telegram', 'Postage, Telegram & Telephone'),
                       ('expense_Power_Fuel', 'Power & Fuel'),
                       ('expense_repairs_maintenance', 'Repairs & Maintenance'),
                       ('rent_rates_taxes', 'Rent,Rates & Taxes'),
                       ('printing_stationary', 'Printing & Stationary'),
                       ('expense_salaries_allowances', 'Salaries & Allowances'),
                       ('expense_travelling_conveyance', 'Travelling & Conveyance'),
                       ('expense_water_charges', 'Water Charges'),
                       ('expense_administrative_expenses', 'General & Administrative expenses'),
                       ('expense_interest_bank_charges', 'Interest and Bank Charges'),
                       ('expense_forgien_exchange', 'FOREIGN EXCHANGE FLUCTUATION'),
                       ("off_balance", "Others"),
                       ],
        string='Account Type',
        ondelete={'equity_capital': 'cascade', 'equity_current': 'cascade','equity_retained_earnings': 'cascade','equity_year_profit_loss':'cascade','liability_secured_loan':'cascade','asset_inventories':'cascade','off_balance':'cascade','expense_purchases':'cascade','expense_inventory_adjustment_account':'cascade','expense_sales_and_distribution_expenses':'cascade','expense_house_keeping':'cascade','expense_insurance':'cascade',
                  'expense_legal_professional':'cascade','expense_marketing_expenses':'cascade','expense_miscellaneous_expenses':'cascade','expense_office_expenses':'cascade', 'expense_postage_telegram':'cascade','expense_Power_Fuel':'cascade','expense_repairs_maintenance':'cascade','expense_salaries_allowances':'cascade','expense_travelling_conveyance':'cascade','expense_water_charges':'cascade','expense_administrative_expenses':'cascade',
                  'expense_interest_bank_charges':'cascade','expense_forgien_exchange':'cascade','rent_rates_taxes':'cascade','printing_stationary':'cascade','equity_share_capital': 'cascade',}
    )