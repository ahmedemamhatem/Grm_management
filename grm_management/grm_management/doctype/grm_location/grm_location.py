# -*- coding: utf-8 -*-
# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class GRMLocation(Document):
	"""
	GRM Location DocType Controller

	Manages coworking locations with:
	- Basic information (name, code, contact details)
	- Address information
	- Operating hours
	- Space statistics
	"""

	@frappe.whitelist()
	def update_statistics(self):
		"""
		Calculate and update space statistics from Space records

		Updates:
		- total_spaces: Count of all spaces at this location
		- occupied_spaces: Count of spaces with status 'Occupied'
		- available_spaces: Count of spaces with status 'Available'
		- reserved_spaces: Count of spaces with status 'Reserved'
		- occupancy_rate: Percentage of occupied spaces
		"""
		# Get total spaces count
		self.total_spaces = frappe.db.count("Space", {"location": self.name})

		# Get occupied spaces count
		self.occupied_spaces = frappe.db.count("Space", {
			"location": self.name,
			"status": "Occupied"
		})

		# Get available spaces count
		self.available_spaces = frappe.db.count("Space", {
			"location": self.name,
			"status": "Available"
		})

		# Get reserved spaces count
		self.reserved_spaces = frappe.db.count("Space", {
			"location": self.name,
			"status": "Reserved"
		})

		# Calculate occupancy rate
		if self.total_spaces > 0:
			self.occupancy_rate = (self.occupied_spaces / self.total_spaces) * 100
		else:
			self.occupancy_rate = 0

		self.save()

		frappe.msgprint(
			f"Statistics updated: {self.occupied_spaces}/{self.total_spaces} spaces occupied ({self.occupancy_rate:.1f}%)",
			title="Location Statistics Updated"
		)

	@frappe.whitelist()
	def get_location_summary(self):
		"""
		Get comprehensive location summary with statistics

		Returns:
			dict: Location summary with spaces, contracts, bookings
		"""
		# Get active contracts count
		active_contracts = frappe.db.count("GRM Contract", {
			"status": "Active"
		})

		# Get today's bookings count
		today_bookings = frappe.db.count("Booking", {
			"location": self.name,
			"booking_date": frappe.utils.today(),
			"status": ["in", ["Confirmed", "Checked-In"]]
		})

		return {
			"location_name": self.location_name,
			"location_code": self.location_code,
			"status": self.status,
			"total_spaces": self.total_spaces or 0,
			"occupied_spaces": self.occupied_spaces or 0,
			"available_spaces": self.available_spaces or 0,
			"reserved_spaces": self.reserved_spaces or 0,
			"occupancy_rate": self.occupancy_rate or 0,
			"active_contracts": active_contracts,
			"today_bookings": today_bookings
		}
