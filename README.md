# ABAC Policy Classifier

This repository contains the tool developed for my MSc Business Analytics dissertation in partnership with J.P. Morgan. The tool is a rule-based classifier designed to recommend ABAC (Attribute-Based Access Control) policies by identifying patterns in user entitlement data.

The application is deployed using Streamlit and allows users to upload a CSV file, view detected attribute patterns, and receive recommended policy groupings.

## Repository Contents

- `ABAC_Toolset_Notebook.ipynb`: Jupyter notebook showing the development of the tool, including exploratory data analysis (EDA), rule framework logic, and testing. The notebook also contains a final section titled "Archive," which documents early experimentation with machine learning and how it could potentially supplement the tool in future iterations.
- `Sample_Data.csv`: A synthetic dataset created to help users test and validate the tool.

## How It Works

The classifier detects shared attributes across entitlement records and suggests structured ABAC policy recommendations using a set of deterministic rules. The goal is to provide a transparent and scalable approach to policy creation based on common attribute patterns.

## Streamlit App

You can access and interact with the tool using the link below:

[https://abac-toolset.streamlit.app](https://abac-toolset.streamlit.app)
