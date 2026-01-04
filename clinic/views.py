from django.shortcuts import render, redirect
from .models import Patient,Contact,Doctor,Newsletter,Appointment
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.core.mail import send_mail
from .utils import send_auto_reply
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
import calendar
from datetime import date

def home(request):
    return render(request, 'Nav-tab/index.html')


def contact(request):
    return render(request, 'Nav-tab/contact.html')


def about(request):
    return render(request, "Nav-tab/about.html")

def departments(request):
    return render(request, "Nav-tab/departments.html")

def insurance(request):
    return render(request, 'Nav-tab/insurance.html') 

def cardiology(request):
    return render(request,'Departments/cardiology.html')

def neurology(request):
    return render(request,'Departments/neurology.html')

def orthopaedics(request):
    return render(request,'Departments/orthopaedics.html')

def booking(request):
    return render(request,'Appointment/booking.html')


def login(request):
    role = request.GET.get("role")

    # Save HOME only once
    if "login_entry" not in request.session:
        request.session["login_entry"] = "/"

    context = {
        "role": role,
        "login_entry": request.session.get("login_entry", "/"),
    }

    return render(request, "nav-tab/login.html", context)




def new_patient_register(request):
    if request.method == "POST":

        source = request.POST.get("source")  # admin ya None

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # ❌ password mismatch
        if password != confirm_password:
            messages.error(request, "Passwords do not match")

            if source == "admin":
                return redirect("admin_add_patient")
            else:
                return redirect("/login/?role=new_patient")

        # ❌ email already exists
        if Patient.objects.filter(email=request.POST.get("email")).exists():
            messages.error(request, "Email already registered")

            if source == "admin":
                return redirect("admin_add_patient")
            else:
                return redirect("/login/?role=new_patient")

        # ✅ save patient
        Patient.objects.create(
            salutation=request.POST.get("salutation"),
            name=request.POST.get("name"),
            gender=request.POST.get("gender"),
            age=request.POST.get("age"),
            email=request.POST.get("email"),
            mobile=request.POST.get("mobile"),
            address=request.POST.get("address"),
            image=request.FILES.get("image"),
            password=make_password(password),
        )

        # ✅ success redirect
        if source == "admin":
            messages.success(request, "Patient added successfully")
            return redirect("admin_patients")   # admin dashboard
        else:
            messages.success(request, "Registration successful! Please login.")
            return redirect("login")

    return redirect("login")



def role_login(request, role):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # ================= ADMIN LOGIN =================
        if role == "admin":
            if (
                email == settings.ADMIN_EMAIL
                and password == settings.ADMIN_PASSWORD
            ):
                request.session["admin_logged_in"] = True
                messages.success(request, "Admin login successful")
                return render(request,'admin/admin_dashboard.html')
            else:
                messages.error(request, "Invalid admin credentials")
                return redirect("/login/?role=admin")

        # ================= PATIENT LOGIN =================
        elif role == "patient":
            from .models import Patient
            from django.contrib.auth.hashers import check_password

            try:
                patient = Patient.objects.get(email=email)
                if check_password(password, patient.password):
                    request.session["patient_id"] = patient.id
                    messages.success(request, "Login successful")
                    return redirect("patient_dashboard")
                else:
                    messages.error(request, "Wrong password")

            except Patient.DoesNotExist:
                messages.error(request, "Email not registered")

        # ================= DOCTOR LOGIN =================
        elif role == "doctor":
            from .models import Doctor
            from django.contrib.auth.hashers import check_password

            try:
                doctor = Doctor.objects.get(email=email)
                if check_password(password, doctor.password):
                    request.session["doctor_id"] = doctor.id
                    messages.success(request, "Login successful")
                    return redirect("doctor_dashboard")
                else:
                    messages.error(request, "Wrong password")

            except Doctor.DoesNotExist:
                messages.error(request, "Email not registered")

        else:
            messages.error(request, "Invalid role")

    return redirect("login")



def admin_dashboard(request):
    if not request.session.get("admin_logged_in"):
        return redirect("login")

    return render(request, "admin/admin_dashboard.html", {
        "page": "dashboard"
    })


def admin_logout(request):
    request.session.flush()
    return redirect("login")


def admin_patients(request):
    if not request.session.get("admin_logged_in"):
        return redirect("login")

    patients = Patient.objects.all()

    return render(request, "admin/admin_dashboard.html", {
        "page": "patients",
        "patients": patients
    })

def delete_patient(request, id):
    if not request.session.get("admin_logged_in"):
        return redirect("login")

    Patient.objects.filter(id=id).delete()
    messages.success(request, "Patient deleted successfully")
    return redirect("admin_patients")



def edit_patient(request, id):
    if not request.session.get("admin_logged_in"):
        return redirect("login")

    patient = Patient.objects.get(id=id)

    if request.method == "POST":
        patient.name = request.POST.get("name")
        patient.age = request.POST.get("age")
        patient.mobile = request.POST.get("mobile")
        patient.address = request.POST.get("address")
        patient.save()

        messages.success(request, "Patient updated successfully")
        return redirect("admin_patients")

    return render(request, "admin/admin_dashboard.html", {
        "patient": patient ,
        "page" : "edit_patient"
    })


