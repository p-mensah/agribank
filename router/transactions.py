# # router/transactions.py
# from typing import List, Optional
# from fastapi import APIRouter, Depends, HTTPException
# from db import accounts_collection, transactions_collection
# from router.transaction_schemas import (
#     TransactionCreate,
#     TransferRequest,
#     TransactionResponse,
# )
# from dependencies.authn import authenticated_user
# from utils import replace_mongo_id
# from datetime import datetime
# import uuid

# router = APIRouter(prefix="/transactions", tags=["Transactions"])


# def record_transaction(
#     *,
#     account_id: str,
#     account_number: str,
#     trans_type: str,
#     amount: float,
#     balance_after: float,
#     description: str = "",
# ) -> dict:
#     """
#     Centralised transaction recorder.
#     All arguments are **named** → impossible to swap `balance_after` and `description`.
#     """
#     trans = {
#         "_id": str(uuid.uuid4()),
#         "account_id": account_id,
#         "account_number": account_number,
#         "type": trans_type,
#         "amount": float(amount),
#         "balance_after": float(balance_after),
#         "description": description,
#         "timestamp": datetime.utcnow(),
#         "next": None,
#     }
#     transactions_collection.insert_one(trans)
#     return trans


# # -------------------------------------------------
# # DEPOSIT
# # -------------------------------------------------
# @router.post("/deposit")
# def deposit(
#     req: TransactionCreate,
#     account_number: str,
#     user=Depends(authenticated_user),
# ):
#     acc = accounts_collection.find_one(
#         {"account_number": account_number, "user_id": user["_id"]}
#     )
#     if not acc:
#         raise HTTPException(404, "Account not found")
#     if acc["status"] != "ACTIVE":
#         raise HTTPException(400, "Account is not active")
#     if acc["type"] == "FIXED_DEPOSIT":
#         raise HTTPException(400, "Cannot deposit into fixed deposit")

#     new_balance = acc["balance"] + req.amount
#     accounts_collection.update_one(
#         {"_id": acc["_id"]},
#         {"$set": {"balance": new_balance, "updated_at": datetime.utcnow()}},
#     )

#     trans = record_transaction(
#         account_id=acc["_id"],
#         account_number=account_number,
#         trans_type="DEPOSIT",
#         amount=req.amount,
#         balance_after=new_balance,
#         description=f"Deposit of GH¢{req.amount:.2f}",
#     )
#     return replace_mongo_id(trans)


# # -------------------------------------------------
# # WITHDRAW
# # -------------------------------------------------
# @router.post("/withdraw")
# def withdraw(
#     req: TransactionCreate,
#     account_number: str,
#     user=Depends(authenticated_user),
# ):
#     acc = accounts_collection.find_one(
#         {"account_number": account_number, "user_id": user["_id"]}
#     )
#     if not acc:
#         raise HTTPException(404, "Account not found")
#     if acc["status"] != "ACTIVE":
#         raise HTTPException(400, "Account is not active")

#     # ----- balance checks -----
#     if acc["type"] == "SAVINGS" and (acc["balance"] - req.amount) < 100:
#         raise HTTPException(400, "Minimum balance of GH¢100 required for savings")

#     if acc["type"] == "CURRENT":
#         overdraft = acc.get("overdraft_limit", 0)
#         if (acc["balance"] - req.amount) < -overdraft:
#             raise HTTPException(400, "Overdraft limit exceeded")

#     if acc["type"] == "FIXED_DEPOSIT":
#         raise HTTPException(400, "Cannot withdraw from fixed deposit before maturity")

#     new_balance = acc["balance"] - req.amount
#     accounts_collection.update_one(
#         {"_id": acc["_id"]},
#         {"$set": {"balance": new_balance, "updated_at": datetime.utcnow()}},
#     )

