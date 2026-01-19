import frappe
from frappe.model.document import Document
from frappe import _

class Package(Document):
    def autoname(self):
        # use provided package_code if present or generate PKG-.#####
        code = self.get("package_code")
        if code:
            self.name = code
            return
        self.name = frappe.model.naming.make_autoname('PKG-.#####')

    def validate(self):
        self._validate_uniqueness()
        self._validate_access()
        self._validate_time_restrictions()
        self._validate_locations_and_space_types()

    def _validate_uniqueness(self):
        if self.package_code:
            exists = frappe.db.exists("Package", {"package_code": self.package_code, "name": ["!=", self.name or ""]})
            if exists:
                frappe.throw(_("Package Code must be unique"))

    def _validate_access(self):
        if self.access_type and self.access_type != "Unlimited":
            if not self.access_limit_value or self.access_limit_value <= 0:
                frappe.throw(_("Access Limit Value must be greater than 0 when Access Type is not Unlimited"))
        if self.rollover_unused:
            if not self.max_rollover or self.max_rollover <= 0:
                frappe.throw(_("Max Rollover must be greater than 0 when Rollover Unused is checked"))

    def _validate_time_restrictions(self):
        if not self.access_24_7:
            if not self.access_start_time or not self.access_end_time:
                frappe.throw(_("Start and End time are required when Access 24/7 is not checked"))
            if self.access_start_time >= self.access_end_time:
                frappe.throw(_("Access End Time must be after Access Start Time"))

    def _validate_locations_and_space_types(self):
        if not self.all_locations:
            if not self.allowed_locations or len(self.allowed_locations) == 0:
                frappe.throw(_("At least one Allowed Location is required when All Locations is not checked"))
        if not self.allowed_space_types or len(self.allowed_space_types) == 0:
            frappe.throw(_("At least one Allowed Space Type is required"))
