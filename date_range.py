from datetime import datetime

def validate_date(date_str: str) -> str:
    """Validate YYYYMMDD and return formatted YYYY-MM-DD string."""
    try:
        dt = datetime.strptime(date_str, "%Y%m%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date: {date_str}")


def past_date_input():
    dates_list = []
    while True:
        user_in = input("Enter YYYYMMDD-YYYYMMDD (or press Enter to exit): ").strip()
        if not user_in:
            break

        try:

            start_str, end_str = user_in.split('-', 1)

            start_date = validate_date(start_str)
            end_date = validate_date(end_str)

            if start_date > end_date:
                print("Start date must be before end date. Try again.")
                continue

            dates_list.append([start_date, end_date])
            print("Current ranges:", dates_list)

        except Exception as e:
            print("Invalid format. Please use YYYYMMDD-YYYYMMDD. Error:", e)

    return dates_list


def future_date_input():
    print("Under construction for now.")
    return []


if __name__ == "__main__":
    past_future = input("Enter 'past' or 'future' for your data range: ").strip().lower()
    if past_future == 'past':
        ranges = past_date_input()
        print("Final parsed ranges:", ranges)
    else:
        ranges = future_date_input()
