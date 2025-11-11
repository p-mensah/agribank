# router/account_type.py
from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

AccountType = Literal["SAVINGS", "CURRENT", "FIXED_DEPOSIT"]
AccountStatus = Literal["ACTIVE", "FROZEN", "CLOSED"]

class AccountCreate(BaseModel):
    type: AccountType
    holder_name: str
    initial_balance: float = 0.0
    overdraft_limit: Optional[float] = None
    tenure_months: Optional[int] = None

class AccountResponse(BaseModel):
    id: str
    account_number: str
    type: AccountType
    holder_name: str
    balance: float
    status: AccountStatus
    created_at: datetime

class AccountSummary(BaseModel):
    account_number: str
    type: AccountType
    balance: float
    status: AccountStatus

class InterestCalculation(BaseModel):
    interest_earned: float
    new_balance: float