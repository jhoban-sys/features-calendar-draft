import streamlit as st
from streamlit_calendar import calendar
import sqlite3
from datetime import datetime

st.set_page_config(layout="wide", page_title="Features Calendar Draft")
st.title("📆 Features Calendar Draft (Shared)")

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("calendar.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events 
                 (id INTEGER PRIMARY KEY AUTO_INCREMENT, title TEXT, start TEXT, description TEXT, color TEXT)''')
    conn.commit()
    conn.close()

def get_events():
    conn = sqlite3.connect("calendar.db")
    c = conn.cursor()
    c.execute("SELECT id, title, start, description, color FROM events")
    rows = c.fetchall()
    conn.close()
    return [{"id": str(r[0]), "title": r[1], "start": r[2], "description": r[3], "color": r[4]} for r in rows]

def add_event(title, start, desc, color):
    conn = sqlite3.connect("calendar.db")
    c = conn.cursor()
    c.execute("INSERT INTO events (title, start, description, color) VALUES (?, ?, ?, ?)", (title, start, desc, color))
    conn.commit()
    conn.close()

def update_event_date(event_id, new_start):
    conn = sqlite3.connect("calendar.db")
    c = conn.cursor()
    c.execute("UPDATE events SET start = ? WHERE id = ?", (new_start, event_id))
    conn.commit()
    conn.close()

# Initialize Database
init_db()

# --- SIDEBAR INPUT ---
with st.sidebar:
    st.header("➕ Add New Feature Box")
    item_title = st.text_input("Feature Title", placeholder="e.g., Dashboard UI")
    item_desc = st.text_area("Short Description", placeholder="Keep it brief...")
    item_date = st.date_input("Target Date", datetime.now())
    
    if st.button("Add to Calendar", use_container_width=True):
        if item_title:
            add_event(item_title, item_date.strftime("%Y-%m-%d"), item_desc, "#4D96FF")
            st.rerun()
        else:
            st.error("Please enter a title!")

# --- CALENDAR CONFIG ---
calendar_options = {
    "editable": True,  # Allows dragging/moving
    "selectable": True,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek"
    },
    "initialView": "dayGridMonth",
    "timeZone": "America/Phoenix"  # Arizona Time
}

# Fetch fresh data from database
events = get_events()

st.markdown("💡 *Drag and drop any box to instantly update its calendar date for the whole team.*")
custom_calendar = calendar(events=events, options=calendar_options, key="features_cal")

# --- HANDLE MOVING BOXES ---
if custom_calendar.get("eventChange"):
    moved_event = custom_calendar["eventChange"]["event"]
    event_id = moved_event["id"]
    new_start = moved_event["start"].split("T")[0]
    
    # Update SQLite Database instantly
    update_event_date(event_id, new_start)
    st.rerun()