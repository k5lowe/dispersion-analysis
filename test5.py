import calendar
import re
import datetime

def _parse_date_part(date_str: str) -> tuple[datetime.date, bool]:
    """
    Parses a single date string into a (datetime.date, is_month_year) tuple.

    is_month_year is True if the input was only Month Year (e.g., "Aug 2022"),
    False otherwise (e.g., "2022-08-15", "Aug 15 2022", "20220815").        

    The datetime.date object returned for a Month Year input will be the 1st
    day of that month. This design simplifies handling the start of a month-based range.
    """
    date_str = date_str.strip()

    # Try Month Year formats (e.g., "Aug 2022", "August 2022")
    # This format implies the entire month.
    for fmt in ["%b %Y", "%B %Y"]:
        try:
            dt = datetime.datetime.strptime(date_str, fmt).date()
            return dt, True  # Indicate it was a month-year specification   
        except ValueError:
            pass

    # Try full date formats, which specify a particular day.

    # Try YYYYMMDD (e.g., "20220915")
    if len(date_str) == 8 and date_str.isdigit():
        try:
            dt = datetime.datetime.strptime(date_str, "%Y%m%d").date()      
            return dt, False  # This is a specific day
        except ValueError:
            pass

    # Try YYYY-MM-DD (e.g., "2024-09-30")
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()        
        return dt, False  # This is a specific day
    except ValueError:
        pass

    # Try Month Day Year formats (e.g., "Sep 23 2021", "September 23 2021") 
    for fmt in ["%b %d %Y", "%B %d %Y"]:
        try:
            dt = datetime.datetime.strptime(date_str, fmt).date()
            return dt, False  # This is a specific day
        except ValueError:
            pass

    raise ValueError(f"Could not parse date string in any known format: '{date_str}'")

def get_last_day_of_month(year: int, month: int) -> int:
    """Returns the last day of the given month and year, handling leap years."""
    return calendar.monthrange(year, month)[1]

def process_user_input(user_input: str) -> list[list[str]]:
    """
    Parses a user's input describing one or more dates or date ranges       
    and returns ALL valid ranges as a list of lists in strict ISO format YYYY-MM-DD.
    Each inner list has exactly two entries: the start date and the end date.
    """
    all_ranges = []

    # Split by comma to get individual date/range specifications.
    # Ensure to strip whitespace from each part to handle inputs like "Aug 2021, Aug 2022".
    parts = [part.strip() for part in user_input.split(',')]

    for part_str in parts:
        start_date_obj: datetime.date
        end_date_obj: datetime.date

        if ' - ' in part_str:
            # This is a custom range with two explicit date/month-year strings.
            start_str, end_str = [s.strip() for s in part_str.split(' - ')] 

            # Parse the start string. If it's a month-year, it implies the 1st of that month.
            # If it's a full date, it's that exact date.
            start_dt, _ = _parse_date_part(start_str)
            start_date_obj = start_dt

            # Parse the end string.
            # If it's a month-year (e.g., "Aug 2022"), it implies the LAST day of that month.
            # If it's a full date (e.g., "Aug 15 2022"), it's that exact date.
            end_dt, end_is_month_year = _parse_date_part(end_str)
            if end_is_month_year:
                # If the end string was just Month Year, expand to the last day of that month.
                last_day = get_last_day_of_month(end_dt.year, end_dt.month) 
                end_date_obj = datetime.date(end_dt.year, end_dt.month, last_day)
            else:
                # Otherwise, it was a specific day, so use it as is.        
                end_date_obj = end_dt

        else:
            # This is a single date or month-year specification (not a range with '-').
            parsed_dt, is_month_year = _parse_date_part(part_str)

            if is_month_year:
                # If it's a month-year (e.g., "Aug 2022"), expand to the first and last day of that month.
                start_date_obj = datetime.date(parsed_dt.year, parsed_dt.month, 1)
                last_day = get_last_day_of_month(parsed_dt.year, parsed_dt.month)
                end_date_obj = datetime.date(parsed_dt.year, parsed_dt.month, last_day)
            else:
                # If it's a specific full date (YYYY-MM-DD, YYYYMMDD, Month Day Year),
                # the start and end dates are the same.
                start_date_obj = parsed_dt
                end_date_obj = parsed_dt

                end_date_obj = datetime.date(parsed_dt.year, parsed_dt.month, last_day)
            else:
                # If it's a specific full date (YYYY-MM-DD, YYYYMMDD, Month Day Year),
                # the start and end dates are the same.
                start_date_obj = parsed_dt
                end_date_obj = parsed_dt

            else:
                # If it's a specific full date (YYYY-MM-DD, YYYYMMDD, Month Day Year),
                # the start and end dates are the same.
                start_date_obj = parsed_dt
                end_date_obj = parsed_dt

                # the start and end dates are the same.
                start_date_obj = parsed_dt
                end_date_obj = parsed_dt

        # Add the formatted range (YYYY-MM-DD) to the list
        all_ranges.append([start_date_obj.isoformat(), end_date_obj.isoformat()])

    return all_ranges