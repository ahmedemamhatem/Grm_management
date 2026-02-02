import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime

class GRMContract(Document):
    def before_insert(self):
        # set created_by and creation_date
        self.created_by = frappe.session.user
        self.creation_date = frappe.utils.nowdate()

    def validate(self):
        self._validate_dates()
        self._validate_spaces()
        self._compute_duration()
        self._compute_financials()
        self._expire_if_needed()

    def _validate_dates(self):
        if self.end_date < self.start_date:
            frappe.throw(_("End Date must be the same as or after Start Date"))

    def _validate_spaces(self):
        total = 0
        for r in self.spaces or []:
            if r.from_date and r.to_date:
                if r.from_date < self.start_date or r.to_date > self.end_date:
                    frappe.throw(_("Space row dates must be within contract start and end dates"))
                if r.from_date > r.to_date:
                    frappe.throw(_("Space row From Date must be before or equal to To Date"))
            # check for overlapping ACTIVE contracts
            if self.status == 'Active':
                from_date = r.from_date or self.start_date
                to_date = r.to_date or self.end_date
                if check_space_conflicts(r.space, from_date, to_date, self.name):
                    frappe.throw(_("Space {0} has conflicting active contracts in the specified period").format(r.space))
            total += (r.monthly_rent or 0)
        # set monthly_rent to sum if not provided
        if total and (not self.monthly_rent or self.monthly_rent==0):
            self.monthly_rent = total

    def _compute_duration(self):
        try:
            sd = frappe.utils.getdate(self.start_date)
            ed = frappe.utils.getdate(self.end_date)
            months = (ed.year - sd.year) * 12 + (ed.month - sd.month)
            self.duration_months = months if months>0 else 0
        except Exception:
            self.duration_months = 0

    def _compute_financials(self):
        self.discount_amount = (self.discount_percent or 0) * (self.monthly_rent or 0) / 100.0
        self.net_monthly_rent = (self.monthly_rent or 0) - (self.discount_amount or 0)

    def _expire_if_needed(self):
        if self.status == 'Active' and frappe.utils.getdate(frappe.utils.nowdate()) > frappe.utils.getdate(self.end_date):
            self.status = 'Expired'
            frappe.msgprint(_('Contract has been marked Expired as end date passed'))


    @frappe.whitelist()
    def approve(self):
        """Approve contract - set status to Active, occupy spaces, create access rules, create invoice"""
        if self.status != 'Draft':
            frappe.throw(_("Only Draft contracts can be approved"))

        # Validate all spaces are available
        self._validate_spaces_available()

        # Set status to Active
        self.status = 'Active'
        self.save()

        # Occupy all spaces
        self._occupy_spaces()

        # Create Access Rules for granted users
        self._create_access_rules()

        # Create Sales Invoice
        self._create_invoice()

        # Update member statistics
        self._update_member_stats()

        frappe.msgprint(_("Contract approved and activated successfully"), indicator="green", alert=True)

    @frappe.whitelist()
    def reject(self, reason=None):
        """Reject contract - set status to Cancelled, release spaces"""
        if self.status != 'Draft':
            frappe.throw(_("Only Draft contracts can be rejected"))

        self.status = 'Cancelled'
        self.termination_reason = 'Breach'
        self.termination_date = frappe.utils.nowdate()
        if reason:
            self.termination_notes = f"Rejected: {reason}"

        self.save()

        # Release any reserved spaces
        self._release_spaces()

        frappe.msgprint(_("Contract rejected"), indicator="red", alert=True)

    @frappe.whitelist()
    def terminate(self, reason=None):
        """Terminate active contract - release spaces, deactivate access"""
        if self.status not in ['Active']:
            frappe.throw(_("Only Active contracts can be terminated"))

        self.status = 'Terminated'
        self.termination_date = frappe.utils.nowdate()
        if reason:
            self.termination_notes = reason

        # Calculate early termination fee if applicable
        if frappe.utils.getdate(self.termination_date) < frappe.utils.getdate(self.end_date):
            months_remaining = (frappe.utils.getdate(self.end_date).year - frappe.utils.getdate(self.termination_date).year) * 12 + \
                             (frappe.utils.getdate(self.end_date).month - frappe.utils.getdate(self.termination_date).month)
            if months_remaining > 0:
                # Early termination fee could be 1 month rent or custom
                self.early_termination_fee = self.net_monthly_rent

        self.save()

        # Release spaces
        self._release_spaces()

        # Deactivate Access Rules
        self._deactivate_access_rules()

        # Update member statistics
        self._update_member_stats()

        frappe.msgprint(_("Contract terminated successfully"), indicator="orange", alert=True)

    @frappe.whitelist()
    def expire(self):
        """Expire contract when end_date is reached - called by scheduler"""
        if self.status != 'Active':
            return

        if frappe.utils.getdate(frappe.utils.nowdate()) > frappe.utils.getdate(self.end_date):
            self.status = 'Expired'
            self.save()

            # Release spaces
            self._release_spaces()

            # Deactivate Access Rules
            self._deactivate_access_rules()

            # Send notification to member
            self._send_expiry_notification()

            # Update member statistics
            self._update_member_stats()

            frappe.msgprint(_("Contract expired"), indicator="orange", alert=True)

    def _validate_spaces_available(self):
        """Check all spaces are Available or Reserved"""
        for row in self.spaces or []:
            space = frappe.get_doc("Space", row.space)
            if space.status not in ['Available', 'Reserved']:
                frappe.throw(_("Space {0} is not available (current status: {1})").format(space.space_name, space.status))

    def _occupy_spaces(self):
        """Set all contract spaces to Occupied"""
        for row in self.spaces or []:
            try:
                space = frappe.get_doc("Space", row.space)
                space.set_occupied(self.member, self.name)
            except Exception as e:
                frappe.log_error(f"Error occupying space {row.space}: {str(e)}", "Contract Approval Error")

    def _release_spaces(self):
        """Release all contract spaces to Available"""
        for row in self.spaces or []:
            try:
                space = frappe.get_doc("Space", row.space)
                if space.current_contract == self.name:
                    space.set_available()
            except Exception as e:
                frappe.log_error(f"Error releasing space {row.space}: {str(e)}", "Contract Release Error")

    def _create_access_rules(self):
        """Create Access Rules for each granted user"""
        for user_row in self.granted_users or []:
            if not user_row.access_granted:
                continue

            try:
                # Create Access Rule
                access_rule = frappe.new_doc("Access Rule")
                access_rule.rule_type = "Contract"
                access_rule.reference_type = "GRM Contract"
                access_rule.reference_name = self.name
                access_rule.member = self.member
                access_rule.member_user = user_row.member_user
                access_rule.valid_from = self.start_date
                access_rule.valid_until = self.end_date
                access_rule.status = "Active"

                # Set access times
                if self.access_24_7:
                    access_rule.access_24_7 = 1
                else:
                    access_rule.access_start_time = self.access_start_time
                    access_rule.access_end_time = self.access_end_time

                # Add devices from spaces
                for space_row in self.spaces or []:
                    space = frappe.get_doc("Space", space_row.space)
                    if space.access_device:
                        access_rule.append("devices", {
                            "access_device": space.access_device
                        })

                access_rule.insert(ignore_permissions=True)

                # Update sync status
                user_row.zk_synced = 1
                user_row.sync_date = frappe.utils.now()

            except Exception as e:
                frappe.log_error(f"Error creating access rule for user {user_row.member_user}: {str(e)}", "Access Rule Creation Error")

    def _deactivate_access_rules(self):
        """Deactivate all Access Rules for this contract"""
        access_rules = frappe.get_all("Access Rule", filters={
            "reference_type": "GRM Contract",
            "reference_name": self.name,
            "status": "Active"
        })

        for rule in access_rules:
            try:
                rule_doc = frappe.get_doc("Access Rule", rule.name)
                rule_doc.status = "Expired"
                rule_doc.save()
            except Exception as e:
                frappe.log_error(f"Error deactivating access rule {rule.name}: {str(e)}", "Access Rule Deactivation Error")

    def _create_invoice(self):
        """Create Sales Invoice for the contract"""
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
            invoice.due_date = frappe.utils.add_days(frappe.utils.nowdate(), 30)

            # Add contract rent as item
            invoice.append("items", {
                "item_code": "Coworking Space Rent",  # This should be a standard Item
                "item_name": f"Contract {self.contract_number} - Monthly Rent",
                "description": f"Monthly rent for contract {self.contract_number}",
                "qty": 1,
                "rate": self.net_monthly_rent,
                "amount": self.net_monthly_rent
            })

            invoice.insert(ignore_permissions=True)
            frappe.msgprint(_("Sales Invoice {0} created").format(invoice.name), indicator="green", alert=True)

        except Exception as e:
            frappe.log_error(f"Error creating invoice for contract {self.name}: {str(e)}", "Invoice Creation Error")
            frappe.msgprint(_("Error creating invoice. Please create manually."), indicator="orange", alert=True)

    def _update_member_stats(self):
        """Update member statistics"""
        try:
            member = frappe.get_doc("Member", self.member)
            if hasattr(member, 'update_statistics'):
                member.update_statistics()
        except Exception as e:
            frappe.log_error(f"Error updating member statistics: {str(e)}", "Member Stats Update Error")

    def _send_expiry_notification(self):
        """Send email notification when contract expires"""
        try:
            member = frappe.get_doc("Member", self.member)
            if member.primary_email:
                frappe.sendmail(
                    recipients=[member.primary_email],
                    subject=f"Contract {self.contract_number} has expired",
                    message=f"""
                    <p>Dear {member.member_name},</p>
                    <p>Your contract {self.contract_number} has expired as of {self.end_date}.</p>
                    <p>Please contact us if you wish to renew.</p>
                    <p>Thank you.</p>
                    """
                )
        except Exception as e:
            frappe.log_error(f"Error sending expiry notification: {str(e)}", "Contract Expiry Notification Error")


def check_space_conflicts(space, from_date, to_date, exclude_contract_name=None):
    # look for Contracts with status Active where overlapping dates exist
    if not space:
        return False
    filters = [
        ["Contract Space","space","=", space],
        ["Contract","status","in", ["Active"]],
        ["Contract","name","!=", exclude_contract_name or ""],
    ]
    # query Contract Space join Contract
    conflicts = frappe.db.sql("""
        SELECT cs.parent FROM `tabContract Space` cs
        JOIN `tabContract` c ON c.name=cs.parent
        WHERE cs.space=%s AND c.status='Active' AND c.name!=%s
        AND ( (c.start_date<=%s AND c.end_date>=%s) OR (cs.from_date<=%s AND cs.to_date>=%s) OR (cs.from_date IS NULL AND cs.to_date IS NULL AND c.start_date<=%s AND c.end_date>=%s) )
    """, (space, exclude_contract_name or '', from_date, to_date, from_date, to_date, from_date, to_date))
    return len(conflicts) > 0
