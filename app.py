import streamlit as st
import sqlite3
import json
import os
from base64 import b64encode
from openai import OpenAI
from dotenv import load_dotenv

# Load API environment variables
load_dotenv()
st.set_page_config(page_title="PartsRecognition", page_icon="📐", layout="wide")

# -----------------------------------------------------------------------------
# DATABASE SETUP
# -----------------------------------------------------------------------------
DB_FILE = "archive.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS drawings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            drawing_type TEXT,
            medium TEXT,
            style_era TEXT,
            elements TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(filename, analysis):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO drawings (filename, drawing_type, medium, style_era, elements, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (filename, analysis.get("drawing_type"), analysis.get("medium"), 
          analysis.get("style_era"), ", ".join(analysis.get("detected_elements", [])), 
          analysis.get("architectural_description")))
    conn.commit()
    conn.close()

def fetch_drawings():
    conn = sqlite3.connect(DB_FILE)
    # FIX 1: Change database rows from index numbers into readable dictionary structures
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()
    c.execute("SELECT * FROM drawings ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

init_db()

# -----------------------------------------------------------------------------
# AI INFERENCE LAYER (Vision API)
# -----------------------------------------------------------------------------
def analyze_drawing_with_ai(image_bytes, filename):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    base64_image = b64encode(image_bytes).decode("utf-8")
    
    prompt = """
    You are an expert industrial archivist and mechanical engineer. Analyze this technical drawing or image of a substation component.
    Provide a valid JSON response containing strictly the following keys:
    {
      "drawing_type": "e.g., Schematic, Assembly Drawing, Isometric, Site Photograph, Component Sketch",
      "medium": "e.g., CAD Export, Ink Blueprint, Digital Photograph, Pencil Draft",
      "style_era": "e.g., High-Voltage System, Legacy Grid, Automation Module, Modern Compact",
      "detected_elements": ["List", "of", "parts/systems", "like", "Transformer", "Circuit Breaker", "Busbar", "Isolator", "Insulator"],
      "architectural_description": "A precise 2-sentence technical description of the component's function and physical layout."
    }
    Do not output markdown block wrappers (like ```json). Return raw string JSON only.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ],
                }
            ],
            max_tokens=500,
        )
        return json.loads(response.choices.message.content)
    except Exception as e:
        st.error(f"AI Processing Failed: {e}")
        return None

# -----------------------------------------------------------------------------
# APP UI / FRONTEND
# -----------------------------------------------------------------------------
st.title("📐 PartsRecognition")
st.caption("Digital Infrastructure Prototype // Automated Image recognition & Labelling")

col_upload, col_gallery = st.columns(2, gap="large")

with col_upload:
    st.header("1. Ingest Asset")
    uploaded_file = st.file_uploader("Upload drawing (JPG/PNG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Staged for Archiving", width='stretch')
        
        if st.button("Run AI Digitisation & Save", width='stretch'):
            with st.spinner("Extracting architectural features via VLM..."):
                file_bytes = uploaded_file.read()
                
                # Run AI pipeline
                ai_analysis = analyze_drawing_with_ai(file_bytes, uploaded_file.name)
                
                if ai_analysis:
                    # Save image locally to simulate an archival server storage
                    os.makedirs("archive_vault", exist_ok=True)
                    saved_path = os.path.join("archive_vault", uploaded_file.name)
                    with open(saved_path, "wb") as f:
                        f.write(file_bytes)
                    
                    # Log into SQLite DB
                    save_to_db(uploaded_file.name, ai_analysis)
                    st.success("Asset enriched and written to secure archive database!")
                    st.json(ai_analysis)
                    
                    # FIX 2: Immediately reload page states so the visual grid reflects changes instantly
                    st.rerun()

with col_gallery:
    st.header("2. Central Digital Archive Explorer")
    
    # Simple filtering UI
    db_records = fetch_drawings()
    
    if not db_records:
        st.info("The archive database is currently empty. Upload a drawing to populate the grid.")
    else:
        # Display data in a structured, scannable table format
        st.subheader("Database Ledger")
        display_data = []
        for r in db_records:
            # FIX 3: Swapped numeric indices (r[0]) to direct column text-key callouts
            display_data.append({
                "ID": r["id"],
                "Filename": r["filename"],
                "Type": r["drawing_type"],
                "Medium": r["medium"],
                "Era/Style": r["style_era"],
                "Detected Entities": r["elements"],
                "Architectural Summary": r["description"]
            })
        st.dataframe(display_data, width='stretch')
        
        # Display visual grid
        st.subheader("Visual Grid")
        grid_cols = st.columns(3)
        for idx, r in enumerate(db_records):
            col = grid_cols[idx % 3]
            img_path = os.path.join("archive_vault", r["filename"])
            if os.path.exists(img_path):
                col.image(img_path, caption=f"#{r['id']}: {r['filename']} ({r['drawing_type']})", width='stretch')
                with col.expander("View Labels"):
                    st.write(f"**Medium:** {r['medium']}")
                    st.write(f"**Elements:** {r['elements']}")
