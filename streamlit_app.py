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
                 (id INTEGER PRIMARY KEY, title TEXT, start TEXT, description TEXT, color TEXT)''')
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

# Initialize Database
init_db()
events = get_events()

# --- SIDEBAR: INTERACTIVE CONTROLS ---
with st.sidebar:
    st.header("⚙️ Calendar Controls")
    
    # 1. Create a dictionary to map titles to events for easy editing lookup
    event_titles = {e["title"]: e for e in events}
    
    tabs = st.tabs(["➕ Add New", "✏️ Edit / Delete"])
    
    # --- TAB 1: ADD NEW EVENT ---
    with tabs[0]:
        item_title = st.text_input("Feature Title", placeholder="e.g., Dashboard UI", key="add_title")
        item_desc = st.text_area("Short Description", placeholder="Keep it brief...", key="add_desc")
        item_date = st.date_input("Target Date", datetime.now(), key="add_date")
        item_color = st.color_picker("Pick a color for this box", "#4D96FF", key="add_color")
        
        if st.button("Add to Calendar", use_container_width=True):
            if item_title:
                add_event(item_title, item_date.strftime("%Y-%m-%d"), item_desc, item_color)
                st.rerun()
            else:
                st.error("Please enter a title!")
                
    # --- TAB 2: EDIT OR DELETE EXISTING EVENT ---
    with tabs[1]:
        if not events:
            st.info("No events created yet to edit.")
        else:
            selected_title = st.selectbox("Select a box to modify:", list(event_titles.keys()))
            selected_event = event_titles[selected_title]
            
            # Populate fields with existing data for editing
            edit_title = st.text_input("Edit Title", value=selected_event["title"])
            edit_desc = st.text_area("Edit Description", value=selected_event["description"])
            edit_color = st.color_picker("Change Box Color", value=selected_event["color"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Changes", use_container_width=True, type="primary"):
                    update_full_event(selected_event["id"], edit_title, edit_desc, edit_color)
                    st.success("Updated successfully!")
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete Box", use_container_width=True):
                    delete_event(selected_event["id"])
                    st.warning("Box deleted.")
                    st.rerun()

# --- CALENDAR CONFIG ---
calendar_options = {
    "editable": True,
    "selectable": True,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek"
    },
    "initialView": "dayGridMonth",
    "timeZone": "America/Phoenix"  # Arizona Time
}

st.markdown("💡 *Drag and drop any box to reschedule it. Use the sidebar to color-code, edit text, or delete items.*")
custom_calendar = calendar(events=events, options=calendar_options, key="features_cal")

# --- HANDLE DRAG & DROP MOVING ---
if custom_calendar.get("eventChange"):
    moved_event = custom_calendar["eventChange"]["event"]
    event_id = moved_event["id"]
    new_start = moved_event["start"].split("T")[0]
    
    update_event_date(event_id, new_start)
    st.rerun()