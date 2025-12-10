# Copyright 2025 The android_world Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tasks for Bluecoins personal finance app."""

import abc
import dataclasses
import datetime
import random
import re
from typing import Any, Optional

from absl import logging
from android_world.env import adb_utils
from android_world.env import interface
from android_world.task_evals import task_eval
from android_world.task_evals.common_validators import sqlite_validators
from android_world.task_evals.utils import sqlite_schema_utils
from android_world.task_evals.utils import sqlite_utils
from android_world.utils import fuzzy_match_lib


_APP_NAME = 'bluecoins'
_PACKAGE_NAME = 'com.rammigsoftware.bluecoins'
# Verified database path (note: .fydb extension, not .db)
_DB_PATH = f'/data/data/{_PACKAGE_NAME}/databases/bluecoins.fydb'
_TRANSACTIONS_TABLE = 'TRANSACTIONSTABLE'
_DB_KEY = 'transactionsTableID'

# Transaction type IDs (from TRANSACTIONTYPETABLE)
_TRANSACTION_TYPE_EXPENSE = 3
_TRANSACTION_TYPE_INCOME = 4
_TRANSACTION_TYPE_TRANSFER = 5
_TRANSACTION_TYPE_NEW_ACCOUNT = 2


@dataclasses.dataclass(frozen=True)
class BluecoinsTransaction(sqlite_schema_utils.SQLiteRow):
  """Represents a transaction in the Bluecoins database.

  Schema from actual database (bluecoins.fydb) - all 33 columns:
    - transactionsTableID: Primary key
    - itemID: Foreign key to ITEMTABLE
    - amount: Transaction amount (INTEGER)
    - transactionCurrency: Currency code (e.g., "USD")
    - conversionRateNew: Exchange rate
    - date: Date string in format "YYYY-MM-DD HH:MM:SS"
    - transactionTypeID: 3=Expense, 4=Income, 5=Transfer
    - categoryID: Foreign key to CHILDCATEGORYTABLE
    - accountID: Foreign key to ACCOUNTSTABLE
    - notes: Additional notes
    - status: Status flag
    - accountReference, accountPairID, uidPairID: Account references
    - deletedTransaction: Soft delete flag
    - newSplitTransactionID, transferGroupID: Split/transfer IDs
    - reminder*: Reminder-related fields
    - creditCardInstallment, dataExtraColumnString1: Extra fields
  """

  transactionsTableID: Optional[int] = None
  itemID: int = 0
  amount: int = 0  # Stored as integer
  transactionCurrency: str = 'USD'
  conversionRateNew: float = 1.0
  date: str = ''  # String format "YYYY-MM-DD HH:MM:SS"
  transactionTypeID: int = 3  # 3=Expense, 4=Income
  categoryID: int = 0
  accountID: int = 1
  notes: str = ''
  status: int = 0
  accountReference: Optional[int] = None
  accountPairID: Optional[int] = None
  uidPairID: Optional[int] = None
  deletedTransaction: int = 0
  newSplitTransactionID: Optional[int] = None
  transferGroupID: Optional[int] = None
  reminderTransaction: Optional[int] = None
  reminderGroupID: Optional[int] = None
  reminderFrequency: Optional[int] = None
  reminderRepeatEvery: Optional[int] = None
  reminderEndingType: Optional[int] = None
  reminderStartDate: Optional[str] = None
  reminderEndDate: Optional[str] = None
  reminderAfterNoOfOccurences: Optional[int] = None
  reminderAutomaticLogTransaction: Optional[int] = None
  reminderRepeatByDayOfMonth: Optional[int] = None
  reminderExcludeWeekend: Optional[int] = None
  reminderWeekDayMoveSetting: Optional[int] = None
  reminderUnbilled: Optional[int] = None
  creditCardInstallment: Optional[int] = None
  reminderVersion: Optional[int] = None
  dataExtraColumnString1: Optional[str] = None

  @property
  def amount_float(self) -> float:
    """Returns amount as float."""
    return float(self.amount)

  @property
  def amount_usd(self) -> float:
    """Returns amount in USD (database stores in micro-units, divide by 1,000,000)."""
    return abs(self.amount) / 1_000_000

  @property
  def is_expense(self) -> bool:
    """Returns True if this is an expense."""
    return self.transactionTypeID == _TRANSACTION_TYPE_EXPENSE

  @property
  def is_income(self) -> bool:
    """Returns True if this is income."""
    return self.transactionTypeID == _TRANSACTION_TYPE_INCOME

  @property
  def is_transfer(self) -> bool:
    """Returns True if this is a transfer."""
    return self.transactionTypeID == _TRANSACTION_TYPE_TRANSFER

  @property
  def date_str(self) -> str:
    """Returns date as formatted string (e.g., 'May 10, 2024')."""
    if not self.date:
      return ''
    try:
      dt = datetime.datetime.strptime(self.date, '%Y-%m-%d %H:%M:%S')
      return dt.strftime('%B %d, %Y')
    except ValueError:
      return self.date

  @property
  def date_obj(self) -> Optional[datetime.datetime]:
    """Returns date as datetime object."""
    if not self.date:
      return None
    try:
      return datetime.datetime.strptime(self.date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
      return None


# Sample data for generating random params
_EXPENSE_CATEGORIES = ['Food', 'Transportation', 'Shopping', 'Entertainment', 'Bills']
_INCOME_CATEGORIES = ['Salary', 'Bonus', 'Gift', 'Investment', 'Other']
_NOTES = ['taxi', 'eating', 'grocery', 'salary', 'gift', 'shopping', 'Weixin red packet']


def _get_fixed_date(day: int) -> str:
  """Returns a formatted date string for October 2023 (frozen emulator date)."""
  dt = datetime.datetime(2023, 10, day)
  return dt.strftime('%B %d, %Y').replace(' 0', ' ')  # Remove leading zero from day


# ===========================================================================
# DATA IN BLUECOINS (October 15, 2023)
# ===========================================================================
# 4 expenses on October 15, 2023:
#   - 512 USD (category: Other, no notes)
#   - 888 USD (category: Other, no notes)
#   - 256 USD (category: Other, no notes)
#   - 768 USD (category: Other, no notes)
# Total: 2424 USD, Transaction count: 4
# ===========================================================================

_FIXED_DAY = 15  # October 15, 2023

# Expected data on October 15, 2023
_EXPECTED_AMOUNTS = ['512', '888', '256', '768']
_EXPECTED_TOTAL = '2424'  # 512 + 888 + 256 + 768
_EXPECTED_COUNT = '4'
_EXPECTED_CATEGORY = 'other'


def _generate_transaction(
    is_income: bool = False,
    amount: Optional[int] = None,
    date_str: Optional[str] = None,
    notes: Optional[str] = None,
) -> BluecoinsTransaction:
  """Generates a random transaction.
  
  Args:
    is_income: If True, generates an income transaction; otherwise expense.
    amount: Transaction amount as integer.
    date_str: Date string in format "YYYY-MM-DD HH:MM:SS".
    notes: Transaction notes.
  
  Returns:
    A BluecoinsTransaction object.
  """
  if amount is None:
    amount = random.randint(10, 1000)
  if date_str is None:
    # Random date in October 2023 (frozen emulator date)
    day = random.randint(1, 15)
    hour = random.randint(8, 20)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    date_str = f'2023-10-{day:02d} {hour:02d}:{minute:02d}:{second:02d}'
  if notes is None:
    notes = random.choice(_NOTES)

  return BluecoinsTransaction(
      amount=amount,
      date=date_str,
      notes=notes,
      transactionTypeID=_TRANSACTION_TYPE_INCOME if is_income else _TRANSACTION_TYPE_EXPENSE,
  )


# ============================================================================
# Base class for Bluecoins tasks
# ============================================================================


class _Bluecoins(task_eval.TaskEval, abc.ABC):
  """Base class for Bluecoins task evaluations."""

  schema = {}
  app_names = (_APP_NAME,)
  template = ''

  # SQLite database info
  app_name_with_db = _APP_NAME
  db_path = _DB_PATH
  db_key = _DB_KEY
  table_name = _TRANSACTIONS_TABLE
  row_type = BluecoinsTransaction

  def list_transactions(
      self,
      env: interface.AsyncEnv,
      timeout_sec: Optional[float] = None,
  ) -> list[BluecoinsTransaction]:
    """Lists all transactions from the Bluecoins database."""
    try:
      return sqlite_utils.get_rows_from_remote_device(
          self.table_name, self.db_path, self.row_type, env, timeout_sec
      )
    except Exception as e:
      logging.warning('Failed to list transactions: %s', e)
      return []

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)


