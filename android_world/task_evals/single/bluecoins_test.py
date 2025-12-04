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

"""Tests for Bluecoins tasks."""

from unittest import mock

from absl.testing import absltest
from android_world.task_evals.single import bluecoins
from android_world.utils import test_utils


# ============================================================================
# Tests for is_successful() SQLite Validation
# ============================================================================


class BluecoinsAddExpenseValidationTest(absltest.TestCase):
  """Tests for BluecoinsAddExpense is_successful() validation."""

  def setUp(self):
    self.mock_env = mock.MagicMock()
    self.mock_env.interaction_cache = None

  @mock.patch.object(bluecoins, 'sqlite_utils')
  def test_validate_new_expense_success(self, mock_sqlite):
    """Test successful validation when matching expense is found."""
    # Before: no transactions
    before_transactions = []

    # After: one new expense with amount 512
    after_transactions = [
        bluecoins.BluecoinsTransaction(
            transactionsTableID=1,
            amount=512,
            transactionTypeID=bluecoins._TRANSACTION_TYPE_EXPENSE,
            date='2024-05-10 10:00:00',
        )
    ]

    mock_sqlite.get_rows_from_remote_device.side_effect = [
        after_transactions  # Called in is_successful
    ]

    params = {'amount': 512}
    task = bluecoins.BluecoinsAddExpense(params)
    task.initialized = True
    task.before_transactions = before_transactions

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 1.0)

  @mock.patch.object(bluecoins, 'sqlite_utils')
  def test_validate_no_new_transaction(self, mock_sqlite):
    """Test when no new transaction was added."""
    before_transactions = []
    after_transactions = []  # Still empty

    mock_sqlite.get_rows_from_remote_device.return_value = after_transactions

    params = {'amount': 512}
    task = bluecoins.BluecoinsAddExpense(params)
    task.initialized = True
    task.before_transactions = before_transactions

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 0.0)

  @mock.patch.object(bluecoins, 'sqlite_utils')
  def test_validate_wrong_amount(self, mock_sqlite):
    """Test when transaction added but with wrong amount."""
    before_transactions = []
    after_transactions = [
        bluecoins.BluecoinsTransaction(
            transactionsTableID=1,
            amount=999,  # Wrong amount
            transactionTypeID=bluecoins._TRANSACTION_TYPE_EXPENSE,
        )
    ]

    mock_sqlite.get_rows_from_remote_device.return_value = after_transactions

    params = {'amount': 512}
    task = bluecoins.BluecoinsAddExpense(params)
    task.initialized = True
    task.before_transactions = before_transactions

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 0.0)


class BluecoinsAddIncomeWithLabelValidationTest(absltest.TestCase):
  """Tests for BluecoinsAddIncomeWithLabel is_successful() validation."""

  def setUp(self):
    self.mock_env = mock.MagicMock()

  @mock.patch.object(bluecoins, 'sqlite_utils')
  def test_validate_income_with_label_success(self, mock_sqlite):
    """Test successful validation when income with label is found."""
    after_transactions = [
        bluecoins.BluecoinsTransaction(
            transactionsTableID=1,
            amount=8000,
            transactionTypeID=bluecoins._TRANSACTION_TYPE_INCOME,
            notes='salary',
        )
    ]

    mock_sqlite.get_rows_from_remote_device.return_value = after_transactions

    params = {'amount': 8000, 'label': 'salary'}
    task = bluecoins.BluecoinsAddIncomeWithLabel(params)
    task.initialized = True
    task.before_transactions = []

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 1.0)

  @mock.patch.object(bluecoins, 'sqlite_utils')
  def test_validate_income_without_label_partial(self, mock_sqlite):
    """Test partial credit when income added but without correct label."""
    after_transactions = [
        bluecoins.BluecoinsTransaction(
            transactionsTableID=1,
            amount=8000,
            transactionTypeID=bluecoins._TRANSACTION_TYPE_INCOME,
            notes='',  # No label
        )
    ]

    mock_sqlite.get_rows_from_remote_device.return_value = after_transactions

    params = {'amount': 8000, 'label': 'salary'}
    task = bluecoins.BluecoinsAddIncomeWithLabel(params)
    task.initialized = True
    task.before_transactions = []

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 0.5)


