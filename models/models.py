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
    related_model = fields.Many2one('ir.model', string="Related Model",  default=lambda self: self.env.context.get('related_model', False),
                                    domain="[('model', 'in', ['hr.contract', 'sd_hr_relatives.members', ])]"  )
    related_res_id = fields.Integer(string="Related ID", default=lambda self: self.env.context.get('related_res_id', False))
    related_res_name = fields.Char(string="Related Name", default=lambda self: self.env.context.get('related_res_name', False))

    related_model_records1 = fields.Many2one('',  )
    # related_model_record = fields.Many2one(related='related_model.id')
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




    @api.onchange('related_model')
    def _onchange_model_id(self):
        if self.related_model:
            # Update the record_id domain to filter based on the selected model
            model_name = self.related_model.model
            # return {'domain': {'related_model_records': [('model', '=', model_name)]}}
            return {'domain': {'related_model_records': []}}
        else:
            return {'domain': {'related_model_records': []}}

    # TODO: Notify process

    @api.onchange('issue_date', 'expire_date', 'notify_days')
    def _expiration_calculation(self):
        today = fields.Date.today()
        for rec in self:
            if rec.issue_date and rec.issue_date > fields.Date.today():
                raise UserError(_("Issue date cannot be after today's date."))

            if rec.expire_date:
                if rec.issue_date and (rec.expire_date < rec.issue_date):
                    raise UserError(_("Expire date is not correct."))

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
    #   Ignore notification if it is expired. Otherwise it will send notification forever.
    def expiration_cron(self):
        pass

    employee_document_count = fields.Integer(compute='_compute_employee_document_count')


    def _compute_employee_document_count(self):
        attachments = self.search([])
        for rec in self:
            rec.employee_document_count = len(list([att for att in attachments if att.employee_id == rec.employee_id ]))

    def employee_action_document_view(self):
        self.ensure_one()
        context = dict(self.env.context)
        context['employee_id'] = self.employee_id.id
        print(f"\n *************\n employee_action_document_view: {self}")
        return {
            'name': _('documents'),
            'domain': [('employee_id', '=', self.employee_id.id)],
            'res_model': 'sd_hr_documents.attachments',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'context': context
        }

    def related_model_action(self):
        print(f"\n MMMMMMMMMMMMM \n related_model_action: {self.related_model}")
        context = {}
        domain = []
        return {
                    # 'name': _('documents'),
                    'domain': domain,
                    'res_model': self.related_model.model,
                    'res_id': self.related_res_id,
                    'type': 'ir.actions.act_window',
                    'view_id': False,
                    'view_mode': 'form',
                    'context': context
                }

class SdHrDocumentsTypes(models.Model):
    _name = 'sd_hr_documents.document_type'
    _description = 'document Type'

    name = fields.Char(required=True, translate=True)