#     trans = record_transaction(
#         account_id=acc["_id"],
#         account_number=account_number,
#         trans_type="WITHDRAWAL",
#         amount=req.amount,
#         balance_after=new_balance,
#         description=f"Withdrawal of GH¢{req.amount:.2f}",
#     )
#     return replace_mongo_id(trans)


# # -------------------------------------------------
# # TRANSFER
# # -------------------------------------------------
# @router.post("/transfer")
# def transfer(
#     req: TransferRequest,
#     from_account: str,
#     user=Depends(authenticated_user),
# ):
#     from_acc = accounts_collection.find_one(
#         {"account_number": from_account, "user_id": user["_id"]}
#     )
#     to_acc = accounts_collection.find_one({"account_number": req.to_account_number})

#     if not from_acc:
#         raise HTTPException(404, "Source account not found")
#     if not to_acc:
#         raise HTTPException(404, "Destination account not found")
#     if from_acc["status"] != "ACTIVE" or to_acc["status"] != "ACTIVE":
#         raise HTTPException(400, "One or both accounts are not active")
#     if from_acc["balance"] < req.amount:
#         raise HTTPException(400, "Insufficient funds")

#     new_from = from_acc["balance"] - req.amount
#     new_to = to_acc["balance"] + req.amount

#     accounts_collection.update_one(
#         {"_id": from_acc["_id"]},
#         {"$set": {"balance": new_from, "updated_at": datetime.utcnow()}},
#     )
#     accounts_collection.update_one(
#         {"_id": to_acc["_id"]},
#         {"$set": {"balance": new_to, "updated_at": datetime.utcnow()}},
#     )

#     record_transaction(
#         account_id=from_acc["_id"],
#         account_number=from_account,
#         trans_type="TRANSFER_OUT",
#         amount=req.amount,
#         balance_after=new_from,
#         description=f"Transfer to {req.to_account_number}",
#     )
#     record_transaction(
#         account_id=to_acc["_id"],
#         account_number=req.to_account_number,
#         trans_type="TRANSFER_IN",
#         amount=req.amount,
#         balance_after=new_to,
#         description=f"Transfer from {from_account}",
#     )
#     return {"message": "Transfer successful"}


# # -------------------------------------------------
# # HISTORY (by account_number)
# # -------------------------------------------------
# @router.get("/{account_number}/history", response_model=List[TransactionResponse])
# def get_transaction_history(
#     account_number: str,
#     user=Depends(authenticated_user),
#     skip: int = 0,
#     limit: int = 50,
# ):
#     # 1. Find account by public number + ownership
#     account = accounts_collection.find_one(
#         {"account_number": account_number, "user_id": user["_id"]}
#     )
#     if not account:
#         raise HTTPException(404, "Account not found or access denied")

#     # 2. Pull transactions using internal _id
#     cursor = (
#         transactions_collection.find({"account_id": account["_id"]})
#         .sort("timestamp", -1)
#         .skip(skip)
#         .limit(limit)
#     )
#     return [replace_mongo_id(t) for t in cursor]

# router/transactions.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from db import accounts_collection, transactions_collection
from router.transaction_schemas import (
    TransactionCreate,
    TransferRequest,
    TransactionResponse,
)
from dependencies.authn import authenticated_user
from utils import replace_mongo_id
from datetime import datetime
import uuid

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def record_transaction(
    account_id: str,
    account_number: str,
    trans_type: str,
    amount: float,
    balance_after: float,
    description: str = "",
) -> dict:
    """Creates and stores a new transaction record in the database.

    This is a centralized function for recording all types of transactions to ensure
    consistency. All arguments must be passed as keyword arguments for clarity.

    Args:
        account_id (str): The unique identifier of the account.
        account_number (str): The public-facing account number.
        trans_type (str): The type of transaction (e.g., DEPOSIT, WITHDRAWAL).
        amount (float): The amount of the transaction.
        balance_after (float): The account balance after the transaction.
        description (str, optional): A description of the transaction. Defaults to "".

    Returns:
        dict: The newly created transaction record.
    """
    trans = {
        "_id": str(uuid.uuid4()),
        "account_id": account_id,
        "account_number": account_number,
        "type": trans_type,
        "amount": float(amount),
        "balance_after": float(balance_after),
        "description": description,
        "timestamp": datetime.utcnow(),
        "next": None,
    }
    transactions_collection.insert_one(trans)
    return trans


