import frappe
from frappe.model.document import Document
from frappe import _

class Membership(Document):
    def validate(self):
        self._validate_dates()
        self._apply_package_snapshot()
        self._compute_financials()
        self._validate_pause_fields()
        self._expire_if_needed()

    def _validate_dates(self):
        if self.end_date < self.start_date:
            frappe.throw(_("End Date must be the same as or after Start Date"))

    def _apply_package_snapshot(self):
        if not self.package:
            return
        pkg = frappe.get_doc('Package', self.package)
        self.package_price = pkg.price
        self.access_type = pkg.access_type
        self.meeting_hours_allowed = pkg.meeting_room_hours
        self.guest_passes_allowed = pkg.guest_passes
        self.printing_pages_allowed = (pkg.printing_bw_pages or 0) + (pkg.printing_color_pages or 0)
        if pkg.access_type == 'Unlimited':
            self.total_access_allowed = 0
            # unlimited: represent as 0
        else:
            self.total_access_allowed = pkg.access_limit_value or 0
        # compute remaining
        self.access_remaining = (self.total_access_allowed - (self.access_used or 0) + (self.rollover_from_previous or 0)) if (self.total_access_allowed or 0) >= 0 else 0

    def _compute_financials(self):
        self.discount_amount = ((self.discount_percent or 0) * (self.package_price or 0) / 100.0)
        self.final_price = (self.package_price or 0) - (self.discount_amount or 0)

    def _validate_pause_fields(self):
        if self.status == 'Paused':
            if not self.pause_start or not self.pause_end:
                frappe.throw(_("Pause start and end dates are required when status is Paused"))
            if self.pause_end < self.pause_start:
                frappe.throw(_("Pause End must be equal to or after Pause Start"))

    def _expire_if_needed(self):
        if self.status == 'Active' and frappe.utils.getdate(frappe.utils.nowdate()) > frappe.utils.getdate(self.end_date):
            self.status = 'Expired'
            frappe.msgprint(_('Membership has been marked Expired as end date passed'))

    @frappe.whitelist()
    def decrement_access(self, qty=1):
        # used when booking checked-in; handles unlimited
        qty = int(qty)
        if self.access_type == 'Unlimited':
            # nothing to decrement
            return True
        if (self.access_remaining or 0) <= 0:
            frappe.throw(_("No remaining access units"))
        self.access_used = (self.access_used or 0) + qty
        self.access_remaining = (self.total_access_allowed or 0) - (self.access_used or 0)
        self.last_access_date = frappe.utils.nowdate()
        self.save()
        return True
