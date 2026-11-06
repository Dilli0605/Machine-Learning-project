# Student Performance Prediction System Using Machine Learning

A complete, production-ready college mini-project built with **Python Flask**, **Scikit-learn**, **Pandas**, **SQLite**, and **Bootstrap 5**.

---

## 📌 Project Overview
The **Student Performance Prediction System** allows educational institutions and students to forecast upcoming final examination marks using a supervised machine learning model (**Random Forest Regressor**). It assesses continuous indicators including attendance, previous academic scores, internal assessments, self-study hours, assignment submissions, and class absences.

---

## 💻 Tech Stack
- **Backend:** Python 3.10+ & Flask
- **Machine Learning:** Scikit-learn (RandomForestRegressor)
- **Data Analysis:** Pandas, NumPy
- **Database:** SQLite3
- **Model Serialization:** Joblib
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js

---

## 🚀 Step-by-Step Installation & Execution Guide (Windows / VS Code)

### Step 1: Install Python and VS Code
1. Download and install **Python 3.10+** from [python.org](https://www.python.org/).
   - ⚠️ **Important:** Check the box **"Add Python to PATH"** during installation.
2. Download and install **Visual Studio Code** from [code.visualstudio.com](https://code.visualstudio.com/).
3. In VS Code, install the official **Python Extension** by Microsoft.

### Step 2: Open Project in VS Code
1. Extract or place the project folder:
   ```
   student_performance_prediction/
   ```
2. Open VS Code, go to **File** -> **Open Folder...**, and select the `student_performance_prediction` directory.
3. Open the integrated terminal in VS Code using `Ctrl + `` (or **Terminal** -> **New Terminal**).

### Step 3: Create a Virtual Environment (Recommended)
In the VS Code terminal, run:
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment on Windows
venv\Scripts\activate
```

### Step 4: Install Required Python Libraries
```powershell
pip install -r requirements.txt
```

### Step 5: Initialize the SQLite Database
```powershell
python database/init_db.py
```
*This creates `database/student_system.db` and pre-seeds the administrator account and sample students.*

### Step 6: Train the Machine Learning Model
```powershell
python train_model.py
```
*This reads `dataset/student_data.csv`, splits 80% train / 20% test, calculates MAE, MSE, and R² scores, and saves the trained model to `models/student_performance_model.pkl`.*

### Step 7: Run the Flask Web Application
```powershell
python app.py
```

### Step 8: Open in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Default Credentials for College Viva Demonstration

### Administrator Credentials:
- **Username:** `admin`
- **Password:** `admin123`

### Sample Student Credentials:
- **Roll Number:** `CS2026-001`
- **Password:** `student123`
*(Or register any new student directly using the registration page)*

---

## 🎓 Viva Voce Questions & Answers for Examination

**Q1: Why did you choose Random Forest Regression over Linear Regression?**  
*Answer:* Academic performance exhibits non-linear interactions (e.g., the attendance cliff below 75%, diminishing returns on study hours, and compounding effect of multiple absences). Random forest regression builds an ensemble of decision trees, effectively capturing non-linear feature interactions and preventing overfitting without requiring strict normality assumptions.

**Q2: What evaluation metrics are used to validate the model?**  
*Answer:*  
1. **MAE (Mean Absolute Error):** Measures average absolute deviation between predicted and actual marks in the same unit (marks percentage).
2. **MSE (Mean Squared Error):** Penalizes larger prediction errors more heavily.
3. **RMSE (Root Mean Squared Error):** Square root of MSE, providing error scale in marks.
4. **R² Score (Coefficient of Determination):** Explains the proportion of variance in final marks predicted from the academic features (typically > 0.92 in our trained model).

**Q3: How are missing values handled in the pipeline?**  
*Answer:* In `train_model.py`, the Pandas pipeline removes or imputes missing entries using column mean/median and validates feature types prior to feeding into the Scikit-learn estimator.

**Q4: How does the model file persist in production?**  
*Answer:* Using `joblib.dump(model, 'models/student_performance_model.pkl')` for compact binary serialization, and loaded dynamically at server runtime via `joblib.load()`.
