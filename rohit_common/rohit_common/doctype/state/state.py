# -*- coding: utf-8 -*-
# Copyright (c) 2017, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class State(Document):
    def validate(self):
        if self.country:
            country_doc = frappe.get_doc("Country", self.country)
            if country_doc.known_states != 1:
                frappe.throw("{} does not have Known States Checked for {}".format(
                    frappe.get_desk_link("Country", self.country), frappe.get_desk_link("State", self.name)))