class BluecoinsEditExpenseAmountValidationTest(absltest.TestCase):
  """Tests for BluecoinsEditExpenseAmount is_successful() validation."""

  def setUp(self):
    self.mock_env = mock.MagicMock()

  @mock.patch.object(bluecoins, 'sqlite_utils')
  def test_validate_edit_amount_success(self, mock_sqlite):
    """Test successful validation when amount was edited correctly."""
    after_transactions = [
        bluecoins.BluecoinsTransaction(
            transactionsTableID=1,
            amount=500,  # New amount
            transactionTypeID=bluecoins._TRANSACTION_TYPE_EXPENSE,
            date='2024-05-15 10:00:00',
        )
    ]

    mock_sqlite.get_rows_from_remote_device.return_value = after_transactions

    params = {'date': 'May 15, 2024', 'new_amount': 500}
    task = bluecoins.BluecoinsEditExpenseAmount(params)
    task.initialized = True
    task.before_transactions = []

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 1.0)


# ============================================================================
# Tests for BluecoinsTransaction Dataclass
# ============================================================================


class BluecoinsTransactionTest(absltest.TestCase):
  """Tests for BluecoinsTransaction dataclass."""

  def test_amount_float(self):
    transaction = bluecoins.BluecoinsTransaction(amount=388)
    self.assertEqual(transaction.amount_float, 388.0)

  def test_is_expense(self):
    # transactionTypeID=3 is expense
    transaction = bluecoins.BluecoinsTransaction(
        amount=512, transactionTypeID=bluecoins._TRANSACTION_TYPE_EXPENSE
    )
    self.assertTrue(transaction.is_expense)
    self.assertFalse(transaction.is_income)

  def test_is_income(self):
    # transactionTypeID=4 is income
    transaction = bluecoins.BluecoinsTransaction(
        amount=8000, transactionTypeID=bluecoins._TRANSACTION_TYPE_INCOME
    )
    self.assertTrue(transaction.is_income)
    self.assertFalse(transaction.is_expense)

  def test_date_str(self):
    transaction = bluecoins.BluecoinsTransaction(date='2024-05-10 14:30:00')
    self.assertEqual(transaction.date_str, 'May 10, 2024')

  def test_date_obj(self):
    transaction = bluecoins.BluecoinsTransaction(date='2024-05-10 14:30:00')
    self.assertIsNotNone(transaction.date_obj)
    self.assertEqual(transaction.date_obj.year, 2024)
    self.assertEqual(transaction.date_obj.month, 5)
    self.assertEqual(transaction.date_obj.day, 10)


class BluecoinsQuerySpendingOnDateTest(absltest.TestCase):
  """Tests for BluecoinsQuerySpendingOnDate task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsQuerySpendingOnDate.generate_random_params()
    self.assertIn('date', params)
    self.assertIn('expected_amount', params)

  def test_goal_format(self):
    params = {'date': 'May 10, 2024', 'expected_amount': '388.88'}
    task = bluecoins.BluecoinsQuerySpendingOnDate(params)
    self.assertEqual(
        task.goal, 'Could you tell me how much I spent on May 10, 2024?'
    )

  def test_expected_answer(self):
    params = {'date': 'May 10, 2024', 'expected_amount': '388.88'}
    task = bluecoins.BluecoinsQuerySpendingOnDate(params)
    self.assertEqual(task.expected_answer, '388.88')


class BluecoinsQuerySpendingCategoryTest(absltest.TestCase):
  """Tests for BluecoinsQuerySpendingCategory task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsQuerySpendingCategory.generate_random_params()
    self.assertIn('amount', params)
    self.assertIn('date', params)
    self.assertIn('expected_reason', params)

  def test_goal_format(self):
    params = {
        'amount': '388.88',
        'date': 'May 3, 2024',
        'expected_reason': 'taxi',
    }
    task = bluecoins.BluecoinsQuerySpendingCategory(params)
    self.assertEqual(
        task.goal,
        'What was the reason behind the 388.88 CNY I spent on May 3, 2024?',
    )


