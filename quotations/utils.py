import datetime
from decimal import Decimal

def generate_bill_number():
    """
    Generates a unique Bill Number sequence: M4-YYYY-XXX (e.g. M4-2026-001)
    """
    from quotations.models import Bill
    year = datetime.datetime.now().year
    prefix = f"M4-{year}-"
    
    existing_bills = Bill.objects.filter(bill_number__startswith=prefix).order_counts() if hasattr(Bill.objects, 'order_counts') else Bill.objects.filter(bill_number__startswith=prefix)
    
    max_num = 0
    for bill in existing_bills:
        try:
            num_part = int(bill.bill_number.split('-')[-1])
            if num_part > max_num:
                max_num = num_part
        except (ValueError, IndexError):
            continue
            
    next_num = max_num + 1
    return f"M4-{year}-{next_num:03d}"


_ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
         "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
         "Seventeen", "Eighteen", "Nineteen"]

_tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def _two_digits_to_words(n):
    if n < 20:
        return _ones[n]
    tens_val = n // 10
    ones_val = n % 10
    return f"{_tens[tens_val]} {_ones[ones_val]}".strip()


def _three_digits_to_words(n):
    hundreds = n // 100
    rem = n % 100
    res = ""
    if hundreds > 0:
        res += f"{_ones[hundreds]} Hundred"
    if rem > 0:
        if res:
            res += " "
        res += _two_digits_to_words(rem)
    return res


def number_to_words_indian(amount):
    """
    Converts a float/decimal number to Indian Rupees in words.
    Example: 77035.00 -> Rupees Seventy Seven Thousand Thirty Five Only
    """
    try:
        val = Decimal(str(amount))
    except Exception:
        return "Rupees Zero Only"

    if val <= 0:
        return "Rupees Zero Only"

    rupees = int(val)
    paise = int(round((val - rupees) * 100))

    if rupees == 0:
        words_str = "Zero"
    else:
        # Indian numbering system groups:
        # Crores (10^7), Lakhs (10^5), Thousands (10^3), Hundreds
        crores = rupees // 10000000
        rem = rupees % 10000000

        lakhs = rem // 100000
        rem = rem % 100000

        thousands = rem // 1000
        rem = rem % 1000

        hundreds = rem

        parts = []
        if crores > 0:
            parts.append(f"{_three_digits_to_words(crores)} Crore")
        if lakhs > 0:
            parts.append(f"{_two_digits_to_words(lakhs)} Lakh")
        if thousands > 0:
            parts.append(f"{_two_digits_to_words(thousands)} Thousand")
        if hundreds > 0:
            parts.append(_three_digits_to_words(hundreds))

        words_str = " ".join(parts)

    res = f"Rupees {words_str}"
    if paise > 0:
        res += f" and {_two_digits_to_words(paise)} Paise"

    res += " Only"
    return res