# ============================================================================
# Query Tasks (Information Retrieval)
# ============================================================================


class _BluecoinsQuery(_Bluecoins):
  """Base class for Bluecoins query tasks.

  For query tasks, we check if the agent's answer contains the expected information.
  The agent should use the 'answer' action to provide their response.
  """

  complexity = 2

  @property
  @abc.abstractmethod
  def expected_answer(self) -> str:
    """The expected answer to the query."""

  def is_successful(self, env: interface.AsyncEnv) -> float:
    """Check if the agent provided the correct answer.

    The agent's answer is stored in env.interaction_cache when they use
    the 'answer' action.
    """
    super().is_successful(env)
    agent_answer = env.interaction_cache.lower() if env.interaction_cache else ''
    expected = self.expected_answer.lower()

    if not agent_answer:
      logging.warning('Agent did not provide an answer.')
      return 0.0

    # For numeric answers, check if the number is in the response
    if expected.replace('.', '').replace(',', '').isdigit():
      # Normalize expected: remove commas
      expected_normalized = expected.replace(',', '')
      expected_int = int(expected_normalized)
      
      # Extract money-like numbers from agent answer
      # Priority 1: Numbers with currency symbols ($2,424.00, $2424)
      money_patterns = [
          r'\$[\d,]+(?:\.\d{2})?',  # $2,424.00 or $2424
          r'[\d,]+(?:\.\d{2})?\s*(?:usd|dollars?)',  # 2,424.00 USD or 2424 dollars
          r'[\d,]+\.\d{2}',  # 2,424.00 (decimal with 2 digits = likely money)
      ]
      
      money_numbers = []
      for pattern in money_patterns:
        matches = re.findall(pattern, agent_answer, re.IGNORECASE)
        money_numbers.extend(matches)
      
      # If no money patterns found, look for larger numbers (4+ digits) 
      # that are likely amounts, not dates
      if not money_numbers:
        # Match numbers with commas (like 2,424) or 4+ digit numbers
        all_numbers = re.findall(r'[\d,]+', agent_answer)
        for num in all_numbers:
          clean_num = num.replace(',', '')
          # Skip year-like numbers (1900-2100) and small numbers (likely dates)
          if clean_num.isdigit():
            num_val = int(clean_num)
            if num_val >= 100 and not (1900 <= num_val <= 2100):
              money_numbers.append(num)
      
      # Check each extracted money number
      for num_str in money_numbers:
        # Normalize: remove $, commas, currency words, trailing decimals
        normalized = re.sub(r'[$a-zA-Z\s]', '', num_str)
        normalized = normalized.replace(',', '')
        # Remove trailing .00 or .0
        if '.' in normalized:
          normalized = normalized.rstrip('0').rstrip('.')
        if normalized == expected_normalized:
          return 1.0
      
      # For small numbers (counts like 4, 10), use word boundary matching
      # to avoid matching "4" in "14" or "2024"
      if expected_int < 100:
        # Match the number as a standalone word (with word boundaries)
        pattern = r'\b' + expected_normalized + r'\b'
        if re.search(pattern, agent_answer):
          return 1.0
      else:
        # For larger numbers, check simple containment as fallback
        if expected_normalized in agent_answer.replace(',', ''):
          return 1.0
    # For text answers, use multiple matching strategies
    else:
      # Strategy 1: Check if expected word is contained in answer (with word boundaries)
      # This handles cases like agent says "Others" when expected is "other"
      expected_pattern = r'\b' + re.escape(expected) + r's?\b'  # Allow optional 's' for plural
      if re.search(expected_pattern, agent_answer, re.IGNORECASE):
        return 1.0
      
      # Strategy 2: Check if expected is in the answer (simple containment)
      if expected in agent_answer:
        return 1.0
      
      # Strategy 3: Fuzzy matching as fallback
      if fuzzy_match_lib.fuzzy_match(expected, agent_answer):
        return 1.0

    logging.warning(
        'Agent answer "%s" does not match expected "%s"', agent_answer, expected
    )
    return 0.0


