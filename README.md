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
- XGBoost

## Model Evaluation
The test set performance (0 = not delayed, 1 = delayed) 
|              |   precision |   recall |   f1-score |   support |
|:-------------|------------:|---------:|-----------:|----------:|
| 0            |        0.81 |     0.29 |       0.43 |   1344    |
| 1            |        0.39 |     0.87 |       0.54 |    695    |
| accuracy     |        0.49 |     0.49 |       0.49 |      0.49 |
| macro avg    |        0.6  |     0.58 |       0.48 |   2039    |
| weighted avg |        0.66 |     0.49 |       0.46 |   2039    |

## Interactive Features

A Streamlit application allows users to enter flight characteristics and receive an estimated probability of arrival delay exceeding 15 minutes.

The application uses the trained XGBoost model and its corresponding preprocessing pipeline.


## Limitations
- The current dataset covers only three weeks of flight operations due to the API's daily request limit.
- Consequently, the analysis may not capture longer-term trends, seasonal variations, or recurring operational patterns.
- The reliability and generalizability of the findings are expected to improve as additional flight records are collected.
