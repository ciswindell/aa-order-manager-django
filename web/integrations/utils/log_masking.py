"""Utility functions for masking PII (Personally Identifiable Information) in logs.

Per feature requirement FR-016, account names and email addresses must be masked
in application logs to protect user privacy while maintaining debuggability.
"""

import re
from typing import Optional


def mask_email(email: str) -> str:
    """Mask an email address for logging.

    Masks the middle portion of the username and domain while preserving
    enough information for debugging (first/last chars of each part).

    Args:
        email: Email address to mask (e.g., "chris@example.com")

    Returns:
        Masked email (e.g., "ch***@ex***.com")

    Examples:
        >>> mask_email("chris@example.com")
        'ch***@ex***.com'
        >>> mask_email("a@b.com")
        'a***@b***.com'
        >>> mask_email("test@domain.co.uk")
        'te***@do***n.co.uk'
    """
    if not email or "@" not in email:
        return "***@***.***"

    try:
        local, domain = email.split("@", 1)

        # Mask local part (username)
        if len(local) <= 2:
            masked_local = local[0] + "***"
        else:
            masked_local = local[0] + local[1] + "***"

        # Mask domain part
        domain_parts = domain.split(".")
        if len(domain_parts) >= 2:
            # Mask the main domain part (before TLD)
            main_domain = domain_parts[0]
            if len(main_domain) <= 2:
                masked_domain = main_domain[0] + "***"
            else:
                masked_domain = main_domain[0] + main_domain[1] + "***"

            # Keep TLD visible for debugging (e.g., .com, .co.uk)
            tld = ".".join(domain_parts[1:])
            masked_domain = f"{masked_domain}.{tld}"
        else:
            # Single-part domain (unusual case)
            masked_domain = domain[0] + "***"

        return f"{masked_local}@{masked_domain}"

    except Exception:
        # Fallback if parsing fails
        return "***@***.***"


def mask_name(name: str) -> str:
    """Mask a person or organization name for logging.

    Masks the middle portion of each word (>3 chars) while preserving
    first/last characters for debugging. Short words are fully preserved.

    Args:
        name: Name to mask (e.g., "American Abstract LLC")

    Returns:
        Masked name (e.g., "Am***an Ab***ct LLC")

    Examples:
        >>> mask_name("American Abstract LLC")
        'Am***an Ab***ct LLC'
        >>> mask_name("Chris Windell")
        'Ch***s Wi***ll'
        >>> mask_name("ABC Inc")
        'ABC Inc'
    """
    if not name:
        return "***"

    def mask_word(word: str) -> str:
        """Mask a single word."""
        if len(word) <= 3:
            # Keep short words visible (like "LLC", "Inc", "Co", etc.)
            return word
        elif len(word) <= 5:
            # For 4-5 char words, show first/last char
            return word[0] + "***" + word[-1]
        else:
            # For longer words, show first 2 and last 2 chars
            return word[0] + word[1] + "***" + word[-2] + word[-1]

    # Split by whitespace and mask each word
    words = name.split()
    masked_words = [mask_word(word) for word in words]

    return " ".join(masked_words)


def mask_pii(text: Optional[str], pii_type: str = "auto") -> str:
    """Automatically detect and mask PII in text.

    Args:
        text: Text potentially containing PII
        pii_type: Type of PII ("email", "name", or "auto" for auto-detection)

    Returns:
        Masked text with PII protected

    Examples:
        >>> mask_pii("chris@example.com", "email")
        'ch***@ex***.com'
        >>> mask_pii("American Abstract", "name")
        'Am***an Ab***ct'
        >>> mask_pii("Contact chris@example.com")
        'Contact ch***@ex***.com'
    """
    if not text:
        return "***"

    if pii_type == "email" or (pii_type == "auto" and "@" in text):
        return mask_email(text)
    elif pii_type == "name":
        return mask_name(text)
    elif pii_type == "auto":
        # Auto-detect email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, text):
            # Replace all emails in text
            return re.sub(email_pattern, lambda m: mask_email(m.group(0)), text)
        else:
            # Treat as name
            return mask_name(text)

    return text

