import json
import datetime
from django.test import TestCase, Client
from django.urls import reverse
from quotations.models import CustomUser, Bill
from quotations.utils import generate_bill_number, number_to_words_indian
from quotations.pdf_generator import generate_quotation_pdf


class UtilityAndModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@m4interior.com",
            password="Password123",
            display_name="Test Architect",
            phone_primary="+91 99999 88888"
        )

    def test_user_display_name(self):
        self.assertEqual(self.user.get_full_display_name(), "Test Architect")

    def test_number_to_words_indian(self):
        words = number_to_words_indian(77035.00)
        self.assertIn("Seventy Seven Thousand", words)
        self.assertIn("Thirty Five", words)

        words_lakh = number_to_words_indian(125000.00)
        self.assertIn("One Lakh Twenty Five Thousand", words_lakh)

    def test_generate_bill_number(self):
        year = datetime.datetime.now().year
        bill_num_1 = generate_bill_number()
        self.assertTrue(bill_num_1.startswith(f"M4-{year}-"))

        Bill.objects.create(
            user=self.user,
            bill_number=bill_num_1,
            architect_name="Test Architect",
            project_title="Home 1",
            client_name="Test Client",
            client_phone="+91 90000 00000",
            bill_date=datetime.date.today(),
            items=[],
            grand_total=1000.00
        )

        bill_num_2 = generate_bill_number()
        self.assertNotEqual(bill_num_1, bill_num_2)

    def test_pdf_generation(self):
        bill_data = {
            'bill_number': 'M4-2026-999',
            'company_name': 'M4 Interior & Architect',
            'architect_name': 'Test Architect',
            'project_title': 'Unit Test Project',
            'client_name': 'John Doe',
            'client_phone': '+91 98765 43210',
            'bill_date': '2026-08-11',
            'items': [
                {'sl_no': 1, 'particulars': 'Wardrobe', 'size': '2100*2120', 'qty': 10, 'unit': 'Sq.Ft', 'rate': 1000, 'amount': 10000}
            ],
            'grand_total': 10000.00,
            'amount_in_words': 'Rupees Ten Thousand Only'
        }
        pdf_bytes = generate_quotation_pdf(bill_data)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username="architect1",
            email="arch1@m4interior.com",
            password="Password123",
            display_name="Er. Arch",
            phone_primary="+91 98765 11111"
        )
        self.bill = Bill.objects.create(
            user=self.user,
            bill_number="M4-2026-101",
            company_name="M4 Interior & Architect",
            architect_name="Er. Arch",
            project_title="Villa 10",
            client_name="Sharma Family",
            client_phone="+91 98765 22222",
            bill_date=datetime.date.today(),
            items=[{'sl_no': 1, 'particulars': 'Woodwork', 'size': '100*100', 'qty': 5, 'unit': 'Sq.Ft', 'rate': 500, 'amount': 2500}],
            grand_total=2500.00,
            amount_in_words="Rupees Two Thousand Five Hundred Only"
        )

    def test_login_and_dashboard(self):
        response = self.client.post(reverse('login'), {
            'login_input': 'arch1@m4interior.com',
            'password': 'Password123'
        })
        self.assertEqual(response.status_code, 302)

        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertContains(dashboard_response, "M4-2026-101")
        self.assertContains(dashboard_response, "Sharma Family")

    def test_dashboard_search(self):
        self.client.login(username="architect1", password="Password123")
        search_res = self.client.get(reverse('dashboard') + '?bill_number=M4-2026-101')
        self.assertContains(search_res, "Sharma Family")

        search_res_client = self.client.get(reverse('dashboard') + '?client_name=Sharma')
        self.assertContains(search_res_client, "M4-2026-101")

    def test_fresh_quotation_create_view(self):
        self.client.login(username="architect1", password="Password123")
        create_res = self.client.get(reverse('bill_create'))
        self.assertEqual(create_res.status_code, 200)
        self.assertNotContains(create_res, 'value="Antu"')
        self.assertNotContains(create_res, 'value="Home 1"')
        self.assertNotContains(create_res, 'particulars": "Wardrobe"')
        self.assertContains(create_res, 'placeholder="e.g. Client Name"')

    def test_live_pdf_preview_api(self):
        self.client.login(username="architect1", password="Password123")
        payload = {
            'bill_number': 'M4-2026-888',
            'quotation_title': 'Labour Quotation',
            'company_name': 'M4 Interior & Architect',
            'project_title': 'Site A',
            'client_name': 'Ramesh',
            'client_phone': '9876543210',
            'bill_date': '2026-08-12',
            'items': [{'is_section': False, 'sl_no': 1, 'particulars': 'Painting', 'size': '', 'qty': 10, 'unit': 'Sq.Ft', 'rate': 50, 'amount': 500}]
        }
        res = self.client.post(
            reverse('fastapi_generate_pdf'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.content.startswith(b"%PDF"))
