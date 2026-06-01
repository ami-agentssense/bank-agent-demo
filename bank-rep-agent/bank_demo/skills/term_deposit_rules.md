12-month term deposit rules

1. Ask for deposit amount.
2. Validate:
   - amount must be a positive number
   - amount must not exceed customer.balance
3. Calculate with annual interest rate 0.03:
   - Return Amount = Principal × (1 + 0.03)
   - Interest Earned = Return Amount - Principal
4. Maturity Date = today + 12 months.
5. Require confirmation before reducing balance:
   - "Your account balance will be reduced by $[principal] immediately. Shall I confirm this deposit?"
6. After confirmation:
   - deduct balance
   - add the term deposit entry

