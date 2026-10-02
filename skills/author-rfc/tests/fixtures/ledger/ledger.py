"""Observed fixture baseline; design tasks leave this module unchanged."""
import csv

DEFAULT_TIMEOUT_SECONDS = 45


def export(entries, output):
    with open(output, 'w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['account', 'amount'])
        for entry in entries:
            writer.writerow([entry['account'], entry['amount']])
