# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import msgprint

def validate(self):
	self.validate_primary_address()
	self.validate_shipping_address()


def validate(doc,method):
	valid_chars_gstin = "0123456789ABCDEFGIHJKLMNOPQRSTUVYWXZ"
	
	if doc.gstin != "NA":
		if len(doc.gstin)!= 15:
			frappe.msgprint("GSTIN should be exactly as 15 digits or NA",raise_exception=1)
		else:
			for n, char in enumerate(reversed(doc.gstin)):
				if not valid_chars_gstin.count(char):
					frappe.msgprint("Only Numbers and alphabets in UPPERCASE are allowed in GSTIN or NA", raise_exception=1)
			if doc.state_rigpl:
				state = frappe.get_doc("State", doc.state_rigpl)
			else:
				frappe.throw(("Selected State is NOT Valid for {0}").format(doc.state_rigpl))
				
			if doc.gstin[:2] <> state.state_code_numeric:
				#fetch and update the state automatically else throw error
				state_from_gst = frappe.db.sql("""SELECT name FROM `tabState` \
					WHERE state_code_numeric = '%s'"""%(doc.gstin[:2]), as_list=1)
				if state_from_gst:
					doc.state_rigpl = state_from_gst[0][0]
					doc.gst_state = state_from_gst[0][0]
				else:
					frappe.throw(("State Selected {0} for Address {1}, GSTIN number should begin \
						with {2}").format(doc.state_rigpl, doc.name, state.state_code_numeric)) 

	if doc.gstin != "NA":
		doc.pan = doc.gstin[2:12]
	else:
		doc.pan = ""
		
	#Todo: Add the GST check digit checksum for the last digit so that all GST numbers are
	#checked and entered properly.
	
	def validate_primary_address(self):
		"""Validate that there can only be one primary address for particular customer, supplier"""
		if self.is_primary_address == 1:
			self._unset_other("is_primary_address")

		else:
			#This would check if there is any Primary Address if not then would make current as Primary address
			for fieldname in ["customer", "supplier", "sales_partner", "lead"]:
				if self.get(fieldname):
					if not frappe.db.sql("""select name from `tabAddress` where is_primary_address=1
						and `%s`=%s and name!=%s""" % (fieldname, "%s", "%s"),
						(self.get(fieldname), self.name)):
							self.is_primary_address = 1
					break

	def validate_shipping_address(self):
		"""Validate that there can only be one shipping address for particular customer, supplier"""
		if self.is_shipping_address == 1:
			self._unset_other("is_shipping_address")
		else:
			#This would check if there is any Shipping Address if not then would make current as Shipping address
			for fieldname in ["customer", "supplier", "sales_partner", "lead"]:
				if self.get(fieldname):
					if not frappe.db.sql("""select name from `tabAddress` where is_shipping_address=1
						and `%s`=%s and name!=%s""" % (fieldname, "%s", "%s"),
						(self.get(fieldname), self.name)):
							self.is_shipping_address = 1
					break

	def _unset_other(self, is_address_type):
		for fieldname in ["customer", "supplier", "sales_partner", "lead"]:
			if self.get(fieldname):
				frappe.db.sql("""update `tabAddress` set `%s`=0 where `%s`=%s and name!=%s""" %
					(is_address_type, fieldname, "%s", "%s"), (self.get(fieldname), self.name))
				break
