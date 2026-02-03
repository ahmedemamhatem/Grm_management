# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class GRMLocation(Document):
	def validate(self):
		"""Validate location data before saving"""
		self.validate_contact_info()
		self.validate_operating_hours()
		
	def before_save(self):
		"""Update statistics before saving"""
		# Only update statistics if not in insert mode to avoid recursion
		if not self.is_new():
			self.update_statistics_values()
		self.last_updated = frappe.utils.now()
		
	def validate_contact_info(self):
		"""Validate email and phone format"""
		if self.primary_email and not frappe.utils.validate_email_address(self.primary_email):
			frappe.throw(_("Invalid email address: {0}").format(self.primary_email))
			
	def validate_operating_hours(self):
		"""Validate operating hours"""
		if not self.operating_hours_24_7:
			if not self.operating_start_time or not self.operating_end_time:
				frappe.throw(_("Please specify operating hours or enable 24/7 access"))
				
			if self.operating_start_time >= self.operating_end_time:
				frappe.throw(_("Start time must be before end time"))
				
	def update_statistics_values(self):
		"""Update location statistics values without saving"""
		# Count properties
		self.total_properties = frappe.db.count("GRM Property", {
			"location": self.name
		})

		# Count spaces
		self.total_spaces = frappe.db.count("GRM Space", {
			"location": self.name
		})

		# Count available spaces
		self.available_spaces = frappe.db.count("GRM Space", {
			"location": self.name,
			"status": "Available"
		})

		# Count occupied spaces
		self.occupied_spaces = frappe.db.count("GRM Space", {
			"location": self.name,
			"status": "Rented"
		})

		# Calculate occupancy rate
		if self.total_spaces > 0:
			self.occupancy_rate = (self.occupied_spaces / self.total_spaces) * 100
		else:
			self.occupancy_rate = 0

		# Calculate monthly capacity (sum of all space monthly rates)
		spaces = frappe.get_all("GRM Space",
			filters={"location": self.name},
			fields=["monthly_rate"]
		)
		self.monthly_capacity = sum([s.monthly_rate or 0 for s in spaces])

	@frappe.whitelist()
	def update_statistics(self):
		"""Update location statistics - properties, spaces, occupancy"""
		self.update_statistics_values()
		self.save()

		return {
			"total_properties": self.total_properties,
			"total_spaces": self.total_spaces,
			"available_spaces": self.available_spaces,
			"occupied_spaces": self.occupied_spaces,
			"occupancy_rate": self.occupancy_rate,
			"monthly_capacity": self.monthly_capacity
		}
