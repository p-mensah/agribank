# # test_api.py
# import requests

# BASE = "http://localhost:8000"

# def test_all():
#     print("Testing AgricBank API...\n")
    
#     # 1. Signup
#     r = requests.post(f"{BASE}/users/signup", data={
#         "name": "{Peter} Mensah", "email": "peter@example.com", "password": "password123"
#     })
#     print("Signup:", r.json())

#     # 2. Login
#     r = requests.post(f"{BASE}/users/login", data={
#         "email": "peter@example.com", "password": "password123"
#     })
#     token = r.json()["access_token"]
#     headers = {"Authorization": f"Bearer {token}"}
#     print("Login: Success")

#     # 3. Create Savings
#     r = requests.post(f"{BASE}/accounts", json={
#         "type": "SAVINGS", "holder_name": "Kofi", "initial_balance": 200
#     }, headers=headers)
#     acc_id = r.json()["id"]
#     print("Savings Created:", r.json()["account_number"])

#     # 4. Deposit
#     requests.post(f"{BASE}/transactions/deposit?account_number={r.json()['account_number']}", 
#                   json={"amount": 50}, headers=headers)

#     print("All tests passed!")

# if __name__ == "__main__":
#     test_all()