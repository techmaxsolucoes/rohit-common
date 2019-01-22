# Copyright (c) 2013, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def execute(filters=None):
	if not filters: filters = {}
	conditions, cond_dep = get_conditions(filters)
	columns = get_columns()
	assets = get_assets(conditions, filters)
	acc_dep = get_acc_dep(assets, cond_dep)
	data = []
	for a in assets:
		open_acc_dep = a.opening_accumulated_depreciation
		purchase = a.gross_purchase_amount
		row = [a.name, a.item_code, a.purchase_date, purchase, a.total_number_of_depreciations, \
		open_acc_dep]
		check = 0
		for acc in acc_dep:
			if acc.parent == a.name:
				total_dep = flt(round(acc.dep,2))
				period_dep = flt(round(acc.monthly, 2))
				row += [(total_dep - period_dep), total_dep, period_dep]
				check = 1
		if check == 0: #if fully depreciated asset
			total_dep = purchase - a.salvage
			period_dep = 0
			row += [(total_dep - period_dep), total_dep, period_dep]
		row += [(purchase - total_dep), a.salvage, a.fixed_asset_account, a.asset_category, \
		a.warehouse, a.model, a.manufacturer, a.description]
		

		data.append(row)
	return columns, data

def get_columns():
	return [
		"Asset:Link/Asset:150", "Item:Link/Item:150",
		"Purchase Date:Date:80", "Gross Purchase Amt:Currency:100", "Total # Dep:Int:60", 
		"Op Acc Dep:Currency:100", "Op Dep Period:Currency:100", 
		"Total Depreciation:Currency:100", "Period Dep:Currency:100",
		"Net Block:Currency:100", "Salvage Value:Currency:100", "Account:Link/Account:200",
		"AssetCategory:Link/Asset Category:150", "Warehouse::150", "Model::150", 
		"Manufacturer::150", "Description::250"
	]
	
def get_assets(conditions, filters):
	query = """SELECT ass.name, ass.item_code, ass.asset_category, 
		IFNULL(ass.warehouse, "NIL") as warehouse, IFNULL(ass.model, "NIL") as model, 
		IFNULL(ass.manufacturer, "NIL") as manufacturer,
		IFNULL(ass.description, "NIL") as description, ass.purchase_date, 
		ass.gross_purchase_amount, ass.opening_accumulated_depreciation, 
		IFNULL(ass_fb.expected_value_after_useful_life, 0) AS salvage, 
		ass_fb.total_number_of_depreciations, as_cat_acc.fixed_asset_account
		FROM `tabAsset` ass, `tabAsset Category` as_cat, `tabAsset Category Account` as_cat_acc,
			`tabAsset Finance Book` ass_fb
		WHERE ass.docstatus != 2 AND ass.asset_category = as_cat.name 
			AND ass_fb.parent = ass.name AND ass_fb.parenttype = 'Asset'
			AND IFNULL(ass.disposal_date, '2099-12-31') >= '%s' 
			AND as_cat_acc.parent = as_cat.name  %s
		ORDER BY ass.purchase_date DESC, ass.asset_category""" %(filters.get("to_date"),conditions)
	assets = frappe.db.sql(query, as_dict = 1)
	if assets:
		pass
	else:
		frappe.throw("No Assets in the Selected Criterion")
	#frappe.msgprint(str(assets))
	return assets

def get_acc_dep(asset, cond_dep):
	acc_dep = frappe.db.sql("""SELECT MAX(ds.accumulated_depreciation_amount) as dep,
		ds.parent, SUM(ds.depreciation_amount) as monthly
		FROM `tabDepreciation Schedule` ds
		WHERE ds.docstatus != 2 {condition} AND ds.parent IN (%s)
		GROUP BY ds.parent""".format(condition = cond_dep) % 
		(', '.join(['%s']*len(asset))), tuple([d.name for d in asset]), as_dict=1)
	return acc_dep
	
def get_conditions(filters):
	conditions = ""
	cond_dep = ""
	
	if filters.get("from_date"):
		if filters["from_date"] > filters["to_date"]:
			frappe.throw("From Date cannot be greater than To Date")
		cond_dep += "AND ds.schedule_date >= '%s'"% filters["from_date"]
	
	if filters.get("to_date"):
		conditions += "AND ass.purchase_date <= '%s'" % filters["to_date"]
		cond_dep += "AND ds.schedule_date <= '%s'"% filters["to_date"]
		
	if filters.get("asset_category"):
		conditions += "AND ass.asset_category = '%s'" % filters["asset_category"]
		
	if filters.get("asset"):
		conditions += "AND ass.name = '%s'" % filters["asset"]
		
	if filters.get("account"):
		conditions += "AND as_cat_acc.fixed_asset_account = '%s'" % filters["account"]
		
		
	return conditions, cond_dep