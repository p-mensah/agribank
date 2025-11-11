# # router/account_type.py
# from pydantic import BaseModel
# from typing import Literal, Optional
# from datetime import datetime

# AccountType = Literal["SAVINGS", "CURRENT", "FIXED_DEPOSIT"]
# AccountStatus = Literal["ACTIVE", "FROZEN", "CLOSED"]

# class AccountCreate(BaseModel):
#     type: AccountType
#     holder_name: str
#     initial_balance: float = 0.0
#     overdraft_limit: Optional[float] = None
#     tenure_months: Optional[int] = None

# class AccountResponse(BaseModel):
#     id: str
#     account_number: str
#     type: AccountType
#     holder_name: str
#     balance: float
#     status: AccountStatus
#     created_at: datetime

# class AccountSummary(BaseModel):
#     account_number: str
#     type: AccountType
#     balance: float
#     status: AccountStatus

# class InterestCalculation(BaseModel):
#     interest_earned: float
#     new_balance: float



from pydantic import BaseModel, field_validator
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
    
    @field_validator('tenure_months')
    @classmethod
    def validate_tenure(cls, v):
        """Convert string to int and validate range"""
        if v is not None:
            if isinstance(v, str):
                try:
                    v = int(v)
                except ValueError:
                    raise ValueError("Tenure months must be a valid integer")
            if v < 1 or v > 120:
                raise ValueError("Tenure must be between 1 and 120 months")
        return v

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