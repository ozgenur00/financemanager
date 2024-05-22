import unittest
from app import app, db
from models import User, Expense, Category, Accounts, Budgets, Transactions, Goals
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import uuid

class ModelTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test variables and create tables."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test data
        self.category = Category(name="Food")
        db.session.add(self.category)
        db.session.commit()

        unique_suffix = str(uuid.uuid4())
        unique_email = f"johndoe_{unique_suffix}@example.com"
        unique_username = f"johndoe_{unique_suffix}"

        try:
            self.user = User.signup(
                first_name="John", last_name="Doe", username=unique_username, email=unique_email, password="password"
            )
            if self.user is None:
                raise Exception("User creation returned None")
        except Exception as e:
            print(f"Error creating user: {e}")
            raise e

        try:
            self.account = Accounts(name="Test Account", account_type="Savings", balance=1000.00, user_id=self.user.id)
            self.budget = Budgets(category_name="Food Budget", amount=500.00, user_id=self.user.id, category_id=self.category.id)
            db.session.add_all([self.account, self.budget])
            db.session.commit()

            self.expense = Expense(amount=50.00, description="Grocery Shopping", category_id=self.category.id, user_id=self.user.id, budget_id=self.budget.id)
            self.transaction = Transactions(type="Debit", description="Bought groceries", amount=50.00, account_id=self.account.id, user_id=self.user.id)
            self.goal = Goals(name="Vacation Fund", target_amount=1000.00, user_id=self.user.id)
            
            db.session.add_all([self.expense, self.transaction, self.goal])
            db.session.commit()
        except Exception as e:
            print(f"Error creating test data: {e}")
            db.session.rollback()
            raise e

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_model(self):
        """Test User model."""
        user = db.session.get(User, self.user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")

    def test_expense_model(self):
        """Test Expense model."""
        expense = db.session.get(Expense, self.expense.id)
        self.assertIsNotNone(expense)
        self.assertEqual(expense.amount, 50.00)
        self.assertEqual(expense.description, "Grocery Shopping")
        self.assertEqual(expense.category.name, "Food")
        self.assertEqual(expense.user.first_name, "John")
        self.assertEqual(expense.budget.category_name, "Food Budget")

    def test_category_model(self):
        """Test Category model."""
        category = db.session.get(Category, self.category.id)
        self.assertIsNotNone(category)
        self.assertEqual(category.name, "Food")

    def test_accounts_model(self):
        """Test Accounts model."""
        account = db.session.get(Accounts, self.account.id)
        self.assertIsNotNone(account)
        self.assertEqual(account.name, "Test Account")
        self.assertEqual(account.account_type, "Savings")
        self.assertEqual(account.balance, 1000.00)
        self.assertEqual(account.user.first_name, "John")

    def test_budgets_model(self):
        """Test Budgets model."""
        budget = db.session.get(Budgets, self.budget.id)
        self.assertIsNotNone(budget)
        self.assertEqual(budget.category_name, "Food Budget")
        self.assertEqual(budget.amount, 500.00)
        self.assertEqual(budget.user.first_name, "John")
        self.assertEqual(budget.category.name, "Food")

    def test_transactions_model(self):
        """Test Transactions model."""
        transaction = db.session.get(Transactions, self.transaction.id)
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.type, "Debit")
        self.assertEqual(transaction.description, "Bought groceries")
        self.assertEqual(transaction.amount, 50.00)
        self.assertEqual(transaction.account.name, "Test Account")
        self.assertEqual(transaction.user.first_name, "John")

    def test_goals_model(self):
        """Test Goals model."""
        goal = db.session.get(Goals, self.goal.id)
        self.assertIsNotNone(goal)
        self.assertEqual(goal.name, "Vacation Fund")
        self.assertEqual(goal.target_amount, 1000.00)
        self.assertEqual(goal.user.first_name, "John")

if __name__ == '__main__':
    unittest.main()
