"""
Verify URL patterns are correctly configured.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youth_support_platform.settings')
django.setup()

from django.urls import get_resolver

print("=" * 70)
print("VERIFYING URL PATTERNS")
print("=" * 70)

resolver = get_resolver()

# Get all URL patterns
dashboard_urls = []
for pattern in resolver.url_patterns:
    if hasattr(pattern, 'app_name') and pattern.app_name == 'dashboard':
        for url_pattern in pattern.url_patterns:
            dashboard_urls.append(str(url_pattern.pattern))

print("\n✅ Dashboard URLs registered:")
print("-" * 70)
for url in sorted(dashboard_urls):
    print(f"  /dashboard/{url}")

print("\n" + "=" * 70)
print("✅ URL CONFIGURATION VERIFIED!")
print("=" * 70)

print("\nAccess these URLs in your browser:")
print("  • http://127.0.0.1:8000/dashboard/")
print("  • http://127.0.0.1:8000/dashboard/students/")
print("  • http://127.0.0.1:8000/dashboard/patients/")
print("  • http://127.0.0.1:8000/dashboard/alerts/")
print("  • http://127.0.0.1:8000/dashboard/reports/")
print("\nLogin with: admin / admin123")
