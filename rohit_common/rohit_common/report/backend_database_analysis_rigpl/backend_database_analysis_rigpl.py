#  Copyright (c) 2021. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ....patches.backend_table_analysis import get_size_of_all_tables


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	cond = get_conditions(filters)
	if filters.get("all_tables") == 1:
		return[
			"Database Name::200", "Table Name::400", "Size in MB:Float:100", "Data MB::100", "Index MB::100",
			"Total Row:Int:150"
		]
	else:
		return[

		]


def get_data(filters):
	data = []
	if filters.get("all_tables") == 1:
		data_dict = get_size_of_all_tables()
		for d in data_dict:
			row = [
				d.db_name, d.tbl_name, d.size_mb, d.dl_mb, d.ind_mb, d.tbl_rows
			]
			data.append(row)
	return data


def get_conditions(filters):
	cond = ""
	if filters.get("all_tables") == 1 and filters.get("dt"):
		frappe.throw("If you want the Details of Specific Table then Uncheck All Tables")

	return cond