class BluecoinsQueryTransactionCountTest(absltest.TestCase):
  """Tests for BluecoinsQueryTransactionCount task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsQueryTransactionCount.generate_random_params()
    self.assertIn('date', params)
    self.assertIn('expected_count', params)

  def test_goal_format(self):
    params = {'date': 'May 6, 2024', 'expected_count': '5'}
    task = bluecoins.BluecoinsQueryTransactionCount(params)
    self.assertEqual(
        task.goal,
        'How many transactions did I make all together on May 6, 2024?',
    )


class BluecoinsQueryCategorySpendingTest(absltest.TestCase):
  """Tests for BluecoinsQueryCategorySpending task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsQueryCategorySpending.generate_random_params()
    self.assertIn('category', params)
    self.assertIn('expected_total', params)

  def test_goal_format(self):
    params = {'category': 'taxis', 'expected_total': '500'}
    task = bluecoins.BluecoinsQueryCategorySpending(params)
    self.assertEqual(
        task.goal, "What's the total amount I spent on taxis this week?"
    )


class BluecoinsAddExpenseTest(absltest.TestCase):
  """Tests for BluecoinsAddExpense task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsAddExpense.generate_random_params()
    self.assertIn('amount', params)
    self.assertIsInstance(params['amount'], int)

  def test_goal_format(self):
    params = {'amount': 512}
    task = bluecoins.BluecoinsAddExpense(params)
    self.assertEqual(task.goal, 'Log an expenditure of 512 CNY in the books.')

  def test_complexity(self):
    params = {'amount': 512}
    task = bluecoins.BluecoinsAddExpense(params)
    self.assertEqual(task.complexity, 1.5)


class BluecoinsAddIncomeWithLabelTest(absltest.TestCase):
  """Tests for BluecoinsAddIncomeWithLabel task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsAddIncomeWithLabel.generate_random_params()
    self.assertIn('amount', params)
    self.assertIn('label', params)

  def test_goal_format(self):
    params = {'amount': 8000, 'label': 'salary'}
    task = bluecoins.BluecoinsAddIncomeWithLabel(params)
    self.assertEqual(
        task.goal,
        "Record an income of 8000 CNY in the books, and mark it as 'salary'.",
    )


class BluecoinsAddExpenseOnDateTest(absltest.TestCase):
  """Tests for BluecoinsAddExpenseOnDate task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsAddExpenseOnDate.generate_random_params()
    self.assertIn('amount', params)
    self.assertIn('date', params)

  def test_goal_format(self):
    params = {'amount': 768, 'date': 'May 11, 2024'}
    task = bluecoins.BluecoinsAddExpenseOnDate(params)
    self.assertEqual(
        task.goal, 'Note down an expense of 768 CNY for May 11, 2024.'
    )


class BluecoinsAddIncomeOnDateWithNoteTest(absltest.TestCase):
  """Tests for BluecoinsAddIncomeOnDateWithNote task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsAddIncomeOnDateWithNote.generate_random_params()
    self.assertIn('amount', params)
    self.assertIn('date', params)
    self.assertIn('note', params)

  def test_goal_format(self):
    params = {'date': 'March 8, 2024', 'amount': 3, 'note': 'Weixin red packet'}
    task = bluecoins.BluecoinsAddIncomeOnDateWithNote(params)
    self.assertEqual(
        task.goal,
        "For March 8, 2024, jot down an income of 3 CNY with 'Weixin red packet' as the note.",
    )