class BluecoinsQuerySpendingOnDate(_BluecoinsQuery):
  """Query: How much did I spend in total on a specific date?"""

  template = 'In the Bluecoins app, how much did I spend in total on {date}?'
  complexity = 2

  @property
  def expected_answer(self) -> str:
    # Total of all 4 expenses: 512 + 888 + 256 + 768 = 2424
    return _EXPECTED_TOTAL

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {'date': _get_fixed_date(_FIXED_DAY)}


class BluecoinsQuerySpendingCategory(_BluecoinsQuery):
  """Query: What category is a specific expense under?"""

  template = 'In the Bluecoins app, what category is the {amount} USD expense on {date} under?'
  complexity = 2

  @property
  def expected_answer(self) -> str:
    # All expenses are under "Other" category
    return _EXPECTED_CATEGORY

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    amount = random.choice(_EXPECTED_AMOUNTS)
    return {'amount': amount, 'date': _get_fixed_date(_FIXED_DAY)}


class BluecoinsQueryTotalSpendingOnDate(_BluecoinsQuery):
  """Query: How much did I shell out in total on a specific date?"""

  template = 'In the Bluecoins app, how much did I shell out in total on {date}?'
  complexity = 2

  @property
  def expected_answer(self) -> str:
    return str(self.params['expected_total'])

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    # Total of 512 + 888 + 256 + 768 = 2424 USD on October 15, 2023
    return {'date': _get_fixed_date(_FIXED_DAY), 'expected_total': _EXPECTED_TOTAL}


