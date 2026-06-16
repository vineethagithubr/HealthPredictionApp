# HealthPredictionApp

This is a simple AI-powered Health Prediction Web Application built using Streamlit, Python, and SQLite database. The application collects patient health data such as glucose, haemoglobin, and cholesterol levels, and predicts possible health risks using Google Gemini AI. If the AI service is unavailable, the system automatically uses a fallback rule-based prediction model.

The main goal of this project is to demonstrate how AI can be integrated into a real-world healthcare-style application for basic health risk analysis and data management.

The application allows users to:

Add new patient records
View all stored patient data
Update existing patient information
Delete patient records
Get AI-based health risk predictions

All patient data is stored locally using SQLite, ensuring fast and lightweight database management without external dependencies.

This project also includes input validation such as email verification and date-of-birth checks to improve data quality. It demonstrates the combination of frontend UI (Streamlit), backend logic (Python), database handling (SQLite), and AI integration (Gemini API).

Overall, this project is useful for understanding how machine learning APIs and web applications can work together in a simple healthcare prediction system.