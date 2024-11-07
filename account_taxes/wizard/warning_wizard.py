from odoo import models


class WarningWizard(models.TransientModel):
    _name = 'warning.wizard'
    _description = 'Warning Wizard'


class WarningsWizard(models.TransientModel):
    _name = 'warnings.wizard'
    _description = 'Warnings Wizard'