class BluecoinsQueryTransactionCount(_BluecoinsQuery):
  """Query: How many transactions did I make on a specific date?"""

  template = 'In the Bluecoins app, how many transactions did I make all together on {date}?'
  complexity = 2

  @property
  def expected_answer(self) -> str:
    return str(self.params['expected_count'])

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    # 4 transactions on October 15, 2023
    return {'date': _get_fixed_date(_FIXED_DAY), 'expected_count': _EXPECTED_COUNT}


class BluecoinsQueryCategorySpending(_BluecoinsQuery):
  """Query: What's the total amount I spent on a category on a date?"""

  template = "In the Bluecoins app, what's the total amount I spent on '{category}' category on {date}?"
  complexity = 2.5

  @property
  def expected_answer(self) -> str:
    # All 4 expenses are under "Other" category, total = 2424
    return _EXPECTED_TOTAL

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {'category': 'Other', 'date': _get_fixed_date(_FIXED_DAY)}


# ============================================================================
# Operation Create Tasks - with SQLite validation
# ============================================================================


class _BluecoinsCreate(_Bluecoins):
  """Base class for Bluecoins create operation tasks.

  These tasks verify success by querying the SQLite database before and after
  the operation to check if the expected transaction was added.
  """

  complexity = 2

  def __init__(self, params: dict[str, Any]):
    super().__init__(params)
    self.before_transactions: list[BluecoinsTransaction] = []

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    # Store the state before the task
    self.before_transactions = self.list_transactions(env)
    logging.info('Before: %d transactions', len(self.before_transactions))

  def is_successful(self, env: interface.AsyncEnv) -> float:
    """Check if the transaction was created correctly by querying the database."""
    super().is_successful(env)
    after_transactions = self.list_transactions(env)
    logging.info('After: %d transactions', len(after_transactions))

    # Check if a new transaction was added
    if len(after_transactions) <= len(self.before_transactions):
      logging.warning('No new transaction was added.')
      return 0.0

    # Find new transactions
    before_ids = {t.transactionsTableID for t in self.before_transactions}
    new_transactions = [t for t in after_transactions if t.transactionsTableID not in before_ids]

    return self._validate_new_transaction(new_transactions)

  @abc.abstractmethod
  def _validate_new_transaction(self, new_transactions: list[BluecoinsTransaction]) -> float:
    """Validate that the expected transaction was created."""


