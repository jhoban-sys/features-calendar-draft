import streamlit as st
from streamlit_calendar import calendar
import sqlite3
from datetime import datetime

# Page Configuration
st.set_page_config(layout="wide", page_title="KJZZ Feature Planning")
st.title("📻 KJZZ Feature Planning")

# --- DATABASE ENGINE ---
def init_db():
    conn = sqlite3.connect("calendar.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events 
                 (id INTEGER PRIMARY KEY, title TEXT, start TEXT, description TEXT, color TEXT)''')
    conn.commit()
    conn.close()

def get_events():
    conn = sqlite3.connect("calendar.db")
    c = conn.cursor()
    c.execute("SELECT id, title, start, description, color FROM events")
    rows = c.fetchall()
    conn.close()
    # Adding 'textColor': 'black' to every event object
    return [{"id": str(r[0]), "title": r[1], "start": r[2], "description": r[3], "color": r[4], "textColor": "black"} for r in rows]

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

def update_full_event(event_id, title, desc, color):
    conn = sqlite3.connect("calendar.db")
    c = conn.cursor()
    c.execute("UPDATE events SET title = ?, description = ?, color = ? WHERE id = ?", (title, desc, color, event_id))
    conn.commit()
    conn.close()

def delete_event(event_id):
    conn = sqlite3.connect("calendar.db")
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()

# Initialize App State & DB
init_db()
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

events = get_events()

# --- SIDEBAR: EDITING & INPUT ---
with st.sidebar:
    st.header("📋 Feature Management")
    
    # If a user clicks a box, this section appears
    if st.session_state.selected_event:
        st.subheader("📝 Edit Selected Feature")
        ev = st.session_state.selected_event
        
        with st.form("edit_form"):
            new_title = st.text_input("Title", value=ev['title'])
            new_desc = st.text_area("Short Description", value=ev['description'])
            new_color = st.color_picker("Box Color", value=ev['color'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save"):
                    update_full_event(ev['id'], new_title, new_desc, new_color)
                    st.session_state.selected_event = None
                    st.rerun()
            with col2:
                if st.form_submit_button("🗑️ Delete"):
                    delete_event(ev['id'])
                    st.session_state.selected_event = None
                    st.rerun()
        
        if st.button("Cancel Editing"):
            st.session_state.selected_event = None
            st.rerun()
            
        st.divider()

    # Always show the Add New section
    st.subheader("➕ Create New Feature")
    with st.form("add_form"):
        add_title = st.text_input("Feature Title")
        add_desc = st.text_area("Description")
        add_date = st.date_input("Date", datetime.now())
        add_color = st.color_picker("Pick Box Color", "#FAD02C") # KJZZ Gold-ish default
        
        if st.form_submit_button("Add to Calendar"):
            if add_title:
                add_event(add_title, add_date.strftime("%Y-%m-%d"), add_desc, add_color)
                st.rerun()
            else:
                st.error("Title required")

# --- CALENDAR DISPLAY ---
calendar_options = {
    "editable": True,
    "selectable": True,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek"
    },
    "initialView": "dayGridMonth",
    "timeZone": "America/Phoenix", # AZ Time
    "eventClick": True, # Enables the click trigger
}

st.info("💡 **Tip:** Click any box to edit its text, change its color, or delete it.")

custom_calendar = calendar(
    events=events, 
    options=calendar_options, 
    key="kjzz_planning_cal"
)

# --- EVENT HANDLERS ---

# 1. Handle clicking a box (To Edit/Delete)
if custom_calendar.get("eventClick"):
    clicked_data = custom_calendar["eventClick"]["event"]
    # Look up full details from our database list
    for e in events:
        if e["id"] == clicked_data["id"]:
            st.session_state.selected_event = e
            st.rerun()

# 2. Handle dragging a box (To Reschedule)
if custom_calendar.get("eventChange"):
    moved_event = custom_calendar["eventChange"]["event"]
    update_event_date(moved_event["id"], moved_event["start"].split("T")[0])
    st.rerun()