# -------------------------------------------------
# DEPOSIT
# -------------------------------------------------
@router.post("/deposit")
def deposit(
    req: TransactionCreate,
    account_number: str,
    user=Depends(authenticated_user),
):
    """Deposits a specified amount into an account.

    Args:
        req (TransactionCreate): The request body containing the deposit amount.
        account_number (str): The account number to deposit into.
        user (dict): The authenticated user's data.

    Raises:
        HTTPException: If the account is not found, not active, or is a fixed deposit account.

    Returns:
        dict: The transaction record for the deposit.
    """
    acc = accounts_collection.find_one(
        {"account_number": account_number, "user_id": user["_id"]}
    )
    if not acc:
        raise HTTPException(404, "Account not found")
    if acc["status"] != "ACTIVE":
        raise HTTPException(400, "Account is not active")
    if acc["type"] == "FIXED_DEPOSIT":
        raise HTTPException(400, "Cannot deposit into fixed deposit")

    new_balance = acc["balance"] + req.amount
    accounts_collection.update_one(
        {"_id": acc["_id"]},
        {"$set": {"balance": new_balance, "updated_at": datetime.utcnow()}},
    )

    trans = record_transaction(
        account_id=acc["_id"],
        account_number=account_number,
        trans_type="DEPOSIT",
        amount=req.amount,
        balance_after=new_balance,
        description=f"Deposit of GH¢{req.amount:.2f}",
    )
    return replace_mongo_id(trans)


# -------------------------------------------------
# WITHDRAW
# -------------------------------------------------
@router.post("/withdraw")
def withdraw(
    req: TransactionCreate,
    account_number: str,
    user=Depends(authenticated_user),
):
    """Withdraws a specified amount from an account.

    Args:
        req (TransactionCreate): The request body containing the withdrawal amount.
        account_number (str): The account number to withdraw from.
        user (dict): The authenticated user's data.

    Raises:
        HTTPException: If the account is not found, not active, or if withdrawal
                       violates account-specific rules (e.g., minimum balance).

    Returns:
        dict: The transaction record for the withdrawal.
    """
    acc = accounts_collection.find_one(
        {"account_number": account_number, "user_id": user["_id"]}
    )
    if not acc:
        raise HTTPException(404, "Account not found")
    if acc["status"] != "ACTIVE":
        raise HTTPException(400, "Account is not active")

    # ----- balance checks -----
    if acc["type"] == "SAVINGS" and (acc["balance"] - req.amount) < 100:
        raise HTTPException(400, "Minimum balance of GH¢100 required for savings")

    if acc["type"] == "CURRENT":
        overdraft = acc.get("overdraft_limit", 0)
        if (acc["balance"] - req.amount) < -overdraft:
            raise HTTPException(400, "Overdraft limit exceeded")

    if acc["type"] == "FIXED_DEPOSIT":
        raise HTTPException(400, "Cannot withdraw from fixed deposit before maturity")

    new_balance = acc["balance"] - req.amount
    accounts_collection.update_one(
        {"_id": acc["_id"]},
        {"$set": {"balance": new_balance, "updated_at": datetime.utcnow()}},
    )

    trans = record_transaction(
        account_id=acc["_id"],
        account_number=account_number,
        trans_type="WITHDRAWAL",
        amount=req.amount,
        balance_after=new_balance,
        description=f"Withdrawal of GH¢{req.amount:.2f}",
    )
    return replace_mongo_id(trans)


