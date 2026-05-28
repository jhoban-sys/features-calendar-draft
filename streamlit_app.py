import streamlit as st
from streamlit_calendar import calendar
import sqlite3
import uuid
from datetime import datetime

# Page Configuration & Brand Title
st.set_page_config(layout="wide", page_title="KJZZ Feature Planning")
st.title("📻 KJZZ Feature Planning")

# --- CUSTOM PRODUCTION WORKFLOW COLOR CHOICES ---
COLOR_PALETTE = {
    "🔵 Pitch": "#A2CFFE",
    "🟡 Feature": "#FAD02C",
    "🟠 In Progress": "#FFD3B6",
    "🟣 Edited": "#E2C6FF",
    "🟢 Approved": "#B2F7EF",
    "🔴 Other": "#FF9B9B"
}

# Helper function to find the label match by its hex value
def get_color_label(hex_value):
    for label, hex_code in COLOR_PALETTE.items():
        if hex_code == hex_value:
            return label
    return "🔵 Pitch" # Fallback default

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
    return [{
        "id": str(r[0]), 
        "title": r[1], 
        "start": r[2], 
        "description": r[3], 
        "backgroundColor": r[4],
        "borderColor": r[4],
        "textColor": "#000000"  # Forces text color to black
    } for r in rows]

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

# Initialize Engine
init_db()

# Session state key to force-refresh calendar interface dynamically
if "cal_key" not in st.session_state:
    st.session_state.cal_key = str(uuid.uuid4())

events = get_events()

# --- SIDEBAR: INTERACTIVE CONTROLS ---
with st.sidebar:
    st.header("📋 Feature Management")
    
    tabs = st.tabs(["➕ Create New", "✏️ Edit / Delete"])
    
    # --- TAB 1: ADD NEW FEATURE ---
    with tabs[0]:
        add_title = st.text_input("Feature Title", placeholder="e.g., Election Coverage Draft")
        add_desc = st.text_area("Short Description", placeholder="Enter draft summary...")
        add_date = st.date_input("Target Date", datetime.now())
        
        selected_label = st.radio("Select Production State:", list(COLOR_PALETTE.keys()), key="new_box_color")
        add_color = COLOR_PALETTE[selected_label]
        
        if st.button("Add to Calendar", use_container_width=True, type="primary"):
            if add_title:
                add_event(add_title, add_date.strftime("%Y-%m-%d"), add_desc, add_color)
                st.session_state.cal_key = str(uuid.uuid4()) 
                st.success(f"Added '{add_title}'")
                st.rerun()
            else:
                st.error("Title is required.")
                
    # --- TAB 2: RELIABLE EDIT / DELETE WORKFLOW ---
    with tabs[1]:
        if not events:
            st.info("No active boxes available to edit.")
        else:
            event_map = {e["title"]: e for e in events}
            selected_title = st.selectbox("Choose a box to change or delete:", list(event_map.keys()))
            
            selected_event = event_map[selected_title]
            
            # Form fields pre-loaded with current layout details
            edit_title = st.text_input("Modify Title", value=selected_event["title"])
            edit_desc = st.text_area("Modify Description", value=selected_event["description"])
            
            current_label = get_color_label(selected_event["backgroundColor"])
            edit_label = st.radio("Modify Production State:", list(COLOR_PALETTE.keys()), index=list(COLOR_PALETTE.keys()).index(current_label), key="edit_box_color")
            edit_color = COLOR_PALETTE[edit_label]
            
            col1, col2 = st.columns(2)
            with col1:
                # REWORKED: Simply labeled "Save"
                if st.button("💾 Save", use_container_width=True):
                    update_full_event(selected_event["id"], edit_title, edit_desc, edit_color)
                    st.session_state.cal_key = str(uuid.uuid4()) 
                    st.success("Saved!")
                    st.rerun()
            with col2:
                # REWORKED: Simply labeled "Delete"
                if st.button("🗑️ Delete", use_container_width=True):
                    delete