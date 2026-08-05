# =====================================================
# SmartFit - Clothing Size Recommendation System
# =====================================================

import streamlit as st
import joblib
import numpy as np
import pandas as pd

# -----------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------

st.set_page_config(
    page_title="SmartFit",
    page_icon="🛍️",
    layout="wide"
)

# -----------------------------------------------------
# CONFIG — swap this with your real PayHero Payment Link.
# Sign up at https://app.payhero.co.ke (Kenyan gateway,
# supports M-Pesa natively), create a Payment Link from your
# dashboard (Payment Links / Hosted Payment Pages section),
# and paste the URL below.
# -----------------------------------------------------

PAYMENT_LINK = "https://short.payhero.co.ke/s/7X62bzW5MnGdPdsnqcgpzW"

# -----------------------------------------------------
# FASHION THEME (CSS)
# -----------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Poppins:wght@300;400;500;600&display=swap');

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    letter-spacing: 0.5px;
}

.stApp {
    background: linear-gradient(180deg, #f4f8f1 0%, #e9f1e4 100%);
}

section[data-testid="stSidebar"] {
    background: #2e3b2f;
}
section[data-testid="stSidebar"] * {
    color: #eef4ea !important;
}

.stButton > button, .stFormSubmitButton > button, .stLinkButton > a, .stDownloadButton > button {
    background: linear-gradient(90deg, #7fa87f, #a9c9a0);
    color: #000000 !important;
    border: none;
    border-radius: 30px;
    font-weight: 600;
    padding: 0.6em 1.2em;
    transition: 0.2s ease-in-out;
    text-decoration: none !important;
    text-align: center;
}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stLinkButton > a:hover, .stDownloadButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 14px rgba(127,168,127,0.4);
}

.fit-card {
    background: #ffffff;
    border-radius: 24px;
    padding: 40px;
    border: 2px solid #a9c9a0;
    text-align: center;
    box-shadow: 0 8px 24px rgba(43,35,32,0.08);
}

/* Fix faint number/text input contrast */
input[type="number"], input[type="text"], input[type="password"] {
    color: #1f2a21 !important;
    font-weight: 600 !important;
    background-color: #ffffff !important;
}
.stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
    color: #1f2a21 !important;
    font-weight: 600 !important;
}

