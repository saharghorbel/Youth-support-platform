#!/usr/bin/env python
"""
Reset or create user accounts for Youth Support Platform
Usage: python reset_users.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youth_support_platform.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_or_reset_users():
    """Create or reset all user accounts with default passwords"""
    
    print("=" * 70)
    print("  YOUTH SUPPORT PLATFORM - Reset Users")
    print("=" * 70)
    print()
    
    users_config = [
        {
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'supervisor',
            'password': 'super123',
            'email': 'supervisor@example.com',
            'first_name': 'Supervisor',
            'last_name': 'User',
            'role': 'SUPERVISOR',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'username': 'operator',
            'password': 'oper123',
            'email': 'operator@example.com',
            'first_name': 'Operator',
            'last_name': 'User',
            'role': 'OPERATOR',
            'is_staff': False,
            'is_superuser': False,
        },
    ]
    
    for config in users_config:
        username = config.pop('username')
        password = config.pop('password')
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults=config
        )
        
        # Update user properties
        for key, value in config.items():
            setattr(user, key, value)
        
        # Set password
        user.set_password(password)
        user.is_active = True
        user.save()
        
        status = "✅ Created" if created else "✅ Updated"
        print(f"{status} {config['role']:12} | username: {username:12} | password: {password}")
    
    print()
    print("=" * 70)
    print("  All Users Active")
    print("=" * 70)
    
    for user in User.objects.filter(username__in=['admin', 'supervisor', 'operator']):
        print(f"  {user.get_role_display():12} | {user.username:12} | Active: {user.is_active}")
    
    print()
    print("✅ All users created/reset successfully!")
    print()
    print("🔐 Login at: http://127.0.0.1:8000/accounts/login/")
    print()

if __name__ == '__main__':
    create_or_reset_users()
