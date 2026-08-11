import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Sum

from quotations.models import CustomUser, Bill
from quotations.utils import generate_bill_number, number_to_words_indian
from quotations.pdf_generator import generate_quotation_pdf


# --- AUTHENTICATION VIEWS ---

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        display_name = request.POST.get('display_name', '').strip()
        phone_primary = request.POST.get('phone_primary', '').strip()
        phone_secondary = request.POST.get('phone_secondary', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not username or not email or not password or not phone_primary:
            messages.error(request, "Please fill in all required fields (Username, Email, Phone, Password).")
            return render(request, 'auth/register.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'auth/register.html')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'auth/register.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'auth/register.html')

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            display_name=display_name or username,
            phone_primary=phone_primary,
            phone_secondary=phone_secondary
        )

        login(request, user)
        messages.success(request, f"Welcome to M4 Interior Quotation Platform, {user.get_full_display_name()}!")
        return redirect('dashboard')

    return render(request, 'auth/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        login_input = request.POST.get('login_input', '').strip()
        password = request.POST.get('password', '').strip()

        if not login_input or not password:
            messages.error(request, "Please provide your email/username and password.")
            return render(request, 'auth/login.html')

        user = None
        if '@' in login_input:
            try:
                user_obj = CustomUser.objects.get(email__iexact=login_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                user = None
        else:
            user = authenticate(request, username=login_input, password=password)

        if user is not None:
            login(request, user)
            request.session.set_expiry(1209600)  # 2 weeks
            messages.success(request, f"Welcome back, {user.get_full_display_name()}!")
            next_url = request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid login credentials. Please try again.")

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


def forgot_password_view(request):
    reset_url = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            try:
                user = CustomUser.objects.get(email__iexact=email)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = request.build_absolute_uri(f"/reset-password/{uid}/{token}/")
                messages.success(request, f"Password reset link generated for {email}.")
            except CustomUser.DoesNotExist:
                messages.error(request, "No account found with this email address.")
    
    return render(request, 'auth/forgot_password.html', {'reset_url': reset_url})


def reset_password_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()

            if not new_password or new_password != confirm_password:
                messages.error(request, "Passwords must match and cannot be empty.")
                return render(request, 'auth/reset_password.html', {'valid_link': True})

            user.set_password(new_password)
            user.save()
            messages.success(request, "Your password has been successfully reset. Please log in.")
            return redirect('login')

        return render(request, 'auth/reset_password.html', {'valid_link': True})
    else:
        return render(request, 'auth/reset_password.html', {'valid_link': False})


# --- PROFILE VIEW (ENABLE EDITING USERNAME & EMAIL) ---

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        display_name = request.POST.get('display_name', '').strip()
        phone_primary = request.POST.get('phone_primary', '').strip()
        phone_secondary = request.POST.get('phone_secondary', '').strip()
        profile_picture_url = request.POST.get('profile_picture_url', '').strip()

        if not username or not email or not phone_primary:
            messages.error(request, "Username, Email Address, and Primary Phone Number are required.")
            return render(request, 'profile/profile.html', {'user': user})

        # Check if username is taken by another account
        if CustomUser.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, f"Username '{username}' is already taken by another account.")
            return render(request, 'profile/profile.html', {'user': user})

        # Check if email is taken by another account
        if CustomUser.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
            messages.error(request, f"Email address '{email}' is already registered with another account.")
            return render(request, 'profile/profile.html', {'user': user})

        user.username = username
        user.email = email
        user.display_name = display_name or user.username
        user.phone_primary = phone_primary
        user.phone_secondary = phone_secondary
        user.profile_picture_url = profile_picture_url

        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        messages.success(request, "Profile details (including Username & Email) updated successfully!")
        return redirect('profile')

    return render(request, 'profile/profile.html', {'user': user})


# --- DASHBOARD & CRUD VIEWS ---

@login_required
def dashboard_view(request):
    bills = Bill.objects.filter(user=request.user)

    bill_number_query = request.GET.get('bill_number', '').strip()
    client_name_query = request.GET.get('client_name', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    if bill_number_query:
        bills = bills.filter(bill_number__icontains=bill_number_query)
    if client_name_query:
        bills = bills.filter(client_name__icontains=client_name_query)
    if date_from:
        bills = bills.filter(bill_date__gte=date_from)
    if date_to:
        bills = bills.filter(bill_date__lte=date_to)

    total_bills_count = bills.count()
    total_amount_sum = bills.aggregate(Sum('grand_total'))['grand_total__sum'] or 0.00
    unique_clients_count = bills.values('client_name').distinct().count()

    context = {
        'bills': bills,
        'total_bills_count': total_bills_count,
        'total_amount_sum': total_amount_sum,
        'unique_clients_count': unique_clients_count,
        'bill_number_query': bill_number_query,
        'client_name_query': client_name_query,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def bill_create_view(request):
    if request.method == 'POST':
        quotation_title = request.POST.get('quotation_title', 'Labour Quotation').strip()
        company_name = request.POST.get('company_name', 'M4 Interior & Architect').strip()
        project_title = request.POST.get('project_title', 'Home 1').strip()
        client_name = request.POST.get('client_name', '').strip()
        client_phone = request.POST.get('client_phone', '').strip()
        bill_date = request.POST.get('bill_date', str(datetime.date.today()))
        items_json_raw = request.POST.get('items_json', '[]')

        if not client_name:
            messages.error(request, "Client Name is required.")
            return render(request, 'bills/form.html', {
                'is_edit': False,
                'bill_number': generate_bill_number(),
                'today_date': str(datetime.date.today()),
            })

        try:
            items = json.loads(items_json_raw)
        except Exception:
            items = []

        bill_number = generate_bill_number()

        grand_total = 0.0
        cleaned_items = []
        sl_counter = 1

        for item in items:
            if item.get('is_section') or item.get('type') == 'section':
                cleaned_items.append({
                    'is_section': True,
                    'particulars': item.get('particulars', '')
                })
            else:
                qty = float(item.get('qty', 0))
                rate = float(item.get('rate', 0))
                amount = round(qty * rate, 2)
                grand_total += amount
                cleaned_items.append({
                    'is_section': False,
                    'sl_no': sl_counter,
                    'particulars': item.get('particulars', ''),
                    'size': item.get('size', ''),
                    'qty': qty,
                    'unit': item.get('unit', 'Sq.Ft'),
                    'rate': rate,
                    'amount': amount
                })
                sl_counter += 1

        grand_total = round(grand_total, 2)
        amount_in_words = number_to_words_indian(grand_total)

        bill = Bill.objects.create(
            user=request.user,
            bill_number=bill_number,
            quotation_title=quotation_title or 'Labour Quotation',
            company_name=company_name or 'M4 Interior & Architect',
            architect_name=request.user.get_full_display_name(),
            project_title=project_title,
            client_name=client_name,
            client_phone=client_phone,
            bill_date=bill_date,
            items=cleaned_items,
            grand_total=grand_total,
            amount_in_words=amount_in_words
        )

        messages.success(request, f"Quotation {bill.bill_number} created successfully!")
        return redirect('bill_detail', pk=bill.pk)

    auto_bill_number = generate_bill_number()
    today_date = datetime.date.today().strftime('%Y-%m-%d')

    reference_demo_items = [
        {"is_section": True, "particulars": "Bed room 1"},
        {"is_section": False, "sl_no": 1, "particulars": "Wardrobe", "size": "2100*2120", "qty": 49, "unit": "Sq.Ft", "rate": 180, "amount": 8820},
        {"is_section": True, "particulars": "Bed room 2"},
        {"is_section": False, "sl_no": 2, "particulars": "wardrobe", "size": "2100*1680", "qty": 39.2, "unit": "Sq.Ft", "rate": 180, "amount": 7056},
        {"is_section": False, "sl_no": 3, "particulars": "Study unit", "size": "", "qty": 1, "unit": "Nos", "rate": 2500, "amount": 2500},
        {"is_section": True, "particulars": "Upper Bedroom 1"},
        {"is_section": False, "sl_no": 4, "particulars": "Wardrobe", "size": "2100*1680", "qty": 39.2, "unit": "Sq.Ft", "rate": 180, "amount": 7056},
        {"is_section": False, "sl_no": 5, "particulars": "Study unit", "size": "", "qty": 1, "unit": "Nos", "rate": 2500, "amount": 2500},
        {"is_section": True, "particulars": "Upper Bed room 2"},
        {"is_section": False, "sl_no": 6, "particulars": "Wardrobe", "size": "2100*1680", "qty": 39.2, "unit": "Sq.Ft", "rate": 180, "amount": 7056},
        {"is_section": False, "sl_no": 7, "particulars": "Study unit", "size": "", "qty": 1, "unit": "Nos", "rate": 2500, "amount": 2500},
        {"is_section": False, "sl_no": 8, "particulars": "Dressing", "size": "", "qty": 1, "unit": "Nos", "rate": 2000, "amount": 2000},
        {"is_section": True, "particulars": "Wash Area"},
        {"is_section": False, "sl_no": 9, "particulars": "Celling Work", "size": "", "qty": 22, "unit": "Sq.Ft", "rate": 180, "amount": 3960},
        {"is_section": False, "sl_no": 10, "particulars": "Architrave", "size": "2040*300\n1410*300", "qty": 18.3, "unit": "Sq.Ft", "rate": 180, "amount": 3294},
        {"is_section": False, "sl_no": 11, "particulars": "Wash basin box", "size": "1410*750", "qty": 11.8, "unit": "Sq.Ft", "rate": 180, "amount": 2115},
        {"is_section": False, "sl_no": 12, "particulars": "Wash unit mirror fixing", "size": "", "qty": 1, "unit": "Nos", "rate": 600, "amount": 600},
        {"is_section": False, "sl_no": 13, "particulars": "Stair bottom unit", "size": "", "qty": 22, "unit": "Sq.Ft", "rate": 180, "amount": 3960},
        {"is_section": False, "sl_no": 14, "particulars": "DB Box door", "size": "", "qty": 1, "unit": "Nos", "rate": 2000, "amount": 2000},
        {"is_section": True, "particulars": "Kitchen"},
        {"is_section": False, "sl_no": 15, "particulars": "Kitchen Celling work", "size": "", "qty": 1, "unit": "Nos", "rate": 1800, "amount": 1800},
        {"is_section": False, "sl_no": 16, "particulars": "Tall unit", "size": "2100*840", "qty": 19, "unit": "Sq.Ft", "rate": 180, "amount": 3420},
        {"is_section": False, "sl_no": 17, "particulars": "Loft Unit", "size": "2240*760", "qty": 18.3, "unit": "Sq.Ft", "rate": 180, "amount": 3294},
        {"is_section": False, "sl_no": 18, "particulars": "Wall unit", "size": "760*600\n430*600\n960*600\n930*600\n640*330", "qty": 22, "unit": "Sq.Ft", "rate": 180, "amount": 3960},
        {"is_section": False, "sl_no": 19, "particulars": "Base unit", "size": "1680*850\n2260*850\n1630*850", "qty": 50.8, "unit": "Sq.Ft", "rate": 180, "amount": 9144}
    ]

    return render(request, 'bills/form.html', {
        'is_edit': False,
        'bill_number': auto_bill_number,
        'today_date': today_date,
        'initial_items_json': json.dumps(reference_demo_items),
    })


@login_required
def bill_edit_view(request, pk):
    bill = get_object_or_404(Bill, pk=pk, user=request.user)

    if request.method == 'POST':
        quotation_title = request.POST.get('quotation_title', bill.quotation_title).strip()
        company_name = request.POST.get('company_name', bill.company_name).strip()
        project_title = request.POST.get('project_title', bill.project_title).strip()
        client_name = request.POST.get('client_name', bill.client_name).strip()
        client_phone = request.POST.get('client_phone', bill.client_phone).strip()
        bill_date = request.POST.get('bill_date', str(bill.bill_date))
        items_json_raw = request.POST.get('items_json', '[]')

        try:
            items = json.loads(items_json_raw)
        except Exception:
            items = bill.items

        grand_total = 0.0
        cleaned_items = []
        sl_counter = 1

        for item in items:
            if item.get('is_section') or item.get('type') == 'section':
                cleaned_items.append({
                    'is_section': True,
                    'particulars': item.get('particulars', '')
                })
            else:
                qty = float(item.get('qty', 0))
                rate = float(item.get('rate', 0))
                amount = round(qty * rate, 2)
                grand_total += amount
                cleaned_items.append({
                    'is_section': False,
                    'sl_no': sl_counter,
                    'particulars': item.get('particulars', ''),
                    'size': item.get('size', ''),
                    'qty': qty,
                    'unit': item.get('unit', 'Sq.Ft'),
                    'rate': rate,
                    'amount': amount
                })
                sl_counter += 1

        grand_total = round(grand_total, 2)
        amount_in_words = number_to_words_indian(grand_total)

        bill.quotation_title = quotation_title or 'Labour Quotation'
        bill.company_name = company_name or 'M4 Interior & Architect'
        bill.project_title = project_title
        bill.client_name = client_name
        bill.client_phone = client_phone
        bill.bill_date = bill_date
        bill.items = cleaned_items
        bill.grand_total = grand_total
        bill.amount_in_words = amount_in_words
        bill.save()

        messages.success(request, f"Quotation {bill.bill_number} updated successfully!")
        return redirect('bill_detail', pk=bill.pk)

    formatted_date = bill.bill_date.strftime('%Y-%m-%d') if hasattr(bill.bill_date, 'strftime') else str(bill.bill_date)

    return render(request, 'bills/form.html', {
        'is_edit': True,
        'bill': bill,
        'bill_number': bill.bill_number,
        'today_date': formatted_date,
        'initial_items_json': json.dumps(bill.items or []),
    })


@login_required
def bill_detail_view(request, pk):
    bill = get_object_or_404(Bill, pk=pk, user=request.user)
    return render(request, 'bills/detail.html', {'bill': bill})


@login_required
def bill_delete_view(request, pk):
    bill = get_object_or_404(Bill, pk=pk, user=request.user)
    if request.method == 'POST':
        num = bill.bill_number
        bill.delete()
        messages.success(request, f"Quotation {num} deleted successfully.")
        return redirect('dashboard')
    return render(request, 'bills/delete_confirm.html', {'bill': bill})


# --- PDF PREVIEW & DOWNLOAD VIEWS ---

@login_required
def bill_pdf_preview_view(request, pk):
    bill = get_object_or_404(Bill, pk=pk, user=request.user)
    
    owner_phone_1 = getattr(bill.user, 'phone_primary', '') or 'Ph.97 44 94 52 08'
    owner_phone_2 = getattr(bill.user, 'phone_secondary', '') or '97 44 94 52 09'

    bill_dict = {
        'bill_number': bill.bill_number,
        'quotation_title': bill.quotation_title,
        'company_name': bill.company_name,
        'architect_name': bill.architect_name or bill.user.get_full_display_name() or "Rajeev c.s",
        'architect_phone_primary': owner_phone_1,
        'architect_phone_secondary': owner_phone_2,
        'project_title': bill.project_title,
        'client_name': bill.client_name,
        'client_phone': bill.client_phone,
        'bill_date': str(bill.bill_date),
        'items': bill.items,
        'grand_total': float(bill.grand_total),
        'amount_in_words': bill.amount_in_words,
    }
    pdf_bytes = generate_quotation_pdf(bill_dict)
    return HttpResponse(pdf_bytes, content_type='application/pdf')


@login_required
def bill_pdf_download_view(request, pk):
    bill = get_object_or_404(Bill, pk=pk, user=request.user)

    owner_phone_1 = getattr(bill.user, 'phone_primary', '') or 'Ph.97 44 94 52 08'
    owner_phone_2 = getattr(bill.user, 'phone_secondary', '') or '97 44 94 52 09'

    bill_dict = {
        'bill_number': bill.bill_number,
        'quotation_title': bill.quotation_title,
        'company_name': bill.company_name,
        'architect_name': bill.architect_name or bill.user.get_full_display_name() or "Rajeev c.s",
        'architect_phone_primary': owner_phone_1,
        'architect_phone_secondary': owner_phone_2,
        'project_title': bill.project_title,
        'client_name': bill.client_name,
        'client_phone': bill.client_phone,
        'bill_date': str(bill.bill_date),
        'items': bill.items,
        'grand_total': float(bill.grand_total),
        'amount_in_words': bill.amount_in_words,
    }
    pdf_bytes = generate_quotation_pdf(bill_dict)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{bill.bill_number}.pdf"'
    return response