# -------------------------------------------------
# TRANSFER
# -------------------------------------------------
@router.post("/transfer")
def transfer(
    req: TransferRequest,
    from_account: str,
    user=Depends(authenticated_user),
):
    """Transfers a specified amount from one account to another.

    Args:
        req (TransferRequest): The request body containing transfer details.
        from_account (str): The account number to transfer from.
        user (dict): The authenticated user's data.

    Raises:
        HTTPException: If either account is not found, not active, or if the
                       source account has insufficient funds.

    Returns:
        dict: A message indicating the transfer was successful.
    """
    from_acc = accounts_collection.find_one(
        {"account_number": from_account, "user_id": user["_id"]}
    )
    to_acc = accounts_collection.find_one({"account_number": req.to_account_number})

    if not from_acc:
        raise HTTPException(404, "Source account not found")
    if not to_acc:
        raise HTTPException(404, "Destination account not found")
    if from_acc["status"] != "ACTIVE" or to_acc["status"] != "ACTIVE":
        raise HTTPException(400, "One or both accounts are not active")
    if from_acc["balance"] < req.amount:
        raise HTTPException(400, "Insufficient funds")

    new_from = from_acc["balance"] - req.amount
    new_to = to_acc["balance"] + req.amount

    accounts_collection.update_one(
        {"_id": from_acc["_id"]},
        {"$set": {"balance": new_from, "updated_at": datetime.utcnow()}},
    )
    accounts_collection.update_one(
        {"_id": to_acc["_id"]},
        {"$set": {"balance": new_to, "updated_at": datetime.utcnow()}},
    )

    record_transaction(
        account_id=from_acc["_id"],
        account_number=from_account,
        trans_type="TRANSFER_OUT",
        amount=req.amount,
        balance_after=new_from,
        description=f"Transfer to {req.to_account_number}",
    )
    record_transaction(
        account_id=to_acc["_id"],
        account_number=req.to_account_number,
        trans_type="TRANSFER_IN",
        amount=req.amount,
        balance_after=new_to,
        description=f"Transfer from {from_account}",
    )
    return {"message": "Transfer successful"}


# -------------------------------------------------
# HISTORY (by account_number)
# -------------------------------------------------
@router.get("/{account_number}/history", response_model=List[TransactionResponse])
def get_transaction_history(
    account_number: str,
    user=Depends(authenticated_user),
    skip: int = 0,
    limit: int = 50,
):
    """Retrieves the transaction history for a specific account.

    Args:
        account_number (str): The account number to retrieve history for.
        user (dict): The authenticated user's data.
        skip (int, optional): The number of transactions to skip. Defaults to 0.
        limit (int, optional): The maximum number of transactions to return. Defaults to 50.

    Raises:
        HTTPException: If the account is not found or the user does not have access.

    Returns:
        list: A list of transaction records.
    """
    # 1. Find account by public number + ownership
    account = accounts_collection.find_one(
        {"account_number": account_number, "user_id": user["_id"]}
    )
    if not account:
        raise HTTPException(404, "Account not found or access denied")

    # 2. Pull transactions using internal _id
    cursor = (
        transactions_collection.find({"account_id": account["_id"]})
        .sort("timestamp", -1)
        .skip(skip)
        .limit(limit)
    )
    
    # 3. Process each transaction explicitly
    transactions = []
    for t in cursor:
        t_dict = replace_mongo_id(t)
        # Ensure all fields are present with correct types
        transactions.append({
            "id": t_dict.get("id"),
            "account_id": t_dict.get("account_id"),
            "account_number": t_dict.get("account_number"),
            "type": t_dict.get("type"),
            "amount": float(t_dict.get("amount", 0)),
            "balance_after": float(t_dict.get("balance_after", 0)),
            "description": t_dict.get("description", ""),
            "timestamp": t_dict.get("timestamp"),
            "next": t_dict.get("next"),
        })
    
    return transactions