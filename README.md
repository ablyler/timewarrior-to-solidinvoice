# Overview
Currently this script will take the output from timewarrior and generate json that can be used to POST to the `/api/invoices` API endpoint to create an invoice.

# Example usage
`timew export from 2024-09-22 for 1wks | python main.py --client_id 7a7be599-9b04-433b-9241-8e11db5bcc3c --contact_id 964dd5aa-d652-4d03-b1f2-c8fc8196a855 --price_per_hour 20`
