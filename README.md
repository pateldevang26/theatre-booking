# Theatre Booking

A Frappe app for managing theatre shows and seat bookings.

## Overview

This app lets an admin schedule movie shows on specific screens, and book
seats for those shows on behalf of customers. It does not handle payment.

## Data Model

**Screen**
A physical theatre screen/hall. Reusable across many shows.
- Screen Name (unique)
- Total Seats

**Show**
A single scheduled screening of a movie on a Screen.
- Movie Name
- Screen (link to Screen)
- Show Date
- Show Time (datetime)
- Price Per Seat
- Status (Scheduled / Cancelled / Completed)

**Booking**
A booking transaction for a customer against a Show.
- Show (link to Show)
- Customer Name
- Customer Phone
- Booking Datetime (auto-set on creation)
- Status (Confirmed / Cancelled)
- Seats (child table of Booking Seat)
- Total Amount (auto-calculated: seats x Show's Price Per Seat)

**Booking Seat** (child table of Booking)
- Seat Number

### Design notes

Screen is kept separate from Show because a screen is reused across many
shows - storing seat count on Show itself would duplicate that data every
time a new show is scheduled on the same screen.

Seats are stored in a child table (Booking Seat) rather than a
comma-separated text field on Booking, so individual seat numbers can be
queried and validated directly, instead of parsing a string every time.

A standalone Seat master doctype (pre-creating every seat as its own
record) was considered and rejected - seat numbers are just labels here,
not entities with their own lifecycle or pricing tiers. That would be
worth revisiting if the app needed per-seat pricing (e.g. VIP seats).

## Validations

On Show:
- Show Time cannot be in the past.

On Booking:
- Customer Phone must be exactly 10 digits.
- At least one seat must be selected.
- No duplicate seat numbers within the same booking.
- The linked Show must have status "Scheduled".
- The linked Show's time cannot be in the past (checked again here as
  defense in depth - a Show can be created validly in the future and
  still be "Scheduled" once its time has actually passed).
- A seat cannot be booked twice for the same Show across different
  Confirmed bookings.
- Total Amount is auto-calculated on save (seats x Show's price), not
  user-enterable.

## Viewing today's shows

The Show list view has "Show Date" enabled as both a list column and a
list filter, so shows can be filtered down to the current date directly
from the list view UI.

## Not implemented

Payment handling is out of scope per the task requirements.
