
import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Set paths
data_folder = "data"
output_folder = "reports"

def calculate_metrics(df):
    total_duration = df['duration'].sum()
    avg_fixation_duration = df['duration'].mean()
    time_to_first_fixation = df['timestamp'].min()

    return {
        "Total Fixation Duration": round(total_duration, 2),
        "Avg Fixation Duration": round(avg_fixation_duration, 2),
        "Time to First Fixation": round(time_to_first_fixation, 2),
        "Efficiency Score": calculate_efficiency_score(avg_fixation_duration, time_to_first_fixation)
    }

def calculate_efficiency_score(avg_fix, time_to_first):
    score = 0
    if avg_fix < 200:
        score += 40
    if time_to_first < 1000:
        score += 30
    if avg_fix < 180 and time_to_first < 800:
        score += 30
    return score

def classify_performance(score):
    if score >= 85:
        return "Efficient"
    elif score >= 70:
        return "Acceptable"
    elif score >= 50:
        return "Needs Attention"
    else:
        return "High Risk"

def generate_pdf_report(worker_id, metrics, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Worker #{worker_id} – Eye Tracking Efficiency Report", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"📅 Date: {datetime.now().strftime('%B %d, %Y')}", ln=True)
    pdf.cell(0, 10, f"🔧 Task: Airbag Housing Assembly", ln=True)
    pdf.cell(0, 10, f"Total Fixation Duration: {metrics['Total Fixation Duration']} ms", ln=True)
    pdf.cell(0, 10, f"Avg Fixation Duration: {metrics['Avg Fixation Duration']} ms", ln=True)
    pdf.cell(0, 10, f"Time to First Fixation: {metrics['Time to First Fixation']} ms", ln=True)
   pdf.cell(0, 10, f"Efficiency Score: {metrics['Efficiency Score']}/100 - {classify_performance(metrics['Efficiency Score'])}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "📝 Notes:\nEfficiency calculated from total gaze data without AOI-specific metrics.")
    pdf.output(output_path)

# Process all CSVs in folder
if __name__ == "__main__":
    for file in os.listdir(data_folder):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(data_folder, file))
            metrics = calculate_metrics(df)
            worker_id = os.path.splitext(file)[0]
            report_path = os.path.join(output_folder, f"{worker_id}_report.pdf")
            generate_pdf_report(worker_id, metrics, report_path)
