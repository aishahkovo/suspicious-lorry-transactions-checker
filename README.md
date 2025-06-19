# suspicious-lorry-transactions-checker
Detect suspicious lorry weighbridge transactions using smart flag rules with a Streamlit-powered app.
# 🚛 Suspicious Lorry Transaction Checker

This Streamlit web app allows users to upload CSV files of weighbridge lorry records and automatically flag suspicious transactions based on defined business rules. It helps identify data anomalies that may indicate weighing manipulation, incorrect durations, or repeated accepted weights.

## 📌 Features

- Upload your own `.csv` lorry weighbridge log
- Applies 4 business logic rules:
  - 🚨 Check-in time gap < 2 minutes
  - 🚨 Trip duration outside the average range
  - 🚨 Large BTM weight differences across trips
  - 🚨 Accepted weight repeated for the same lorry
- Filters and displays only rows matching a custom suspicious pattern
- 💾 Download the filtered result as CSV

## 🧠 Rules Used

| Rule | Description |
|------|-------------|
| 1️⃣ | Check-in time difference < 2 minutes |
| 2️⃣ | Trip duration significantly shorter or longer than average (±40%) |
| 3️⃣ | BTM variation > 1500kg happens more than 2 times per lorry |
| 4️⃣ | Accepted weight same as previous trip for same lorry |

## ▶️ How to Use

1. Run `streamlit run app.py` locally, or
2. Deploy it directly to [Streamlit Cloud](https://streamlit.io/cloud)
3. Upload your CSV file
4. View results and download the suspicious records

## 🧩 Dependencies

Add these to your `requirements.txt`:

