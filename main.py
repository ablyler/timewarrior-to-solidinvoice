import argparse
import json
import os
import sys
from datetime import datetime

import pytz
import requests

# Set up argument parser
parser = argparse.ArgumentParser(
    description="Generate invoice from timewarrior export."
)
parser.add_argument("--client_id", required=True, help="ID of the client")
parser.add_argument(
    "--contact_id", required=True, help="ID of the contact at the client"
)
parser.add_argument(
    "--price_per_hour", type=float, required=True, help="Hourly rate in dollars"
)
parser.add_argument(
    "--invoice_id",
    help="ID of the invoice to replace, if none is provided a new invoice will be created",
)

# Parse arguments
args = parser.parse_args()

# Variables from command line arguments
client_id = args.client_id
contact_id = args.contact_id
price_per_hour = args.price_per_hour
invoice_id = args.invoice_id

# Read data from stdin
data = sys.stdin.read()

# Parse the input JSON
entries = json.loads(data)


# Function to calculate time difference in decimal hours
def calculate_hours(start, end):
    start_dt = datetime.strptime(start, "%Y%m%dT%H%M%SZ")
    end_dt = datetime.strptime(end, "%Y%m%dT%H%M%SZ")
    time_diff = end_dt - start_dt
    return time_diff.total_seconds() / 3600  # Convert seconds to hours


# Function to filter out tags that are single words and contain at least one period
def filter_tags(tags):
    return [tag for tag in tags if not ("." in tag and len(tag.split()) == 1)]


# Initialize a dictionary to store total hours per day and tag
work_log = {}

# Process each entry
for entry in entries:
    start = entry["start"]
    end = entry.get("end", None)  # Handle cases where 'end' might not exist

    # Parse the datetime strings
    start_dt = datetime.strptime(start, "%Y%m%dT%H%M%SZ")
    end_dt = datetime.strptime(end, "%Y%m%dT%H%M%SZ") if end else None

    # Convert to UTC timezone
    start_dt = start_dt.replace(tzinfo=pytz.utc)
    end_dt = end_dt.replace(tzinfo=pytz.utc) if end_dt else None

    # Convert to local timezone
    local_tz = datetime.now().astimezone().tzinfo
    start_local = start_dt.astimezone(local_tz)
    end_local = end_dt.astimezone(local_tz) if end_dt else None

    # Format the date as YYYYMMDD
    date = start_local.strftime("%Y%m%d")

    # Calculate hours if both start and end are present
    if end:
        total_hours = calculate_hours(start, end)
    else:
        total_hours = 0

    # Filter out the tags as per the requirement
    filtered_tags = filter_tags(entry["tags"])

    # Skip entries if all tags were filtered out
    if not filtered_tags:
        continue

    # Combine remaining tags into a single string for easier use in the output
    tags = ", ".join(filtered_tags)

    # Add to work log for each date and tag
    if date not in work_log:
        work_log[date] = {}

    if tags not in work_log[date]:
        work_log[date][tags] = 0

    work_log[date][tags] += total_hours

# Prepare the output JSON structure
output = {
    "@context": "/api/contexts/Invoice",
    "@type": "Invoice",
    "client": f"/api/clients/{client_id}",
    "items": [],
    "users": [f"/api/contacts/{contact_id}"],
    "status": "draft",
    "terms": None,
    "notes": None,
}

# Iterate through the work log and prepare the items
for date, tags in work_log.items():
    for tag, total_hours in tags.items():
        formatted_date = datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
        description = f"{formatted_date}: {tag}"
        item_total = round(total_hours * price_per_hour, 2)
        item = {
            "@type": "Item",
            "description": description,
            "price": f"{price_per_hour:.2f}",
            "qty": round(total_hours, 2),
            "tax": None,
        }
        output["items"].append(item)

# Retrieve base URL and API token from environment variables
base_url = os.getenv("SOLIDINVOICE_BASE_URL")
api_token = os.getenv("SOLIDINVOICE_API_TOKEN")

# Check if either the base URL or API token is not set
if not base_url or not api_token:
    print(json.dumps(output, indent=4))
else:
    # Determine if we are creating a new invoice or updating an existing one
    if "invoice_id" in locals() and invoice_id is not None:
        url = f"{base_url}/api/invoices/{invoice_id}"
        method = "PUT"
    else:
        url = f"{base_url}/api/invoices"
        method = "POST"

    # Set up headers
    headers = {
        "accept": "application/ld+json",
        "Content-Type": "application/ld+json",
        "X-API-TOKEN": api_token,
    }

    # Make the HTTP request
    response = requests.request(method, url, headers=headers, data=json.dumps(output))

    # Print the response from the server
    print(response.status_code)
    print(response.json())
