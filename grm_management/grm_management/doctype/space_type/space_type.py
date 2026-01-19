import frappe
from frappe.model.document import Document


class SpaceType(Document):
	def validate(self):
		if not (self.type_code or "").strip():
			frappe.throw("Type Code is required.")

		if self.default_capacity is not None and self.default_capacity < 0:
			frappe.throw("Default Capacity cannot be negative.")

		min_hours = getattr(self, "min_booking_hours", None)
		max_hours = getattr(self, "max_booking_hours", None)
		if min_hours is not None and max_hours is not None and min_hours > max_hours:
			frappe.throw("Min Booking Hours cannot be greater than Max Booking Hours.")

		allow_fields = ["allow_hourly", "allow_daily", "allow_monthly", "allow_long_term"]
		has_allow_field = any(hasattr(self, field) for field in allow_fields)
		if has_allow_field:
			if not any(getattr(self, field, 0) for field in allow_fields):
				frappe.throw("At least one booking type must be allowed.")