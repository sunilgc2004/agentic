import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List


class TestDataGenerator:
    """Generates synthetic, safe test data and negative test payloads."""

    FIRST_NAMES = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley"]
    LAST_NAMES = ["Smith", "Doe", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis"]
    DOMAINS = ["qa-test.example.com", "synthetic-qa.internal", "mock-sandbox.test"]

    @classmethod
    def generate_name(cls) -> str:
        return f"{random.choice(cls.FIRST_NAMES)} {random.choice(cls.LAST_NAMES)}"

    @classmethod
    def generate_email(cls, prefix: str = "qa.user") -> str:
        unique_id = uuid.uuid4().hex[:6]
        domain = random.choice(cls.DOMAINS)
        return f"{prefix}.{unique_id}@{domain}"

    @classmethod
    def generate_phone(cls) -> str:
        return f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

    @classmethod
    def generate_case_number(cls) -> str:
        year = datetime.utcnow().year
        return f"ARB-{year}-{random.randint(10000, 99999)}"

    @classmethod
    def generate_date(cls, days_in_future: int = 7) -> str:
        target = datetime.utcnow() + timedelta(days=days_in_future)
        return target.strftime("%Y-%m-%d")

    @classmethod
    def generate_random_string(cls, length: int = 12) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    @classmethod
    def generate_dataset(cls, template: Dict[str, str] = None) -> Dict[str, Any]:
        """Generates a complete suite of synthetic inputs for common form fields."""
        return {
            "name": cls.generate_name(),
            "claimant_name": f"Claimant {cls.generate_name()}",
            "respondent_name": f"Respondent {cls.generate_name()}",
            "email": cls.generate_email(),
            "phone": cls.generate_phone(),
            "case_number": cls.generate_case_number(),
            "dispute_amount": str(random.randint(5000, 250000)),
            "date": cls.generate_date(),
            "description": "Standard synthetic dispute verification case created by Autonomous QA Agent.",
        }

    @classmethod
    def get_negative_payloads(cls) -> Dict[str, List[Any]]:
        """Returns standard negative and boundary test values."""
        return {
            "empty": [""],
            "whitespace": ["   "],
            "invalid_email": [
                "plainaddress",
                "@missingusername.com",
                "username@.com",
                "user@domain..com",
                "user space@domain.com"
            ],
            "invalid_phone": [
                "123",
                "phone-number-letters",
                "++199999999999999999999999"
            ],
            "boundary_numbers": [
                "-1",
                "-99999999",
                "0",
                "99999999999999999999999999999999"
            ],
            "sql_injection_payloads": [
                "' OR '1'='1",
                "admin' --",
                "1; DROP TABLE users;--"
            ],
            "xss_test_payloads": [
                "<script>alert(1)</script>",
                "\"><svg onload=alert(1)>"
            ],
            "overflow_string": [
                "A" * 1000,
                "B" * 5000
            ],
            "special_characters": [
                "!@#$%^&*()_+~`|}{[]:;?><,./",
                "¥§©®¶™"
            ]
        }
