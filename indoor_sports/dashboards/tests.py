from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from sports.models import Sport, Location
from accounts.models import User

'''class DashboardTests(TestCase):
    def setUp(self):
        """Setup test data before running each test"""
        self.client = Client()

        # Create a test user
        self.user = User.objects.create(
            userid=1,
            firstname="John",
            lastname="Doe",
            contactnumber="1234567890",
            emailid="john@example.com",
            password="securepassword",
            address="123 Test St",
            city="Test City",
            state="Test State",
            country="Test Country",
            zip_code="123456",
            gender="Male",
           
        )

        # Create test locations
        self.location1 = Location.objects.create(id=1, name="Denton Downtown")
        self.location2 = Location.objects.create(id=2, name="Plano")

        # Create test sports
        self.sport1 = Sport.objects.create(
            name="Badminton",
            category="Indoor",
            id=self.location1.id,
            description="Indoor Badminton Court",
        )

        self.sport2 = Sport.objects.create(
            name="Basketball",
            category="Outdoor",
            id=self.location2.id,
            description="Outdoor Basketball Court",
        )
        # ✅ Assign a default location to any sport with NULL location_id
        default_location = Location.objects.first()
        Sport.objects.filter(location__isnull=True).update(location=default_location)

    def test_sports_list_view(self):
        """Test if sports are listed in the dashboard"""
        session = self.client.session
        session["userid"] = self.user.userid
        session["role"] = "user"  # ✅ Make sure session role is present before request
        session["is_authenticated"] = True
        session.save()

        response = self.client.get(reverse("user_dashboard"))

        # DEBUG CHECK
        print("RESPONSE STATUS:", response.status_code)
        print("RESPONSE CONTENT:", response.content.decode())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Badminton")
        self.assertContains(response, "Basketball")

    def test_user_dashboard_requires_login(self):
        """Test that dashboard redirects if user is not logged in"""
        response = self.client.get(reverse("user_dashboard"))  # No session added (unauthenticated)
        self.assertRedirects(response, reverse("loginpage"))  #  Correct: Check if redirected'''

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User

class RegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.registration_url = reverse("register_user")

        # Create a user to test duplicate email/username
        self.existing_user = User.objects.create(
            firstname="Test",
            lastname="User",
            username="existinguser",
            emailid="existing@example.com",
            password="hashedpassword",  # Assuming already hashed or test value
            contactnumber="1234567890",
            address="Test Street",
            city="Test City",
            state="Test State",
            country="Test Country",
            zip_code="123456",
            gender="Male",
            referral_code="REF12345"
        )

    def test_registration_success(self):
        """ Register user with all valid data"""
        response = self.client.post(self.registration_url, {
            "username": "newuser",
            "firstname": "John",
            "lastname": "Doe",
            "emailid": "john.doe@example.com",
            "password": "password123",
            "phone": "9876543210",
            "address": "456 Elm Street",
            "city": "New City",
            "state": "New State",
            "country": "New Country",
            "zip_code": "654321",
            "gender": "Male",
            "referral_code": "REF12345"
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_registration_duplicate_email(self):
        """ Register with already existing email should fail"""
        response = self.client.post(self.registration_url, {
            "username": "uniqueuser",
            "firstname": "Alice",
            "lastname": "Smith",
            "emailid": "existing@example.com",  # Email already exists
            "password": "password456",
            "phone": "1234567890",
            "address": "123 Some St",
            "city": "City",
            "state": "State",
            "country": "Country",
            "zip_code": "111111",
            "gender": "Female"
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn("Email already registered. Please use another email.", [m.message for m in response.wsgi_request._messages])

    def test_registration_missing_fields(self):
        """ Register with missing required fields (email, password)"""
        response = self.client.post(self.registration_url, {
            "username": "missingfieldsuser",
            "firstname": "Tom",
            "lastname": "Hanks",
            "password": "",  # Password missing
            "emailid": "",   # Email missing
            "phone": "0000000000",
            "address": "Nowhere St",
            "city": "X",
            "state": "Y",
            "country": "Z",
            "zip_code": "000000",
            "gender": "Male"
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn("Email and password are required.", [m.message for m in response.wsgi_request._messages])


class DashboardTests(TestCase):
    def setUp(self):
        """Setup test data before running each test"""
        self.client = Client()

        # Create a test user
        self.user = User.objects.create(
            userid=1,
            firstname="John",
            lastname="Doe",
            contactnumber="1234567890",
            emailid="john@example.com",
            password="securepassword",
            address="123 Test St",
            city="Test City",
            state="Test State",
            country="Test Country",
            zip_code="123456",
            gender="Male"
        )

        # Create test locations
        self.location1 = Location.objects.create(id=1, name="Denton Downtown")
        self.location2 = Location.objects.create(id=2, name="Plano")

        # Create test sports
        self.sport1 = Sport.objects.create(
            name="Badminton",
            category="Indoor",
            location=self.location1,
            description="Indoor Badminton Court",
        )

        self.sport2 = Sport.objects.create(
            name="Basketball",
            category="Outdoor",
            location=self.location2,
            description="Outdoor Basketball Court",
        )

        #  Assign default location to NULL location_id sports
        default_location = Location.objects.first()
        Sport.objects.filter(location__isnull=True).update(location=default_location)

    def test_sports_list_view(self):
        """ Test if sports are listed in the dashboard"""
        session = self.client.session
        session["user_id"] = self.user.userid
        session["role"] = "user"
        session["is_authenticated"] = True
        session.save()

        response = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Badminton")
        self.assertContains(response, "Basketball")

    def test_user_dashboard_requires_login(self):
        """Test dashboard redirects if user is not logged in"""
        response = self.client.get(reverse("user_dashboard"))  # No session set
        self.assertRedirects(response, reverse("loginpage"))

    def test_add_sport(self):
        """Test adding a new sport via form"""
        session = self.client.session
        session["user_id"] = self.user.userid
        session["role"] = "admin"
        session["is_authenticated"] = True
        session.save()

        response = self.client.post(reverse("add_sport"), {
            "name": "Tennis",
            "category": "Outdoor",
            "location_id": self.location1.id,
            "description": "Tennis Court Description",
            "image_path": "images/tennis.jpg"
        })

        self.assertEqual(response.status_code, 302)  # Assuming redirect after add
        self.assertTrue(Sport.objects.filter(name="Tennis").exists())

    def test_delete_sport(self):
        """Test deleting a sport from a location"""
        session = self.client.session
        session["user_id"] = self.user.userid
        session["role"] = "admin"
        session["is_authenticated"] = True
        session.save()

        response = self.client.post(reverse("del_sport"), {
            "name": "Badminton",
            "location_id": self.location1.id
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Sport.objects.filter(name="Badminton", location=self.location1).exists())

