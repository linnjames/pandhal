from odoo import fields, models, _
from odoo.exceptions import ValidationError


class TdsManagement(models.Model):
    _name = "tds.management"
    _description = "Tds Management"

    name = fields.Char(string='Name')
    tds_type = fields.Selection([('with_pan', 'With PAN'), ('without_pan', 'Without PAN')], string="TDS Type")
    tds_percentage = fields.Float(string="TDS %")
    tds_account = fields.Many2one('account.account', string="TDS Account")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    def tds_multicompany(self):
        if self.name:
            company = self.env.company
            companies = self.env['res.company'].search([('id', '!=', company.id)])
            for comp in companies:
                tds = self.env['tds.management'].sudo().search([('name', '=', self.name), ('company_id', '=', comp.id)])
                if tds:
                    pass
                else:
                    account = self.env['account.account'].sudo().search([('name', 'ilike', self.tds_account.name), ('company_id', '=', comp.id)])
                    if account:
                        self.env['tds.management'].sudo().create({
                            'name': self.name,
                            'tds_type': self.tds_type,
                            'tds_percentage': self.tds_percentage,
                            'tds_account': account.id,
                            'company_id': comp.id,
                        })
                    else:
                        raise ValidationError(_("This account does not exists in %s ") % (comp.name))