class BluecoinsAddExpenseOnDateWithLabelTest(absltest.TestCase):
  """Tests for BluecoinsAddExpenseOnDateWithLabel task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsAddExpenseOnDateWithLabel.generate_random_params()
    self.assertIn('amount', params)
    self.assertIn('date', params)
    self.assertIn('label', params)

  def test_goal_format(self):
    params = {'date': 'May 14, 2024', 'amount': 256, 'label': 'eating'}
    task = bluecoins.BluecoinsAddExpenseOnDateWithLabel(params)
    self.assertEqual(
        task.goal,
        "For May 14, 2024, record an expenditure of 256 CNY, marked as 'eating'.",
    )


class BluecoinsEditExpenseAmountTest(absltest.TestCase):
  """Tests for BluecoinsEditExpenseAmount task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsEditExpenseAmount.generate_random_params()
    self.assertIn('date', params)
    self.assertIn('new_amount', params)

  def test_goal_format(self):
    params = {'date': 'May 15, 2024', 'new_amount': 500}
    task = bluecoins.BluecoinsEditExpenseAmount(params)
    self.assertEqual(
        task.goal,
        'Adjust the expenditure on May 15, 2024, to 500 CNY.',
    )


class BluecoinsEditIncomeDateAndAmountTest(absltest.TestCase):
  """Tests for BluecoinsEditIncomeDateAndAmount task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsEditIncomeDateAndAmount.generate_random_params()
    self.assertIn('old_date', params)
    self.assertIn('new_date', params)
    self.assertIn('new_amount', params)

  def test_goal_format(self):
    params = {
        'old_date': 'May 12th, 2024',
        'new_date': 'May 10th, 2024',
        'new_amount': '18250',
    }
    task = bluecoins.BluecoinsEditIncomeDateAndAmount(params)
    self.assertEqual(
        task.goal,
        'Shift the income entry from May 12th, 2024, to May 10th, 2024, and '
        'update the amount to 18250 CNY.',
    )


class BluecoinsEditTransactionTypeTest(absltest.TestCase):
  """Tests for BluecoinsEditTransactionType task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsEditTransactionType.generate_random_params()
    self.assertIn('old_date', params)
    self.assertIn('old_type', params)
    self.assertIn('new_type', params)
    self.assertIn('note', params)

  def test_goal_format(self):
    params = {
        'old_date': 'May 13, 2024',
        'old_type': 'expense',
        'new_type': 'income',
        'note': 'Gift',
    }
    task = bluecoins.BluecoinsEditTransactionType(params)
    self.assertEqual(
        task.goal,
        "Switch the May 13, 2024 transaction from 'expense' to 'income' and "
        "add 'Gift' as the note.",
    )


class BluecoinsEditTransactionTypeAmountNoteTest(absltest.TestCase):
  """Tests for BluecoinsEditTransactionTypeAmountNote task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsEditTransactionTypeAmountNote.generate_random_params()
    self.assertIn('date', params)
    self.assertIn('old_type', params)
    self.assertIn('new_type', params)
    self.assertIn('new_amount', params)
    self.assertIn('new_note', params)

  def test_goal_format(self):
    params = {
        'date': 'May 2, 2024',
        'old_type': 'income',
        'new_type': 'expense',
        'new_amount': 520,
        'new_note': 'Wrong Operation',
    }
    task = bluecoins.BluecoinsEditTransactionTypeAmountNote(params)
    self.assertEqual(
        task.goal,
        "Change the type of the transaction on May 2, 2024, from 'income' to "
        "'expense', adjust the amount to 520 CNY, and change the note to "
        "'Wrong Operation'.",
    )


class BluecoinsEditExpenseDateAmountNoteTest(absltest.TestCase):
  """Tests for BluecoinsEditExpenseDateAmountNote task."""

  def test_generate_random_params(self):
    params = bluecoins.BluecoinsEditExpenseDateAmountNote.generate_random_params()
    self.assertIn('old_date', params)
    self.assertIn('new_date', params)
    self.assertIn('new_amount', params)
    self.assertIn('new_note', params)

  def test_goal_format(self):
    params = {
        'old_date': 'May 12, 2024',
        'new_date': 'May 13, 2024',
        'new_amount': 936,
        'new_note': 'Grocery Shopping',
    }
    task = bluecoins.BluecoinsEditExpenseDateAmountNote(params)
    self.assertEqual(
        task.goal,
        'Move the expense entry from May 12, 2024, to May 13, 2024, adjust the '
        "amount to 936 CNY, and update the note to 'Grocery Shopping'.",
    )


if __name__ == '__main__':
  absltest.main()