class BluecoinsAddExpense(_BluecoinsCreate):
  """Task: Log an expenditure in the books."""

  template = 'In the Bluecoins app, log an expenditure of {amount} USD.'
  complexity = 1.5

  def _validate_new_transaction(self, new_transactions: list[BluecoinsTransaction]) -> float:
    expected_amount = float(self.params['amount'])
    for t in new_transactions:
      # Check if amount matches and it's an expense
      # Use amount_usd which converts from micro-units to USD
      if abs(t.amount_usd - expected_amount) <= 1 and t.is_expense:
        logging.info('Found matching expense: %s (amount_usd=%s)', t, t.amount_usd)
        return 1.0
      # Also check without type restriction (amount only)
      if abs(t.amount_usd - expected_amount) <= 1:
        logging.info('Found transaction with matching amount: %s (amount_usd=%s)', t, t.amount_usd)
        return 0.8
    logging.warning('No matching expense found for amount %s', expected_amount)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {'amount': random.choice([512, 256, 768, 100, 350, 888])}


class BluecoinsAddIncomeWithLabel(_BluecoinsCreate):
  """Task: Record an income with a specific label."""

  template = "In the Bluecoins app, record an income of {amount} USD and mark it as '{label}'."
  complexity = 2

  def _validate_new_transaction(self, new_transactions: list[BluecoinsTransaction]) -> float:
    expected_amount = float(self.params['amount'])
    expected_label = self.params['label'].lower()
    for t in new_transactions:
      if abs(t.amount_usd - expected_amount) <= 1:
        # Check label in notes (notes is the main field for labels)
        if expected_label in (t.notes or '').lower():
          logging.info('Found matching income with label: %s', t)
          return 1.0
        # Amount matches but no label
        if t.is_income:
          logging.info('Found income with matching amount but different label: %s', t)
          return 0.5
    logging.warning('No matching income found for amount %s with label %s', expected_amount, expected_label)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {'amount': 8000, 'label': 'salary'}


class BluecoinsAddExpenseOnDate(_BluecoinsCreate):
  """Task: Note down an expense for a specific date."""

  template = 'In the Bluecoins app, note down an expense of {amount} USD for {date}.'
  complexity = 2.5

  def _validate_new_transaction(self, new_transactions: list[BluecoinsTransaction]) -> float:
    expected_amount = float(self.params['amount'])
    for t in new_transactions:
      if abs(t.amount_usd - expected_amount) <= 1 and t.is_expense:
        logging.info('Found matching expense on date: %s', t)
        return 1.0
      if abs(t.amount_usd - expected_amount) <= 1:
        logging.info('Found matching amount (but may not be expense): %s', t)
        return 0.8
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    amount = random.choice([768, 512, 256, 1024])
    return {'amount': amount, 'date': _get_fixed_date(_FIXED_DAY)}


