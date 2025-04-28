## ? Code Quality Standards: Guard Clauses & Imperative Docstrings

### 1. Use Guard Clauses to Simplify Conditional Logic

**Guideline:**?When a function contains multiple conditional checks, use guard clauses to handle exceptional or edge cases early. This approach reduces nesting and enhances readability??

**Example (Before):**
?
```python
def process_data(data):
    if data is not None:
        if data.is_valid():
            process(data)
        else:
            log_error("Invalid data")
    else:
        log_error("No data provided")
```??

**Example (After):**
?
```python
def process_data(data):
    if data is None:
        log_error("No data provided")
        return
    if not data.is_valid():
        log_error("Invalid data")
        return
    process(data)
```??

**Rationale:**?Using guard clauses allows the main logic of the function to proceed without unnecessary indentation, making the code cleaner and easier to maintain??

### 2. Write Docstrings in Imperative Mood

**Guideline:**?Begin docstrings with an imperative verb to clearly state the function's purpose. This style is consistent with Python's conventions and enhances clarity??

**Example (Preferred):**
?
```python
def calculate_total(items):
    """Calculate the total price of all items."""
    ...
```??

**Example (To Avoid):**
?
```python
def calculate_total(items):
    """Calculates the total price of all items."""
    ...
```??

**Rationale:**?Imperative mood ("Calculate") directly instructs what the function does, aligning with Python's docstring standards??
