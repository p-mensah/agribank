from fastapi import APIRouter, Depends, HTTPException
from typing import List
from db import accounts_collection, transactions_collection
from router.account_type import AccountCreate, AccountResponse, AccountSummary
from router.transaction_schemas import TransactionResponse
from dependencies.authn import authenticated_user
from utils import replace_mongo_id
from datetime import datetime
import uuid
import random

router = APIRouter(prefix="/accounts", tags=["Accounts"])

# GENERATE 10-DIGIT ACCOUNT NUMBER: GH + 8 DIGITS
def generate_account_number():
    digits = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f"GH{digits}"  # → GH12345678

@router.post("/", response_model=AccountResponse)
def create_account(
    req: AccountCreate,
    user=Depends(authenticated_user)
):
    # Generate unique 10-digit account number
    acc_num = generate_account_number()
    max_tries = 10
    for _ in range(max_tries):
        if not accounts_collection.find_one({"account_number": acc_num}):
            break
        acc_num = generate_account_number()
    else:
        raise HTTPException(500, "Failed to generate unique account number")

    account = {
        "_id": str(uuid.uuid4()),
        "user_id": user["_id"],
        "account_number": acc_num,  # 10-DIGIT: GH12345678
        "type": req.type,
        "holder_name": req.holder_name,
        "balance": req.initial_balance,
        "status": "ACTIVE",
        "currency": "GHS",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    # SAVINGS ACCOUNT
    if req.type == "SAVINGS":
        if req.initial_balance < 100:
            raise HTTPException(400, "Minimum GH¢100 required for savings")
        account.update({
            "minimum_balance": 100.0,
            "interest_rate": 3.5
        })

    # CURRENT ACCOUNT
    elif req.type == "CURRENT":
        limit = req.overdraft_limit or 5000
        account["overdraft_limit"] = min(limit, 5000)

    # FIXED DEPOSIT
    elif req.type == "FIXED_DEPOSIT":
        if not req.tenure_months:
            raise HTTPException(400, "Tenure in months is required")
        from dateutil.relativedelta import relativedelta
        maturity = datetime.now() + relativedelta(months=req.tenure_months)
        maturity_amount = req.initial_balance * (1 + 0.055/12) ** req.tenure_months
        account.update({
            "tenure_months": req.tenure_months,
            "maturity_date": maturity,
            "maturity_amount": round(maturity_amount, 2)
        })

    # INSERT INTO DATABASE
    accounts_collection.insert_one(account)
    return replace_mongo_id(account)

@router.get("/", response_model=List[AccountSummary])
def get_my_accounts(user=Depends(authenticated_user)):
    accounts = accounts_collection.find({"user_id": user["_id"]})
    return [AccountSummary(**replace_mongo_id(a)) for a in accounts]

@router.get("/{id}", response_model=AccountResponse)
def get_account(id: str, user=Depends(authenticated_user)):
    acc = accounts_collection.find_one({"_id": id, "user_id": user["_id"]})
    if not acc:
        raise HTTPException(404, "Account not found")
    return replace_mongo_id(acc)

@router.get("/{id}/balance")
def check_balance(id: str, user=Depends(authenticated_user)):
    acc = accounts_collection.find_one({"_id": id, "user_id": user["_id"]})
    if not acc:
        raise HTTPException(404, "Account not found")
    return {"balance": acc["balance"], "currency": "GHS"}

@router.delete("/{id}")
def close_account(id: str, user=Depends(authenticated_user)):
    acc = accounts_collection.find_one({"_id": id, "user_id": user["_id"]})
    if not acc:
        raise HTTPException(404, "Account not found")
    if acc["balance"] != 0:
        raise HTTPException(400, "Balance must be zero to close account")
    accounts_collection.update_one({"_id": id}, {"$set": {"status": "CLOSED", "updated_at": datetime.now()}})
    return {"message": "Account closed successfully"}

@router.post("/{id}/calculate-interest")
def calculate_interest(id: str, user=Depends(authenticated_user)):
    acc = accounts_collection.find_one({"_id": id, "user_id": user["_id"]})
    if not acc or acc["type"] != "SAVINGS":
        raise HTTPException(400, "Only savings accounts earn interest")
    
    interest = acc["balance"] * 0.035 / 12
    new_balance = acc["balance"] + interest

    accounts_collection.update_one(
        {"_id": id},
        {"$set": {"balance": new_balance, "updated_at": datetime.now()}}
    )

    # Record interest transaction
    trans = {
        "_id": str(uuid.uuid4()),
        "account_id": id,
        "type": "INTEREST_CREDIT",
        "amount": round(interest, 2),
        "balance_after": round(new_balance, 2),
        "timestamp": datetime.now(),
        "description": "Monthly interest"
    }
    transactions_collection.insert_one(trans)

    return {
        "interest_earned": round(interest, 2),
        "new_balance": round(new_balance, 2)
    }

@router.patch("/{id}/freeze")
def freeze_account(id: str, freeze: bool = True, user=Depends(authenticated_user)):
    acc = accounts_collection.find_one({"_id": id, "user_id": user["_id"]})
    if not acc:
        raise HTTPException(404, "Account not found")
    status = "FROZEN" if freeze else "ACTIVE"
    accounts_collection.update_one({"_id": id}, {"$set": {"status": status, "updated_at": datetime.now()}})
    return {"status": status}

@router.get("/portfolio/summary")
def portfolio_summary(user=Depends(authenticated_user)):
    accounts = list(accounts_collection.find({"user_id": user["_id"]}))
    total = sum(a["balance"] for a in accounts)
    return {
        "total_accounts": len(accounts),
        "total_balance": round(total, 2),
        "currency": "GHS",
        "accounts": [AccountSummary(**replace_mongo_id(a)) for a in accounts]
    }