class BluecoinsAddIncomeOnDateWithNote(_BluecoinsCreate):
  """Task: Record income for a specific date with a note."""

  template = "In the Bluecoins app, for {date}, jot down an income of {amount} USD with '{note}' as the note."
  complexity = 3

  def _validate_new_transaction(self, new_transactions: list[BluecoinsTransaction]) -> float:
    expected_amount = float(self.params['amount'])  # Handle decimal input
    expected_note = self.params['note'].lower()
    for t in new_transactions:
      if abs(t.amount_usd - expected_amount) <= 1:
        if expected_note in (t.notes or '').lower():
          logging.info('Found matching income with note: %s', t)
          return 1.0
        if t.is_income:
          logging.info('Found income with matching amount: %s', t)
          return 0.5
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {'date': _get_fixed_date(_FIXED_DAY), 'amount': 100, 'note': 'gift'}


class BluecoinsAddExpenseOnDateWithLabel(_BluecoinsCreate):
  """Task: Record expenditure for a specific date with a label."""

  template = "In the Bluecoins app, for {date}, record an expenditure of {amount} USD, marked as '{label}'."
  complexity = 3

  def _validate_new_transaction(self, new_transactions: list[BluecoinsTransaction]) -> float:
    expected_amount = float(self.params['amount'])
    expected_label = self.params['label'].lower()
    for t in new_transactions:
      if abs(t.amount_usd - expected_amount) <= 1:
        if expected_label in (t.notes or '').lower():
          logging.info('Found matching expense with label: %s', t)
          return 1.0
        if t.is_expense:
          logging.info('Found expense with matching amount: %s', t)
          return 0.5
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {'date': _get_fixed_date(_FIXED_DAY), 'amount': 256, 'label': 'eating'}


# ============================================================================
# Operation Edit Tasks - with SQLite validation
# ============================================================================


class _BluecoinsEdit(_Bluecoins):
  """Base class for Bluecoins edit operation tasks.

  These tasks verify success by querying the SQLite database before and after
  the operation to check if the expected modification was made.
  """

  complexity = 3

  def __init__(self, params: dict[str, Any]):
    super().__init__(params)
    self.before_transactions: list[BluecoinsTransaction] = []

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    self.before_transactions = self.list_transactions(env)
    logging.info('Before edit: %d transactions', len(self.before_transactions))

  def is_successful(self, env: interface.AsyncEnv) -> float:
    """Check if the transaction was edited correctly by querying the database."""
    super().is_successful(env)
    after_transactions = self.list_transactions(env)
    logging.info('After edit: %d transactions', len(after_transactions))
    return self._validate_edit(after_transactions)

  @abc.abstractmethod
  def _validate_edit(self, after_transactions: list[BluecoinsTransaction]) -> float:
    """Validate that the expected edit was made."""


class BluecoinsEditExpenseAmount(_BluecoinsEdit):
  """Task: Adjust an expenditure to a new amount."""

  template = 'In the Bluecoins app, adjust the expenditure on {date} to {new_amount} USD.'
  complexity = 2.5

  def _validate_edit(self, after_transactions: list[BluecoinsTransaction]) -> float:
    expected_amount = float(self.params['new_amount'])
    for t in after_transactions:
      if abs(t.amount_usd - expected_amount) <= 1 and t.is_expense:
        logging.info('Found transaction with updated amount: %s', t)
        return 1.0
    logging.warning('No transaction found with amount %s', expected_amount)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {'date': _get_fixed_date(_FIXED_DAY), 'new_amount': 500}


class BluecoinsEditIncomeDateAndAmount(_BluecoinsEdit):
  """Task: Shift an income entry to a new date and update amount."""

  template = (
      'In the Bluecoins app, shift the income entry from {old_date} to {new_date}, '
      'and update the amount to {new_amount} USD.'
  )
  complexity = 3.5

  def _validate_edit(self, after_transactions: list[BluecoinsTransaction]) -> float:
    expected_amount = float(self.params['new_amount'].replace(',', ''))
    for t in after_transactions:
      if abs(t.amount_usd - expected_amount) <= 1 and t.is_income:
        logging.info('Found transaction with updated amount: %s', t)
        return 1.0
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {
        'old_date': _get_fixed_date(13),  # Oct 13, 2023
        'new_date': _get_fixed_date(_FIXED_DAY),
        'new_amount': '18250'
    }


