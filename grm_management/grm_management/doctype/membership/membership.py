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
        self.access_remaining = (self.total_access_allowed or 0) - (self.access_used or 0) + (self.rollover_from_previous or 0)
        self.last_access_date = frappe.utils.nowdate()
        self.save()
        return True

    @frappe.whitelist()
    def activate(self):
        """Activate membership - create Access Rule, create invoice"""
        if self.status != 'Draft':
            frappe.throw(_("Only Draft memberships can be activated"))

        # Validate package is Active
        package = frappe.get_doc("Package", self.package)
        if package.status != 'Active':
            frappe.throw(_("Package {0} is not active").format(package.package_name))

        # Set status to Active
        self.status = 'Active'

        # Reset counters and add rollover
        self.access_used = 0
        self.access_remaining = (self.total_access_allowed or 0) + (self.rollover_from_previous or 0)

        self.save()

        # Create Access Rule
        self._create_access_rule()

        # Create Sales Invoice
        self._create_invoice()

        # Update member statistics
        self._update_member_stats()

        frappe.msgprint(_("Membership activated successfully"), indicator="green", alert=True)

    @frappe.whitelist()
    def pause(self, reason=None):
        """Pause membership - suspend Access Rule"""
        if self.status != 'Active':
            frappe.throw(_("Only Active memberships can be paused"))

        self.status = 'Paused'
        self.pause_start = frappe.utils.nowdate()
        if reason:
            self.pause_reason = reason

        self.save()

        # Suspend Access Rule
        self._suspend_access_rule()

        frappe.msgprint(_("Membership paused"), indicator="orange", alert=True)

    @frappe.whitelist()
    def resume(self):
        """Resume paused membership - reactivate Access Rule, extend end_date by pause duration"""
        if self.status != 'Paused':
            frappe.throw(_("Only Paused memberships can be resumed"))

        # Calculate pause duration
        if self.pause_start and not self.pause_end:
            self.pause_end = frappe.utils.nowdate()

        if self.pause_start and self.pause_end:
            pause_days = (frappe.utils.getdate(self.pause_end) - frappe.utils.getdate(self.pause_start)).days
            # Extend end_date by pause duration
            self.end_date = frappe.utils.add_days(self.end_date, pause_days)

        self.status = 'Active'
        self.save()

        # Reactivate Access Rule
        self._reactivate_access_rule()

        frappe.msgprint(_("Membership resumed. End date extended by {0} days").format(pause_days if self.pause_start and self.pause_end else 0), indicator="green", alert=True)

    @frappe.whitelist()
    def renew(self):
        """Create new Membership for renewal with rollover calculation"""
        if self.status not in ['Active', 'Expired']:
            frappe.throw(_("Only Active or Expired memberships can be renewed"))

        # Calculate rollover - unused access
        rollover = self._calculate_rollover()

        # Create new membership
        new_membership = frappe.new_doc("Membership")
        new_membership.member = self.member
        new_membership.package = self.package
        new_membership.status = 'Draft'
        new_membership.start_date = frappe.utils.add_days(self.end_date, 1)

        # Calculate end_date based on package billing cycle
        package = frappe.get_doc("Package", self.package)
        if package.billing_cycle == 'Monthly':
            new_membership.end_date = frappe.utils.add_months(new_membership.start_date, 1)
        elif package.billing_cycle == 'Quarterly':
            new_membership.end_date = frappe.utils.add_months(new_membership.start_date, 3)
        elif package.billing_cycle == 'Semi-Annual':
            new_membership.end_date = frappe.utils.add_months(new_membership.start_date, 6)
        elif package.billing_cycle == 'Annual':
            new_membership.end_date = frappe.utils.add_months(new_membership.start_date, 12)
        else:
            new_membership.end_date = frappe.utils.add_months(new_membership.start_date, 1)

        # Set rollover
        new_membership.rollover_from_previous = rollover

        # Link to previous membership
        new_membership.renewed_from = self.name
        new_membership.insert()

        # Update current membership
        self.renewed_to = new_membership.name
        self.save()

        frappe.msgprint(_("Renewal membership {0} created with {1} rollover units").format(new_membership.name, rollover), indicator="green", alert=True)

        return new_membership.name

    @frappe.whitelist()
    def expire(self):
        """Expire membership when end_date is reached - called by scheduler"""
        if self.status != 'Active':
            return

        if frappe.utils.getdate(frappe.utils.nowdate()) > frappe.utils.getdate(self.end_date):
            self.status = 'Expired'
            self.save()

            # Deactivate Access Rule
            self._deactivate_access_rule()

            # Send renewal reminder
            self._send_renewal_reminder()

            # Update member statistics
            self._update_member_stats()

            frappe.msgprint(_("Membership expired"), indicator="orange", alert=True)

    def _calculate_rollover(self):
        """Calculate unused access for transfer to renewal"""
        if self.access_type == 'Unlimited':
            return 0

        # Rollover = Total Allowed - Used + Previous Rollover
        rollover = (self.total_access_allowed or 0) - (self.access_used or 0) + (self.rollover_from_previous or 0)
        return max(0, rollover)  # Don't return negative

    def _create_access_rule(self):
        """Create Access Rule for this membership"""
        try:
            # Get package to check allowed locations
            package = frappe.get_doc("Package", self.package)

            access_rule = frappe.new_doc("Access Rule")
            access_rule.rule_type = "Membership"
            access_rule.reference_type = "Membership"
            access_rule.reference_name = self.name
            access_rule.member = self.member
            access_rule.valid_from = self.start_date
            access_rule.valid_until = self.end_date
            access_rule.status = "Active"

            # Set access type
            access_rule.access_type = self.access_type

            # Add devices from allowed locations in package
            if package.allowed_locations:
                for loc_row in package.allowed_locations:
                    # Get all access devices at this location
                    spaces = frappe.get_all("Space", filters={"location": loc_row.location}, fields=["access_device"])
                    for space in spaces:
                        if space.access_device:
                            access_rule.append("devices", {
                                "access_device": space.access_device
                            })

            access_rule.insert(ignore_permissions=True)

        except Exception as e:
            frappe.log_error(f"Error creating access rule for membership {self.name}: {str(e)}", "Membership Access Rule Error")

    def _suspend_access_rule(self):
        """Suspend Access Rule temporarily"""
        access_rules = frappe.get_all("Access Rule", filters={
            "reference_type": "Membership",
            "reference_name": self.name,
            "status": "Active"
        })

        for rule in access_rules:
            try:
                rule_doc = frappe.get_doc("Access Rule", rule.name)
                rule_doc.status = "Suspended"
                rule_doc.save()
            except Exception as e:
                frappe.log_error(f"Error suspending access rule {rule.name}: {str(e)}", "Access Rule Suspension Error")

    def _reactivate_access_rule(self):
        """Reactivate suspended Access Rule"""
        access_rules = frappe.get_all("Access Rule", filters={
            "reference_type": "Membership",
            "reference_name": self.name,
            "status": "Suspended"
        })

        for rule in access_rules:
            try:
                rule_doc = frappe.get_doc("Access Rule", rule.name)
                rule_doc.status = "Active"
                rule_doc.valid_until = self.end_date  # Update with extended end date
                rule_doc.save()
            except Exception as e:
                frappe.log_error(f"Error reactivating access rule {rule.name}: {str(e)}", "Access Rule Reactivation Error")

    def _deactivate_access_rule(self):
        """Deactivate Access Rule"""
        access_rules = frappe.get_all("Access Rule", filters={
            "reference_type": "Membership",
            "reference_name": self.name,
            "status": ["in", ["Active", "Suspended"]]
        })

        for rule in access_rules:
            try:
                rule_doc = frappe.get_doc("Access Rule", rule.name)
                rule_doc.status = "Expired"
                rule_doc.save()
            except Exception as e:
                frappe.log_error(f"Error deactivating access rule {rule.name}: {str(e)}", "Access Rule Deactivation Error")

    def _create_invoice(self):
        """Create Sales Invoice for the membership"""
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

            # Add membership as item
            invoice.append("items", {
                "item_code": "Coworking Membership",  # Standard Item
                "item_name": f"Membership {self.membership_number}",
                "description": f"Membership package for {self.package}",
                "qty": 1,
                "rate": self.final_price,
                "amount": self.final_price
            })

            invoice.insert(ignore_permissions=True)
            frappe.msgprint(_("Sales Invoice {0} created").format(invoice.name), indicator="green", alert=True)

        except Exception as e:
            frappe.log_error(f"Error creating invoice for membership {self.name}: {str(e)}", "Invoice Creation Error")

    def _update_member_stats(self):
        """Update member statistics"""
        try:
            member = frappe.get_doc("Member", self.member)
            if hasattr(member, 'update_statistics'):
                member.update_statistics()
        except Exception as e:
            frappe.log_error(f"Error updating member statistics: {str(e)}", "Member Stats Update Error")

    def _send_renewal_reminder(self):
        """Send renewal reminder email"""
        try:
            member = frappe.get_doc("Member", self.member)
            if member.primary_email:
                frappe.sendmail(
                    recipients=[member.primary_email],
                    subject=f"Membership {self.membership_number} has expired",
                    message=f"""
                    <p>Dear {member.member_name},</p>
                    <p>Your membership {self.membership_number} has expired as of {self.end_date}.</p>
                    <p>Please contact us to renew your membership.</p>
                    <p>Thank you.</p>
                    """
                )
                self.renewal_reminder_sent = 1
                self.save()
        except Exception as e:
            frappe.log_error(f"Error sending renewal reminder: {str(e)}", "Membership Renewal Reminder Error")
