from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import users, accounts, transactions
from db import get_db

app = FastAPI(title="AgricBank Management Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(transactions.router)

# Remove this line: app = FastAPI()  # <-- This was overwriting your configured app!

@app.get("/")
def root():
    """Returns a welcome message for the AgricBank API.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Agric Bank is a leading financial institution committed to advancing agricultural development through comprehensive banking services. We partner with farmers and agribusinesses to provide accessible credit, secure savings solutions, and investment opportunities that drive productivity and sustainability in the agricultural sector"}

@app.get("/health")
def health():
    """Returns the health status of the application and the database connection.

    Returns:
        dict: A dictionary containing the application status and database connection string.
    """
    return {"status": "healthy", "db": str(get_db())}
