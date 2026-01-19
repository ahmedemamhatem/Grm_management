import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime

CONFLICT_STATUSES = ['Confirmed', 'Checked-In']

class Booking(Document):
    def before_insert(self):
        # ensure booking_number generated via autoname
        pass

    def validate(self):
        self._validate_times()
        self._compute_duration()
        self._set_location_from_space()
        self._prevent_overlaps()
        self._compute_pricing()
        self._compute_services_totals()

    def on_update(self):
        # handle status transitions
        if self.status == 'Checked-In':
            self._on_check_in()
        if self.status == 'Completed':
            self._on_completed()

    def _validate_times(self):
        if not self.all_day:
            if not self.end_time or not self.start_time:
                frappe.throw(_("Start and End times are required unless All Day is checked"))
            if self.end_time <= self.start_time:
                frappe.throw(_("End Time must be after Start Time"))

    def _compute_duration(self):
        if self.all_day:
            self.duration_hours = 24.0
            return
        # compute duration in hours between start_time and end_time
        try:
            fmt = '%H:%M:%S' if len((self.start_time or '00:00').split(':'))==3 else '%H:%M'
            # use datetime on same booking_date
            sd = frappe.utils.parse_time(self.start_time)
            ed = frappe.utils.parse_time(self.end_time)
            # convert to seconds
            sh = sd.hour*3600 + sd.minute*60 + sd.second
            eh = ed.hour*3600 + ed.minute*60 + ed.second
            self.duration_hours = (eh - sh)/3600.0 if eh>sh else 0
        except Exception:
            self.duration_hours = 0

    def _set_location_from_space(self):
        if self.space:
            try:
                sp = frappe.get_doc('Space', self.space)
                if hasattr(sp, 'location') and sp.location:
                    self.location = sp.location
            except Exception:
                # guard for missing linked doc
                pass

    def _prevent_overlaps(self):
        # For same space and booking_date ensure no overlapping Confirmed/Checked-In bookings
        if not self.space or not self.booking_date:
            return
        start = self.start_time
        end = self.end_time
        bookings = frappe.db.sql("""
            SELECT name FROM `tabBooking`
            WHERE space=%s AND booking_date=%s AND status IN (%s,%s) AND name!=%s
        """, (self.space, self.booking_date, CONFLICT_STATUSES[0], CONFLICT_STATUSES[1], self.name or ''), as_dict=True)
        for b in bookings:
            row = frappe.get_doc('Booking', b.name)
            # if any overlap
            if self.all_day or row.all_day:
                frappe.throw(_("Conflicting booking exists: {0}").format(b.name))
            if row.start_time < self.end_time and row.end_time > self.start_time:
                frappe.throw(_("Conflicting booking exists: {0}").format(b.name))

    def _compute_services_totals(self):
        total = 0
        for r in (self.additional_services or []):
            r.amount = (r.qty or 0) * (r.rate or 0)
            total += r.amount
        self.services_total = total

    def _compute_pricing(self):
        # compute subtotal based on rate type
        subtotal = 0
        if self.rate_type == 'Hourly Rate':
            if not self.hourly_rate:
                frappe.throw(_("Hourly rate is required for Hourly Rate type"))
            subtotal = (self.duration_hours or 0) * self.hourly_rate
        elif self.rate_type == 'Daily Rate':
            if not self.daily_rate:
                frappe.throw(_("Daily rate is required for Daily Rate type"))
            subtotal = self.daily_rate
        elif self.rate_type == 'Package':
            if not self.membership:
                frappe.throw(_("Membership is required for Package rate type"))
            mem = frappe.get_doc('Membership', self.membership)
            if mem.status != 'Active':
                frappe.throw(_("Membership must be Active to be used for Package rate"))
            if mem.access_type != 'Unlimited' and (mem.access_remaining or 0) <= 0:
                frappe.throw(_("Membership has no remaining access units"))
            # pricing: assume package price as 0 for booking or could be 0
            subtotal = mem.final_price or 0
        self.subtotal = subtotal
        self.discount_amount = ((self.discount_percent or 0) * (self.subtotal or 0) / 100.0)
        self.total_amount = (self.subtotal or 0) + (self.services_total or 0) - (self.discount_amount or 0)

    def _on_check_in(self):
        if not self.actual_check_in:
            self.actual_check_in = frappe.utils.now_datetime()
        if not self.checked_in_by:
            self.checked_in_by = frappe.session.user
        self.access_granted = 1
        # if package, decrement membership access
        if self.rate_type == 'Package' and self.membership:
            try:
                mem = frappe.get_doc('Membership', self.membership)
                mem.decrement_access(1)
            except Exception as e:
                frappe.throw(_("Error decrementing membership access: {0}").format(e))

    def _on_completed(self):
        if not self.actual_check_out:
            self.actual_check_out = frappe.utils.now_datetime()

