import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, now


class Show(Document):
	def validate(self):
		self.validate_show_time_not_in_past()

	def validate_show_time_not_in_past(self):
		show_datetime = get_datetime(self.show_time).replace(tzinfo=None)
		current_datetime = get_datetime(now()).replace(tzinfo=None)

		if show_datetime < current_datetime:
			frappe.throw("Show Time cannot be in the past.")
