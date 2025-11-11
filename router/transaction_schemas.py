# router/transaction_schemas.py
from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

# === TRANSACTION TYPES ===
TransactionType = Literal[
    "DEPOSIT", "WITHDRAWAL", "TRANSFER"
]

# === REQUEST MODELS ===
class TransactionCreate(BaseModel):
    amount: float

class TransferRequest(BaseModel):
    to_account_number: str
    amount: float

# === RESPONSE MODELS  ===
class TransactionResponse(BaseModel):
    id: str
    type: TransactionType
    amount: float
    balance_after: float
    timestamp: datetime
    description: str = ""

class TransactionFilter(BaseModel):
    type: Optional[TransactionType] = None
    limit: Optional[int] = 10

class AccountStatement(BaseModel):
    account_number: str
    opening_balance: float
    closing_balance: float
    total_credit: float
    total_debit: float
    transactions: list[TransactionResponse]