import frappe
from frappe.model.document import Document

class BookingService(Document):
    def validate(self):
        self.amount = (self.qty or 0) * (self.rate or 0)
