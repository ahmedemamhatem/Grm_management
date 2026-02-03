# Copyright (c) 2026, Wael ELsafty and contributors
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class GRMSubscriptionPackage(Document):
	def validate(self):
		self.calculate_final_price()
		
	def calculate_final_price(self):
		discount = flt(self.standard_price) * flt(self.discount_percentage) / 100
		self.final_price = flt(self.standard_price) - discount
