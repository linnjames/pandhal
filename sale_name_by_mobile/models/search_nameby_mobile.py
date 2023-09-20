from odoo import models, fields, api, exceptions


class SearchNameByMobile(models.Model):
    _inherit = "res.partner"

    phone = fields.Char(required=True)

    def name_get(self):
        result = []
        for rec in self:
            if rec.phone:
                result.append((rec.id, '%s - %s' % (rec.name, rec.phone)))
            if not rec.phone:
                result.append((rec.id, '%s' % rec.name,))
        return result

    @api.constrains('phone')
    def _check_unique_phone(self):
        for partner in self:
            if partner.phone:
                duplicate_partners = self.search([('phone', '=', partner.phone), ('id', '!=', partner.id)])
                if duplicate_partners:
                    raise exceptions.ValidationError("Phone number must be unique!")
