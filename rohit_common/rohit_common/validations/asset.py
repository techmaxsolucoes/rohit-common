# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import msgprint
from frappe.utils import getdate, get_last_day, today, flt, cint, add_months, add_days, date_diff
from rigpl_erpnext.rigpl_erpnext.item import fn_next_string, fn_check_digit
from datetime import datetime
from dateutil import relativedelta

def validate(doc, method):
	ass_cat = frappe.get_doc("Asset Category", doc.asset_category)
	doc.expected_value_after_useful_life = round((ass_cat.residual_value_percent * \
	doc.gross_purchase_amount)/100,0)
	doc.total_number_of_depreciations = ass_cat.total_number_of_depreciations
	doc.frequency_of_depreciation = ass_cat.frequency_of_depreciation
	doc.depreciation_method = ass_cat.depreciation_method
	get_next_dep_date(doc,method)
	make_dep_schedule(doc, method)
	
def autoname(doc, method):
	if doc.autoname == 1:
		ass_cat = frappe.get_doc("Asset Category", doc.asset_category)
		'''
		fa = frappe.db.sql("""SELECT name FROM `tabItem Attribute Value` 
			WHERE parent = 'Tool Type' AND 
			attribute_value = 'Fixed Asset'""", as_list = 1)
		att = frappe.get_doc("Item Attribute Value", fa[0][0])
		'''
		purchase = getdate(doc.purchase_date)
		#name = YearMonth-AssetCategorySmall-SerialCheckDigit
		#Don't use - in the actual name for check digit
		name = str(purchase.year) + str('{:02d}'.format(purchase.month)) + \
			ass_cat.asset_short_name + str(ass_cat.serial)
		next_serial = fn_next_string(doc, str(ass_cat.serial))
		cd = fn_check_digit(doc, name)
		name = name + str(cd)
		doc.name = name
		#frappe.db.set_value("Item Attribute Value", fa[0][0], "serial", next_serial)
		frappe.db.set_value("Asset Category", ass_cat.name, "serial", next_serial)
	else:
		doc.name = doc.asset_name
	doc.asset_name = doc.name

def get_next_dep_date(doc,method):
	#Next depreciation date shoud be last date of the purchase date if monthly or last date
	#of period of depreciation
	#if monthly depreciation then last day or month, if bi-monthly then last day of month+1
	#if 3 monthly then last day of quarter and not 3 months
	#if 4 monthly then last day of third and not 4 months and so on and so forth
	fy_doc = get_fy_doc(doc,method)
	r = relativedelta.relativedelta(add_days(fy_doc.year_end_date,1), fy_doc.year_start_date)
	fy_months = r.years*12 + r.months
	dep_in_fy = cint(fy_months)/flt(doc.frequency_of_depreciation)
	booked_deps_months = (cint(doc.number_of_depreciations_booked)*cint(doc.frequency_of_depreciation))
	last_day = add_months(get_last_day(doc.purchase_date), booked_deps_months)
	if dep_in_fy >= 1 and dep_in_fy % 1  == 0:
		for i in range(0, cint(doc.total_number_of_depreciations)):
			dep_date = get_last_day(add_months(fy_doc.year_start_date, (i*doc.frequency_of_depreciation -1)))
			if last_day <= dep_date:
				doc.next_depreciation_date = dep_date
				break
			else:
				doc.next_depreciation_date = fy_doc.year_end_date
	elif dep_in_fy % 1  != 0:
		frappe.throw('Frequency Causing Depreciations not to be posted equally in FY, \
			please change the frequency of depreciation')
	else:
		frappe.throw('Months between depreciation cannot be less than 1')

def make_dep_schedule(doc,method):
	fy_doc = get_fy_doc(doc,method)
	diff_pd_npd = relativedelta.relativedelta(add_days(doc.next_depreciation_date,1), getdate(doc.purchase_date))
	diff_months = diff_pd_npd.years*12 + diff_pd_npd.months
	diff_days = date_diff(add_days(doc.next_depreciation_date,1), doc.purchase_date)
	fy_days = date_diff(fy_doc.year_end_date, fy_doc.year_start_date)
	middle_purchase_factor = flt(diff_days)/flt(fy_days)

	if doc.depreciation_method != 'Manual':
		doc.schedules = []

	if not doc.get("schedules") and doc.next_depreciation_date:
		value_after_depreciation = flt(doc.value_after_depreciation)

		if diff_months < doc.frequency_of_depreciation:
			number_of_pending_depreciations = cint(doc.total_number_of_depreciations) - \
				cint(doc.number_of_depreciations_booked) + 1
		else:
			number_of_pending_depreciations = cint(doc.total_number_of_depreciations) - \
					cint(doc.number_of_depreciations_booked)
		if number_of_pending_depreciations:
			for n in xrange(number_of_pending_depreciations):
				schedule_date = get_last_day(add_months(doc.next_depreciation_date, 
					n * cint(doc.frequency_of_depreciation)))

				if diff_months < doc.frequency_of_depreciation and n==0 and cint(doc.number_of_depreciations_booked) == 0:
					depreciation_amount = get_depreciation_amount(doc,value_after_depreciation, middle_purchase_factor)
				else:
					depreciation_amount = get_depreciation_amount(doc, value_after_depreciation, 1)
				value_after_depreciation -= flt(depreciation_amount)

				doc.append("schedules", {
					"schedule_date": schedule_date,
					"depreciation_amount": depreciation_amount
				})
		#frappe.throw(str(number_of_pending_depreciations))
	accumulated_depreciation = flt(doc.opening_accumulated_depreciation)
	value_after_depreciation = flt(doc.value_after_depreciation)
	for i, d in enumerate(doc.get("schedules")):
		depreciation_amount = flt(d.depreciation_amount, d.precision("depreciation_amount"))
		value_after_depreciation -= flt(depreciation_amount)

		if i==len(doc.get("schedules"))-1 and doc.depreciation_method == "Straight Line":
			depreciation_amount += flt(value_after_depreciation - flt(doc.expected_value_after_useful_life),
				d.precision("depreciation_amount"))

		d.depreciation_amount = depreciation_amount
		accumulated_depreciation += d.depreciation_amount
		d.accumulated_depreciation_amount = flt(accumulated_depreciation, d.precision("accumulated_depreciation_amount"))

def get_depreciation_amount(doc, depreciable_value, middle_purchase_factor):
	if doc.depreciation_method in ("Straight Line", "Manual"):
		depreciation_amount = round((flt(doc.value_after_depreciation) -
			flt(doc.expected_value_after_useful_life))* middle_purchase_factor / (cint(doc.total_number_of_depreciations) -
			cint(doc.number_of_depreciations_booked)),0)
	else:
		factor = 200.0 /  doc.total_number_of_depreciations
		depreciation_amount = flt(depreciable_value * factor / 100, 0)

		value_after_depreciation = flt(depreciable_value) - depreciation_amount
		if value_after_depreciation < flt(doc.expected_value_after_useful_life):
			depreciation_amount = flt(depreciable_value) - flt(doc.expected_value_after_useful_life)

	return depreciation_amount

def get_fy_doc(doc,method):
	fy = frappe.db.sql("""SELECT name FROM `tabFiscal Year` 
		WHERE year_start_date <= '%s' AND year_end_date >= '%s'""" %(doc.purchase_date, doc.purchase_date), as_list=1)
	fy_doc = frappe.get_doc("Fiscal Year", fy[0][0])
	return fy_doc