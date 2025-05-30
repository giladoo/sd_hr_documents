# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
from collections import defaultdict


class SdHrDocumentsIrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        # add res_field=False in domain if not present; the arg[0] trick below
        # works for domain items and '&'/'|'/'!' operators too
        # if res_model and res_model == 'sd_hr_documents.attachments':
        # is_match = any(item[0] == 'res_model' and item[2] == 'sd_hr_resume.records' for item in domain)

        # print(f"+++++++++++++++++>>>\n domain:{domain}\n is_match:{is_match}")  # Output: True or False
        print(f"$$$$$$$$$\n   _search 1 {domain, offset, limit, order, access_rights_uid}")


        # print(f"\n>>>>>>>>>>>>>>>>>>>>>>>>>>> _search() \n {domain} {access_rights_uid}")
        disable_binary_fields_attachments = False
        if not self.env.context.get('skip_res_field_check') and not any(arg[0] in ('id', 'res_field') for arg in domain):
            disable_binary_fields_attachments = True
            domain = [('res_field', '=', False)] + domain
            print(f"$$$$$$$$$\n   _search 3 {domain, offset, limit, order, access_rights_uid}")

        if self.env.is_superuser():
            # rules do not apply for the superuser
            print(f"$$$$$$$$$\n   _search 4 {domain, offset, limit, order, access_rights_uid}")

            return super()._search(domain, offset, limit, order, access_rights_uid)

        # For attachments, the permissions of the document they are attached to
        # apply, so we must remove attachments for which the user cannot access
        # the linked document. For the sake of performance, fetch the fields to
        # determine those permissions within the same SQL query.
        print(f"$$$$$$$$$\n   _search 2.1 {self}")
        self.flush_model(['res_model', 'res_id', 'res_field', 'public', 'create_uid'])
        print(f"$$$$$$$$$\n   _search 2.2 {self}")

        query = super()._search(domain, offset, limit, order, access_rights_uid)
        # query = self._search(domain, offset, limit, order, access_rights_uid)
        # maximum recursion depth exceeded while getting the repr of an object
        print(f"AAAAAAAAAAAAAA {query} {super()}")
        query_str, params = query.select(
            f'"{self._table}"."id"',
            f'"{self._table}"."res_model"',
            f'"{self._table}"."res_id"',
            f'"{self._table}"."res_field"',
            f'"{self._table}"."public"',
            f'"{self._table}"."create_uid"',
        )
        self.env.cr.execute(query_str, params)
        rows = self.env.cr.fetchall()
        print(f"OOOOOOOOOOOOOO {rows}")

        # determine permissions based on linked records
        all_ids = []
        allowed_ids = set()
        model_attachments = defaultdict(lambda: defaultdict(set))   # {res_model: {res_id: set(ids)}}
        for id_, res_model, res_id, res_field, public, create_uid in rows:
            print(f"HHHHHHHHHHHHHHH {res_model} {id_}")
            all_ids.append(id_)
            if public:
                allowed_ids.add(id_)
                continue
            if not res_id and (self.env.is_system() or create_uid == self.env.uid):
                allowed_ids.add(id_)
                continue
            if res_model and res_model == 'sd_hr_documents.attachments' and (self.env.user.has_group('hr.group_hr_manager') or self.env.user.has_group('sd_hr_documents.group_sd_hr_documents_users')):
                allowed_ids.add(id_)
                continue
            if not (res_field and disable_binary_fields_attachments) and res_model and res_id:
                model_attachments[res_model][res_id].add(id_)
        print(f"HHHHHHHHHHHHHHH allowed_ids{allowed_ids}")

        # check permissions on records model by model
        for res_model, targets in model_attachments.items():
            if res_model not in self.env:
                allowed_ids.update(id_ for ids in targets.values() for id_ in ids)
                continue
            if not self.env[res_model].check_access_rights('read', False):
                continue
            # filter ids according to what access rules permit
            ResModel = self.env[res_model].with_context(active_test=False)
            for res_id in ResModel.search([('id', 'in', list(targets))])._ids:
                allowed_ids.update(targets[res_id])

        # filter out all_ids by keeping allowed_ids only
        result = [id_ for id_ in all_ids if id_ in allowed_ids]

        # If the original search reached the limit, it is important the
        # filtered record set does so too. When a JS view receive a
        # record set whose length is below the limit, it thinks it
        # reached the last page. To avoid an infinite recursion due to the
        # permission checks the sub-call need to be aware of the number of
        # expected records to retrieve
        if len(all_ids) == limit and len(result) < self._context.get('need', limit):
            need = self._context.get('need', limit) - len(result)
            more_ids = self.with_context(need=need)._search(
                domain, offset + len(all_ids), limit, order, access_rights_uid,
                        )
            result.extend(list(more_ids)[:limit - len(result)])

        return self.browse(result)._as_query(order)


