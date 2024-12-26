# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SdHrDocumentsAttachments(models.Model):
    _name = 'sd_hr_documents.attachments'
    _description = 'document attachments'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _order = 'employee_id,issue_date'

    state = fields.Selection([('valid', 'Valid'), ('expiring', 'Expiring'), ('expired', 'Expired')],
                             default='valid', required=True, store=True, copy=False, tracking=True )
    name = fields.Char(required=True, tracking=True, copy=False)

    employee_id = fields.Many2one('hr.employee', default=lambda self: self.env.context.get('employee_id', False),
                                  string="Employee", index=True,
                                  required=True)
    document_type = fields.Many2one('sd_hr_documents.document_type', required=True, tracking=True,)
    issue_date = fields.Date()
    expire_date = fields.Date()
    expiration = fields.Integer(compute='_expiration_calculation', store=True)
    notify_days = fields.Selection([('1', '1'), ('10', '10'), ('30', '30'), ('60', '60'), ('90', '90')],
                                   default='30', required=True )
    notify_type = fields.Selection([('odoo', 'Odoo'), ('email', 'Email'), ('odoo_email', 'Odoo & Email')],
                                   default='odoo', required=True )
    notify_duration = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly'), ],
                                   default='weekly',  )

    # TODO: Notify process

    @api.onchange('issue_date', 'expire_date', 'notify_days')
    def _expiration_calculation(self):
        today = fields.Date.today()
        for rec in self:
            if rec.issue_date and rec.issue_date > fields.Date.today():
                raise UserError(_('Issue date cannot after today date.'))

            if rec.expire_date:
                if rec.issue_date and (rec.expire_date < rec.issue_date):
                    raise UserError(_('Expire date is not correct.'))

                expiration = int((rec.expire_date - today).days)

                if expiration > int(rec.notify_days):
                    rec.state = 'valid'
                elif expiration < 0:
                    rec.state = 'expired'
                else:
                    rec.state = 'expiring'
            else:
                expiration = 0
                rec.state = 'valid'
            rec.expiration = expiration

    # TODO: cron for recalculate expirations
    def expiration_cron(self):
        pass


class SdHrDocumentsTypes(models.Model):
    _name = 'sd_hr_documents.document_type'
    _description = 'document Type'

    name = fields.Char(required=True, translate=True)



