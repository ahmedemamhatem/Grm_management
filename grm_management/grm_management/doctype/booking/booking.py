import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta

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

    @frappe.whitelist()
    def confirm(self):
        """Confirm booking - validate final availability, deduct from membership if Package"""
        if self.status != 'Draft':
            frappe.throw(_("Only Draft bookings can be confirmed"))

        # Final availability check
        self._prevent_overlaps()

        # If using package/membership, check access remaining
        if self.rate_type == 'Package' and self.membership:
            mem = frappe.get_doc('Membership', self.membership)
            if mem.status != 'Active':
                frappe.throw(_("Membership is not Active"))
            if mem.access_type != 'Unlimited' and (mem.access_remaining or 0) <= 0:
                frappe.throw(_("Membership has no remaining access units"))

        # Set status to Confirmed
        self.status = 'Confirmed'
        self.save()

        # Create invoice if prepaid
        if self.rate_type in ['Hourly Rate', 'Daily Rate']:
            self._create_invoice()

        # Send confirmation email
        self._send_confirmation_email()

        frappe.msgprint(_("Booking confirmed successfully"), indicator="green", alert=True)

    @frappe.whitelist()
    def check_in(self):
        """Check-in to booking - record actual check-in, grant access, create Access Log"""
        if self.status != 'Confirmed':
            frappe.throw(_("Only Confirmed bookings can be checked in"))

        # Validate booking is for today
        if frappe.utils.getdate(self.booking_date) != frappe.utils.getdate(frappe.utils.nowdate()):
            frappe.throw(_("Cannot check-in to booking that is not for today"))

        # Set status to Checked-In
        self.status = 'Checked-In'
        self.actual_check_in = frappe.utils.now_datetime()
        self.checked_in_by = frappe.session.user
        self.access_granted = 1

        # If package, decrement membership access
        if self.rate_type == 'Package' and self.membership:
            try:
                mem = frappe.get_doc('Membership', self.membership)
                mem.decrement_access(1)
            except Exception as e:
                frappe.throw(_("Error decrementing membership access: {0}").format(e))

        self.save()

        # Grant temporary access to space
        self._grant_temporary_access()

        # Create Access Log
        self._create_access_log('Check-In')

        # Update member last visit
        self._update_member_last_visit()

        frappe.msgprint(_("Checked-in successfully"), indicator="green", alert=True)

    @frappe.whitelist()
    def check_out(self):
        """Check-out from booking - record actual check-out, calculate overtime, revoke access"""
        if self.status != 'Checked-In':
            frappe.throw(_("Only Checked-In bookings can be checked out"))

        # Set status to Completed
        self.status = 'Completed'
        self.actual_check_out = frappe.utils.now_datetime()

        # Calculate overtime
        planned_end = datetime.combine(frappe.utils.getdate(self.booking_date), frappe.utils.parse_time(self.end_time))
        actual_end = self.actual_check_out

        if actual_end > planned_end:
            overtime_hours = (actual_end - planned_end).total_seconds() / 3600
            self.overtime_hours = overtime_hours

            # Calculate overtime charges (1.5x hourly rate)
            if self.hourly_rate:
                self.overtime_charges = overtime_hours * self.hourly_rate * 1.5
                self.total_amount = (self.total_amount or 0) + (self.overtime_charges or 0)

        self.save()

        # Revoke temporary access
        self._revoke_temporary_access()

        # Create Access Log for check-out
        self._create_access_log('Check-Out')

        # Create invoice if postpaid (daily rate) or if overtime charges
        if self.rate_type == 'Daily Rate' or (self.overtime_charges or 0) > 0:
            self._create_invoice()

        frappe.msgprint(_("Checked-out successfully. Overtime: {0} hours").format(self.overtime_hours or 0), indicator="green", alert=True)

    @frappe.whitelist()
    def cancel_booking(self, reason=None):
        """Cancel booking - return membership credits if applicable"""
        if self.status in ['Completed', 'Cancelled']:
            frappe.throw(_("Cannot cancel {0} booking").format(self.status))

        previous_status = self.status
        self.status = 'Cancelled'
        if reason:
            self.cancellation_reason = reason

        # If checked-in, revoke access first
        if previous_status == 'Checked-In':
            self._revoke_temporary_access()

        # If package and was checked-in, return credit
        if self.rate_type == 'Package' and self.membership and previous_status == 'Checked-In':
            try:
                mem = frappe.get_doc('Membership', self.membership)
                # Return the access credit
                mem.access_used = max(0, (mem.access_used or 0) - 1)
                mem.access_remaining = (mem.total_access_allowed or 0) - (mem.access_used or 0) + (mem.rollover_from_previous or 0)
                mem.save()
                frappe.msgprint(_("Membership credit returned"), indicator="green")
            except Exception as e:
                frappe.log_error(f"Error returning membership credit: {str(e)}", "Booking Cancellation Error")

        self.save()

        frappe.msgprint(_("Booking cancelled"), indicator="orange", alert=True)

    @frappe.whitelist()
    def mark_no_show(self):
        """Mark booking as No-Show - called by scheduler for missed bookings"""
        if self.status != 'Confirmed':
            return

        # Check if booking date + end time has passed
        booking_end = datetime.combine(frappe.utils.getdate(self.booking_date), frappe.utils.parse_time(self.end_time))
        current_time = frappe.utils.now_datetime()

        # Add grace period (e.g., 30 minutes)
        grace_minutes = 30
        booking_end_with_grace = booking_end + timedelta(minutes=grace_minutes)

        if current_time > booking_end_with_grace:
            self.status = 'No-Show'
            self.save()

            # Create no-show fee invoice if configured
            # self._create_no_show_invoice()

            frappe.msgprint(_("Booking marked as No-Show"), indicator="red", alert=True)

    def _grant_temporary_access(self):
        """Grant temporary access to the booked space"""
        if not self.space:
            return

        try:
            space = frappe.get_doc("Space", self.space)
            if not space.access_device:
                return

            # Get member's ZK User ID
            member = frappe.get_doc("Member", self.member)
            if not member.zk_user_id:
                return

            # Create temporary Access Rule for this booking
            access_rule = frappe.new_doc("Access Rule")
            access_rule.rule_type = "Booking"
            access_rule.reference_type = "Booking"
            access_rule.reference_name = self.name
            access_rule.member = self.member
            access_rule.valid_from = self.booking_date
            access_rule.valid_until = self.booking_date
            access_rule.status = "Active"

            # Set time restrictions
            access_rule.access_start_time = self.start_time
            access_rule.access_end_time = self.end_time

            # Add device
            access_rule.append("devices", {
                "access_device": space.access_device
            })

            access_rule.insert(ignore_permissions=True)

        except Exception as e:
            frappe.log_error(f"Error granting temporary access: {str(e)}", "Booking Access Grant Error")

    def _revoke_temporary_access(self):
        """Revoke temporary access granted for this booking"""
        # Find and deactivate Access Rules for this booking
        access_rules = frappe.get_all("Access Rule", filters={
            "reference_type": "Booking",
            "reference_name": self.name,
            "status": "Active"
        })

        for rule in access_rules:
            try:
                rule_doc = frappe.get_doc("Access Rule", rule.name)
                rule_doc.status = "Expired"
                rule_doc.save()
            except Exception as e:
                frappe.log_error(f"Error revoking access: {str(e)}", "Booking Access Revoke Error")

    def _create_access_log(self, event_type):
        """Create Access Log entry for check-in/check-out"""
        try:
            member = frappe.get_doc("Member", self.member)

            log = frappe.new_doc("Access Log")
            log.member = self.member
            log.zk_user_id = member.zk_user_id
            log.event_type = event_type
            log.event_time = frappe.utils.now_datetime()
            log.context_type = "Booking"
            log.context_name = self.name
            if self.location:
                log.location = self.location
            if self.space:
                space = frappe.get_doc("Space", self.space)
                if space.access_device:
                    log.device = space.access_device

            log.insert(ignore_permissions=True)

        except Exception as e:
            frappe.log_error(f"Error creating access log: {str(e)}", "Access Log Creation Error")

    def _create_invoice(self):
        """Create Sales Invoice for the booking"""
        try:
            # Get member's customer
            member = frappe.get_doc("Member", self.member)
            if not member.customer:
                frappe.msgprint(_("Member has no linked Customer. Invoice not created."), indicator="orange", alert=True)
                return

            # Create Sales Invoice
            invoice = frappe.new_doc("Sales Invoice")
            invoice.customer = member.customer
            invoice.posting_date = frappe.utils.nowdate()
            invoice.due_date = frappe.utils.add_days(frappe.utils.nowdate(), 7)

            # Add booking charge
            invoice.append("items", {
                "item_code": "Coworking Space Booking",
                "item_name": f"Booking - {self.space}",
                "description": f"Booking for {self.booking_date} from {self.start_time} to {self.end_time}",
                "qty": 1,
                "rate": self.total_amount,
                "amount": self.total_amount
            })

            invoice.insert(ignore_permissions=True)
            frappe.msgprint(_("Sales Invoice {0} created").format(invoice.name), indicator="green", alert=True)

        except Exception as e:
            frappe.log_error(f"Error creating invoice for booking {self.name}: {str(e)}", "Invoice Creation Error")

    def _send_confirmation_email(self):
        """Send booking confirmation email"""
        try:
            member = frappe.get_doc("Member", self.member)
            if member.primary_email:
                frappe.sendmail(
                    recipients=[member.primary_email],
                    subject=f"Booking Confirmation - {self.name}",
                    message=f"""
                    <p>Dear {member.member_name},</p>
                    <p>Your booking has been confirmed:</p>
                    <ul>
                        <li>Space: {self.space}</li>
                        <li>Date: {self.booking_date}</li>
                        <li>Time: {self.start_time} to {self.end_time}</li>
                        <li>Total Amount: {self.total_amount}</li>
                    </ul>
                    <p>Thank you!</p>
                    """
                )
        except Exception as e:
            frappe.log_error(f"Error sending confirmation email: {str(e)}", "Booking Confirmation Email Error")

    def _update_member_last_visit(self):
        """Update member's last visit date"""
        try:
            member = frappe.get_doc("Member", self.member)
            member.last_visit_date = frappe.utils.nowdate()
            member.save()
        except Exception as e:
            frappe.log_error(f"Error updating member last visit: {str(e)}", "Member Update Error")

