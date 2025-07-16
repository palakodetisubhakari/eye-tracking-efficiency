import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Set paths
data_folder = "data"
output_folder = "reports"

# Define AOIs (example coordinates)
AOIs = {
    "Component Bin": ((100, 100), (200, 200)),
    "Instruction Label": ((300, 100), (400, 200)),
    "Tool Area": ((100, 300), (200, 400)),
    "Assembly Zone": ((300, 300), (400, 400))
}

def is_in_aoi(x, y, aoi_bounds):
    (x1, y1), (x2, y2) = aoi_bounds
    return x1 <= x <= x2 and y1 <= y <= y2

def calculate_metrics(df):
    df['AOI'] = 'Outside'
    for name, bounds in AOIs.items():
        mask = df.apply(lambda row: is_in_aoi(row['x'], row['y'], bounds), axis=1)
        df.loc[mask, 'AOI'] = name

    fixation_time = df.groupby('AOI')['duration'].sum()
    total_fixation = fixation_time.sum()

    if total_fixation == 0:
        return {}  # Avoid division by zero or empty results

    aoi_coverage = (total_fixation - fixation_time.get('Outside', 0)) / total_fixation * 100
    avg_fixation_duration = df['duration'].mean()
    time_to_first_fixation = df[df['AOI'] == "Instruction Label"]['timestamp'].min()

    return {
        "AOI Coverage": round(aoi_coverage, 2),
        "Avg Fixation Duration": round(avg_fixation_duration, 2),
        "Time to First Fixation (Instruction Label)": round(time_to_first_fixation, 2) if not pd.isna(time_to_first_fixation) else "N/A",
        "Efficiency Score": calculate_efficiency_score(aoi_coverage, avg_fixation_duration, time_to_first_fixation)
    }

def calculate_efficiency_score(coverage, avg_fix, time_to_first):
    if isinstance(time_to_first, str):  # "N/A" fallback
        time_to_first = 99999
    score = 0
    if coverage >= 90:
        score += 30
    if avg_fix < 200:
        score += 10
    if time_to_first < 1000:
        score += 15
    if coverage > 95:
        score += 20
    if coverage > 85 and avg_fix < 220:
        score += 25
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
    pdf.cell(0, 10, f"Worker #{worker_id} - Eye Tracking Efficiency Report", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%B %d, %Y')}", ln=True)
    pdf.cell(0, 10, "Task: Airbag Housing Assembly", ln=True)
    pdf.cell(0, 10, f"AOI Coverage: {metrics.get('AOI Coverage', 'N/A')}%", ln=True)
    pdf.cell(0, 10, f"Avg Fixation Duration: {metrics.get('Avg Fixation Duration', 'N/A')} ms", ln=True)
    pdf.cell(0, 10, f"Time to First Fixation (Instruction Label): {metrics.get('Time to First Fixation (Instruction Label)', 'N/A')} ms", ln=True)
    score = metrics.get('Efficiency Score', 0)
    pdf.cell(0, 10, f"Efficiency Score: {score}/100 - {classify_performance(score)}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "Notes:\nGood focus observed. Continue monitoring in future tasks.")
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
