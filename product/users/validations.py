
def validate_balance(balance):
    if balance < 0:
        raise ValueError('Balance cannot be negative')

    return balance
