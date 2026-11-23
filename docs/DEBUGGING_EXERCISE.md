\# Debugging Exercise: Order Total Calculation



\## 1. Problem

The original code used `total = amount`, which overwrote the previous amount on every iteration.



\## 2. Corrected Code

```python

def calculate\_total(items):

&#x20;   total = 0

&#x20;   for item in items:

&#x20;       amount = item\["quantity"] \* item\["rate"]

&#x20;       total += amount

&#x20;   return total

```



\## 3. Example

```python

items = \[

&#x20;   {"quantity": 2, "rate": 100},

&#x20;   {"quantity": 3, "rate": 50}

]

print(calculate\_total(items))

```



Expected output: `350`



Calculation: (2 × 100) + (3 × 50) = 350.



\## 4. Edge Cases

\- Empty list: returns 0.

\- Missing quantity or rate: raises KeyError; validate required fields.

\- Invalid non-numeric values: may raise TypeError; validate input types.

\- Zero or negative quantity/rate: validate against business rules.



\## 5. Suggested Tests

```python

def test\_multiple\_items():

&#x20;   assert calculate\_total(\[

&#x20;       {"quantity": 2, "rate": 100},

&#x20;       {"quantity": 3, "rate": 50}

&#x20;   ]) == 350



def test\_empty\_items():

&#x20;   assert calculate\_total(\[]) == 0

```



\## 6. Conclusion

Using `total += amount` accumulates every item's amount instead of overwriting the previous total. Production code should also validate input values.