def admin_add_patient(request):
    return render(request, "admin/admin_dashboard.html", {
        "page": "add_patient"
    })


def admin_doctors(request):
    doctors = Doctor.objects.all()
    return render(request, "admin/admin_dashboard.html", {
        "page": "doctors",
        "doctors": doctors
    })


def admin_add_doctor(request):
    return render(request, "admin/admin_dashboard.html", {
        "page": "add_doctor"
    })

def save_doctor(request):
    if request.method == "POST":

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        email = request.POST.get("email")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("admin_add_doctor")

        # Save doctor
        Doctor.objects.create(
            name=request.POST.get("name"),
            specialization=request.POST.get("specialization"),
            email=email,
            mobile=request.POST.get("mobile"),
            experience=request.POST.get("experience"),
            address=request.POST.get("address"),
            image=request.FILES.get("image"),
            document=request.FILES.get("document"),
            password=make_password(password),
        )

        # EMAIL CONTENT
        subject = "Medical Clinic | Doctor Login Details"
        message = f"""
Hello Doctor,

Welcome to Medical Clinic.

Your account has been created successfully.

Login Details:
Email: {email}
Password: {password}

Please login to the Medical Clinic portal using the above credentials.

Regards,
Medical Clinic Team
"""

        # SEND EMAIL using utils
        send_auto_reply(
            email=email,
            subject=subject,
            message=message
        )

        messages.success(request, "Doctor added successfully & email sent")
        return redirect("admin_doctors")



def edit_doctor(request, id):
    doctor = Doctor.objects.get(id=id)

    if request.method == "POST":

        doctor.name = request.POST.get("name")
        doctor.specialization = request.POST.get("specialization")
        doctor.mobile = request.POST.get("mobile")
        doctor.experience = request.POST.get("experience")
        doctor.address = request.POST.get("address")

        if request.FILES.get("image"):
            doctor.image = request.FILES.get("image")

        if request.FILES.get("document"):
            doctor.document = request.FILES.get("document")

        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password:
            if password != confirm:
                messages.error(request, "Passwords do not match")
                return redirect("edit_doctor", id=id)
            doctor.password = make_password(password)

        doctor.save()
        messages.success(request, "Doctor updated successfully")
        return redirect("admin_doctors")

    return render(request, "admin/admin_dashboard.html", {
        "page": "edit_doctor",
        "doctor": doctor
    })



def delete_doctor(request, id):
    Doctor.objects.get(id=id).delete()
    messages.success(request, "Doctor deleted successfully")
    return redirect("admin_doctors")



def newsletter_signup(request):
    if request.method == "POST":
        email = request.POST.get('email')

        send_auto_reply(
            email=email,
            subject="Thanks for Subscribing!",
            message="Hello 👋\n\n"
                "Thank you for subscribing to our newsletter.\n"
                "We’re glad to have you with us!\n\n"
                "Regards,\n"
                "Medical-Clinic Team"
        )

        return render(request, 'Nav-tab/index.html')
    


def contact_view(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        message = request.POST.get('message')

        # 1️⃣ SAVE INTO DATABASE
        contact = Contact.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            message=message
        )

        # 2️⃣ SEND AUTO EMAIL
        send_auto_reply ( 

            email=email,
            subject="Thanks for contacting us",
            message=(
            f"Hello {first_name},\n\n"
            "Thank you for contacting us.\n"
            "We have received your message and will get back to you shortly.\n\n"
            "Regards,\n"
            "Support Team" 
             )
        )

        return render(request, 'Nav-tab/contact.html')

    return render(request, 'Nav-tab/contact.html')


from django.contrib.auth import logout

def custom_logout(request):
    logout(request)
    return redirect('home')

#================================================PATIENT DASHBOARD ============================================

