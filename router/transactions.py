# router/transactions.py
from fastapi import APIRouter, Depends, HTTPException
from db import accounts_collection, transactions_collection
from router.transaction_schemas import TransactionCreate, TransferRequest, TransactionResponse
from dependencies.authn import authenticated_user
from utils import replace_mongo_id
from datetime import datetime
import uuid

router = APIRouter(prefix="/transactions", tags=["Transactions"])

def record_transaction(account_id, trans_type, amount, balance_after, desc=""):
    trans = {
        "_id": str(uuid.uuid4()),
        "account_id": account_id,
        "type": trans_type,
        "amount": amount,
        "balance_after": balance_after,
        "description": desc,
        "timestamp": datetime.now(),
        "next": None
    }
    transactions_collection.insert_one(trans)
    return trans

@router.post("/deposit")
def deposit(req: TransactionCreate, account_number: str, user=Depends(authenticated_user)):
    acc = accounts_collection.find_one({"account_number": account_number, "user_id": user["_id"]})
    if not acc or acc["status"] != "ACTIVE":
        raise HTTPException(400, "Invalid account")
    if acc["type"] == "FIXED_DEPOSIT":
        raise HTTPException(400, "Cannot deposit into fixed deposit")

    new_balance = acc["balance"] + req.amount
    accounts_collection.update_one(
        {"_id": acc["_id"]},
        {"$set": {"balance": new_balance, "updated_at": datetime.now()}}
    )
    trans = record_transaction(acc["_id"], "DEPOSIT", req.amount, new_balance)
    return replace_mongo_id(trans)

@router.post("/withdraw")
def withdraw(req: TransactionCreate, account_number: str, user=Depends(authenticated_user)):
    acc = accounts_collection.find_one({"account_number": account_number, "user_id": user["_id"]})
    if not acc or acc["status"] != "ACTIVE":
        raise HTTPException(400, "Invalid account")

    if acc["type"] == "SAVINGS" and acc["balance"] - req.amount < 100:
        raise HTTPException(400, "Minimum balance required")
    if acc["type"] == "CURRENT" and acc["balance"] - req.amount < -acc.get("overdraft_limit", 0):
        raise HTTPException(400, "Overdraft limit exceeded")
    if acc["type"] == "FIXED_DEPOSIT":
        raise HTTPException(400, "Cannot withdraw before maturity")

    new_balance = acc["balance"] - req.amount
    accounts_collection.update_one(
        {"_id": acc["_id"]},
        {"$set": {"balance": new_balance, "updated_at": datetime.now()}}
    )
    trans = record_transaction(acc["_id"], "WITHDRAWAL", req.amount, new_balance)
    return replace_mongo_id(trans)

@router.post("/transfer")
def transfer(req: TransferRequest, from_account: str, user=Depends(authenticated_user)):
    from_acc = accounts_collection.find_one({"account_number": from_account, "user_id": user["_id"]})
    to_acc = accounts_collection.find_one({"account_number": req.to_account_number})
    if not from_acc or not to_acc:
        raise HTTPException(404, "Account not found")
    if from_acc["balance"] < req.amount:
        raise HTTPException(400, "Insufficient funds")

    # Deduct
    from_acc["balance"] -= req.amount
    to_acc["balance"] += req.amount

    accounts_collection.update_one({"_id": from_acc["_id"]}, {"$set": {"balance": from_acc["balance"]}})
    accounts_collection.update_one({"_id": to_acc["_id"]}, {"$set": {"balance": to_acc["balance"]}})

    record_transaction(from_acc["_id"], "TRANSFER_OUT", req.amount, from_acc["balance"], f"To {req.to_account_number}")
    record_transaction(to_acc["_id"], "TRANSFER_IN", req.amount, to_acc["balance"], f"From {from_account}")
    return {"message": "Transfer successful"}

@router.get("/{account_id}/history")
def get_history(account_id: str, limit: int = 10, user=Depends(authenticated_user)):
    trans = transactions_collection.find({"account_id": account_id}).sort("timestamp", -1).limit(limit)
    return [replace_mongo_id(t) for t in trans]