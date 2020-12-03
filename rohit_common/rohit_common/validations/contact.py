# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from rohit_common.utils.rohit_common_utils import validate_email_addresses


def validate(doc, method):
    for row in doc.email_ids:
        validate_email_addresses(row.email_id)
