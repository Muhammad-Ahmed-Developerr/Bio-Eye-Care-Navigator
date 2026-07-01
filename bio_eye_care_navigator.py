# bio_eye_care_navigator.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import csv
import os
from fpdf import FPDF
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import tempfile
import uuid

# Page configuration
st.set_page_config(
    page_title="Bio-Eye Care Navigator",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
            
        .main-header {
        font-size: 3rem;
        color: #667EEA;
        text-align: center;
        margin-bottom: 0;
        padding-bottom: 0;
        font-weight: bold;
    }
        .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-top: 0;
        padding-top: 0;
        margin-bottom: 2rem;
        font-style: italic;
    }
    .diagnosis-box {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: bold;
    }
    .normal {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .abnormal {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }
    .critical {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px;
        border-radius: 5px;
    }
    .report-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .snellen-row {
        text-align: center; 
        font-size: 72px; 
        font-family: monospace; 
        background-color: #f0f2f6; 
        padding: 40px; 
        border-radius: 10px;
        letter-spacing: 10px;
    }
    .download-link {
        display: inline-block;
        padding: 8px 16px;
        margin: 5px;
        background-color: #4CAF50;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        font-weight: bold;
        text-align: center;
        width: 100%;
    }
    .download-link:hover {
        background-color: #45a049;
    }
    .success-message {
        padding: 10px;
        background-color: #d4edda;
        color: #155724;
        border-radius: 4px;
        margin: 10px 0;
    }
    .feature-box {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    .eye-image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px;
    }
    .eye-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state with more comprehensive structure
if 'patients' not in st.session_state:
    st.session_state.patients = []
if 'current_report' not in st.session_state:
    st.session_state.current_report = None
if 'generated_reports' not in st.session_state:
    st.session_state.generated_reports = {}
if 'last_diagnosis' not in st.session_state:
    st.session_state.last_diagnosis = None
if 'report_id' not in st.session_state:
    st.session_state.report_id = None

# ============= USER-DEFINED FUNCTIONS =============

def get_eye_image_for_symptom(symptom):
    """
    Return appropriate eye image URL based on symptom
    Using high-quality medical eye images
    """
    eye_images = {
        "Flash of Light": "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=400&h=300&fit=crop",
        "Blurry Vision": "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=400&h=300&fit=crop",
        "Red Eyes": "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=400&h=300&fit=crop",
        "Eye Strain": "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=400&h=300&fit=crop",
        "default": "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=400&h=300&fit=crop"
    }
    return eye_images.get(symptom, eye_images["default"])

def analyze_symptoms(symptom, age, visual_acuity, eye_pressure, family_history):
    """
    Analyze patient symptoms and determine condition based on all parameters
    Returns: condition, severity, specialist, recommendations
    """
    
    # Convert visual acuity to numeric for comparison
    try:
        acuity_numeric = float(visual_acuity.split('/')[1])
    except:
        acuity_numeric = 40
    
    # Base analysis on symptom
    if symptom == "Flash of Light":
        if age > 50 or eye_pressure > 21:
            condition = "Retinal Detachment with Glaucoma Risk"
            severity = "Critical"
            specialist = "Emergency Retinal Surgeon"
            reasons = [
                "Sudden photopsia indicates retinal traction in older patient",
                f"Elevated IOP ({eye_pressure} mmHg) suggests glaucoma comorbidity",
                "High myopia risk factor present",
                "Previous retinal pathology in family history" if family_history != "None" else "No family history but acute symptoms"
            ]
            recommendations = [
                "IMMEDIATE emergency room visit within 2 hours",
                "Absolute bed rest with head elevated",
                "No eye rubbing or pressure on eyes",
                "Avoid straining, bending, or heavy lifting",
                "Urgent ophthalmology consultation required"
            ]
        else:
            condition = "Acute Photopsia - Possible Posterior Vitreous Detachment"
            severity = "Abnormal"
            specialist = "Retina Specialist"
            reasons = [
                "Sudden flash of light in younger patient",
                "Rule out retinal tear or detachment",
                "Vitreous traction on retina suspected"
            ]
            recommendations = [
                "Schedule urgent eye exam within 24-48 hours",
                "Dilated fundus examination required",
                "Avoid vigorous activities",
                "Monitor for curtain-like vision loss"
            ]
    
    elif symptom == "Blurry Vision":
        if age > 60:
            condition = "Age-related Cataract with Macular Changes"
            severity = "Abnormal"
            specialist = "Cataract and Retina Specialist"
            reasons = [
                "Age-related lens opacity typical for >60 years",
                f"Visual acuity {visual_acuity} indicates significant vision loss",
                "Possible early macular degeneration"
            ]
            recommendations = [
                "Comprehensive eye exam with OCT scanning",
                "Cataract surgery evaluation if vision affects daily life",
                "Amsler grid monitoring for metamorphopsia",
                "Consider blue light filtering glasses"
            ]
        elif age > 40:
            condition = "Presbyopia with Early Cataract"
            severity = "Abnormal"
            specialist = "Optometrist"
            reasons = [
                "Age-appropriate accommodative loss",
                f"Current acuity {visual_acuity} below age-adjusted normal",
                "Early lens changes suspected"
            ]
            recommendations = [
                "Complete refraction for new glasses",
                "Consider progressive addition lenses",
                "Anti-glare coating for night driving",
                "Review in 6 months for cataract progression"
            ]
        else:
            condition = "Refractive Error / Accommodative Spasm"
            severity = "Normal"
            specialist = "Optometrist"
            reasons = [
                "Young age with correctable vision issues",
                "Possible digital eye strain component",
                "No signs of organic disease"
            ]
            recommendations = [
                "Full cycloplegic refraction",
                "Consider computer glasses if prolonged screen use",
                "20-20-20 rule for eye strain",
                "Artificial tears if associated dryness"
            ]
    
    elif symptom == "Red Eyes":
        if eye_pressure > 24:
            condition = "Acute Angle-Closure Glaucoma"
            severity = "Critical"
            specialist = "Emergency Glaucoma Specialist"
            reasons = [
                f"Critically elevated IOP ({eye_pressure} mmHg)",
                "Angle closure suspected",
                "Ocular emergency requiring immediate intervention"
            ]
            recommendations = [
                "IMMEDIATE emergency room - do NOT wait",
                "Do NOT take any anticholinergic medications",
                "Keep head elevated",
                "Prepare for possible laser iridotomy"
            ]
        elif "Glaucoma" in family_history:
            condition = "Inflammatory Glaucoma Suspect"
            severity = "Abnormal"
            specialist = "Glaucoma Specialist"
            reasons = [
                "Family history of glaucoma",
                f"Elevated IOP ({eye_pressure} mmHg)",
                "Active inflammation present"
            ]
            recommendations = [
                "Urgent glaucoma workup within 1 week",
                "Visual field testing required",
                "Gonioscopy to assess angle",
                "Start IOP-lowering medication if confirmed"
            ]
        else:
            condition = "Allergic Conjunctivitis / Dry Eye"
            severity = "Normal"
            specialist = "Optometrist"
            reasons = [
                "Bilateral involvement typical of allergy",
                "No signs of acute angle closure",
                "Likely environmental trigger"
            ]
            recommendations = [
                "Cold compresses for relief",
                "Preservative-free artificial tears 4-6x daily",
                "Avoid known allergens",
                "Consider antihistamine eye drops if severe"
            ]
    
    elif symptom == "Eye Strain":
        if acuity_numeric > 40:
            condition = "Uncorrected Refractive Error with Asthenopia"
            severity = "Abnormal"
            specialist = "Optometrist"
            reasons = [
                f"Poor visual acuity ({visual_acuity}) contributing to strain",
                "Accommodative fatigue from constant effort",
                "Likely need for optical correction"
            ]
            recommendations = [
                "Comprehensive eye exam for glasses prescription",
                "Consider blue-blocking lenses for screen work",
                "Optimize workstation ergonomics",
                "Use proper lighting - avoid glare"
            ]
        else:
            condition = "Computer Vision Syndrome / Digital Eye Strain"
            severity = "Normal"
            specialist = "Optometrist"
            reasons = [
                "Good visual acuity but prolonged near work",
                "Reduced blink rate with screen use",
                "Accommodative-vergence mismatch"
            ]
            recommendations = [
                "Follow 20-20-20 rule: every 20 min, look 20 ft for 20 sec",
                "Increase blink frequency consciously",
                "Use artificial tears before screen time",
                "Adjust screen brightness to match ambient light",
                "Consider computer glasses with anti-reflective coating"
            ]
    
    # Adjust for high eye pressure regardless of symptom
    if eye_pressure > 25:
        condition += " - HYPERTENSIVE CRISIS"
        severity = "Critical"
        specialist = "Emergency Glaucoma Specialist"
        recommendations.insert(0, "URGENT: IOP >25 requires immediate evaluation")
    
    return {
        "condition": condition,
        "severity": severity,
        "specialist": specialist,
        "reasons": reasons,
        "recommendations": recommendations
    }

def calculate_visual_acuity_score(selected_row):
    """
    Calculate Snellen visual acuity based on row read with proper mapping
    """
    snellen_mapping = {
        "DEFPOTEC": "20/20",
        "EDFCZP": "20/30",
        "PECFD": "20/40",
        "LPED": "20/50",
        "TOZ": "20/70",
        "FP": "20/100",
        "E": "20/200",
        "POTEC": "20/40",
        "OTEC": "20/50",
        "TEC": "20/60",
        "EC": "20/70",
        "C": "20/100"
    }
    return snellen_mapping.get(selected_row, "20/40")

def generate_report_filename(patient_name, format_type):
    """Generate unique filename for report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = patient_name.replace(" ", "_").replace("/", "_")
    return f"{safe_name}_{timestamp}.{format_type}"

def save_report_txt(patient_data, analysis_result):
    """Save report as TXT file and return file data for download"""
    filename = generate_report_filename(patient_data['name'], 'txt')
    content = f"""
========================================
    BIO-EYE CARE NAVIGATOR REPORT
========================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PATIENT INFORMATION:
-------------------
Name: {patient_data['name']}
Age: {patient_data['age']}
Primary Symptom: {patient_data['symptom']}
Visual Acuity: {patient_data['visual_acuity']}
Eye Pressure: {patient_data['eye_pressure']} mmHg
Family History: {patient_data['family_history']}

DIAGNOSTIC ANALYSIS:
-------------------
Condition: {analysis_result['condition']}
Severity: {analysis_result['severity']}
Recommended Specialist: {analysis_result['specialist']}

CLINICAL REASONS:
----------------
{chr(10).join(['- ' + reason for reason in analysis_result['reasons']])}

RECOMMENDATIONS:
---------------
{chr(10).join(['- ' + rec for rec in analysis_result['recommendations']])}

========================================
This is a computer-generated report.
Please consult with a healthcare professional.
========================================
"""
    
    # Return as bytes for download
    return filename, content.encode('utf-8')

def save_report_csv(patient_data, analysis_result):
    """Save report as CSV file and return file data for download"""
    filename = generate_report_filename(patient_data['name'], 'csv')
    
    data = {
        'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        'Patient Name': [patient_data['name']],
        'Age': [patient_data['age']],
        'Symptom': [patient_data['symptom']],
        'Visual Acuity': [patient_data['visual_acuity']],
        'Eye Pressure': [patient_data['eye_pressure']],
        'Family History': [patient_data['family_history']],
        'Condition': [analysis_result['condition']],
        'Severity': [analysis_result['severity']],
        'Specialist': [analysis_result['specialist']],
        'Recommendations': ['; '.join(analysis_result['recommendations'])]
    }
    
    df = pd.DataFrame(data)
    
    # Return as bytes for download
    csv_bytes = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    return filename, csv_bytes

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Bio-Eye Care Navigator Report', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def save_report_pdf(patient_data, analysis_result):
    """Save report as PDF file and return file data for download"""
    filename = generate_report_filename(patient_data['name'], 'pdf')
    
    pdf = PDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font('Arial', '', 11)
    
    # Date
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 6, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
    pdf.ln(5)
    
    # Patient Information
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'PATIENT INFORMATION:', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 6, f"Name: {patient_data['name']}", 0, 1)
    pdf.cell(0, 6, f"Age: {patient_data['age']} years", 0, 1)
    pdf.cell(0, 6, f"Primary Symptom: {patient_data['symptom']}", 0, 1)
    pdf.cell(0, 6, f"Visual Acuity: {patient_data['visual_acuity']}", 0, 1)
    pdf.cell(0, 6, f"Eye Pressure: {patient_data['eye_pressure']} mmHg", 0, 1)
    pdf.cell(0, 6, f"Family History: {patient_data['family_history']}", 0, 1)
    pdf.ln(5)
    
    # Diagnostic Analysis
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'DIAGNOSTIC ANALYSIS:', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    # Condition with proper encoding
    pdf.multi_cell(0, 6, f"Condition: {analysis_result['condition']}")
    pdf.cell(0, 6, f"Severity: {analysis_result['severity']}", 0, 1)
    pdf.cell(0, 6, f"Specialist: {analysis_result['specialist']}", 0, 1)
    pdf.ln(5)
    
    # Clinical Reasons
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'CLINICAL REASONS:', 0, 1)
    pdf.set_font('Arial', '', 11)
    for reason in analysis_result['reasons']:
        pdf.multi_cell(0, 5, f"- {reason}")
    pdf.ln(5)
    
    # Recommendations
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'RECOMMENDATIONS:', 0, 1)
    pdf.set_font('Arial', '', 11)
    for rec in analysis_result['recommendations']:
        pdf.multi_cell(0, 5, f"- {rec}")
    
    # Return as bytes for download
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return filename, pdf_bytes

def save_report_image(patient_data, analysis_result, format_type='PNG'):
    """
    Save report as image and return file data for download
    format_type: 'PNG' or 'JPEG' (note: PIL uses 'JPEG', not 'JPG')
    """
    # Map format for filename and PIL
    if format_type.upper() == 'JPG':
        pil_format = 'JPEG'
        file_ext = 'jpg'
    else:
        pil_format = format_type.upper()
        file_ext = format_type.lower()
    
    filename = generate_report_filename(patient_data['name'], file_ext)
    
    # Create image with larger size for better readability
    img = Image.new('RGB', (1000, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fallback to default
    try:
        # Try different font paths for different OS
        font_paths = [
            "arial.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
            "/Library/Fonts/Arial.ttf"
        ]
        font_large = None
        font_medium = None
        font_small = None
        
        for path in font_paths:
            try:
                font_large = ImageFont.truetype(path, 28)
                font_medium = ImageFont.truetype(path, 20)
                font_small = ImageFont.truetype(path, 16)
                break
            except:
                continue
        
        if font_large is None:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    y_position = 30
    margin = 40
    
    # Title
    draw.text((margin, y_position), "BIO-EYE CARE NAVIGATOR REPORT", fill=(0, 51, 102), font=font_large)
    y_position += 40
    
    # Date
    draw.text((margin, y_position), f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
              fill=(100, 100, 100), font=font_small)
    y_position += 35
    
    # Patient Information
    draw.text((margin, y_position), "PATIENT INFORMATION:", fill=(0, 102, 204), font=font_medium)
    y_position += 25
    draw.text((margin+20, y_position), f"Name: {patient_data['name']}", fill=(0, 0, 0), font=font_small)
    y_position += 20
    draw.text((margin+20, y_position), f"Age: {patient_data['age']} years", fill=(0, 0, 0), font=font_small)
    y_position += 20
    draw.text((margin+20, y_position), f"Symptom: {patient_data['symptom']}", fill=(0, 0, 0), font=font_small)
    y_position += 20
    draw.text((margin+20, y_position), f"Visual Acuity: {patient_data['visual_acuity']}", fill=(0, 0, 0), font=font_small)
    y_position += 20
    draw.text((margin+20, y_position), f"Eye Pressure: {patient_data['eye_pressure']} mmHg", fill=(0, 0, 0), font=font_small)
    y_position += 20
    draw.text((margin+20, y_position), f"Family History: {patient_data['family_history']}", fill=(0, 0, 0), font=font_small)
    y_position += 30
    
    # Diagnostic Analysis
    draw.text((margin, y_position), "DIAGNOSTIC ANALYSIS:", fill=(0, 102, 204), font=font_medium)
    y_position += 25
    
    # Color-code severity
    severity_color = {
        "Normal": (0, 100, 0),
        "Abnormal": (255, 140, 0),
        "Critical": (255, 0, 0)
    }.get(analysis_result['severity'], (0, 0, 0))
    
    draw.text((margin+20, y_position), f"Condition: {analysis_result['condition']}", fill=(0, 0, 0), font=font_small)
    y_position += 20
    draw.text((margin+20, y_position), f"Severity: {analysis_result['severity']}", fill=severity_color, font=font_small)
    y_position += 20
    draw.text((margin+20, y_position), f"Specialist: {analysis_result['specialist']}", fill=(102, 0, 204), font=font_small)
    y_position += 30
    
    # Recommendations
    draw.text((margin, y_position), "RECOMMENDATIONS:", fill=(0, 102, 204), font=font_medium)
    y_position += 25
    
    for rec in analysis_result['recommendations']:
        # Wrap text if too long
        words = rec.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Approximate text width (rough estimation)
            if len(test_line) * 7 < 800:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for line in lines:
            draw.text((margin+20, y_position), f"• {line}", fill=(0, 0, 0), font=font_small)
            y_position += 20
    
    # Footer
    y_position = 750
    draw.text((margin, y_position), "This is a computer-generated report. Consult with a healthcare professional.", 
              fill=(150, 150, 150), font=font_small)
    
    # Return as bytes for download - using correct PIL format
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=pil_format)
    img_bytes = img_bytes.getvalue()
    
    return filename, img_bytes

def create_download_button(file_data, filename, button_text, key=None):
    """Create a persistent download button using st.download_button"""
    return st.download_button(
        label=button_text,
        data=file_data,
        file_name=filename,
        mime="application/octet-stream",
        key=key,
        use_container_width=True
    )

# ============= MAIN APPLICATION =============

def main():
    # Header
    st.markdown('<h1 class="main-header">👁️ Bio-Eye Care Navigator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Intelligent Ophthalmic Diagnosis & Visual Acuity Testing System</p>', unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Patient Diagnosis", "👓 Visual Acuity Test", "📊 Patient History", "ℹ️ About"])
    
    with tab1:
        show_diagnosis_page()
    with tab2:
        show_acuity_test()
    with tab3:
        show_history()
    with tab4:
        show_about()

def show_diagnosis_page():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Patient Information")
        st.markdown("Enter patient details for ophthalmic analysis")
        
        with st.form("patient_form"):
            name = st.text_input("**Patient Full Name**", value="Ahmed", 
                                 help="Enter patient's full name")
            age = st.number_input("**Age (years)**", min_value=0, max_value=120, value=18, step=1,
                                  help="Enter patient's age in years")
            
            symptom = st.selectbox(
                "**Select Primary Symptom**",
                ["Flash of Light", "Blurry Vision", "Red Eyes", "Eye Strain"],
                help="Choose the main symptom the patient is experiencing"
            )
            
            visual_acuity = st.select_slider(
                "**Visual Acuity (Snellen)**",
                options=["20/20", "20/30", "20/40", "20/50", "20/70", "20/100", "20/200"],
                value="20/40",
                help="Normal: 20/20 vision"
            )
            
            eye_pressure = st.slider("**Eye Pressure (mmHg)**", min_value=8, max_value=40, value=21, 
                                    help="Normal range: 10-21 mmHg")
            
            family_history = st.radio(
                "**Family History of Eye Disease**",
                ["None", "Glaucoma", "Cataract", "Macular Degeneration", "Diabetic Retinopathy"],
                index=0,
                help="Select any family history of eye conditions"
            )
            
            submitted = st.form_submit_button("🔍 Run Diagnosis", use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Diagnostic Results")
        
        # Display eye image based on symptom
        if submitted:
            # Store patient data
            patient_data = {
                'name': name,
                'age': age,
                'symptom': symptom,
                'visual_acuity': visual_acuity,
                'eye_pressure': eye_pressure,
                'family_history': family_history,
                'timestamp': datetime.now()
            }
            
            # Analyze symptoms with all parameters
            analysis_result = analyze_symptoms(symptom, age, visual_acuity, eye_pressure, family_history)
            
            # Store in session with unique ID
            report_id = str(uuid.uuid4())
            st.session_state.last_diagnosis = {
                'patient': patient_data,
                'analysis': analysis_result,
                'report_id': report_id
            }
            
            st.session_state.patients.append({**patient_data, **analysis_result})
            
            # Store report in session state
            st.session_state.generated_reports[report_id] = {
                'patient': patient_data['name'],
                'reports': {}
            }
            
            st.success("✅ Diagnosis Complete! Reports ready for download.")
            
            # Display results
            display_diagnosis_results(patient_data, analysis_result, report_id)
        
        elif st.session_state.last_diagnosis:
            # Show previous results if available
            diagnosis = st.session_state.last_diagnosis
            patient_data = diagnosis['patient']
            analysis_result = diagnosis['analysis']
            report_id = diagnosis['report_id']
            
            display_diagnosis_results(patient_data, analysis_result, report_id)
        
        else:
            st.info("👈 Please enter patient details and click 'Run Diagnosis'")
            
            # Show sample eye image
            st.markdown("""
            <div class="eye-card">
                <h4>👁️ Eye Health Assessment</h4>
                <img src="https://images.unsplash.com/photo-1576086213369-97a306d36557?w=400&h=300&fit=crop" 
                     style="width: 100%; max-width: 400px; border-radius: 10px; margin: 10px 0;">
                <p style="color: #666;">Enter patient details and run diagnosis to see results</p>
            </div>
            """, unsafe_allow_html=True)

def display_diagnosis_results(patient_data, analysis_result, report_id):
    """Display diagnosis results with all components"""
    
    # Show eye image
    eye_img_url = get_eye_image_for_symptom(patient_data['symptom'])
    st.markdown(f"""
    <div class="eye-card">
        <h4>👁️ Eye Condition Visualization</h4>
        <img src="{eye_img_url}" style="width: 100%; max-width: 400px; border-radius: 10px; margin: 10px 0;">
    </div>
    """, unsafe_allow_html=True)
    
    # Display results with appropriate styling
    severity_class = {
        "Normal": "normal",
        "Abnormal": "abnormal",
        "Critical": "critical"
    }.get(analysis_result['severity'], "normal")
    
    st.markdown(f"""
    <div class="diagnosis-box {severity_class}">
        <h3>Analysis: {analysis_result['condition']}</h3>
        <p><strong>Severity Level:</strong> {analysis_result['severity']}</p>
        <p><strong>Specialist Mapping:</strong> {analysis_result['specialist']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Clinical Reasons
    with st.expander("🔬 Clinical Reasons"):
        for reason in analysis_result['reasons']:
            st.markdown(f"• {reason}")
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    for rec in analysis_result['recommendations']:
        st.info(rec)
    
    # Report Generation Section
    st.markdown("### 💾 Download Reports")
    st.markdown("Click any button below to download reports.")
    
    # Create columns for download buttons
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    
    with col_a:
        filename, file_data = save_report_txt(patient_data, analysis_result)
        create_download_button(file_data, filename, "📄 TXT", key=f"download_txt_{report_id}")
    
    with col_b:
        filename, file_data = save_report_csv(patient_data, analysis_result)
        create_download_button(file_data, filename, "📊 CSV", key=f"download_csv_{report_id}")
    
    with col_c:
        filename, file_data = save_report_pdf(patient_data, analysis_result)
        create_download_button(file_data, filename, "📑 PDF", key=f"download_pdf_{report_id}")
    
    with col_d:
        filename, file_data = save_report_image(patient_data, analysis_result, 'PNG')
        create_download_button(file_data, filename, "🖼️ PNG", key=f"download_png_{report_id}")
    
    with col_e:
        filename, file_data = save_report_image(patient_data, analysis_result, 'JPG')
        create_download_button(file_data, filename, "📸 JPG", key=f"download_jpg_{report_id}")
    
    # Update stored reports with actual data
    st.session_state.generated_reports[report_id] = {
        'patient': patient_data['name'],
        'reports': {
            'txt': {'filename': filename, 'data': file_data},
            'csv': {'filename': filename, 'data': file_data},
            'pdf': {'filename': filename, 'data': file_data},
            'png': {'filename': filename, 'data': file_data},
            'jpg': {'filename': filename, 'data': file_data}
        }
    }

def show_acuity_test():
    st.markdown("## 👓 Snellen Visual Acuity Test")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Test Instructions")
        st.info("""
        1. Position yourself 2 feet away from screen
        2. Cover one eye at a time
        3. Try to read the letters below
        4. Select the smallest row you can read clearly
        """)
        
        st.markdown("### Snellen Chart (20 ft equivalent)")
        
        chart_data = {
            "20/200": "**E**",
            "20/100": "**F P**",
            "20/70": "**T O Z**",
            "20/50": "**L P E D**",
            "20/40": "**P E C F D**",
            "20/30": "**E D F C Z P**",
            "20/20": "**D E F P O T E C**"
        }
        
        for acuity, letters in chart_data.items():
            st.markdown(f"**{acuity}:** {letters}")
    
    with col2:
        st.markdown("### Test Your Vision")
        
        # Large display of test row with proper Snellen letters
        st.markdown("""
        <div class="snellen-row">
            DEFPOTEC
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='text-align: center;'>Can you read this row from 2 feet away?</p>", 
                   unsafe_allow_html=True)
        
        # Snellen dropdown with proper letter combinations
        snellen_options = {
            "DEFPOTEC (20/20)": "DEFPOTEC",
            "EDFCZP (20/30)": "EDFCZP",
            "PECFD (20/40)": "PECFD",
            "LPED (20/50)": "LPED",
            "TOZ (20/70)": "TOZ",
            "FP (20/100)": "FP",
            "E (20/200)": "E"
        }
        
        selected_option = st.selectbox(
            "Select the row you can read clearly:",
            list(snellen_options.keys())
        )
        
        if st.button("Calculate Visual Acuity", use_container_width=True):
            selected_row = snellen_options[selected_option]
            acuity = calculate_visual_acuity_score(selected_row)
            st.success(f"📊 Your visual acuity is: **{acuity}**")
            
            # Personalized interpretation based on acuity
            if acuity == "20/20":
                st.balloons()
                st.success("🎉 Excellent vision! You have normal visual acuity.")
                st.info("**Recommendation:** Regular eye checkup every 2 years")
            elif acuity in ["20/30", "20/40"]:
                st.warning("👓 Mild vision impairment detected")
                st.info("""
                **Recommendations:**
                - Schedule comprehensive eye exam
                - Consider glasses for driving at night
                - Practice good lighting while reading
                """)
            elif acuity in ["20/50", "20/60", "20/70"]:
                st.error("⚠️ Moderate vision impairment")
                st.info("""
                **Recommendations:**
                - Urgent eye examination needed
                - Likely need prescription glasses
                - Avoid driving until vision corrected
                - Consider low vision aids
                """)
            else:
                st.error("🚨 Significant vision impairment detected")
                st.info("""
                **CRITICAL RECOMMENDATIONS:**
                - Schedule immediate comprehensive eye exam
                - Legal requirements for driving may not be met
                - Consider referral to low vision specialist
                - Explore vision rehabilitation services
                """)

def show_history():
    st.markdown("### 📈 Patient History & Trends")
    
    if st.session_state.patients:
        # Convert to DataFrame for display
        df = pd.DataFrame(st.session_state.patients)
        
        # Format timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Select columns for display
        display_cols = ['timestamp', 'name', 'age', 'symptom', 'visual_acuity', 
                       'eye_pressure', 'condition', 'severity', 'specialist']
        
        # Rename for better display
        display_df = df[display_cols].copy()
        display_df.columns = ['Date/Time', 'Name', 'Age', 'Symptom', 'Visual Acuity', 
                            'IOP (mmHg)', 'Condition', 'Severity', 'Specialist']
        
        # Define color mapping function for Styler
        def color_severity(val):
            if val == 'Critical':
                return 'background-color: #ffcccc'
            elif val == 'Abnormal':
                return 'background-color: #fff3cd'
            elif val == 'Normal':
                return 'background-color: #d4edda'
            return ''
        
        # FIX: Use 'map' instead of deprecated 'applymap'
        styled_df = display_df.style.map(color_severity, subset=['Severity'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Statistics
        st.markdown("### 📊 Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            severity_counts = df['severity'].value_counts()
            st.metric("Critical Cases", severity_counts.get('Critical', 0))
        
        with col2:
            st.metric("Total Patients", len(df))
        
        with col3:
            common_symptom = df['symptom'].mode()[0] if not df.empty else "N/A"
            st.metric("Most Common Symptom", common_symptom)
        
        with col4:
            avg_age = df['age'].mean() if not df.empty else 0
            st.metric("Average Age", f"{avg_age:.1f} years")
        
        # Visualizations
        st.markdown("### 📈 Analytics Dashboard")
        
        tab1, tab2, tab3 = st.tabs(["Symptom Distribution", "Severity Breakdown", "Age Analysis"])
        
        with tab1:
            fig, ax = plt.subplots(figsize=(10, 5))
            symptom_counts = df['symptom'].value_counts()
            colors = ['#667eea', '#764ba2', '#ff6b6b', '#4ecdc4']
            ax.bar(symptom_counts.index, symptom_counts.values, color=colors[:len(symptom_counts)])
            ax.set_title('Symptom Distribution', fontsize=14, fontweight='bold')
            ax.set_xlabel('Symptoms')
            ax.set_ylabel('Number of Cases')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        
        with tab2:
            fig, ax = plt.subplots(figsize=(8, 8))
            severity_counts = df['severity'].value_counts()
            colors = {'Normal': '#4CAF50', 'Abnormal': '#FF9800', 'Critical': '#F44336'}
            ax.pie(severity_counts.values, labels=severity_counts.index, autopct='%1.1f%%',
                   colors=[colors.get(x, '#999999') for x in severity_counts.index])
            ax.set_title('Severity Distribution', fontsize=14, fontweight='bold')
            st.pyplot(fig)
        
        with tab3:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.hist(df['age'], bins=15, color='#667eea', edgecolor='white', alpha=0.7)
            ax.set_title('Age Distribution of Patients', fontsize=14, fontweight='bold')
            ax.set_xlabel('Age (years)')
            ax.set_ylabel('Number of Patients')
            st.pyplot(fig)
        
        # Export all records
        if st.button("📥 Export All Records to CSV", use_container_width=True):
            csv_filename = f"all_patients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            csv_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            
            st.download_button(
                label="📥 Download All Records CSV",
                data=csv_data,
                file_name=csv_filename,
                mime="text/csv",
                key="download_all_csv"
            )
        
        # Clear history button
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.patients = []
            st.session_state.generated_reports = {}
            st.session_state.last_diagnosis = None
            st.rerun()
    
    else:
        st.info("📭 No patient records yet. Run some diagnoses first!")

def show_about():
    st.markdown("### ℹ️ About Bio-Eye Care Navigator")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h2>👁️ Bio-Eye Care Navigator</h2>
            <h3>Intelligent Ophthalmic Diagnosis & Visual Acuity Testing System</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
            <h3>📋 System Overview</h3>
            <p>This application implements a <b>Bio-Eye Care Navigator</b> that processes patient symptoms, 
            visual acuity measurements, intraocular pressure, and family history to evaluate ophthalmic 
            patient health status and provide clinical decision support.</p>
            <p><b>Clinical Significance:</b> Eye diseases affect millions worldwide, and early detection 
            with proper triage can prevent blindness. This system demonstrates how computational thinking 
            can assist in medical decision-making by classifying patients into appropriate care pathways.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
            <h3>🧠 System Logic & Design</h3>
            <p><b>Core Logic:</b> The program uses a multi-parameter decision tree algorithm that analyzes:</p>
            <ol>
                <li><b>Symptom-based branching:</b> Different decision paths for Flash of Light, Blurry Vision, Red Eyes, and Eye Strain</li>
                <li><b>Threshold-based classification:</b> IOP levels (normal <21 mmHg, suspect 21-25, emergency >25)</li>
                <li><b>Age-adjusted rules:</b> Age-specific condition probabilities (e.g., cataract risk >60 years)</li>
                <li><b>Risk factor modification:</b> Family history modifies diagnostic probability</li>
                <li><b>Visual acuity grading:</b> Snellen chart interpretation for vision impairment staging</li>
            </ol>
            <p><b>Decision Logic Example:</b> If symptom is "Flash of Light" AND age >50 AND IOP >21 → "Retinal Detachment with Glaucoma Risk" (CRITICAL)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
            <h3>🔬 Clinical Parameters Assessed</h3>
            <ul>
                <li><b>Flash of Light:</b> Retinal detachment, posterior vitreous detachment</li>
                <li><b>Blurry Vision:</b> Cataract, refractive error, presbyopia</li>
                <li><b>Red Eyes:</b> Acute glaucoma, allergic conjunctivitis, dry eye</li>
                <li><b>Eye Strain:</b> Computer vision syndrome, uncorrected refractive error</li>
                <li><b>Intraocular Pressure (IOP):</b> Glaucoma risk assessment</li>
                <li><b>Visual Acuity:</b> Snellen chart based vision assessment</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <h3>🏆 Key Features</h3>
            <ul>
                <li>✓ Multi-parameter clinical diagnosis</li>
                <li>✓ 3-level severity classification</li>
                <li>✓ 5 export formats (TXT, CSV, PDF, PNG, JPG)</li>
                <li>✓ Interactive visual acuity testing</li>
                <li>✓ Patient history analytics</li>
                <li>✓ Clinical decision support</li>
                <li>✓ Eye condition visualization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
            <h3>👨‍⚕️ Specialist Mapping</h3>
            <ul>
                <li><b>Emergency Retinal Surgeon:</b> Retinal detachment</li>
                <li><b>Retina Specialist:</b> PVD, retinal tears</li>
                <li><b>Cataract Surgeon:</b> Age-related cataracts</li>
                <li><b>Glaucoma Specialist:</b> High IOP, angle-closure</li>
                <li><b>Optometrist:</b> Refractive errors, eye strain</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
            <h3>📊 Technology Stack</h3>
            <ul>
                <li>🐍 Python</li>
                <li>🎨 Streamlit</li>
                <li>📊 Pandas</li>
                <li>📈 Matplotlib</li>
                <li>🖼️ PIL</li>
                <li>📑 FPDF</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    
    # Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 1rem;'>
    Bio-Eye Care Navigator | Intelligent Ophthalmic Diagnosis System
</div>
""", unsafe_allow_html=True)