from fpdf import FPDF
import io
import base64
from datetime import datetime
from PIL import Image

def generate_pdf_report(
    prediction: str, 
    confidence: float, 
    explanation: str, 
    image_base64: str = None,
    estimated_cost: float = None,
    recommendations: str = None,
    damage_percentage: int = None
) -> io.BytesIO:
    # 1. Initialize FPDF2
    pdf = FPDF()
    pdf.add_page()
    
    # 2. Header: "CAR DAMAGE REPORT"
    pdf.set_font("helvetica", 'B', 20)
    pdf.cell(0, 15, "CAR DAMAGE REPORT", ln=True, align="C")
    
    # Horizontal line
    pdf.set_line_width(0.5)
    pdf.line(10, 25, 200, 25)
    pdf.ln(5)
    
    # 3. Report Date
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 10, f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)
    
    # 4. Car Image Integration (Centered)
    if image_base64:
        try:
            # Decode base64
            header, encoded = image_base64.split(",", 1) if "," in image_base64 else (None, image_base64)
            img_data = base64.b64decode(encoded)
            img_ptr = io.BytesIO(img_data)
            
            # Use PIL to get original aspect ratio
            with Image.open(img_ptr) as pil_img:
                w_orig, h_orig = pil_img.size
                aspect = h_orig / w_orig
            
            # Place image in PDF (centered, max width 120mm)
            img_w = 120
            img_h = img_w * aspect
            # Limit max height to 80mm
            if img_h > 80:
                img_h = 80
                img_w = img_h / aspect
            
            x_pos = (210 - img_w) / 2
            pdf.image(img_ptr, x=x_pos, y=None, w=img_w, h=img_h)
            pdf.ln(10)
        except Exception as e:
            print(f"Error embedding image in PDF: {e}")
            pdf.set_text_color(200, 0, 0)
            pdf.cell(0, 10, "[Image could not be rendered]", ln=True, align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(5)

    # 5. Content Sections (Matching Screenshot Style)
    
    # I. PREDICTION RESULT
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "I. PREDICTION RESULT", ln=True)
    pdf.set_font("helvetica", '', 11)
    pdf.cell(0, 8, prediction.replace("_", " "), ln=True)
    pdf.ln(5)
    
    # II. DESCRIPTION
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "II. DESCRIPTION", ln=True)
    pdf.set_font("helvetica", '', 10)
    # Wrap text cleanly
    pdf.multi_cell(0, 6, explanation if explanation else "No detailed description available.")
    pdf.ln(5)
    
    # III. DAMAGE SEVERITY
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "III. DAMAGE SEVERITY", ln=True)
    pdf.set_font("helvetica", '', 11)
    severity_val = f"{damage_percentage}%" if damage_percentage is not None else f"{confidence*100:.1f}%"
    pdf.cell(0, 8, severity_val, ln=True)
    pdf.ln(5)
    
    # IV. ESTIMATED COST
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "IV. ESTIMATED COST", ln=True)
    pdf.set_font("helvetica", '', 11)
    # Using INR (Rupee) or USD ($) depending on logic
    cost_val = estimated_cost if estimated_cost is not None else (confidence * 10000)
    pdf.cell(0, 8, f"INR {cost_val:,.2f}", ln=True)
    pdf.ln(5)
    
    # V. RECOMMENDATIONS
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "V. RECOMMENDATIONS", ln=True)
    pdf.set_font("helvetica", '', 10)
    rec_text = recommendations if recommendations else "Please schedule a professional inspection with an authorized service center."
    pdf.multi_cell(0, 6, rec_text)
    
    # 6. Return PDF as Bytes
    pdf_bytes = pdf.output()
    return io.BytesIO(pdf_bytes)
