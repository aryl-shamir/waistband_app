# Waistband & Hip Size Prediction App 👖✨  

This project is a **Streamlit web application** that predicts an individual’s **waistband size and hip size** based on their **gender, age, height, and weight**. The prediction is powered by a **Linear Regression model** built in Python and deployed with Streamlit.  

The app was built **gradually after encountering several deployment errors**  

---

## 🌍 Live Demo  

🚀 Try the app here: **[Waistband & Hip Size Predictor](https://waistbandapp-ys7vlhzvtfnwpmnvvl3fcq.streamlit.app/)**  

---

## 🚀 Features  
- Predicts **waistband size** and **hip size** (in cm and inches).  
- Converts predictions from **centimeters to inches** with a custom rounding logic.  
- Provides a **feedback loop** where users can confirm whether the prediction is correct.  
- If incorrect, users can **submit the correct measurements**, which are stored in a connected **Google Sheet** for continuous improvement.  
- Clean and interactive **Streamlit interface** with images and session state management.  

---

## 🛠 Tech Stack  
- **Python** (3.9+)  
- **Streamlit** – for web UI  
- **scikit-learn** – for model building & preprocessing  
- **joblib** – for saving/loading the ML model  
- **Pandas & NumPy** – for data manipulation  
- **Google Sheets API** (`streamlit_gsheets`, `gspread`, `oauth2client`) – for storing user feedback  

---
## 🖥️ How It Works
-**User provides**:
-**Gender (Male/Female)**
-**Age (18–67)**
-**Height (cm)**
-**Weight (kg)**
-**Model predicts waistband and hip size in cm & inches.**

User confirms accuracy:

✅ Yes → Thank-you screen with animation.

❌ No → User submits correct values → Stored in Google Sheets.


