# Bluecoins App Tasks Documentation

## Overview

The Bluecoins app tasks test personal finance management operations using the Bluecoins budget and finance tracker app. Tasks include querying spending information, adding transactions, and editing existing entries.

**Package Name**: `com.rammigsoftware.bluecoins`  
**Total Tasks**: 15  
**Complexity Range**: 2.0 - 4.0

## Data Setup

The emulator date is frozen to **October 15, 2023**. The following transactions are expected to exist:

| Amount | Category | Notes |
|--------|----------|-------|
| 512 USD | Other | (none) |
| 888 USD | Other | (none) |
| 256 USD | Other | (none) |
| 768 USD | Other | (none) |

**Total**: 2424 USD | **Transaction Count**: 4

## Task List

### Query Tasks (5)

#### BluecoinsQuerySpendingOnDate
- **Complexity**: 2.0
- **Description**: Query total spending on a specific date
- **Goal**: "In the Bluecoins app, how much did I spend in total on {date}?"
- **Success Criteria**: Agent provides correct total amount (2424)

#### BluecoinsQuerySpendingCategory
- **Complexity**: 2.0
- **Description**: Query what category a specific expense is under
- **Goal**: "In the Bluecoins app, what category is the {amount} USD expense on {date} under?"
- **Success Criteria**: Agent provides correct category (other)

#### BluecoinsQueryTotalSpendingOnDate
- **Complexity**: 2.0
- **Description**: Query total spending on a specific date (alternate phrasing)
- **Goal**: "In the Bluecoins app, how much did I shell out in total on {date}?"
- **Success Criteria**: Agent provides correct total amount (2424)

#### BluecoinsQueryTransactionCount
- **Complexity**: 2.0
- **Description**: Query number of transactions on a specific date
- **Goal**: "In the Bluecoins app, how many transactions did I make all together on {date}?"
- **Success Criteria**: Agent provides correct count (4)

#### BluecoinsQueryCategorySpending
- **Complexity**: 2.5
- **Description**: Query total spending for a category on a date
- **Goal**: "In the Bluecoins app, what's the total amount I spent on '{category}' category on {date}?"
- **Success Criteria**: Agent provides correct total for category

### Create Tasks (5)

#### BluecoinsAddExpense
- **Complexity**: 2.0
- **Description**: Log a simple expense
- **Goal**: "In the Bluecoins app, log an expenditure of {amount} USD."
- **Success Criteria**: New expense transaction found in SQLite database

#### BluecoinsAddIncomeWithLabel
- **Complexity**: 2.5
- **Description**: Log income with a label
- **Goal**: "In the Bluecoins app, record an income of {amount} USD and mark it as '{label}'."
- **Success Criteria**: New income transaction with matching label in database

#### BluecoinsAddExpenseOnDate
- **Complexity**: 2.5
- **Description**: Log an expense for a specific date
- **Goal**: "In the Bluecoins app, note down an expense of {amount} USD for {date}."
- **Success Criteria**: New expense with correct date in database

#### BluecoinsAddIncomeOnDateWithNote
- **Complexity**: 3.0
- **Description**: Log income with date and note
- **Goal**: "In the Bluecoins app, for {date}, jot down an income of {amount} USD with '{note}' as the note."
- **Success Criteria**: New income with matching date and note

#### BluecoinsAddExpenseOnDateWithLabel
- **Complexity**: 3.0
- **Description**: Log expense with date and label
- **Goal**: "In the Bluecoins app, for {date}, record an expenditure of {amount} USD, marked as '{label}'."
- **Success Criteria**: New expense with matching date and label

### Edit Tasks (5)

#### BluecoinsEditExpenseAmount
- **Complexity**: 3.0
- **Description**: Change an expense amount
- **Goal**: "In the Bluecoins app, adjust the expenditure on {date} to {new_amount} USD."
- **Success Criteria**: Transaction amount updated in database

#### BluecoinsEditIncomeDateAndAmount
- **Complexity**: 3.5
- **Description**: Move income to new date and update amount
- **Goal**: "In the Bluecoins app, shift the income entry from {old_date} to {new_date}, and update the amount to {new_amount} USD."
- **Success Criteria**: Transaction with new date and amount

#### BluecoinsEditTransactionType
- **Complexity**: 3.5
- **Description**: Switch transaction type and add note
- **Goal**: "In the Bluecoins app, switch the {old_date} transaction from '{old_type}' to '{new_type}' and add '{note}' as the note."
- **Success Criteria**: Transaction type changed and note added

#### BluecoinsEditTransactionTypeAmountNote
- **Complexity**: 4.0
- **Description**: Change type, amount, and note
- **Goal**: "In the Bluecoins app, change the type of the transaction on {date} from '{old_type}' to '{new_type}', adjust the amount to {new_amount} USD, and change the note to '{new_note}'."
- **Success Criteria**: All three fields updated correctly

#### BluecoinsEditExpenseDateAmountNote
- **Complexity**: 4.0
- **Description**: Move expense, adjust amount, update note
- **Goal**: "In the Bluecoins app, move the expense entry from {old_date} to {new_date}, adjust the amount to {new_amount} USD, and update the note to '{new_note}'."
- **Success Criteria**: Date, amount, and note all updated

## Testing

To test Bluecoins tasks, use the test script:

```bash
# Test a specific task
python scripts/test_androidlab_apps.py --app bluecoins --task BluecoinsQuerySpendingOnDate

# Test with custom emulator ports
python scripts/test_androidlab_apps.py --app bluecoins --task BluecoinsAddExpense --console_port 5706 --grpc_port 8556
```

## Implementation Details

### Database Schema

- **Database Path**: `/data/data/com.rammigsoftware.bluecoins/databases/bluecoins.fydb`
- **Main Table**: `TRANSACTIONSTABLE`
- **Primary Key**: `transactionsTableID`
- **Transaction Types**: 3=Expense, 4=Income, 5=Transfer

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `amount` | INTEGER | Transaction amount |
| `transactionCurrency` | TEXT | Currency code (e.g., "USD") |
| `date` | TEXT | Date in "YYYY-MM-DD HH:MM:SS" format |
| `transactionTypeID` | INTEGER | 3=Expense, 4=Income |
| `categoryID` | INTEGER | Foreign key to category table |
| `notes` | TEXT | Transaction notes |

### Validation Methods

- **Query Tasks**: Verify agent's answer matches expected value from database
- **Create Tasks**: Compare before/after transaction counts in SQLite
- **Edit Tasks**: Check for modified transaction matching expected values

## Notes

- All dates use October 2023 (frozen emulator date)
- Currency is USD for all tasks
- SQLite validation provides reliable success detection
- Partial credit given for approximate matches (e.g., correct amount but wrong type)

