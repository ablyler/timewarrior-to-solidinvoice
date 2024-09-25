# Overview

This script generates invoices based on time tracking data exported from Timewarrior. It processes time entries, applies hourly rates, and creates or updates invoices in SolidInvoice via its API. The script reads JSON data from stdin and produces a formatted invoice that can either be displayed or sent directly to SolidInvoice for processing.

# Installation

1. Clone or download this repository.
2. Install the required dependencies (e.g., via pip): `pip install requests`

# Usage

The script is run from the command line and requires several arguments to operate. You need to provide the following details:

## Arguments

- `--client_id`: The client ID for whom the invoice is being generated.
- `--contact_id`: The ID of the contact at the client.
- `--price_per_hour`: The hourly rate (in dollars) to be applied to time entries.
- `--invoice_id`: (Optional) The ID of the invoice to replace. If not provided, a new invoice will be created.

Environment Variables

- `SOLIDINVOICE_BASE_URL`: Base URL for the SolidInvoice API (e.g., https://your-domain.com).
- `SOLIDINVOICE_API_TOKEN`: API token for authenticating requests to SolidInvoice.

# Example usage

`timew export from 2024-09-22 for 1wks | python main.py --client_id 7a7be599-9b04-433b-9241-8e11db5bcc3c --contact_id 964dd5aa-d652-4d03-b1f2-c8fc8196a855 --price_per_hour 20`

# License

This project is licensed under the MIT License.
