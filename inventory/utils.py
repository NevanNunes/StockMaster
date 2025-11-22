from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from django.utils import timezone
def generate_operation_pdf(operation):
    """
    Generates a PDF for a validated operation (Receipt/Delivery/Transfer).
    Returns a BytesIO buffer containing the PDF.
    """
    # Create a buffer to hold the PDF in memory (not saved to disk)
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_text = f"{operation.get_operation_type_display()} - {operation.reference_number}"
    title = Paragraph(title_text, styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Operation Details
    details = [
        ['Status:', operation.get_status_display()],
        ['Created:', operation.created_at.strftime('%Y-%m-%d %H:%M')],
        ['Validated:', operation.validated_at.strftime('%Y-%m-%d %H:%M') if operation.validated_at else 'N/A'],
    ]
    
    if operation.partner_name:
        details.append(['Partner:', operation.partner_name])
    
    if operation.source_location:
        details.append(['From:', str(operation.source_location)])
    
    if operation.destination_location:
        details.append(['To:', str(operation.destination_location)])
    
    details_table = Table(details, colWidths=[2*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Line Items
    line_data = [['Product', 'SKU', 'Demanded', 'Done', 'UOM']]
    for line in operation.lines.all():
        line_data.append([
            line.product.name,
            line.product.sku,
            str(line.quantity_demanded),
            str(line.quantity_done),
            line.product.uom
        ])
    
    line_table = Table(line_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch, 0.8*inch])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(line_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer