# Movie Ticket Booking Web App

## Introduction
This repository contains a web application built using Django and PostgreSQL, designed for users to browse available movies, purchase tickets, and manage their bookings.

## Features
- Users can search for movies, filtering based on different criteria.
- Users can leave messages on the site; the format is validated before being saved locally as a JSON file.
- Admin users can add new movies to the database. When adding a movie, they can provide an IMDb link to automatically fetch some movie details, along with an image URL for the banner.
- Users can create an account, log in, and log out. They can also view their profile information.
- Users receive a custom confirmation email after account creation, which they must access before logging in.
- Admins can create new promotions for different movie categories. Users automatically receive custom emails about new promotions based on their last five accessed movies on the site.
- Suspicious behavior on the site is automatically emailed to admins.
- A custom logging system tracks important events.
- A random banner may appear for logged-in users, offering a 50% discount on their next purchase.
- **Scheduled tasks** (executed via `run_tasks.py`):
  - Remove unconfirmed accounts weekly.
  - Send a newsletter to users every week.
  - Generate a new randomized movie schedule for all cinemas daily.
  - Remind admins to check unread user messages.
- A virtual shopping cart stores tickets users want to purchase. At checkout, users can see all items in the cart, sorted according to various filters, and view applicable promotional discounts.
- When a user buys tickets, a PDF receipt with purchase details is generated and emailed to them. PDFs are also saved under `temporar-facturi/` and the username of the buyer.

---