/* Force readable dropdowns everywhere, including inside the dark sidebar */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #1f2a21 !important;
    font-weight: 600 !important;
}
div[data-baseweb="select"] * {
    color: #1f2a21 !important;
}
div[data-baseweb="popover"] * {
    color: #1f2a21 !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# LOAD TRAINED MODEL
# -----------------------------------------------------

model = joblib.load("clothing_size_model.pkl")

# -----------------------------------------------------
# SESSION STATE
# -----------------------------------------------------

if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"
if "is_pro" not in st.session_state:
    st.session_state.is_pro = False

# Apply any pending programmatic navigation BEFORE the nav widget is created
# (Streamlit forbids setting session_state.page directly after that widget exists)
if "nav_request" in st.session_state:
    st.session_state.page = st.session_state.pop("nav_request")

# -----------------------------------------------------
# UNIT CONVERSION FUNCTIONS
# -----------------------------------------------------

def convert_to_mm(value, unit):
    if unit == "Millimetres (mm)":
        return value
    elif unit == "Centimetres (cm)":
        return value * 10
    elif unit == "Metres (m)":
        return value * 1000
    elif unit == "Inches":
        return value * 25.4
    return value

def feet_inches_to_mm(feet, inches):
    total_inches = (feet * 12) + inches
    return total_inches * 25.4

def convert_weight(value, unit):
    if unit == "Kilograms (kg)":
        return value
    elif unit == "Pounds (lb)":
        return value * 0.453592
    return value

# -----------------------------------------------------
# GARMENT TYPE -> REQUIRED MEASUREMENTS
# -----------------------------------------------------

GARMENT_REQUIREMENTS = {
    "Full Outfit": ["chest", "neck", "shoulder", "arm", "waist", "hip", "thigh", "calf", "leg"],

    # Upper body
    "T-Shirt / Casual Top": ["chest", "shoulder"],
    "Dress Shirt / Button-Down": ["chest", "neck", "shoulder", "arm"],
    "Sleeveless Top / Tank Top": ["chest", "neck", "shoulder"],
    "Sweater / Hoodie": ["chest", "shoulder", "arm"],
    "Jacket / Coat / Blazer": ["chest", "neck", "shoulder", "arm"],

    # Neck-only
    "Poncho / Cape": ["neck"],
    "Scarf": ["neck"],

    # Full-body / one-piece
    "Dress (Full-Length)": ["chest", "shoulder", "waist", "hip"],
    "Jumpsuit / Overall": ["chest", "neck", "shoulder", "arm", "waist", "hip", "thigh", "leg"],

    # Lower body
    "Pants / Trousers": ["waist", "hip", "thigh", "leg"],
    "Shorts": ["waist", "hip", "thigh"],
    "Skirt": ["waist", "hip"],
    "Leggings / Tights": ["waist", "hip", "thigh", "calf", "leg"],
    "Belt": ["waist"],
    "Socks / Leg Warmers": ["calf", "leg"],
}

FIELD_LABELS = {
    "chest": "Chest", "neck": "Neck", "shoulder": "Shoulder", "arm": "Arm Length",
    "waist": "Waist", "hip": "Hip", "thigh": "Thigh", "calf": "Calf", "leg": "Leg Length",
}

# Garment types that don't require SmartFit Pro
# Only these premium/formal garment types require SmartFit Pro — everything else is free
PRO_ONLY_GARMENTS = [
    "Dress (Full-Length)", "Jumpsuit / Overall", "Jacket / Coat / Blazer",
    "Dress Shirt / Button-Down", "Sweater / Hoodie", "Skirt", "Poncho / Cape", "Scarf",
]
FREE_GARMENTS = [g for g in GARMENT_REQUIREMENTS if g not in PRO_ONLY_GARMENTS]

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

with st.sidebar:
    st.markdown("""
    <svg width="60" height="60" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
        <path d="M22 100 C 8 65, 22 25, 62 15 C 105 5, 118 45, 92 62 C 70 76, 48 62, 55 42"
              fill="none" stroke="#3a3226" stroke-width="19" stroke-linecap="round"/>
        <path d="M22 100 C 8 65, 22 25, 62 15 C 105 5, 118 45, 92 62 C 70 76, 48 62, 55 42"
              fill="none" stroke="#f0c419" stroke-width="15" stroke-linecap="round"/>
        <line x1="18" y1="88" x2="30" y2="90" stroke="#3a3226" stroke-width="2"/>
        <line x1="16" y1="72" x2="29" y2="72" stroke="#3a3226" stroke-width="2"/>
        <line x1="20" y1="52" x2="33" y2="50" stroke="#3a3226" stroke-width="2"/>
        <line x1="35" y1="27" x2="40" y2="38" stroke="#3a3226" stroke-width="2"/>
        <line x1="62" y1="16" x2="63" y2="29" stroke="#3a3226" stroke-width="2"/>
        <line x1="90" y1="20" x2="82" y2="30" stroke="#3a3226" stroke-width="2"/>
        <line x1="102" y1="45" x2="90" y2="48" stroke="#3a3226" stroke-width="2"/>
        <rect x="12" y="93" width="18" height="12" rx="2" fill="#c9c9c9" stroke="#3a3226" stroke-width="2"/>
        <circle cx="21" cy="99" r="2.5" fill="#3a3226"/>
    </svg>
    """, unsafe_allow_html=True)
    st.title("SmartFit")
    if st.session_state.is_pro:
        st.markdown("<span style='background:#f0c419;color:#3a3226;padding:2px 10px;border-radius:12px;font-size:0.8em;font-weight:700;'>✨ PRO</span>", unsafe_allow_html=True)
    st.divider()

    st.radio(
        "Navigate",
        ["🏠 Home", "❓ Help", "🔍 Size Guide", "💎 Upgrade"],
        key="page",
        label_visibility="collapsed"
    )

    if st.session_state.page == "🏠 Home":
        st.divider()

        garment_type = st.selectbox(
            "🎯 What are you sizing?",
            list(GARMENT_REQUIREMENTS.keys()),
            format_func=lambda g: g if (g in FREE_GARMENTS or st.session_state.is_pro) else f"🔒 {g} (Pro)"
        )
        required_fields = GARMENT_REQUIREMENTS[garment_type]
        is_locked_garment = garment_type not in FREE_GARMENTS and not st.session_state.is_pro

        if is_locked_garment:
            st.warning(f"🔒 **{garment_type}** requires SmartFit Pro.")

        # Default every field to 0 so unused ones are safely defined
        chest = neck = shoulder = arm = 0.0
        waist = hip = thigh = calf = leg = 0.0
        upper_unit = "Centimetres (cm)"
        lower_unit = "Centimetres (cm)"

        upper_fields = ["chest", "neck", "shoulder", "arm"]
        lower_fields = ["waist", "hip", "thigh", "calf", "leg"]
        needs_upper = any(f in required_fields for f in upper_fields)
        needs_lower = any(f in required_fields for f in lower_fields)

        if needs_upper:
            st.divider()
            st.subheader("👕 Upper Body")
            upper_unit = st.selectbox("Upper Body Unit", ["Centimetres (cm)", "Millimetres (mm)", "Inches"], key="upper_unit")
            if "chest" in required_fields:
                chest = st.number_input("Chest", min_value=0.0)
            if "neck" in required_fields:
                neck = st.number_input("Neck", min_value=0.0)
            if "shoulder" in required_fields:
                shoulder = st.number_input("Shoulder", min_value=0.0)
            if "arm" in required_fields:
                arm = st.number_input("Arm Length", min_value=0.0)

        if needs_lower:
            st.divider()
            st.subheader("👖 Lower Body")
            lower_unit = st.selectbox("Lower Body Unit", ["Centimetres (cm)", "Millimetres (mm)", "Inches"], key="lower_unit")
            if "waist" in required_fields:
                waist = st.number_input("Waist", min_value=0.0)
            if "hip" in required_fields:
                hip = st.number_input("Hip Breadth", min_value=0.0)
            if "thigh" in required_fields:
                thigh = st.number_input("Thigh", min_value=0.0)
            if "calf" in required_fields:
                calf = st.number_input("Calf", min_value=0.0)
            if "leg" in required_fields:
                leg = st.number_input("Leg Length", min_value=0.0)

page = st.session_state.page

# =====================================================
# HOME PAGE
# =====================================================

if page == "🏠 Home":

    st.title("✨ SmartFit")
    st.subheader("Clothing Size Recommendation System")
    st.write(f"👉 You're sizing a **{garment_type}**. Enter your measurements in the sidebar, then hit Recommend My Size.")
    st.divider()

    st.subheader("📋 Basic Information")

    basic1, basic2, basic3 = st.columns(3)

    with basic1:
        gender = st.selectbox("Gender", ["Male", "Female"])

    with basic2:
        height_unit = st.selectbox("Height Unit", ["Centimetres (cm)", "Metres (m)", "Feet & Inches"])
        if height_unit == "Feet & Inches":
            feet = st.number_input("Feet", min_value=0, value=5)
            inches = st.number_input("Inches", min_value=0, max_value=11, value=8)
        else:
            height = st.number_input("Height", min_value=0.0, value=0.0)

    with basic3:
        weight = st.number_input("Weight", min_value=0.0, value=0.0)
        weight_unit = st.selectbox("Weight Unit", ["Kilograms (kg)", "Pounds (lb)"])

    st.divider()

    field_values = {
        "chest": chest, "neck": neck, "shoulder": shoulder, "arm": arm,
        "waist": waist, "hip": hip, "thigh": thigh, "calf": calf, "leg": leg,
    }
    required_fields = GARMENT_REQUIREMENTS[garment_type]
    missing_fields = [f for f in required_fields if field_values[f] <= 0]
    measurements_provided = len(missing_fields) == 0

    button_col1, button_col2, button_col3 = st.columns([1, 2, 1])
    with button_col2:
        predict_button = st.button(
            "✨ Recommend My Size",
            use_container_width=True,
            disabled=(not measurements_provided) or is_locked_garment
        )

    if is_locked_garment:
        st.caption(f"🔒 **{garment_type}** requires SmartFit Pro.")
        if st.button("💎 See Upgrade Options", key="upgrade_btn_locked_garment"):
            st.session_state.nav_request = "💎 Upgrade"
            st.rerun()
    elif not measurements_provided:
        st.caption("⚠️ Enter your measurements in the sidebar to enable this button.")
    elif garment_type != "Full Outfit":
        st.caption("ℹ️ For the most accurate size, fill in all measurements and choose Full Outfit.")

    if predict_button:
        gender_value = 1 if gender == "Male" else 0

        if height_unit == "Feet & Inches":
            height_mm = feet_inches_to_mm(feet, inches)
        else:
            height_mm = convert_to_mm(height, height_unit)

        weight_kg = convert_weight(weight, weight_unit)

        chest_mm = convert_to_mm(chest, upper_unit)
        neck_mm = convert_to_mm(neck, upper_unit)
        shoulder_mm = convert_to_mm(shoulder, upper_unit)
        arm_mm = convert_to_mm(arm, upper_unit)

        waist_mm = convert_to_mm(waist, lower_unit)
        hip_mm = convert_to_mm(hip, lower_unit)
        thigh_mm = convert_to_mm(thigh, lower_unit)
        calf_mm = convert_to_mm(calf, lower_unit)
        leg_mm = convert_to_mm(leg, lower_unit)

        features = np.array([[
            gender_value, height_mm, weight_kg, chest_mm, waist_mm,
            hip_mm, neck_mm, shoulder_mm, arm_mm, thigh_mm, calf_mm, leg_mm
        ]])

        prediction = model.predict(features)[0]

        st.session_state.show_result = True
        st.session_state.prediction = prediction
        st.session_state.gender = gender

    if st.session_state.show_result:
        st.divider()

        size_names = {
            "XS": "EXTRA SMALL (XS)", "S": "SMALL (S)", "M": "MEDIUM (M)",
            "L": "LARGE (L)", "XL": "EXTRA LARGE (XL)",
            "XXL": "DOUBLE EXTRA LARGE (XXL)", "XXXL": "TRIPLE EXTRA LARGE (XXXL)"
        }
        display_size = size_names.get(st.session_state.prediction, st.session_state.prediction)

        person_emoji = "🧍‍♀️" if st.session_state.get("gender") == "Female" else "🧍‍♂️"

        st.markdown("<h2 style='text-align:center;'>🎉 Your Perfect Fit</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="fit-card">
                <h1 style="color:#5f8060; font-size:55px;">{person_emoji} {display_size}</h1>
            </div>
        """, unsafe_allow_html=True)
        st.success("Perfect fit found! ✅")

        st.divider()
        if st.session_state.is_pro:
            st.subheader("📄 Detailed Style Report (Pro)")
            st.write(f"- Recommended size: **{display_size}**")
            st.write(f"- Sizing based on: **{garment_type}**")
            st.write("- Styling tip: fitted cuts work best true-to-size; size up for a relaxed silhouette.")
            st.download_button(
                "⬇️ Download Style Report",
                data=f"SmartFit Style Report\nGarment: {garment_type}\nRecommended Size: {display_size}",
                file_name="smartfit_style_report.txt"
            )
        else:
            st.info("🔒 Unlock a detailed Style Report with personalized styling tips — **SmartFit Pro**.")
            if st.button("💎 See Upgrade Options", key="upgrade_btn_style_report"):
                st.session_state.nav_request = "💎 Upgrade"
                st.rerun()

# =====================================================
# HELP PAGE
# =====================================================

elif page == "❓ Help":

    st.title("❓ Help & Measurement Guide")

    st.info(
        """
        **Instructions**

        • Enter your body measurements.

        • Select the correct units.

        • Click **Recommend My Size**.

        • SmartFit automatically converts your measurements before making a prediction.
        """
    )

    st.divider()

    st.markdown("""
### Height
Measure from the floor to the top of your head while standing upright.

### Weight
Measure using a weighing scale.

### Chest
Measure around the fullest part of your chest.

### Waist
Measure around your natural waistline.

### Hip
Measure around the widest part of your hips.

### Neck
Measure around the base of your neck.

### Shoulder
Measure around your shoulder area.

### Arm Length
Measure from the shoulder to the wrist.

### Thigh
Measure around the widest part of your thigh.

### Calf
Measure around the widest part of your calf.

### Leg Length
Measure from your waist to your ankle.
""")

    st.divider()
    st.subheader("Frequently Asked Questions")
    with st.expander("How accurate is this model?"):
        st.write("The underlying model was trained on the ANSUR II anthropometric dataset and reached ~99% accuracy on held-out test data. Rare sizes (like XS) have fewer training examples, so predictions there are less reliable.")
    with st.expander("Which units can I use?"):
        st.write("You can enter measurements in centimetres, millimetres, inches, or metres — SmartFit converts everything automatically.")

# =====================================================
# SIZE GUIDE / SEARCH PAGE
# =====================================================

elif page == "🔍 Size Guide":

    st.title("🔍 Size Guide")
    st.write("Search the general size chart below by keyword (e.g. a size or measurement name).")

    size_chart = pd.DataFrame({
        "Size": ["XS", "S", "M", "L", "XL", "XXL", "XXXL"],
        "Chest (cm)": ["<86", "86-94", "94-102", "102-110", "110-118", "118-126", "126+"],
        "Waist (cm)": ["<70", "70-78", "78-86", "86-94", "94-102", "102-110", "110+"],
    })

    query = st.text_input("Search size chart", placeholder="e.g. M, or 94")

    if query:
        mask = size_chart.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
        st.dataframe(size_chart[mask], use_container_width=True, hide_index=True)
    else:
        st.dataframe(size_chart, use_container_width=True, hide_index=True)

    st.caption("General reference chart — your actual recommendation is personalized by the ML model on the Home page.")

# =====================================================
# UPGRADE / PAYMENT PAGE
# =====================================================

elif page == "💎 Upgrade":

    st.title("💎 SmartFit Pro")

    if st.session_state.is_pro:
        st.success("You're already a Pro member! Thank you for your support. 🎉")
    else:
        st.write("**Most garment types are always free** — Pro unlocks a few premium/formal styles:")
        st.write("- Sizing for: " + ", ".join(PRO_ONLY_GARMENTS))
        st.write("- A detailed downloadable Style Report with personalized styling tips")
        st.markdown("### KSh 100 / one-time unlock")

        st.markdown("**Step 1: Pay**")
        st.link_button("💳 Pay via M-Pesa / Card (PayHero)", PAYMENT_LINK, use_container_width=True)

        st.markdown("**Step 2: Confirm**")
        st.caption(
            "This demo can't automatically detect your payment — that requires a PayHero webhook "
            "and a backend server, which is a stretch goal beyond this project's scope. "
            "Once you've paid, click below to unlock Pro."
        )
        if st.button("✅ I've Paid — Unlock Pro Now", use_container_width=True):
            st.session_state.is_pro = True
            st.rerun()

# =====================================================
# FOOTER
# =====================================================

st.divider()
st.caption("© 2026 SmartFit — Clothing Size Recommendation System")