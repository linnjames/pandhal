
from odoo import fields, models


class HrEmployee(models.Model):
    """Add field into hr employee"""
    _inherit = 'hr.employee'

    limited_discount = fields.Integer(string="Discount Limit",
                                      help="Provide discount limit to each "
                                           "employee")
    is_manager = fields.Boolean(string="Manager")


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    limited_discount = fields.Integer('hr.employee', related="employee_id.limited_discount", store=True)
    is_manager = fields.Boolean('hr.employee', related="employee_id.is_manager", store=True)