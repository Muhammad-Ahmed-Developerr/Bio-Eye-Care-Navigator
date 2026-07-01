# 👁️ Bio-Eye Care Navigator

> 🏥 Intelligent Ophthalmic Diagnosis & Visual Acuity Testing System

🔗 **Live App:** [https://bio-eye-care-navigator.streamlit.app/](https://bio-eye-care-navigator.streamlit.app/)

---

## 🚀 Overview

**Bio-Eye Care Navigator** is a biomedical Streamlit-based web application designed to evaluate patient eye health using multi-parameter clinical logic.

It analyzes:

* 👤 Patient Age
* 👁️ Primary Symptom
* 🔍 Visual Acuity (Snellen)
* 📊 Intraocular Pressure (IOP)
* 🧬 Family History

The system then classifies the patient into:

* 🟢 Normal
* 🟡 Abnormal
* 🔴 Critical

And provides:

* 🩺 Condition diagnosis
* 👨‍⚕️ Specialist recommendation
* 💡 Clinical reasoning
* 📄 Downloadable reports (5 formats)

---

## ✨ Features

### 📝 1. Smart Patient Diagnosis

* Multi-parameter clinical decision tree
* Age-adjusted medical logic
* IOP threshold analysis
* Risk factor modification (family history)
* Severity classification engine
* Eye condition visualization

---

### 👓 2. Interactive Snellen Visual Acuity Test

* Built-in Snellen chart
* 20/20 to 20/200 grading
* Automated interpretation
* Personalized recommendations

---

### 📊 3. Patient History & Analytics Dashboard

* Session-based patient record storage
* Color-coded severity tracking
* Summary metrics
* Symptom distribution charts
* Age analysis histogram
* Severity breakdown pie chart
* Export all records to CSV

---

### 💾 4. Multi-Format Report Generation

Each diagnosis can be exported as:

* 📄 TXT Report
* 📊 CSV File
* 📑 PDF Document
* 🖼️ PNG Image
* 📸 JPG Image

Reports include:

* Timestamp
* Patient information
* Condition
* Severity
* Clinical reasons
* Recommendations

---

## 🧠 Clinical Logic Example

```python
if symptom == "Flash of Light":
    if age > 50 or eye_pressure > 21:
        condition = "Retinal Detachment with Glaucoma Risk"
        severity = "Critical"