class BluecoinsEditTransactionType(_BluecoinsEdit):
  """Task: Switch transaction type and add a note."""

  template = (
      "In the Bluecoins app, switch the {old_date} transaction from '{old_type}' to '{new_type}' "
      "and add '{note}' as the note."
  )
  complexity = 3.5

  def _validate_edit(self, after_transactions: list[BluecoinsTransaction]) -> float:
    expected_note = self.params['note'].lower()
    expected_new_type = self.params['new_type'].lower()
    for t in after_transactions:
      # Check if note matches
      if expected_note in (t.notes or '').lower():
        # Verify type was changed correctly
        if expected_new_type == 'income' and t.is_income:
          logging.info('Found transaction with updated note and type: %s', t)
          return 1.0
        elif expected_new_type == 'expense' and t.is_expense:
          logging.info('Found transaction with updated note and type: %s', t)
          return 1.0
        else:
          logging.info('Found transaction with note but wrong type: %s', t)
          return 0.5
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {'old_date': _get_fixed_date(_FIXED_DAY), 'old_type': 'expense', 'new_type': 'income', 'note': 'Gift'}


class BluecoinsEditTransactionTypeAmountNote(_BluecoinsEdit):
  """Task: Change transaction type, amount, and note."""

  template = (
      "In the Bluecoins app, change the type of the transaction on {date} from '{old_type}' to "
      "'{new_type}', adjust the amount to {new_amount} USD, and change the "
      "note to '{new_note}'."
  )
  complexity = 4

  def _validate_edit(self, after_transactions: list[BluecoinsTransaction]) -> float:
    expected_amount = float(self.params['new_amount'])
    expected_note = self.params['new_note'].lower()
    expected_new_type = self.params['new_type'].lower()
    for t in after_transactions:
      if abs(t.amount_usd - expected_amount) <= 1:
        if expected_note in (t.notes or '').lower():
          # Verify type
          if expected_new_type == 'expense' and t.is_expense:
            logging.info('Found transaction with updated amount, note, and type: %s', t)
            return 1.0
          elif expected_new_type == 'income' and t.is_income:
            logging.info('Found transaction with updated amount, note, and type: %s', t)
            return 1.0
          else:
            logging.info('Found transaction with amount and note but wrong type: %s', t)
            return 0.7
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {
        'date': _get_fixed_date(14),  # Oct 14, 2023 (where income exists)
        'old_type': 'income',
        'new_type': 'expense',
        'new_amount': 520,
        'new_note': 'Wrong Operation',
    }


class BluecoinsEditExpenseDateAmountNote(_BluecoinsEdit):
  """Task: Move expense to new date, adjust amount, and update note."""

  template = (
      'In the Bluecoins app, move the expense entry from {old_date} to {new_date}, adjust the '
      "amount to {new_amount} USD, and update the note to '{new_note}'."
  )
  complexity = 4

  def _validate_edit(self, after_transactions: list[BluecoinsTransaction]) -> float:
    expected_amount = float(self.params['new_amount'])
    expected_note = self.params['new_note'].lower()
    for t in after_transactions:
      if abs(t.amount_usd - expected_amount) <= 1 and t.is_expense:
        if expected_note in (t.notes or '').lower():
          logging.info('Found transaction with updated amount and note: %s', t)
          return 1.0
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {
        'old_date': _get_fixed_date(_FIXED_DAY),
        'new_date': _get_fixed_date(14),  # Oct 14, 2023
        'new_amount': 936,
        'new_note': 'Grocery Shopping',
    }
