# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _

def execute(filters=None):
	if not filters: filters = {}

	invoice_list = get_invoices(filters)
	columns, expense_accounts, tax_accounts = get_columns(invoice_list)

	if not invoice_list:
		msgprint(_("No record found"))
		return columns, invoice_list

	invoice_expense_map = get_invoice_expense_map(invoice_list)
	invoice_expense_map, invoice_tax_map = get_invoice_tax_map(invoice_list,
		invoice_expense_map, expense_accounts)
	supplier_details = get_supplier_deatils(invoice_list)
	address_map = get_address_details(invoice_list)

	data = []
	for inv in invoice_list:
		# invoice details

		row = [inv.name, inv.posting_date, inv.supplier, 
			address_map.get(inv.supplier_address,{}).get("tin_no"), inv.taxes_and_charges,
			inv.bill_no, inv.bill_date, address_map.get(inv.supplier_address,{}).get("state"), 
			address_map.get(inv.supplier_address,{}).get("country")
			]

		# map expense values
		base_net_total = 0
		for expense_acc in expense_accounts:
			expense_amount = flt(invoice_expense_map.get(inv.name, {}).get(expense_acc))
			base_net_total += expense_amount
			row.append(expense_amount)

		# net total
		row.append(base_net_total or inv.base_net_total)

		# tax account
		total_tax = 0
		for tax_acc in tax_accounts:
			if tax_acc not in expense_accounts:
				tax_amount = flt(invoice_tax_map.get(inv.name, {}).get(tax_acc))
				total_tax += tax_amount
				row.append(tax_amount)

		# total tax, grand total, outstanding amount & rounded total
		row += [total_tax, inv.base_grand_total]
		data.append(row)

	return columns, data


def get_columns(invoice_list):
	"""return columns based on filters"""
	columns = [
		_("Invoice") + ":Link/Purchase Invoice:120", _("Posting Date") + ":Date:80", 
		_("Supplier Id") + ":Link/Supplier:180",  _("Supplier TIN No") + "::100", 
		_("Tax Type") + "::120", _("Bill No") + "::120", _("Bill Date") + ":Date:80",
		_("State") + "::100", _("Country") + "::100"
	]
	expense_accounts = tax_accounts = expense_columns = tax_columns = []

	if invoice_list:
		expense_accounts = frappe.db.sql_list("""select distinct expense_account
			from `tabPurchase Invoice Item` where docstatus = 1
			and (expense_account is not null and expense_account != '')
			and parent in (%s) order by expense_account""" %
			', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]))

		tax_accounts = 	frappe.db.sql_list("""select distinct account_head
			from `tabPurchase Taxes and Charges` where parenttype = 'Purchase Invoice'
			and docstatus = 1 and (account_head is not null and account_head != '')
			and category in ('Total', 'Valuation and Total')
			and parent in (%s) order by account_head""" %
			', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]))


	expense_columns = [(account + ":Currency:120") for account in expense_accounts]
	for account in tax_accounts:
		if account not in expense_accounts:
			tax_columns.append(account + ":Currency:120")

	columns = columns + expense_columns + [_("Net Total") + ":Currency:120"] + tax_columns + \
		[_("Total Tax") + ":Currency:120", _("Grand Total") + ":Currency:120"]

	return columns, expense_accounts, tax_accounts

def get_conditions(filters):
	conditions = ""

	if filters.get("company"): conditions += " and company=%(company)s"
	if filters.get("supplier"): conditions += " and supplier = %(supplier)s"

	if filters.get("from_date"): conditions += " and posting_date>=%(from_date)s"
	if filters.get("to_date"): conditions += " and posting_date<=%(to_date)s"

	return conditions

def get_invoices(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""select name, posting_date, supplier, supplier_address,
		bill_no, bill_date, remarks, base_net_total, base_grand_total, outstanding_amount,
		taxes_and_charges
		from `tabPurchase Invoice` where docstatus = 1 %s
		order by posting_date desc, name desc""" % conditions, filters, as_dict=1)


def get_invoice_expense_map(invoice_list):
	expense_details = frappe.db.sql("""select parent, expense_account, sum(base_net_amount) as amount
		from `tabPurchase Invoice Item` where parent in (%s) group by parent, expense_account""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_expense_map = {}
	for d in expense_details:
		invoice_expense_map.setdefault(d.parent, frappe._dict()).setdefault(d.expense_account, [])
		invoice_expense_map[d.parent][d.expense_account] = flt(d.amount)

	return invoice_expense_map

def get_invoice_tax_map(invoice_list, invoice_expense_map, expense_accounts):
	tax_details = frappe.db.sql("""select parent, account_head, sum(base_tax_amount_after_discount_amount) as tax_amount
		from `tabPurchase Taxes and Charges` where parent in (%s) group by parent, account_head""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_tax_map = {}
	for d in tax_details:
		if d.account_head in expense_accounts:
			if invoice_expense_map[d.parent].has_key(d.account_head):
				invoice_expense_map[d.parent][d.account_head] += flt(d.tax_amount)
			else:
				invoice_expense_map[d.parent][d.account_head] = flt(d.tax_amount)
		else:
			invoice_tax_map.setdefault(d.parent, frappe._dict()).setdefault(d.account_head, [])
			invoice_tax_map[d.parent][d.account_head] = flt(d.tax_amount)

	return invoice_expense_map, invoice_tax_map


def get_account_details(invoice_list):
	account_map = {}
	accounts = list(set([inv.credit_to for inv in invoice_list]))
	for acc in frappe.db.sql("""select name, parent_account from tabAccount
		where name in (%s)""" % ", ".join(["%s"]*len(accounts)), tuple(accounts), as_dict=1):
			account_map[acc.name] = acc.parent_account

	return account_map

def get_supplier_deatils(invoice_list):
	supplier_details = {}
	suppliers = list(set([inv.supplier for inv in invoice_list]))
	for supp in frappe.db.sql("""select name, supplier_type from `tabSupplier`
		where name in (%s)""" % ", ".join(["%s"]*len(suppliers)), tuple(suppliers), as_dict=1):
			supplier_details.setdefault(supp.name, supp.supplier_type)

	return supplier_details
	
def get_address_details(invoice_list):
	address_map = {}
	address = list(set([inv.supplier_address for inv in invoice_list]))
	for add in frappe.db.sql("""SELECT name, city, state, country, tin_no FROM `tabAddress` 
		WHERE name in (%s) """ % ", ".join(["%s"]*len(address)), tuple(address), as_dict=1):
		address_map.setdefault(add.name, add)
	
	return address_map