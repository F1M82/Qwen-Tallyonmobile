# FILE: backend/routers/reconciliation.py
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.reconciliation.matching_engine import ReconciliationMatchingEngine, Transaction
from datetime import date
from decimal import Decimal
import pandas as pd
import io
import uuid

router = APIRouter()

@router.post("/upload/{party_id}")
async def upload_party_statement(
    party_id: str,
    file: UploadFile = File(...),
    period_from: str = Form(None),
    period_to: str = Form(None),
    db: Session = Depends(get_db)
):
    allowed_types = [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/csv"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(400, "Only Excel and CSV files are supported")
    
    try:
        contents = await file.read()
        
        if file.content_type == "text/csv":
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Normalize columns
        df.columns = df.columns.str.lower().str.strip()
        column_mapping = {
            'date': ['date', 'txn date', 'transaction date'],
            'reference': ['reference', 'ref no', 'invoice no'],
            'particulars': ['particulars', 'narration', 'description'],
            'debit': ['debit', 'dr', 'debit amount'],
            'credit': ['credit', 'cr', 'credit amount']
        }
        
        for standard, variants in column_mapping.items():
            for variant in variants:
                if variant in df.columns:
                    df[standard] = df[variant]
                    break
        
        # Convert to transactions
        party_transactions = []
        for idx, row in df.iterrows():
            party_transactions.append(Transaction(
                id=f"party-{idx}",
                date=pd.to_datetime(row.get('date')).date() if row.get('date') else date.today(),
                reference=str(row.get('reference', '')),
                particulars=str(row.get('particulars', '')),
                debit=Decimal(str(row.get('debit', 0))),
                credit=Decimal(str(row.get('credit', 0))),
                source="party_statement"
            ))
        
        # Get your transactions from Tally (placeholder)
        your_transactions = []  # Replace with actual Tally connector call
        
        # Run reconciliation
        engine = ReconciliationMatchingEngine()
        results, summary = engine.reconcile(your_transactions, party_transactions)
        
        recon_id = str(uuid.uuid4())
        
        return {
            "recon_id": recon_id,
            "summary": summary,
            "results": [
                {
                    "id": r.id,
                    "status": r.status,
                    "confidence": r.confidence_score,
                    "reason": r.reason,
                    "requires_review": r.requires_review,
                    "your_transaction": {
                        "id": r.your_transaction.id,
                        "date": r.your_transaction.date.isoformat(),
                        "amount": str(r.your_transaction.amount),
                        "reference": r.your_transaction.reference
                    } if r.your_transaction else None,
                    "party_transaction": {
                        "id": r.party_transaction.id,
                        "date": r.party_transaction.date.isoformat(),
                        "amount": str(r.party_transaction.amount),
                        "reference": r.party_transaction.reference
                    } if r.party_transaction else None
                }
                for r in results
            ]
        }
    
    except Exception as e:
        raise HTTPException(400, f"Failed to process file: {str(e)}")

@router.get("/{recon_id}")
async def get_reconciliation_results(recon_id: str):
    # Fetch from database
    return {"recon_id": recon_id, "status": "completed"}
"""
