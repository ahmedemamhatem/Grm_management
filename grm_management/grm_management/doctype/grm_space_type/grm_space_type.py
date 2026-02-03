# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GRMSpaceType(Document):
	def validate(self):
		"""Validate space type data"""
		if self.min_capacity and self.max_capacity:
			if self.min_capacity > self.max_capacity:
				frappe.throw("Min Capacity cannot be greater than Max Capacity")
		
		if not self.default_capacity:
			self.default_capacity = 1
