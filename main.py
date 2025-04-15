import streamlit as st
import calendar
import datetime
import math
import csv
import os

# --- FUNCTIONS ---

def load_events(filename):
    """
    Load events from a CSV file.
    Each event record is expected to be [date (YYYY-MM-DD), description, expense].
    Returns a list of event records.
    """
    events = []
    try:
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 3:
                    events.append(row)
    except FileNotFoundError:
        st.warning("No event file found; starting fresh!")
    except Exception as e:
        st.error(f"Error reading file: {e}")
    return events

def save_event(filename, event_record):
    """
    Append a new event record to the CSV file.
    """
    try:
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(event_record)
    except Exception as e:
        st.error(f"Error saving event: {e}")

def calculate_total_expense(events):
    """
    Calculate the total expense from the events.
    """
    total = 0.0
    for event in events:
        try:
            expense = float(event[2])
            total += expense
        except Exception:
            continue
    return total

# --- STREAMLIT APP ---

st.title("📅 Personal Event & Expense Planner")

# Sidebar Menu for different functionalities
menu_options = ["Add Event", "View Calendar", "View Expenses"]
choice = st.sidebar.selectbox("Menu", menu_options)

EVENTS_FILE = "events.csv"  # events storage file

# --------------
# Add Event Page
# --------------
if choice == "Add Event":
    st.subheader("Add a New Event")
    
    # Control module: Ask for event details using functions and input widgets.
    event_date = st.date_input("Select Event Date", datetime.date.today())
    event_desc = st.text_input("Event Description")
    expense_input = st.text_input("Expense Incurred ($)", "0")
    
    if st.button("Submit Event"):
        try:
            # Exception handling: Validate the expense input.
            expense_val = float(expense_input)
            # Use math.floor to round down expense to 2 decimal places
            expense_val = math.floor(expense_val * 100) / 100
            
            # Create event record (list used here; tuple could also have been used for immutability)
            event_record = [
                event_date.strftime("%Y-%m-%d"),
                event_desc,
                f"{expense_val:.2f}"
            ]
            save_event(EVENTS_FILE, event_record)
            st.success("Event added successfully!")
        except ValueError:
            st.error("Please enter a valid numerical value for expense.")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

# --------------
# Calendar View Page
# --------------
elif choice == "View Calendar":
    st.subheader("Monthly Calendar & Event Viewer")
    
    # Use the datetime and calendar modules to display the current month's calendar.
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    cal_text = calendar.month(year, month)
    st.text(cal_text)
    
    st.info("Select a date to view events for that day.")
    selected_date = st.date_input("Select Date", datetime.date.today(), key="cal_date")
    
    # Load events from file and filter by selected date.
    events = load_events(EVENTS_FILE)
    filtered_events = [event for event in events if event[0] == selected_date.strftime("%Y-%m-%d")]
    
    if filtered_events:
        for event in filtered_events:
            st.write(f"📌 **{event[1]}** - Expense: ${event[2]}")
    else:
        st.info("No events scheduled for the selected date.")

# --------------
# Expense Summary Page
# --------------
elif choice == "View Expenses":
    st.subheader("Expense Summary")
    
    events = load_events(EVENTS_FILE)
    
    if events:
        # Calculate total expense using our helper function.
        total_expense = calculate_total_expense(events)
        # Calculate average expense.
        avg_expense = total_expense / len(events)
        st.write("**Total Expense:** $", f"{total_expense:.2f}")
        st.write("**Average Expense per Event:** $", f"{avg_expense:.2f}")
        
        # Optional: List all events with expenses.
        st.markdown("### All Events:")
        for event in events:
            st.write(f"Date: {event[0]}, Event: {event[1]}, Expense: ${event[2]}")
    else:
        st.info("No events available to show expense details.")
