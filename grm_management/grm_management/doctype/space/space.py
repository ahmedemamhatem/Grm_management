import frappe
from frappe.model.document import Document
from frappe import _


class Space(Document):
	def validate(self):
		"""Validate space data"""
		self._validate_capacity()
		self.set_pricing()

	def _validate_capacity(self):
		"""Ensure capacity is greater than 0"""
		if not self.capacity or self.capacity <= 0:
			frappe.throw(_("Capacity must be greater than 0"))

	def set_pricing(self):
		"""Set pricing from Space Type if not using custom pricing"""
		if not self.use_custom_pricing and self.space_type:
			try:
				space_type = frappe.get_doc("Space Type", self.space_type)
				self.hourly_rate = space_type.hourly_rate or 0
				self.daily_rate = space_type.daily_rate or 0
				self.monthly_rate = space_type.monthly_rate or 0
			except Exception as e:
				frappe.log_error(f"Error fetching Space Type pricing: {str(e)}", "Space Pricing Error")

	def get_rate(self, rate_type):
		"""Get rate based on rate type (hourly, daily, monthly)

		Args:
			rate_type: String - 'hourly', 'daily', or 'monthly'

		Returns:
			Float - The rate amount
		"""
		rate_type = rate_type.lower()
		if rate_type == "hourly":
			return self.hourly_rate or 0
		elif rate_type == "daily":
			return self.daily_rate or 0
		elif rate_type == "monthly":
			return self.monthly_rate or 0
		else:
			frappe.throw(_("Invalid rate type: {0}").format(rate_type))

	@frappe.whitelist()
	def set_occupied(self, member, contract=None):
		"""Set space as occupied by a member

		Args:
			member: Member document name
			contract: GRM Contract document name (optional)
		"""
		self.status = "Occupied"
		self.current_member = member
		self.current_contract = contract

		# Set contract end date if contract provided
		if contract:
			try:
				contract_doc = frappe.get_doc("GRM Contract", contract)
				self.contract_end_date = contract_doc.end_date
			except Exception as e:
				frappe.log_error(f"Error fetching contract end date: {str(e)}", "Space Occupancy Error")

		self.save()

		# Update location statistics
		if self.location:
			self._update_location_stats()

		frappe.msgprint(_("Space {0} marked as Occupied").format(self.space_name), indicator="green", alert=True)

	@frappe.whitelist()
	def set_available(self):
		"""Clear space to Available status"""
		self.status = "Available"
		self.current_member = None
		self.current_contract = None
		self.contract_end_date = None

		self.save()

		# Update location statistics
		if self.location:
			self._update_location_stats()

		frappe.msgprint(_("Space {0} marked as Available").format(self.space_name), indicator="green", alert=True)

	@frappe.whitelist()
	def set_reserved(self, member=None, contract=None):
		"""Set space as reserved

		Args:
			member: Member document name (optional)
			contract: GRM Contract document name (optional)
		"""
		self.status = "Reserved"
		if member:
			self.current_member = member
		if contract:
			self.current_contract = contract

		self.save()

		# Update location statistics
		if self.location:
			self._update_location_stats()

		frappe.msgprint(_("Space {0} marked as Reserved").format(self.space_name), indicator="orange", alert=True)

	@frappe.whitelist()
	def set_maintenance(self):
		"""Set space as under maintenance"""
		self.status = "Maintenance"
		self.save()

		# Update location statistics
		if self.location:
			self._update_location_stats()

		frappe.msgprint(_("Space {0} marked as Under Maintenance").format(self.space_name), indicator="red", alert=True)

	def _update_location_stats(self):
		"""Update location statistics after status change"""
		if not self.location:
			return

		try:
			# Import here to avoid circular import
			location_doc = frappe.get_doc("Location", self.location)
			if hasattr(location_doc, 'update_statistics'):
				location_doc.update_statistics()
		except Exception as e:
			frappe.log_error(f"Error updating location statistics: {str(e)}", "Location Stats Update Error")
