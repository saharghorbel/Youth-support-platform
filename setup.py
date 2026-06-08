"""
Setup script for Youth Support Platform.
Run this after installing requirements to set up the database and create sample data.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youth_support_platform.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from accounts.models import User

def setup_database():
    """Run migrations and create database schema."""
    print("🔧 Running database migrations...")
    call_command('makemigrations')
    call_command('migrate')
    print("✅ Database migrations completed")

def create_superuser():
    """Create default superuser if it doesn't exist."""
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        print("👤 Creating superuser...")
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role=User.Role.ADMIN,
            first_name='Admin',
            last_name='User',
            organization='SESAME University'
        )
        print("✅ Superuser created (username: admin, password: admin123)")
    else:
        print("ℹ️  Superuser already exists")

def create_sample_users():
    """Create sample users for testing."""
    User = get_user_model()
    
    users_to_create = [
        {
            'username': 'supervisor1',
            'email': 'supervisor@example.com',
            'password': 'super123',
            'role': User.Role.SUPERVISOR,
            'first_name': 'Sarah',
            'last_name': 'Supervisor',
            'organization': 'School District 1'
        },
        {
            'username': 'operator1',
            'email': 'operator@example.com',
            'password': 'oper123',
            'role': User.Role.OPERATOR,
            'first_name': 'Omar',
            'last_name': 'Operator',
            'organization': 'School District 1'
        }
    ]
    
    print("👥 Creating sample users...")
    for user_data in users_to_create:
        if not User.objects.filter(username=user_data['username']).exists():
            User.objects.create_user(**user_data)
            print(f"   ✅ Created {user_data['username']} ({user_data['role']})")
        else:
            print(f"   ℹ️  {user_data['username']} already exists")

def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    directories = [
        'logs',
        'ml_models',
        'media',
        'staticfiles',
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ Created {directory}/")

def main():
    """Main setup function."""
    print("=" * 60)
    print("Youth Support Platform - Setup")
    print("=" * 60)
    print()
    
    try:
        create_directories()
        print()
        
        setup_database()
        print()
        
        create_superuser()
        print()
        
        create_sample_users()
        print()
        
        print("=" * 60)
        print("✅ Setup completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Run: python manage.py runserver")
        print("2. Visit: http://127.0.0.1:8000/admin/")
        print("3. Login with: admin / admin123")
        print()
        print("Sample accounts:")
        print("  - admin / admin123 (Admin)")
        print("  - supervisor1 / super123 (Supervisor)")
        print("  - operator1 / oper123 (Operator)")
        print()
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
