# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from rohit_common.utils.rohit_common_utils import validate_email_addresses


def validate(doc, method):
    for row in doc.email_ids:
        if row.validated != 1:
            emails = row.email_id.split(',')
            for email in emails:
                is_valid_email = validate_email_addresses(email)
                row.validated = is_valid_email
