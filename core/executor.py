import random
import json

def execute_bank_action(account, amount, reason):
    return {
        "status": "تم السحب",
        "account": account,
        "amount": f"{amount} ريال",
        "reason": reason
    }

def execute_wallet_action(wallet, amount, reason):
    return {
        "status": "تم السحب",
        "wallet": wallet,
        "amount": f"{amount} دولار",
        "reason": reason
    }

def create_wallet():
    wallet_id = "0x" + ''.join(random.choices("0123456789abcdef", k=40))
    return {"wallet": wallet_id, "balance": "0"}

def execute_purchase(product, store, reason):
    order_id = "ORD-" + str(random.randint(100000, 999999))
    amount = random.randint(100, 5000)
    return {
        "product": product,
        "store": store,
        "order_id": order_id,
        "amount": f"{amount} ريال",
        "reason": reason
    }