def patient_dashboard(request):
    patient_id = request.session.get("patient_id")
    if not patient_id:
        return redirect("login")

    patient = Patient.objects.get(id=patient_id)

    # ================= URL PARAMS =================
    page = request.GET.get("page", "dashboard")
    specialization = request.GET.get("specialization")
    query = request.GET.get("q", "")
    doctor_id = request.GET.get("doctor_id")

    # ================= DEFAULTS =================
    section = page
    doctors = Doctor.objects.none()
    doctor = None
    selected_date = None
    selected_time = None

    context = {
        "patient": patient,
        "section": section,
        "query": query,
        "selected_specialization": specialization,
    }

    # =================================================
    # 1️⃣ DASHBOARD
    # =================================================
    if page == "dashboard":
        return render(request, "dashboard/patient_dashboard.html", context)

    # =================================================
    # 2️⃣ BOOK APPOINTMENT (DOCTOR LIST)
    # =================================================
    elif page == "book":
        doctors = Doctor.objects.all()

        if query:
            doctors = doctors.filter(
            Q(name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(qualification__icontains=query) |
            Q(bio__icontains=query) |
            Q(experience__icontains=query)
        ).distinct()

        context.update({
        "section": "book",
        "doctors": doctors,
        "query": query,
    })
        return render(request, "dashboard/patient_dashboard.html", context)

    # =================================================
    # 3️⃣ SPECIALIZATION FILTER
    # =================================================
    elif specialization:
        doctors = Doctor.objects.filter(specialization=specialization)

        context.update({
            "section": "specialization",
            "doctors": doctors,
            "selected_specialization": specialization,
        })
        return render(request, "dashboard/patient_dashboard.html", context)

    # =================================================
    # 4️⃣ SCHEDULE PAGE
    # =================================================
    elif page == "schedule" and doctor_id:
        doctor = Doctor.objects.get(id=doctor_id)

        today = date.today()
        month = int(request.GET.get("month", today.month))
        year = int(request.GET.get("year", today.year))

        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1

        cal = calendar.Calendar(calendar.SUNDAY)
        month_days = cal.monthdayscalendar(year, month)

        selected_date = request.POST.get("date") or request.GET.get("date")
        selected_time = request.POST.get("time")

        time_slots = [
            "12:00 am", "12:30 am",
            "1:00 am", "1:30 am",
            "2:00 am", "2:30 am",
            "3:00 am", "3:30 am",
            "4:00 am", "4:30 am",
        ]

        context.update({
            "section": "schedule",
            "doctor": doctor,
            "month": month,
            "year": year,
            "month_name": calendar.month_name[month],
            "month_days": month_days,
            "time_slots": time_slots,
            "selected_date": selected_date,
            "selected_time": selected_time,
        })
        return render(request, "dashboard/patient_dashboard.html", context)

    # =================================================
    # 5️⃣ BOOKING CONFIRM PAGE
    # =================================================
    elif page == "booking" and doctor_id:
        doctor = Doctor.objects.get(id=doctor_id)
        selected_date = request.GET.get("date")
        selected_time = request.GET.get("time")

        if request.method == "POST":
            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=selected_date,
                time=selected_time,
                first_name=request.POST.get("first_name"),
                last_name=request.POST.get("last_name"),
                email=request.POST.get("email"),
                phone=request.POST.get("phone"),
                message=request.POST.get("text"),
                amount=300,
                status="Confirmed"
            )

            send_auto_reply(
                email=patient.email,
                subject="Appointment Confirmed - Medical Clinic",
                message=f"""
                Hello {patient.name},

                Your appointment has been confirmed.

                Doctor: {doctor.name}
                Date: {selected_date}
                Time: {selected_time}

                Thank you!
                """
            )

            messages.success(request, "Appointment booked successfully ✅")
            return redirect("patient_dashboard")

        context.update({
            "section": "booking",
            "doctor": doctor,
            "selected_date": selected_date,
            "selected_time": selected_time,
        })
        return render(request, "dashboard/patient_dashboard.html", context)

    # =================================================
    # FALLBACK
    # =================================================
    return render(request, "dashboard/patient_dashboard.html", context)



def medical_reports(request):
    patient = Patient.objects.get(user=request.user)
    return render(request, 'dashboard/patient_dashboard.html', {
        'patient': patient,
        'section': 'reports'
    })


def live_chat(request):
    patient = Patient.objects.get(user=request.user)
    return render(request, 'dashboard/patient_dashboard.html', {
        'patient': patient,
        'section': 'chat'
    })


def video_call(request):
    patient = Patient.objects.get(user=request.user)
    return render(request, 'dashboard/patient_dashboard.html', {
        'patient': patient,
        'section': 'video'
    })


def notifications(request):
    patient = Patient.objects.get(user=request.user)
    return render(request, 'dashboard/patient_dashboard.html', {
        'patient': patient,
        'section': 'notifications'
    })


def medical_progress(request):
    patient = Patient.objects.get(user=request.user)
    return render(request, 'dashboard/patient_dashboard.html', {
        'patient': patient,
        'section': 'progress'
    })


def medical_health(request):
    patient = Patient.objects.get(user=request.user)
    return render(request, 'dashboard/patient_dashboard.html', {
        'patient': patient,
        'section': 'health'
    })


def doctor_dashboard(request):
    if not request.session.get("doctor_id"):
        return redirect("login")

    doctor = Doctor.objects.get(id=request.session["doctor_id"])

    if request.method == "POST":
        doctor.bio = request.POST.get("bio")
        doctor.qualification = request.POST.get("qualification")
        doctor.hobbies = request.POST.get("hobbies")

        if request.FILES.get("image"):
            doctor.image = request.FILES.get("image")

        doctor.is_profile_completed = True
        doctor.save()

        messages.success(request, "Profile completed successfully")
        return redirect("doctor_dashboard")

    page = request.GET.get("page", "home")

    return render(request, "dashboard/doctor_dashboard.html", {
        "doctor": doctor,
        "page": page
    })

