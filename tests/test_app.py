import unittest
from app import app, db, add_user_to_g
from models import User, Accounts, Transactions, Budgets, Goals, Category
from datetime import datetime
from werkzeug.security import generate_password_hash
from decimal import Decimal

class TestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the before_request handler only once."""
        app.before_request(add_user_to_g)

    def setUp(self):
        """Set up the test client and initialize the database."""
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.seed_database()

    def tearDown(self):
        """Tear down the database."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def seed_database(self):
        """Seed the database with initial data."""
        user_password = generate_password_hash('testpassword')
        user1 = User(
            first_name='John',
            last_name='Doe',
            username='johndoe',
            email='john@example.com',
            password=user_password,
            created_at=datetime.utcnow()
        )
        db.session.add(user1)
        db.session.commit()

        account1 = Accounts(
            name='John Savings',
            account_type='savings',
            balance=1000.00,
            user_id=user1.id,
            created_at=datetime.utcnow()
        )
        db.session.add(account1)
        db.session.commit()

        transaction1 = Transactions(
            type='expense',
            description='Supermarket shopping',
            amount=100,
            date=datetime.now(),
            account_id=account1.id,
            user_id=user1.id
        )
        db.session.add(transaction1)
        db.session.commit()

        categories = ['Home and Utilities', 'Transportation', 'Groceries']
        for category_name in categories:
            category = Category(name=category_name)
            db.session.add(category)
        db.session.commit()

    def test_signup_post(self):
        # Initial GET request to ensure the signup page loads correctly
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Signup', response.data)
        
        # POST request to submit the signup form
        response = self.client.post('/signup', data={
            'first_name': 'Test2',
            'last_name': 'User2',
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'password': 'testpassword2',
            'confirm_password': 'testpassword2'
        }, follow_redirects=True)

        response_text = response.data.decode()

        # Check if the user was created
        user = User.query.filter_by(email='testuser2@example.com').first()
        self.assertIsNotNone(user, "User was not created.")

        # Ensure 'Welcome Back!' is present in the response
        self.assertIn(b'Welcome Back!', response.data)

    def test_login_post(self):
        """Test the /login route with a POST request."""
        response = self.client.post('/login', data=dict(
            email="john@example.com",
            password="testpassword"
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome Back!', response.data)

    def test_logout(self):
        """Test the /logout route."""
        with self.client:
            self.client.post('/login', data=dict(
                email="john@example.com",
                password="testpassword"
            ), follow_redirects=True)
            response = self.client.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'You have successfully logged out.', response.data)

    def test_add_account(self):
        """Test adding a new account."""
        with self.client:
            self.client.post('/login', data=dict(
                email="john@example.com",
                password="testpassword"
            ), follow_redirects=True)
            
            response = self.client.post('/account/add', data={
                'name': 'Test Account',
                'account_type': 'checking',
                'balance': 2000.00
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Account added successfully.', response.data)

            account = Accounts.query.filter_by(name='Test Account').first()
            self.assertIsNotNone(account, "Account was not created.")
            self.assertEqual(account.balance, Decimal('2000.00'))

    def test_add_transaction(self):
        """Test adding a new transaction."""
        with self.client:
            self.client.post('/login', data=dict(
                email="john@example.com",
                password="testpassword"
            ), follow_redirects=True)

            account = Accounts.query.filter_by(name='John Savings').first()
            category = Category.query.filter_by(name='Groceries').first()

            response = self.client.post('/transaction/add', data={
                'type': 'expense',
                'description': 'Grocery Shopping',
                'amount': '150.00',
                'date': '2023-05-01',
                'account_id': str(account.id),
                'category': str(category.id)
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Transaction added successfully!', response.data)

            transaction = Transactions.query.filter_by(description='Grocery Shopping').first()
            self.assertIsNotNone(transaction, "Transaction was not created.")
            self.assertEqual(transaction.amount, Decimal('150.00'))

    def test_set_budget(self):
        """Test setting a new budget."""
        with self.client:
            self.client.post('/login', data=dict(
                email="john@example.com",
                password="testpassword"
            ), follow_redirects=True)

            category = Category.query.filter_by(name='Groceries').first()

            response = self.client.post('/budget/set', data={
                'category': str(category.id),
                'amount': '500.00',
                'start_date': '2023-05-01',
                'end_date': '2023-05-31'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Budget added.', response.data)

            budget = Budgets.query.filter_by(category_id=category.id).first()
            self.assertIsNotNone(budget, "Budget was not created.")
            self.assertEqual(budget.amount, Decimal('500.00'))

    def test_set_goal(self):
        """Test setting a new goal."""
        with self.client:
            self.client.post('/login', data=dict(
                email="john@example.com",
                password="testpassword"
            ), follow_redirects=True)

            response = self.client.post('/goal/set', data={
                'name': 'Save for Vacation',
                'target_amount': '3000.00'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Goal added.', response.data)

            goal = Goals.query.filter_by(name='Save for Vacation').first()
            self.assertIsNotNone(goal, "Goal was not created.")
            self.assertEqual(goal.target_amount, Decimal('3000.00'))

    def test_accounts_page(self):
        """Test accessing the accounts page."""
        with self.client:
            self.client.post('/login', data=dict(
                email="john@example.com",
                password="testpassword"
            ), follow_redirects=True)

            response = self.client.get('/account')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'John Savings', response.data)

    def test_budgets_page(self):
        """Test accessing the budgets page."""
        with self.client:
            self.client.post('/login', data=dict(
                email="john@example.com",
                password="testpassword"
            ), follow_redirects=True)

            response = self.client.get('/budget')
            self.assertEqual(response.status_code, 200)
        
            response_text = response.data.decode()
            print(response_text)  # Print the response data for debugging
        
            self.assertIn(b'Your Budgets', response.data)

    def test_goals_page(self):
        """Test accessing the goals page."""
        with self.client:
            self.client.post('/login', data=dict(
                email="john@example.com",
                password="testpassword"
            ), follow_redirects=True)

            response = self.client.get('/goal')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Goals', response.data)

    def test_transactions_page(self):
        """Test accessing the transactions page."""
        with self.client:
            self.client.post('/login', data=dict(
                email="john@example.com",
                password="testpassword"
            ), follow_redirects=True)

            response = self.client.get('/transaction')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Supermarket shopping', response.data)

    def test_delete_account(self):
        """Test deleting an account."""
        with self.client:
            self.client.post('/login', data=dict(
                email="john@example.com",
                password="testpassword"
            ), follow_redirects=True)

            account = Accounts.query.filter_by(name='John Savings').first()
            transaction = Transactions.query.filter_by(account_id=account.id).first()
            if transaction:
                db.session.delete(transaction)
                db.session.commit()

            response = self.client.post(f'/account/delete/{account.id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Account deleted successfully.', response.data)
            self.assertIsNone(Accounts.query.get(account.id))
    
    def test_delete_goal(self):
        """Test deleting a goal."""
        with self.client:
            self.client.post('/login', data=dict(
                email="john@example.com",
                password="testpassword"
            ), follow_redirects=True)

            self.client.post('/goal/set', data={
                'name': 'Save for Vacation',
                'target_amount': '3000.00'
            }, follow_redirects=True)

            goal = Goals.query.filter_by(name='Save for Vacation').first()
            response = self.client.post(f'/goal/delete/{goal.id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Goal deleted successfully.', response.data)
            self.assertIsNone(Goals.query.get(goal.id))

    def test_delete_budget(self):
        """Test deleting a budget."""
        with self.client:
            self.client.post('/login', data=dict(
                email="john@example.com",
                password="testpassword"
            ), follow_redirects=True)

            category = Category.query.filter_by(name='Groceries').first()
            self.client.post('/budget/set', data={
                'category': str(category.id),
                'amount': '500.00',
                'start_date': '2023-05-01',
                'end_date': '2023-05-31'
            }, follow_redirects=True)

            budget = Budgets.query.filter_by(category_id=category.id).first()
            response = self.client.post(f'/budget/delete/{budget.id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'budget deleted successfully.', response.data)
            self.assertIsNone(Budgets.query.get(budget.id))

    def test_delete_transaction(self):
        """Test deleting a transaction."""
        with self.client:
            self.client.post('/login', data=dict(
                email="john@example.com",
                password="testpassword"
            ), follow_redirects=True)

            transaction = Transactions.query.filter_by(description='Supermarket shopping').first()
            response = self.client.post(f'/transaction/delete/{transaction.id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Transaction deleted successfully.', response.data)
            self.assertIsNone(Transactions.query.get(transaction.id))


if __name__ == '__main__':
    unittest.main()
