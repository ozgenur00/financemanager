from sqlalchemy import inspect
from app import app, db
from models import User, Accounts, Budgets, Transactions, Goals, Category  
from datetime import datetime
from werkzeug.security import generate_password_hash
import os

def seed_database():
    with app.app_context():
        try:
            # Debug: Print existing tables before creating all
            inspector = inspect(db.engine)
            print("Existing tables before creating all:", inspector.get_table_names())
            
            db.drop_all()
            db.create_all()
            
            # Debug: Print existing tables after creating all
            inspector = inspect(db.engine)
            print("Existing tables after creating all:", inspector.get_table_names())
            
            if not db.session.query(User).first():
                print("Seeding data...")

                categories = [
                    'Home and Utilities', 'Transportation', 'Groceries',
                    'Health', 'Restaurants and Dining', 'Shopping and Entertainment',
                    'Cash and Checks', 'Business Expenses', 'Education', 'Finance'
                ]
                
                for category_name in categories:
                    category = Category(name=category_name)
                    db.session.add(category)
                db.session.commit()

                user1 = User(
                    first_name='John',
                    last_name='Doe',
                    username='johndoe',
                    email='john@example.com',
                    password=generate_password_hash('your_plain_text_password')  # Directly hash the password
                )
                db.session.add(user1)
                db.session.commit()

                account1 = Accounts(
                    name='John Savings',
                    account_type='savings',
                    balance=1000.00,
                    user_id=user1.id
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

                print('Database seeded!')
            else:
                print("Database already contains data. No seed performed.")
        except Exception as e:
            print(f"An error occurred while seeding the database: {e}")

if __name__ == '__main__':
    if os.getenv('FLASK_ENV') == 'development':
        seed_database()
    else:
        print('Seeding is skipped. Not in development environment.')
