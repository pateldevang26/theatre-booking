import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime, now


class Booking(Document):
	def before_insert(self):
		self.booking_datetime = now_datetime()

	def validate(self):
		self.validate_seats_not_empty()
		self.validate_no_duplicate_seats_in_this_booking()
		self.show_doc = frappe.get_doc("Show", self.show)
		self.validate_show_is_scheduled()
		self.validate_show_not_in_past()
		self.validate_seats_not_already_booked()
		self.calculate_total_amount()

	def validate_seats_not_empty(self):
		if not self.seats:
			frappe.throw("Please select at least one seat.")

	def validate_no_duplicate_seats_in_this_booking(self):
		seat_numbers = [row.seat_number for row in self.seats]
		if len(seat_numbers) != len(set(seat_numbers)):
			frappe.throw("Duplicate seat numbers are not allowed in the same booking.")

	def validate_show_is_scheduled(self):
		if self.show_doc.status != "Scheduled":
			frappe.throw(f"Cannot book seats for a show that is {self.show_doc.status}.")

	def validate_show_not_in_past(self):
		# Strip any timezone info from both sides before comparing. Frappe's
		# datetime helpers can inconsistently return naive or timezone-aware
		# values depending on site settings, so we force both to naive here
		# rather than relying on now_datetime()/get_datetime() to already agree.
		show_datetime = get_datetime(
			f"{self.show_doc.show_date} {self.show_doc.show_time}"
		).replace(tzinfo=None)
		current_datetime = get_datetime(now()).replace(tzinfo=None)
		if show_datetime < current_datetime:
			frappe.throw("Cannot book seats for a show that has already passed.")

	def validate_seats_not_already_booked(self):
		existing_bookings = frappe.get_all(
			"Booking",
			filters={
				"show": self.show,
				"status": "Confirmed",
				"name": ["!=", self.name or ""],
			},
			pluck="name",
		)

		already_booked_seats = set()
		for booking_name in existing_bookings:
			rows = frappe.get_all(
				"Booking Seat",
				filters={"parent": booking_name},
				pluck="seat_number",
			)
			already_booked_seats.update(rows)

		for row in self.seats:
			if row.seat_number in already_booked_seats:
				frappe.throw(f"Seat {row.seat_number} is already booked for this show.")

	def calculate_total_amount(self):
		self.total_amount = len(self.seats) * self.show_doc.price_per_seat
