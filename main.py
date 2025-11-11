# # main.py
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from router import users, accounts, transactions
# from db import get_db

# app = FastAPI(title="AgricBank Management Platform")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(users.router)
# app.include_router(accounts.router)
# app.include_router(transactions.router)

<<<<<<< HEAD

# app = FastAPI()
=======
>>>>>>> 81bd9a5759716363a962e67877b2e65d80ce4ed8
# @app.get("/")
# def root():
#     return {"message": "Agric Bank is a leading financial institution committed to advancing agricultural development through comprehensive banking services. We partner with farmers and agribusinesses to provide accessible credit, secure savings solutions, and investment opportunities that drive productivity and sustainability in the agricultural sector"}

# @app.get("/health")
# def health():
#     return {"status": "healthy", "db": str(get_db())}

<<<<<<< HEAD
=======


>>>>>>> 81bd9a5759716363a962e67877b2e65d80ce4ed8
# main.py
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
    return {"message": "Agric Bank is a leading financial institution committed to advancing agricultural development through comprehensive banking services. We partner with farmers and agribusinesses to provide accessible credit, secure savings solutions, and investment opportunities that drive productivity and sustainability in the agricultural sector"}

@app.get("/health")
def health():
    return {"status": "healthy", "db": str(get_db())}
