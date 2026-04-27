# Example project with FastAPI - Bank Account
# Manage deposits and withdrawals

from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel, Field

app = FastAPI(
    title="FastAPI Asimov",
    description="Asimov API"
)

# Adds clients
db_clients = {
    "John": 0,
    "Mary": 0,
    "Peter": 0
}

# Transaction class
class Transaction(BaseModel):
    client: str = Field(..., description="Client name")
    amount: float = Field(..., gt=0, description="Transaction amount")

# Home endpoint
@app.get("/")
def read_root():
    return {"message": "Home - Bank"}

# Create GET endpoint to check savings
@app.post("/balance")
def balance(client: str):
    return {"message": f"Client {client}'s balance is ${db_clients[client]}"}

# Create POST endpoint to withdrawal money
@app.post("/withdrawal")
def withdrawal(transaction: Transaction):
    db_clients[transaction.client] -= transaction.amount
    return {"message": {"client": transaction.client, "amount": -transaction.amount, "balance": db_clients[transaction.client]}}

# Create POST endpoint to deposit money
@app.post("/deposit")
def deposit(transaction: Transaction):
    db_clients[transaction.client] += transaction.amount
    return {"message": {"client": transaction.client, "amount": transaction.amount, "balance": db_clients[transaction.client]}}


# Run server
if __name__ == "__main__":
    uvicorn.run("example_2:app", host="0.0.0.0", port=8000, reload=True)