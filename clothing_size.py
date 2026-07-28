# =====================================================
# SmartFit - Clothing Size Recommendation System
# =====================================================

# Import required libraries
import streamlit as st
import joblib
import numpy as np

# -----------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------

st.set_page_config(
    page_title="SmartFit",
    page_icon="👕",
    layout="wide"
)

# -----------------------------------------------------
# LOAD TRAINED MODEL
# -----------------------------------------------------

model = joblib.load("clothing_size_model.pkl")

# -----------------------------------------------------
# APPLICATION TITLE
# -----------------------------------------------------

st.title("✨ SmartFit")
st.subheader("Clothing Size Recommendation System")

st.write(
    "Enter your body measurements below to receive your recommended clothing size."
)

st.divider()

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.image("https://img.icons8.com/color/96/t-shirt.png", width=80)

    st.title("SmartFit")

    st.write("Find your perfect clothing size using your body measurements.")

    st.divider()

    st.info(
        """
        **Instructions**

        • Enter your body measurements.

        • Select the correct units.

        • Click **Recommend Size**.

        • SmartFit automatically converts your measurements before making a prediction.
        """
    )

    # =====================================================
# HOW TO MEASURE
# =====================================================

with st.expander("📏 How to Measure"):

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
Measure around your shoulder area as required.

### Arm Length
Measure from the shoulder to the wrist.

### Thigh
Measure around the widest part of your thigh.

### Calf
Measure around the widest part of your calf.

