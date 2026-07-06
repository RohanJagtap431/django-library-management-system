from django.db import models
from django.utils import timezone

STATE_CHOICES = [
    ("Andhra Pradesh", "Andhra Pradesh"),
    ("Arunachal Pradesh", "Arunachal Pradesh"),
    ("Assam", "Assam"),
    ("Bihar", "Bihar"),
    ("Chhattisgarh", "Chhattisgarh"),
    ("Goa", "Goa"),
    ("Gujarat", "Gujarat"),
    ("Haryana", "Haryana"),
    ("Himachal Pradesh", "Himachal Pradesh"),
    ("Jharkhand", "Jharkhand"),
    ("Karnataka", "Karnataka"),
    ("Kerala", "Kerala"),
    ("Madhya Pradesh", "Madhya Pradesh"),
    ("Maharashtra", "Maharashtra"),
    ("Manipur", "Manipur"),
    ("Meghalaya", "Meghalaya"),
    ("Mizoram", "Mizoram"),
    ("Nagaland", "Nagaland"),
    ("Odisha", "Odisha"),
    ("Punjab", "Punjab"),
    ("Rajasthan", "Rajasthan"),
    ("Sikkim", "Sikkim"),
    ("Tamil Nadu", "Tamil Nadu"),
    ("Telangana", "Telangana"),
    ("Tripura", "Tripura"),
    ("Uttar Pradesh", "Uttar Pradesh"),
    ("Uttarakhand", "Uttarakhand"),
    ("West Bengal", "West Bengal"),
]

GENDER_CHOICES = [
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other"),
]

MEMBER_TYPE_CHOICES =[
    ("student", "Student"),
    ("teacher", "Teacher"),
    ("staff", "Staff"),
]

STATUS_CHOICES = [
    ("active", "Active"),
    ("inactive", "Inactive"),
]

class Member(models.Model):
    member_id = models.CharField(max_length=50, unique=True, editable=False)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=14)
    address = models.TextField()
    profile_photo = models.ImageField(upload_to="member_photo/", blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    member_type = models.CharField(max_length=10, choices=MEMBER_TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    join_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50, choices=STATE_CHOICES)
    pincode = models.CharField(max_length=6)
    
    
    def save(self, *args, **kwargs):
        if not self.member_id:
            last_member = Member.objects.order_by("-id").first()

            if last_member:
                last_id = int(last_member.member_id[3:])
                self.member_id = f"MEM{last_id + 1:04d}"
            else:
                self.member_id = "MEM0001"

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.member_id} - {self.full_name}"
    
    