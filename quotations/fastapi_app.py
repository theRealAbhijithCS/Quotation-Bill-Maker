from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional

from quotations.utils import number_to_words_indian
from quotations.pdf_generator import generate_quotation_pdf

app = FastAPI(title="M4 Quotation Microservice", docs_url="/api/fastapi/docs")
fastapi_app = app


class ItemInput(BaseModel):
    is_section: Optional[bool] = False
    type: Optional[str] = "item"
    sl_no: Optional[int] = None
    particulars: Optional[str] = ""
    size: Optional[str] = ""
    qty: Optional[float] = 0.0
    unit: Optional[str] = "Sq.Ft"
    rate: Optional[float] = 0.0
    amount: Optional[float] = 0.0


class CalculationRequest(BaseModel):
    items: List[ItemInput]


class CalculationResponse(BaseModel):
    grand_total: float
    amount_in_words: str


class BillPdfRequest(BaseModel):
    bill_number: str
    quotation_title: Optional[str] = "Labour Quotation"
    company_name: Optional[str] = "M4 Interior & Architect"
    architect_name: Optional[str] = "Rajeev c.s"
    architect_phone_primary: Optional[str] = "Ph.97 44 94 52 08"
    architect_phone_secondary: Optional[str] = "97 44 94 52 09"
    project_title: Optional[str] = "Home 1"
    client_name: str
    client_phone: Optional[str] = ""
    bill_date: str
    items: List[ItemInput]


@app.post("/api/fastapi/calculate", response_model=CalculationResponse)
def calculate_bill_totals(req: CalculationRequest):
    grand_total = 0.0
    for item in req.items:
        if not item.is_section and item.type != 'section':
            qty = item.qty or 0.0
            rate = item.rate or 0.0
            grand_total += qty * rate
    
    grand_total = round(grand_total, 2)
    amount_in_words = number_to_words_indian(grand_total)
    return CalculationResponse(grand_total=grand_total, amount_in_words=amount_in_words)


@app.post("/api/fastapi/generate-pdf")
def generate_pdf_endpoint(req: BillPdfRequest):
    try:
        items_dict_list = []
        sl_counter = 1
        calculated_total = 0.0

        for item in req.items:
            if item.is_section or item.type == 'section':
                items_dict_list.append({
                    'is_section': True,
                    'particulars': item.particulars or ""
                })
            else:
                qty = item.qty or 0.0
                rate = item.rate or 0.0
                amount = item.amount if item.amount and item.amount > 0 else (qty * rate)
                calculated_total += amount

                items_dict_list.append({
                    'is_section': False,
                    'sl_no': item.sl_no or sl_counter,
                    'particulars': item.particulars or "",
                    'size': item.size or "",
                    'qty': qty,
                    'unit': item.unit or "Sq.Ft",
                    'rate': rate,
                    'amount': amount
                })
                sl_counter += 1

        grand_total = round(calculated_total, 2)
        amount_in_words = number_to_words_indian(grand_total)

        bill_data = {
            'bill_number': req.bill_number,
            'quotation_title': req.quotation_title or "Labour Quotation",
            'company_name': req.company_name or "M4 Interior & Architect",
            'architect_name': req.architect_name or "Rajeev c.s",
            'architect_phone_primary': req.architect_phone_primary or "Ph.97 44 94 52 08",
            'architect_phone_secondary': req.architect_phone_secondary or "97 44 94 52 09",
            'project_title': req.project_title or "Home 1",
            'client_name': req.client_name,
            'client_phone': req.client_phone or "",
            'bill_date': req.bill_date,
            'items': items_dict_list,
            'grand_total': grand_total,
            'amount_in_words': amount_in_words
        }

        pdf_bytes = generate_quotation_pdf(bill_data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={req.bill_number}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
