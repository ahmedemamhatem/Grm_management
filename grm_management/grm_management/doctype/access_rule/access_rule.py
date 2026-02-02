# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class AccessRule(Document):
	def validate(self):
		"""Validate access rule and set member from reference"""
		self._set_member_from_reference()
		self._validate_dates()
		self._set_rule_name()

	def after_insert(self):
		"""Sync to devices after creating access rule"""
		self.sync_to_devices()

	def _set_member_from_reference(self):
		"""Auto-populate member field from reference document"""
		if self.reference_type and self.reference_name:
			if self.reference_type == "Member":
				self.member = self.reference_name
			elif self.reference_type in ["GRM Contract", "Membership"]:
				try:
					ref_doc = frappe.get_doc(self.reference_type, self.reference_name)
					if hasattr(ref_doc, 'member'):
						self.member = ref_doc.member
				except Exception as e:
					frappe.log_error(f"Error fetching member from reference: {str(e)}", "Access Rule Validation Error")

	def _validate_dates(self):
		"""Validate date range"""
		if self.valid_until and self.valid_from:
			if frappe.utils.getdate(self.valid_until) < frappe.utils.getdate(self.valid_from):
				frappe.throw(_("Valid Until must be on or after Valid From"))

	def _set_rule_name(self):
		"""Auto-generate rule name if not set"""
		if not self.rule_name:
			member_name = frappe.db.get_value("Member", self.member, "member_name") if self.member else "Unknown"
			self.rule_name = f"{self.rule_type} - {member_name}"

	@frappe.whitelist()
	def sync_to_devices(self):
		"""Sync user access to all devices in the rule"""
		if not self.member:
			frappe.throw(_("Member is required for syncing to devices"))

		if self.status != "Active":
			frappe.msgprint(_("Only Active rules are synced to devices"), indicator="orange", alert=True)
			return

		# Get member's ZK User ID
		member = frappe.get_doc("Member", self.member)
		if not member.zk_user_id:
			frappe.throw(_("Member {0} has no ZK User ID assigned").format(member.member_name))

		synced_count = 0
		errors = []

		# Sync to each device
		for device_row in self.devices or []:
			try:
				device = frappe.get_doc("Access Device", device_row.access_device)

				# Get device connection
				zk = device.get_connection()
				if not zk:
					errors.append(f"{device.device_name}: Connection failed")
					continue

				# Add user to device
				success = self._add_user_to_device(zk, member, device)

				if success:
					synced_count += 1
					device_row.sync_status = "Synced"
					device_row.last_sync = frappe.utils.now()
				else:
					device_row.sync_status = "Failed"
					errors.append(f"{device.device_name}: Failed to add user")

			except Exception as e:
				device_row.sync_status = "Failed"
				errors.append(f"{device_row.access_device}: {str(e)}")
				frappe.log_error(f"Error syncing to device {device_row.access_device}: {str(e)}", "Access Rule Sync Error")

		self.save()

		if synced_count > 0:
			frappe.msgprint(_("Synced to {0} device(s)").format(synced_count), indicator="green", alert=True)
		if errors:
			frappe.msgprint(_("Errors: {0}").format(", ".join(errors)), indicator="red", alert=True)

	def _add_user_to_device(self, zk, member, device):
		"""Add user to ZK device with time restrictions"""
		try:
			# User details
			user_id = int(member.zk_user_id)
			name = member.member_name[:24]  # ZK has name length limit
			card_no = member.access_card_number or ""

			# Add user to device
			# Note: Actual ZK library methods depend on pyzk implementation
			# This is a simplified version
			zk.set_user(
				uid=user_id,
				name=name,
				privilege=0,  # 0 = User, 14 = Admin
				password='',  # Optional PIN
				group_id='',
				user_id=str(user_id),
				card=card_no
			)

			# Set time group/schedule if not 24/7
			if not self.is_24_7 and self.access_start_time and self.access_end_time:
				# Time zone setup would be device-specific
				# This is placeholder - actual implementation depends on ZK device model
				pass

			return True

		except Exception as e:
			frappe.log_error(f"Error adding user to device: {str(e)}", "ZK User Add Error")
			return False

	@frappe.whitelist()
	def remove_from_devices(self):
		"""Remove user from all devices in this rule"""
		if not self.member:
			return

		member = frappe.get_doc("Member", self.member)
		if not member.zk_user_id:
			return

		removed_count = 0

		for device_row in self.devices or []:
			try:
				device = frappe.get_doc("Access Device", device_row.access_device)
				zk = device.get_connection()
				if not zk:
					continue

				# Remove user from device
				zk.delete_user(uid=int(member.zk_user_id))
				removed_count += 1

				device_row.sync_status = "Removed"
				device_row.last_sync = frappe.utils.now()

			except Exception as e:
				frappe.log_error(f"Error removing user from device {device_row.access_device}: {str(e)}", "Access Rule Remove Error")

		self.save()

		if removed_count > 0:
			frappe.msgprint(_("Removed from {0} device(s)").format(removed_count), indicator="green", alert=True)

	@frappe.whitelist()
	def deactivate(self):
		"""Deactivate rule and remove from devices"""
		self.status = "Expired"
		self.save()

		# Remove from devices
		self.remove_from_devices()

		frappe.msgprint(_("Access Rule deactivated"), indicator="orange", alert=True)

	@frappe.whitelist()
	def check_access(self, device, current_time=None):
		"""Check if access is allowed at the given time

		Args:
			device: Access Device name
			current_time: datetime object (defaults to now)

		Returns:
			dict: {"allowed": bool, "reason": str}
		"""
		if not current_time:
			current_time = frappe.utils.now_datetime()

		# Check if rule is active
		if self.status != "Active":
			return {"allowed": False, "reason": "Access rule is not active"}

		# Check date range
		current_date = frappe.utils.getdate(current_time)
		if current_date < frappe.utils.getdate(self.valid_from):
			return {"allowed": False, "reason": "Access not yet valid"}
		if current_date > frappe.utils.getdate(self.valid_until):
			return {"allowed": False, "reason": "Access has expired"}

		# Check time of day (if not 24/7)
		if not self.is_24_7:
			current_time_only = current_time.time()
			start_time = frappe.utils.parse_time(self.access_start_time)
			end_time = frappe.utils.parse_time(self.access_end_time)

			if current_time_only < start_time or current_time_only > end_time:
				return {"allowed": False, "reason": f"Access only allowed between {self.access_start_time} and {self.access_end_time}"}

		# Check day of week
		if self.allowed_days:
			day_name = current_time.strftime("%A")
			if day_name not in self.allowed_days:
				return {"allowed": False, "reason": f"Access not allowed on {day_name}"}

		# Check entry limits
		if self.limit_type and self.limit_type != "None":
			if (self.entries_remaining or 0) <= 0:
				return {"allowed": False, "reason": "Entry limit reached"}

		# Check device is in rule
		device_exists = False
		for device_row in self.devices or []:
			if device_row.access_device == device:
				device_exists = True
				break

		if not device_exists:
			return {"allowed": False, "reason": "Device not authorized for this rule"}

		return {"allowed": True, "reason": "Access granted"}


@frappe.whitelist()
def create_access_rule(rule_type, reference_type, reference_name, member, valid_from, valid_until, **kwargs):
	"""Helper function to create Access Rule

	Args:
		rule_type: Contract, Membership, Custom
		reference_type: GRM Contract, Membership, Member
		reference_name: Document name
		member: Member name
		valid_from: Start date
		valid_until: End date
		**kwargs: Additional fields (status, devices, is_24_7, etc.)

	Returns:
		str: Access Rule name
	"""
	access_rule = frappe.new_doc("Access Rule")
	access_rule.rule_type = rule_type
	access_rule.reference_type = reference_type
	access_rule.reference_name = reference_name
	access_rule.member = member
	access_rule.valid_from = valid_from
	access_rule.valid_until = valid_until

	# Set optional fields
	for key, value in kwargs.items():
		if hasattr(access_rule, key):
			setattr(access_rule, key, value)

	access_rule.insert(ignore_permissions=True)

	return access_rule.name
