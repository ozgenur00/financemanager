import unittest
from datetime import date, timedelta
from flask import Flask
from forms import (
    RegistrationForm, UserLoginForm, AccountCreationForm,
    BudgetCreationForm, TransactionForm, GoalCreationForm
)

class TestForms(unittest.TestCase):

    def setUp(self):
        """Set up test variables and create tables."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing purposes

        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up after each test."""
        self.app_context.pop()

    def test_registration_form_valid(self):
        form = RegistrationForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertTrue(form.validate())

    def test_registration_form_invalid_email(self):
        form = RegistrationForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'invalid-email',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertFalse(form.validate())
        self.assertIn('email', form.errors)

    def test_user_login_form_valid(self):
        form = UserLoginForm(data={
            'email': 'johndoe@example.com',
            'password': 'password123'
        })
        self.assertTrue(form.validate())

    def test_user_login_form_invalid_email(self):
        form = UserLoginForm(data={
            'email': 'invalid-email',
            'password': 'password123'
        })
        self.assertFalse(form.validate())
        self.assertIn('email', form.errors)

    def test_account_creation_form_valid(self):
        form = AccountCreationForm(data={
            'name': 'My Savings',
            'account_type': 'savings',
            'balance': 1000.00
        })
        self.assertTrue(form.validate())

    def test_account_creation_form_negative_balance(self):
        form = AccountCreationForm(data={
            'name': 'My Savings',
            'account_type': 'savings',
            'balance': -1000.00
        })
        self.assertFalse(form.validate())
        self.assertIn('balance', form.errors)

    def test_budget_creation_form_valid(self):
        form = BudgetCreationForm(data={
            'category': 'Food',
            'amount': 500.00,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=1)  # Ensure end_date is after start_date
        })
        form.category.choices = [('Food', 'Food')]  # Provide choices for the category field
        self.assertTrue(form.validate())

    def test_budget_creation_form_invalid_end_date(self):
        form = BudgetCreationForm(data={
            'category': 'Food',
            'amount': 500.00,
            'start_date': date.today(),
            'end_date': date.today()  # Same day as start_date, should fail
        })
        form.category.choices = [('Food', 'Food')]  # Provide choices for the category field
        form.start_date.data = date.today()
        form.end_date.data = date.today()
        self.assertFalse(form.validate())
        self.assertIn('end_date', form.errors)

    def test_transaction_form_valid(self):
        form_data = {
            'type': 'expense',
            'category': 'Groceries',
            'description': 'Bought groceries',
            'amount': 50.00,
            'date': date.today(),
            'account_id': 1
        }

        form = TransactionForm(data=form_data)

        # Set choices for category and account_id fields
        form.category.choices = [('Groceries', 'Groceries')]
        form.account_id.choices = [(1, 'Account 1')]

        print(f"Form data before validation: {form_data}")
        print(f"Form choices: account_id={form.account_id.choices}, category={form.category.choices}")

        # Perform validation
        valid = form.validate()
        print(f"Form valid: {valid}")
        print(f"Form errors: {form.errors}")

        # Print out the specific error for account_id
        if 'account_id' in form.errors:
            print(f"account_id field error: {form.errors['account_id']}")

        self.assertTrue(valid, msg=f"Form errors: {form.errors}")

        print(f"Form data after validation: {form.data}")

    def test_transaction_form_negative_amount(self):
        form = TransactionForm(data={
            'type': 'expense',
            'category': 'Groceries',
            'description': 'Bought groceries',
            'amount': -50.00,
            'date': date.today(),
            'account_id': '1'  # Ensure account_id is provided as a string to match the SelectField coercion
        })
        form.category.choices = [('Groceries', 'Groceries')]  # Provide choices for the category field
        form.account_id.choices = [(1, 'Account 1')]  # Provide choices for the account_id field

        print(f"Form data before validation: {form.data}")
        self.assertFalse(form.validate())
        self.assertIn('amount', form.errors)
        print(f"Form data after validation: {form.data}")

    def test_goal_creation_form_valid(self):
        form = GoalCreationForm(data={
            'name': 'Vacation Fund',
            'target_amount': 1000.00
        })
        self.assertTrue(form.validate())

    def test_goal_creation_form_negative_target_amount(self):
        form = GoalCreationForm(data={
            'name': 'Vacation Fund',
            'target_amount': -1000.00
        })
        self.assertFalse(form.validate())
        self.assertIn('target_amount', form.errors)

if __name__ == '__main__':
    unittest.main()
