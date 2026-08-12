import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_quotation_pdf(bill_data):
    """
    Generates a PDF byte stream matching the M4 Interior & Architect Labour Quotation format:
    - Left side header: Company Name, Owner Name, BOTH Owner Phone Numbers (STACKED ONE BELOW OTHER), Bill Number (highlighted in accent color).
    - Right side header: Client Name, Client Phone, Project Name, Date.
    - PDF contents: Full table grid lines (table-wise formatting).
    - Total Amount rendered without underline.
    - Amount in Words rendered cleanly without borders.
    - Centered Thank You message for client at the bottom.
    - No header title on Page 2 or subsequent pages.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    text_color = colors.HexColor("#000000")
    bill_no_color = "#1E40AF"  # Accent color ONLY for Bill Number

    quotation_title_str = str(bill_data.get('quotation_title') or 'Labour Quotation')
    
    top_title_style = ParagraphStyle(
        'TopTitle',
        parent=styles['Normal'],
        fontName='Helvetica-BoldOblique',
        fontSize=14,
        leading=16,
        alignment=TA_CENTER,
        textColor=text_color
    )

    meta_left_style = ParagraphStyle(
        'MetaLeft',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        alignment=TA_LEFT,
        textColor=text_color
    )

    meta_right_style = ParagraphStyle(
        'MetaRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        alignment=TA_RIGHT,
        textColor=text_color
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=text_color,
        alignment=TA_CENTER
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=text_color,
        alignment=TA_LEFT
    )

    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=text_color,
        alignment=TA_LEFT
    )

    cell_center_style = ParagraphStyle(
        'TableCellCenter',
        parent=cell_style,
        alignment=TA_CENTER
    )

    size_cell_style = ParagraphStyle(
        'SizeTableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=text_color,
        alignment=TA_CENTER
    )

    cell_right_style = ParagraphStyle(
        'TableCellRight',
        parent=cell_style,
        alignment=TA_RIGHT
    )

    words_style = ParagraphStyle(
        'AmountInWords',
        parent=styles['Normal'],
        fontName='Helvetica-BoldOblique',
        fontSize=9.5,
        leading=13,
        textColor=text_color,
        alignment=TA_CENTER
    )

    thank_you_style = ParagraphStyle(
        'ThankYouMsg',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        alignment=TA_CENTER
    )

    story = []

    # Field Extraction
    bill_number_str = str(bill_data.get('bill_number') or 'M4-2026-001')
    company_name_str = str(bill_data.get('company_name') or 'M4 Interior & Architect')
    owner_name_str = str(bill_data.get('architect_name') or 'Rajeev c.s')
    
    # OWNER BOTH PHONE NUMBERS (STACKED ONE BELOW OTHER)
    owner_phone_1 = str(bill_data.get('architect_phone_primary') or bill_data.get('architect_phone') or 'Ph.97 44 94 52 08')
    owner_phone_2 = str(bill_data.get('architect_phone_secondary') or '')

    if owner_phone_2:
        owner_phones_display = f"Phone: <b>{owner_phone_1},</b><br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>{owner_phone_2}</b>"
    else:
        if "97 44 94 52 08" in owner_phone_1 and "97 44 94 52 09" not in owner_phone_1:
            owner_phones_display = "Phone: <b>Ph.97 44 94 52 08</b><br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Ph.97 44 94 52 09</b>"
        else:
            owner_phones_display = f"Phone: <b>{owner_phone_1}</b>"
    
    project_title_str = str(bill_data.get('project_title') or '')
    client_name_str = str(bill_data.get('client_name') or '')
    client_phone_str = str(bill_data.get('client_phone') or '')

    bill_date_str = str(bill_data.get('bill_date') or '14/05/2026')
    if '-' in bill_date_str and len(bill_date_str.split('-')) == 3:
        parts = bill_date_str.split('-')
        if len(parts[0]) == 4:
            bill_date_str = f"{parts[2]}/{parts[1]}/{parts[0]}"

    # 1. Top Title (Only on Page 1)
    story.append(Paragraph(f"<u>{quotation_title_str}</u>", top_title_style))
    story.append(Spacer(1, 10))

    # 2. Header Layout: Left (Owner details with STACKED phone numbers) / Right (Client Details)
    left_meta_html = (
        f"<font size=22><b>M4</b></font><br/>"
        f"<b>{company_name_str}</b><br/>"
        f"Owner: <b>{owner_name_str}</b><br/>"
        f"{owner_phones_display}<br/>"
        f"<font color='{bill_no_color}'>Bill No: <b>{bill_number_str}</b></font>"
    )

    right_meta_html = f"Client:- <b>{client_name_str}</b><br/>"
    if client_phone_str:
        clean_phone = client_phone_str.strip()
        for pfix in ['ph.-', 'ph:-', 'ph.', 'ph:', 'phone:', 'phone.-', 'phone']:
            if clean_phone.lower().startswith(pfix):
                clean_phone = clean_phone[len(pfix):].strip()
                break
        right_meta_html += f"Ph:- <b>{clean_phone}</b><br/>"
    right_meta_html += f"Project:- <b>{project_title_str}</b><br/>"
    right_meta_html += f"Date:- <b>{bill_date_str}</b>"

    header_table = Table(
        [[Paragraph(left_meta_html, meta_left_style), Paragraph(right_meta_html, meta_right_style)]],
        colWidths=[270, 253]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))

    # 3. Dynamic Line Items Table with FULL TABLE GRID LINES
    raw_items = bill_data.get('items', []) or []
    col_widths = [45, 175, 95, 45, 45, 58, 60]

    grid_border_color = colors.HexColor("#444444")
    table_grid_style = [
        ('GRID', (0, 0), (-1, -1), 0.5, grid_border_color),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]

    calculated_total = 0.0
    sl_counter = 1

    item_rows = []
    for item in raw_items:
        item_type = item.get('type', 'item')
        particulars = str(item.get('particulars') or '')
        
        if item_type == 'section' or item.get('is_section'):
            item_rows.append({
                'is_section': True,
                'particulars': particulars
            })
        else:
            raw_size = str(item.get('size') or '').strip().replace('\r\n', '\n')
            lines = [line.strip() for line in raw_size.split('\n') if line.strip()] if raw_size else []
            size_formatted = "<br/>".join(lines) if lines else ""

            qty = float(item.get('qty') or 0.0)
            unit = str(item.get('unit') or 'Sq.Ft')
            rate = float(item.get('rate') or 0.0)
            amount = float(item.get('amount') if item.get('amount') is not None else (qty * rate))
            calculated_total += amount

            qty_str = f"{qty:g}"
            rate_str = f"{rate:.2f}"
            amount_str = f"{amount:.2f}"

            sl_no_val = str(item.get('sl_no') or sl_counter)
            sl_counter += 1

            item_rows.append({
                'is_section': False,
                'sl_no': sl_no_val,
                'particulars': particulars,
                'size': size_formatted,
                'qty': qty_str,
                'unit': unit,
                'rate': rate_str,
                'amount': amount_str
            })

    # Group into pages of max 20 items per page
    page_chunks = []
    current_chunk = []
    current_item_count = 0

    for idx, row in enumerate(item_rows):
        if row['is_section']:
            if current_item_count >= 17:
                page_chunks.append(current_chunk)
                current_chunk = [row]
                current_item_count = 0
            else:
                current_chunk.append(row)
        else:
            current_chunk.append(row)
            current_item_count += 1
            if current_item_count >= 20:
                page_chunks.append(current_chunk)
                current_chunk = []
                current_item_count = 0

    if current_chunk:
        page_chunks.append(current_chunk)

    # Render page table chunks (No heading on Page 2!)
    for chunk_idx, chunk in enumerate(page_chunks):
        if chunk_idx > 0:
            story.append(PageBreak())
            story.append(Spacer(1, 10))

        table_data = [
            [
                Paragraph("SL No.", table_header_style),
                Paragraph("Particulars", ParagraphStyle('THParticulars', parent=table_header_style, alignment=TA_LEFT)),
                Paragraph("Size", table_header_style),
                Paragraph("Qty", table_header_style),
                Paragraph("Unit", table_header_style),
                Paragraph("Rate", table_header_style),
                Paragraph("Amount", table_header_style),
            ]
        ]

        for row in chunk:
            if row['is_section']:
                sec_para = Paragraph(f"<u><b>{row['particulars']}</b></u>", section_header_style)
                table_data.append([
                    Paragraph("", cell_style),
                    sec_para,
                    Paragraph("", cell_style),
                    Paragraph("", cell_style),
                    Paragraph("", cell_style),
                    Paragraph("", cell_style),
                    Paragraph("", cell_style)
                ])
            else:
                table_data.append([
                    Paragraph(row['sl_no'], cell_center_style),
                    Paragraph(row['particulars'], cell_style),
                    Paragraph(row['size'], size_cell_style),
                    Paragraph(row['qty'], cell_center_style),
                    Paragraph(row['unit'], cell_center_style),
                    Paragraph(row['rate'], cell_right_style),
                    Paragraph(row['amount'], cell_right_style)
                ])

        items_table = Table(table_data, colWidths=col_widths)
        items_table.setStyle(TableStyle(table_grid_style))
        story.append(items_table)
        story.append(Spacer(1, 8))

    # 4. Total Row (NO UNDERLINE ON TOTAL AMOUNT)
    grand_total_val = float(bill_data.get('grand_total') if bill_data.get('grand_total') is not None else calculated_total)
    total_amount_str = f"{grand_total_val:.2f}"

    total_row = [
        [
            Paragraph("<b>Total</b>", ParagraphStyle('TotalLbl', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, alignment=TA_RIGHT)),
            Paragraph(f"<b>{total_amount_str}</b>", ParagraphStyle('TotalVal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, alignment=TA_RIGHT))
        ]
    ]

    total_table = Table(total_row, colWidths=[443, 80])
    total_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, grid_border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))

    if len(item_rows) <= 8 and len(page_chunks) == 1:
        story.append(Spacer(1, 30))
    elif len(item_rows) <= 14 and len(page_chunks) == 1:
        story.append(Spacer(1, 15))

    story.append(total_table)
    story.append(Spacer(1, 8))

    # 5. Amount in Words Block (BORDERLESS)
    words_val = str(bill_data.get('amount_in_words') or '')
    
    words_table = Table(
        [[Paragraph(f"<b>{words_val}</b>", words_style)]],
        colWidths=[523]
    )
    words_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(KeepTogether([
        words_table,
        Spacer(1, 12),
        Paragraph("Thank you for choosing M4 Interior & Architect! We are happy to work with you.", thank_you_style)
    ]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
