import streamlit as st
from datetime import date

# 1. Initialize session state
if 'dates' not in st.session_state:
    st.session_state.dates = []

def add_new_date():
    """Callback function to append a date to the session state list."""
    st.session_state.dates.append(st.session_state.new_date)
    # Optional: clear the temporary widget value after adding
    st.session_state.new_date = date.today()

# 2. Display the current date inputs
st.header("User Dates")
if st.session_state.dates:
    for i, user_date in enumerate(st.session_state.dates):
        st.write(f"Date {i+1}: {user_date}")
else:
    st.write("No dates added yet.")

# 3. Widget for adding a new date
st.divider()
st.subheader("Add another date")

# Use a unique 'key' for the input widget to reference its value in the callback
new_date_value = st.date_input(
    "Select a date to add", 
    value=date.today(), # Default value
    key="new_date" 
)

# Button to trigger the callback function and add the date
st.button(
    "Add Date", 
    on_click=add_new_date
)
