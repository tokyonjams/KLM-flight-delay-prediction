# KLM Flight Delay Prediction

An end-to-end data engineering and machine learning project that investigates the prediction of flight delays at Amsterdam Schiphol Airport using operational flight data from the Air France-KLM API.

## Project Objectives

- Build an automated ETL pipeline to collect and process flight data.
- Store structured flight information in a MySQL database.
- Investigate the relationship between operational and temporal flight characteristics and departure delays.
- Compare machine learning classification models for pre-departure delay prediction.

## Technologies

Python · Pandas · NumPy · MySQL · SQLAlchemy · Scikit-learn · XGBoost

## Pipeline

API data extraction → JSON transformation → Data cleaning and validation → MySQL → Feature engineering → Model training and evaluation

## Machine Learning Models

- Logistic Regression
- Random Forest
- Decision Tree
- k-Nearest Neighbors
- XGBoost

## Limitations
- The current dataset covers only three weeks of flight operations due to the API's daily request limit.
- Consequently, the analysis may not capture longer-term trends, seasonal variations, or recurring operational patterns.
- The reliability and generalizability of the findings are expected to improve as additional flight records are collected.
