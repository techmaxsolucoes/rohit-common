# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from ...utils.contact_utils import validate_contact_emails



def validate(doc, method):
    """
    Validate the Email and Would move Multiple Emails in Single Row in Multiple Rows
    """
    validate_contact_emails(doc, backend=0)
