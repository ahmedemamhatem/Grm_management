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
