from google import genai
import os
from dotenv import load_dotenv
import ast
import re

# Load API key
load_dotenv()
GEMINI_API = os.getenv('GEMINI_API')
client = genai.Client(api_key=GEMINI_API)


def date_input():
    # Clean user prompt (no weird indentation)
    print("""Enter the date(s) you want to fetch data for below.
You can type:
- A month and year → "Aug 2022"
- Multiple months → "Aug 2022, Aug 2023, Sep 2024"
- A single date → "2024-09-30" or "20220930"
- A date range → "Sep 23 2021 - Oct 30 2021"

Examples:
- Aug 2022, Aug 2023
- 20220915
- Sep 23 2021 - Oct 30 2021
""")

    dates = input("Enter dates here: ")

    # Ask Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
You are given a user's input describing one or more dates or date ranges: "{dates}".
Your task is to return ALL valid ranges as a list of lists in strict ISO format YYYY-MM-DD. 
Each list should have exactly two entries: the start date and the end date.

Rules:
- If the user enters a month + year (e.g. "Aug 2022"), output the first and last day of that month, 
  e.g. [[2022-08-01, 2022-08-31]].
- If the user enters multiple months separated by commas (e.g. "Aug 2022, Aug 2023, Sep 2024"), 
  output one range per month, e.g. [[2022-08-01, 2022-08-31],[2023-08-01, 2023-08-31],[2024-09-01, 2024-09-30]].
- If the user enters a single full date (e.g. "2024-09-30"), output a range where start = end, 
  e.g. [[2024-09-30, 2024-09-30]].
- If the user enters a custom range with two explicit dates (e.g. "Sep 23 2021 - Oct 30 2021"), 
  output exactly those as the start and end, e.g. [[2021-09-23, 2021-10-30]].
- If the user enters YYYYMMDD format (e.g. 20220915), convert to [[YYYY-MM-DD, YYYY-MM-DD]].
- Always validate leap years and correct month lengths.
- Always ensure ISO formatting (zero-padded months and days).
- Output ONLY the final list of lists. No explanations, no extra text.

Examples:
Input: "Aug 2022, Aug 2023, Sep 2024"
Output: [[2022-08-01, 2022-08-31],[2023-08-01, 2023-08-31],[2024-09-01, 2024-09-30]]

Input: "Sep 23 2021 - Oct 30 2021"
Output: [[2021-09-23, 2021-10-30]]

Input: "20220915"
Output: [[2022-09-15, 2022-09-15]]
"""
    )

    # Clean Gemini output
    raw_output = response.text.strip()
    raw_output = re.sub(r"^```[a-zA-Z]*\n", "", raw_output)  # remove ```python
    raw_output = re.sub(r"\n```$", "", raw_output)           # remove closing ```

    # Try parsing safely
    try:
        ranges = ast.literal_eval(raw_output)
        print("Parsed ranges:", ranges)
    except Exception as e:
        print("Raw response:", raw_output)
        print("Could not parse:", e)


# Run it
if __name__ == "__main__":
    date_input()
