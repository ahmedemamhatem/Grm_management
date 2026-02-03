# Copyright (c) 2026, Wael ELsafty and contributors
import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_seconds

class GRMAccessLog(Document):
	def after_insert(self):
		"""Handle entry-based subscription counting"""
		if self.event_type == "Check-in" and self.subscription:
			sub = frappe.get_doc("GRM Subscription", self.subscription)
			if sub.subscription_type == "Entry-based":
				sub.record_entry()
				self.entry_number = sub.entries_used
				self.save()