### Leg Length
Measure from your waist to your ankle.
""")



# -----------------------------------------------------
# UNIT CONVERSION FUNCTIONS
# -----------------------------------------------------

# Convert body measurements to millimetres
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


# Convert height from feet and inches to millimetres
def feet_inches_to_mm(feet, inches):

    total_inches = (feet * 12) + inches

    return total_inches * 25.4


# Convert weight to kilograms
def convert_weight(value, unit):

    if unit == "Kilograms (kg)":
        return value

    elif unit == "Pounds (lb)":
        return value * 0.453592

    return value

  # =====================================================
# USER INPUT FORM
# =====================================================

st.header("Enter Your Measurements")

with st.form("measurement_form"):

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    st.subheader("📋 Basic Information")

    basic1, basic2, basic3 = st.columns(3)

    # ---------------- Gender ---------------- #

    with basic1:

        gender = st.selectbox(
            "Gender",
            ["Male", "Female"]
        )

    # ---------------- Height ---------------- #

    with basic2:

        height_unit = st.selectbox(
            "Height Unit",
            ["Centimetres (cm)", "Metres (m)", "Feet & Inches"]
        )

        if height_unit == "Feet & Inches":

            feet = st.number_input(
                "Feet",
                min_value=0,
                value=5
            )

            inches = st.number_input(
                "Inches",
                min_value=0,
                max_value=11,
                value=8
            )

        else:

            height = st.number_input(
                "Height",
                min_value=0.0,
                value=170.0
            )

    # ---------------- Weight ---------------- #

    with basic3:

        weight = st.number_input(
            "Weight",
            min_value=0.0,
            value=70.0
        )

        weight_unit = st.selectbox(
            "Weight Unit",
            ["Kilograms (kg)", "Pounds (lb)"]
        )

    st.divider()

    # =====================================================
       # =====================================================
    # UPPER BODY
    # =====================================================

    st.subheader("👕 Upper Body Measurements")

    # One unit selection for all upper body measurements
    upper_unit = st.selectbox(
        "Upper Body Unit",
        ["Centimetres (cm)", "Millimetres (mm)", "Inches"],
        key="upper_unit"
    )

    upper1, upper2, upper3, upper4 = st.columns(4)

    # Chest
    with upper1:

        chest = st.number_input(
            "Chest",
            min_value=0.0
        )

    # Neck
    with upper2:

        neck = st.number_input(
            "Neck",
            min_value=0.0
        )

    # Shoulder
    with upper3:

        shoulder = st.number_input(
            "Shoulder",
            min_value=0.0
        )

    # Arm Length
    with upper4:

        arm = st.number_input(
            "Arm Length",
            min_value=0.0
        )

    st.divider()
    # =====================================================
        # =====================================================
    # LOWER BODY
    # =====================================================

    st.subheader("👖 Lower Body Measurements")

    lower_unit = st.selectbox(
        "Lower Body Unit",
        ["Centimetres (cm)", "Millimetres (mm)", "Inches"],
        key="lower_unit"
    )

    lower1, lower2, lower3, lower4, lower5 = st.columns(5)

    # Waist
    with lower1:

        waist = st.number_input(
            "Waist",
            min_value=0.0
        )

    # Hip
    with lower2:

        hip = st.number_input(
            "Hip Breadth",
            min_value=0.0
        )

    # Thigh
    with lower3:

        thigh = st.number_input(
            "Thigh",
            min_value=0.0
        )

    # Calf
    with lower4:

        calf = st.number_input(
            "Calf",
            min_value=0.0
        )

    # Leg Length
    with lower5:

        leg = st.number_input(
            "Leg Length",
            min_value=0.0
        )

    st.divider()

    # =====================================================
    # SUBMIT BUTTON
    # =====================================================

    button_col1, button_col2, button_col3 = st.columns([1, 2, 1])

    with button_col2:

        predict_button = st.form_submit_button(
            "✨ Recommend My Size",
            use_container_width=True
        )

    # =====================================================
# MAKE PREDICTION
# =====================================================

if predict_button:

    # Encode gender
    gender_value = 1 if gender == "Male" else 0

    # Convert height
    if height_unit == "Feet & Inches":
        height_mm = feet_inches_to_mm(feet, inches)
    else:
        height_mm = convert_to_mm(height, height_unit)

    # Convert weight
    weight_kg = convert_weight(weight, weight_unit)

    # Convert all body measurements to millimetres
    chest_mm = convert_to_mm(chest, upper_unit)
    neck_mm = convert_to_mm(neck, upper_unit)
    shoulder_mm = convert_to_mm(shoulder, upper_unit)
    arm_mm = convert_to_mm(arm, upper_unit)

    waist_mm = convert_to_mm(waist, lower_unit)
    hip_mm = convert_to_mm(hip, lower_unit)
    thigh_mm = convert_to_mm(thigh, lower_unit)
    calf_mm = convert_to_mm(calf, lower_unit)
    leg_mm = convert_to_mm(leg, lower_unit)

    # Arrange features in the same order used during training
    features = np.array([[
        gender_value,
        height_mm,
        weight_kg,
        chest_mm,
        waist_mm,
        hip_mm,
        neck_mm,
        shoulder_mm,
        arm_mm,
        thigh_mm,
        calf_mm,
        leg_mm
    ]])

    # Make prediction
    prediction = model.predict(features)[0]



    # =====================================================
    # DISPLAY RESULT
    # =====================================================

    st.divider()

    size_names = {
        "XS": "EXTRA SMALL (XS)",
        "S": "SMALL (S)",
        "M": "MEDIUM (M)",
        "L": "LARGE (L)",
        "XL": "EXTRA LARGE (XL)",
        "XXL": "DOUBLE EXTRA LARGE (XXL)",
        "XXXL": "TRIPLE EXTRA LARGE (XXXL)"
    }

    display_size = size_names.get(prediction, prediction)

    st.markdown(
        "<h2 style='text-align:center;'>🎉 Your Perfect Fit</h2>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="
            background:#f8f9fa;
            border-radius:20px;
            padding:35px;
            border:3px solid #4CAF50;
            text-align:center;
        ">
            <h1 style="
                color:#2E8B57;
                font-size:55px;
            ">
                🧍 {display_size}
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.success("Perfect fit found! ✅")


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "© 2026  Clothing Size Recommendation System"
)