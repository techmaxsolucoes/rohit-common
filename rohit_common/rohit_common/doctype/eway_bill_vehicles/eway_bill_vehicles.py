# -*- coding: utf-8 -*-
# Copyright (c) 2020, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import re
from frappe.model.document import Document


class eWayBillVehicles(Document):
	def validate(self):
		'''
		Validate Vehicle Number as per the defined Vehicle Formats
		Refer Link https://docs.ewaybillgst.gov.in/apidocs/master-codes-list.html
		Refer Valid Formats of Vehicle Numbers also enlisted below for ease
		1. AB121234 (First 2 char are State Code)
		2. AB12A1234 (First 2 char are State Code)
		3. AB12AB1234 (First 2 char are State Code)
		4. ABC1234
		5. AB123A1234 (First 2 char are State Code)
		6. AB12ABC1234 (First 2 char are State Code)
		7. DFXXXXXX (Defence Vehicle)
		8. TRXXXXXXXXXXXXX (Temp RC) At least 7 characters
		9. BPXXXXXXXXXXXXX (Bhutan Vehicle) At least 7 characters
		10. NPXXXXXXXXXXXXX (Nepal Vehicle) At least 7 characters
		'''
		# Todo Implement the above Validations on Vehicle Number
		pass

