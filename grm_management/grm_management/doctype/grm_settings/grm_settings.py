# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GRMSettings(Document):
	pass


def get_settings():
	"""Get GRM Settings singleton"""
	return frappe.get_single('GRM Settings')


def get_subscription_item():
	"""Get the configured subscription item"""
	settings = get_settings()
	if not settings.subscription_item:
		frappe.throw('Please configure Subscription Item in GRM Settings')
	return settings.subscription_item
