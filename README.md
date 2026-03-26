# FILE: README.md

# TaxMind Platform - AI Accounting Intelligence

## 🎯 What This Is
Complete accounting intelligence platform for CA firms with:
- TallyPrime/Zoho/QuickBooks integration
- Debtor/Creditor Reconciliation
- SMS/Email Auto-Entry
- Voice & Photo Invoice Entry
- GST Compliance Intelligence
- TaxMind AI Assistant

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or use Railway)
- TallyPrime 7.0+ (for connector)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn main:app --reload --host 0.0.0.0 --port 8000
