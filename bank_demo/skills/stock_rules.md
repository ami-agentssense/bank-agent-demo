Stock query & purchase rules

Stock query:
- If user asks about a stock, look up the ticker in the available STOCKS list.
- If found: respond with company name, ticker, and current price per share, then ask:
  "Would you like to buy shares?"
- If not found: respond with the available tickers list.

Stock purchase:
1. Ask for number of shares:
   "How many shares of [TICKER] would you like to purchase?"
2. Validate affordability:
   - Total Cost = shares × price
   - If Total Cost > customer.balance, tell them the maximum affordable shares.
3. Require confirmation before executing:
   "To confirm: you'd like to buy [N] share(s) of [TICKER] at $[price]/share for a total of $[total]. This will reduce your balance from $[old_balance] to $[new_balance]. Shall I proceed?"
4. After confirmation:
   - deduct cost from balance
   - add shares to customer.portfolio

