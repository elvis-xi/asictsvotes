from voting.models import Student
from django.contrib.auth.hashers import make_password

# Create demo students
students = [
    {'matric': 'SUG/001/2023', 'name': 'John Doe', 'password': 'test123'},
    {'matric': 'SUG/002/2023', 'name': 'Jane Smith', 'password': 'test123'},
    {'matric': 'SUG/003/2023', 'name': 'Mike Johnson', 'password': 'test123'},
    {'matric': 'SUG/004/2023', 'name': 'Sarah Williams', 'password': 'test123'},
]

for s in students:
    student, created = Student.objects.get_or_create(
        matric_number=s['matric'],
        defaults={
            'full_name': s['name'],
            'password': make_password(s['password']),
            'is_active': True
        }
    )
    if created:
        print(f"✓ Created: {s['name']} ({s['matric']})")
    else:
        print(f"• Already exists: {s['matric']}")

print("\n✅ Demo students ready!")
print("Login with: SUG/001/2023 | Password: test123")
exit()



from voting.models import Student
from django.contrib.auth.hashers import make_password

Student.objects.create(
    matric_number='20241477712',
    full_name='Comfort Ugwu',
    email='comfortugwu@example.com',
    department='Computer Science',
    faculty='School of Information Technology',
    password=make_password('20241477712'),
    is_active=True
)

print("✅ Student created successfully!")
print("Name: Comfort Ugwu")
print("Matric: 20241477712")
print("Password: 20241477712")