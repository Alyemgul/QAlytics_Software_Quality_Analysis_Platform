"""
utils/sample_data.py
Realistic sample dataset for demo purposes.
"""
from __future__ import annotations


def load_sample_data() -> dict:
    requirements = [
        {"id": "REQ-001", "text": "The system shall respond quickly to all user interactions."},
        {"id": "REQ-002", "text": "The login page must be user-friendly and intuitive."},
        {"id": "REQ-003", "text": "The system shall validate user input before processing."},
        {"id": "REQ-004", "text": "The application shall provide sufficient storage for user data."},
        {"id": "REQ-005", "text": "The API must handle sensor timeout errors gracefully and retry as needed."},
        {"id": "REQ-006", "text": "The system shall generate reports in PDF and CSV formats."},
        {"id": "REQ-007", "text": "The dashboard must display real-time data to users."},
        {"id": "REQ-008", "text": "All configuration settings shall be flexible and easy to modify."},
        {"id": "REQ-009", "text": "The system must always maintain data integrity and shall not corrupt records."},
        {"id": "REQ-010", "text": "The notification service shall send alerts to users when thresholds are exceeded."},
    ]

    test_cases = [
        {"id": "TC-001", "text": "Verify that form validation rejects empty required fields."},
        {"id": "TC-002", "text": "Test that input fields reject invalid formats such as non-numeric age."},
        {"id": "TC-003", "text": "Validate that sensor timeout triggers a retry after 3 seconds."},
        {"id": "TC-004", "text": "Verify API returns 503 when sensor is unavailable for more than 10 seconds."},
        {"id": "TC-005", "text": "Test PDF report generation with 100 records."},
        {"id": "TC-006", "text": "Verify CSV export contains all required columns."},
        {"id": "TC-007", "text": "Test notification alert is triggered when threshold exceeds defined limit."},
        {"id": "TC-008", "text": "Verify email notification is sent within 30 seconds of threshold breach."},
        {"id": "TC-009", "text": "Test that duplicate records are rejected by the database constraint."},
        {"id": "TC-010", "text": "Verify rollback occurs if a write transaction fails mid-operation."},
        {"id": "TC-011", "text": "Test dashboard auto-refreshes every 5 seconds with live data."},
        {"id": "TC-012", "text": "Verify login page renders correctly on mobile and desktop."},
        {"id": "TC-013", "text": "Test that configuration changes take effect without restarting the service."},
        {"id": "TC-014", "text": "Verify that response time under 50 concurrent users is below 2 seconds."},
        {"id": "TC-015", "text": "Test that user storage quota is enforced and exceeded quota is rejected."},
    ]

    bugs = [
        {"id": "BUG-001", "title": "Sensor timeout not handled", "description": "Sensor stops responding and no retry logic is triggered.", "severity": "HIGH"},
        {"id": "BUG-002", "title": "Login session expires silently", "description": "User session token expires without any notification to the user.", "severity": "MEDIUM"},
        {"id": "BUG-003", "title": "Dashboard data stale after refresh", "description": "Real-time data does not refresh correctly when navigating back to dashboard.", "severity": "MEDIUM"},
        {"id": "BUG-004", "title": "Sensor data drops under load", "description": "Sensor readings are lost when CPU load exceeds 80%.", "severity": "HIGH"},
        {"id": "BUG-005", "title": "CSV export missing columns", "description": "Exported CSV is missing the 'created_at' and 'status' columns.", "severity": "MEDIUM"},
        {"id": "BUG-006", "title": "Validation error message not shown", "description": "When user submits invalid input, no error message appears.", "severity": "LOW"},
        {"id": "BUG-007", "title": "Sensor reconnect fails after timeout", "description": "After a sensor timeout, the reconnect attempt does not succeed and requires manual restart.", "severity": "HIGH"},
        {"id": "BUG-008", "title": "Login fails on password reset flow", "description": "After resetting password, user cannot log in with the new credentials immediately.", "severity": "HIGH"},
        {"id": "BUG-009", "title": "Database deadlock during concurrent writes", "description": "Concurrent write operations cause occasional deadlocks.", "severity": "HIGH"},
        {"id": "BUG-010", "title": "PDF report generation crashes on large datasets", "description": "Generating PDF with over 500 records results in a memory exception.", "severity": "MEDIUM"},
        {"id": "BUG-011", "title": "Notification email delayed by 10+ minutes", "description": "Alert emails are not sent promptly when threshold is breached.", "severity": "MEDIUM"},
        {"id": "BUG-012", "title": "Sensor threshold ignored for Channel 3", "description": "Channel 3 sensor ignores the configured alert threshold.", "severity": "HIGH"},
        {"id": "BUG-013", "title": "UI button unresponsive after first click", "description": "The submit button becomes disabled after first click even on failure.", "severity": "LOW"},
        {"id": "BUG-014", "title": "Config changes require service restart", "description": "Modified configuration values are not picked up at runtime.", "severity": "MEDIUM"},
        {"id": "BUG-015", "title": "Login page layout broken on Safari", "description": "Login form fields overflow their container on Safari 16.", "severity": "LOW"},
        {"id": "BUG-016", "title": "API timeout error not retried", "description": "When the API times out, the client does not retry the request.", "severity": "MEDIUM"},
        {"id": "BUG-017", "title": "User data not saved on session expiry", "description": "In-progress data is lost when session expires without warning.", "severity": "HIGH"},
        {"id": "BUG-018", "title": "CSV import fails silently for malformed rows", "description": "Malformed rows in imported CSV are skipped without any error message.", "severity": "LOW"},
        {"id": "BUG-019", "title": "Sensor calibration data overwritten", "description": "New sensor calibration data overwrites existing data without a confirmation prompt.", "severity": "MEDIUM"},
        {"id": "BUG-020", "title": "Database connection pool exhausted under load", "description": "All DB connections are consumed during peak traffic, causing request failures.", "severity": "HIGH"},
    ]

    return {
        "requirements": requirements,
        "test_cases":   test_cases,
        "bugs":         bugs,
    }
