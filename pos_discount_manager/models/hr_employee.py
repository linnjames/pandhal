
from odoo import fields, models


class HrEmployee(models.Model):
    """Add field into hr employee"""
    _inherit = 'hr.employee'

    limited_discount = fields.Integer(string="Discount Limit",
                                      help="Provide discount limit to each "
                                           "employee")


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    limited_discount = fields.Integer('hr.employee', related="employee_id.limited_discount", store=True)