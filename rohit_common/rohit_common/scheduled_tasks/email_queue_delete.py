# -*- coding: utf-8 -*-
# Copyright (c) 2020, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

#This Scheduled task deletes all the Unneeded Email Queue files to reduce the size of the DB
#1. All Email Queue with reference_doctype == NULL to be deleted is more than Month Old
#2. All Emails Queue with reference_doctype in Long Terms would be deleted after long_term_period = 90 days
#3. Other short-term doctype email queue would be deleted after normal period of 30 days

from __future__ import unicode_literals
import frappe
import time
from datetime import date, datetime

def execute():
	set_days = 30
	set_days_long_term = 90
	no_creation = 0
	old_emails = 0
	new_emails = 0
	no_ref_dt = frappe.db.sql("""SELECT name, creation, modified FROM `tabEmail Queue` 
		WHERE reference_doctype IS NULL ORDER BY creation, modified DESC """, as_dict=1)
	if no_ref_dt:
		for email in no_ref_dt:
			if email.creation is None:
				no_creation +=1
				delete_email(email.name, no_creation)
				print("NO Creation hence deleting " + email.name)
			elif (datetime.now() - email.creation).days > set_days:
				old_emails += 1
				delete_email(email.name, old_emails)
				print("More than " + str(set_days) + " days hence deleting email created on " + str(email.creation))
			else:
				new_emails += 1
				print("No Deleting since less than " + str(set_days) + " old")
		print("No of Emails without Doctype and No Creation Time Deleted = " + str(no_creation))
		print("No of Emails without Doctype and Over " + str(set_days) + " Days Old Deleted = " + str(old_emails))
		print("No of Emails without Doctype and Less " + str(set_days) + " Days Old Not Deleted = " + str(new_emails))
		print("Total No of Emails without Doctype were = " + str(len(no_ref_dt)))

	ref_dt = frappe.db.sql("""SELECT name, creation, modified, reference_doctype FROM `tabEmail Queue` 
		WHERE reference_doctype IS NOT NULL ORDER BY creation DESC, modified DESC """, as_dict=1)
	dt_short = ['Auto Email Report', 'Email Digest']
	no_creation = 0
	short_term = 0
	long_term = 0
	if ref_dt:
		for email in ref_dt:
			if email.creation is None:
				no_creation +=1
				delete_email(email.name, no_creation)
				print ("Deleting Old without Creation Email " + email.name)
			elif email.reference_doctype in dt_short:
				short_term +=1
				if (datetime.now() - email.creation).days > set_days:
					delete_email(email.name, short_term)
					print("More than Short Term " + str(set_days) + " hence deleting Ref Doct = " \
						+ email.reference_doctype)
			else:
				long_term +=1
				if (datetime.now() - email.creation).days > set_days_long_term:
					delete_email(email.name, long_term)
					print("More than Long Term " + str(set_days_long_term) + " hence deleting Ref Doct = " \
						+ email.reference_doctype)
		print("No of Emails with Doctype and No Creation Time Deleted = " + str(no_creation))
		print("No of Emails with Doctype and Short " + str(set_days) + " Days Old Deleted = " + str(short_term))
		print("No of Emails with Doctype and Long " + str(set_days_long_term) + " Days Old Not Deleted = " + str(long_term))

def delete_email(email_name, counting):
	if counting % 5000 == 0:
		frappe.db.sql("""DELETE FROM `tabEmail Queue` WHERE name = '%s'"""%(email_name))
		print ("Committing Changes")
		frappe.db.commit()
		time.sleep(2)
	else:
		frappe.db.sql("""DELETE FROM `tabEmail Queue` WHERE name = '%s'"""%(email_name))