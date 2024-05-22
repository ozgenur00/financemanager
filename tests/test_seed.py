import unittest
from app import app, db
from models import User, Accounts, Transactions, Category
from seed import seed_database

class TestDatabaseSeeding(unittest.TestCase):

    def setUp(self):
        """Set up the test client and initialize the database."""
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Tear down the database."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_database_seeding(self):
        """Test the database seeding functionality."""
        with self.app.app_context():
            seed_database()
            # Verify the seeded data
            user = User.query.filter_by(username='johndoe').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'john@example.com')

            account = Accounts.query.filter_by(name='John Savings').first()
            self.assertIsNotNone(account)
            self.assertEqual(account.balance, 1000.00)
            self.assertEqual(account.user_id, user.id)

            transaction = Transactions.query.filter_by(description='Supermarket shopping').first()
            self.assertIsNotNone(transaction)
            self.assertEqual(transaction.amount, 100)
            self.assertEqual(transaction.account_id, account.id)
            self.assertEqual(transaction.user_id, user.id)

            categories = Category.query.all()
            category_names = [category.name for category in categories]
            expected_categories = [
                'Home and Utilities', 'Transportation', 'Groceries',
                'Health', 'Restaurants and Dining', 'Shopping and Entertainment',
                'Cash and Checks', 'Business Expenses', 'Education', 'Finance'
            ]
            self.assertEqual(sorted(category_names), sorted(expected_categories))

if __name__ == '__main__':
    unittest.main()
