from django.db import models
import user_management.models


class SystemPackage(models.Model):
    package_name = models.CharField(max_length=255)
    package_description = models.TextField()
    package_price = models.CharField(max_length=255)
    package_duration = models.CharField(max_length=255)
    package_status = models.BooleanField(default=True)
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.package_name
    
    class Meta:
        db_table = 'system_package_table'


class SystemOffer(models.Model):
    package = models.ForeignKey(SystemPackage, on_delete=models.CASCADE)
    offer_name = models.CharField(max_length=255)
    offer_description = models.TextField()
    offer_price = models.CharField(max_length=255)
    offer_duration = models.CharField(max_length=255)
    offer_status = models.BooleanField(default=True)
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.offer_name
    
    class Meta:
        db_table = 'system_offer_table'


class ServiceProvider(models.Model):
    church_name = models.CharField(max_length=255, unique=True)
    church_location = models.CharField(max_length=255)
    church_email = models.EmailField(unique=True)
    church_phone = models.CharField(max_length=255)
    church_category = models.CharField(max_length=255)
    church_status = models.BooleanField(default=True)
    churh_leader_name = models.CharField(max_length=255, blank=True, null=True)
    churh_image = models.FileField(upload_to='campaign/images/', blank=True, null=True)
    churh_leader_image = models.FileField(upload_to='campaign/images/', blank=True, null=True)
    sp_admin = models.OneToOneField(user_management.models.User, on_delete=models.CASCADE, null=True, blank=True)
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.church_name
    
    class Meta:
        db_table = 'service_provider_table'

class SpManagers(models.Model):
    sp_manager = models.ForeignKey(user_management.models.User, on_delete=models.CASCADE)
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['sp_manager', 'church'],
                name='unique_user_church'
            ),
            models.UniqueConstraint(
                fields=['sp_manager'],
                name='unique_user_only_one_church'
            )
        ]

    def __str__(self):
        return f'{self.sp_manager.username} - {self.church.church_name}'



class Package(models.Model):
    package = models.ForeignKey(SystemPackage, on_delete=models.CASCADE)
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    package_offer = models.ForeignKey(SystemOffer, on_delete=models.CASCADE, related_name='package_offer')
    is_active = models.BooleanField(default=False)
    payed_amount = models.IntegerField()
    package_start_date = models.DateTimeField()
    package_end_date = models.DateTimeField()
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)


class Kanda(models.Model):
    name = models.CharField(max_length=300)
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_index=True)
    address = models.TextField(null=True, blank=True)
    jina_kiongozi = models.CharField(max_length=300)
    namba_ya_simu = models.CharField(max_length=12, blank=True, null=True)
    location = models.CharField(null=True, blank=True)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Jumuiya: {self.name}"

    class Meta:
        indexes = [
            models.Index(fields=['church', 'name'])
        ]
        ordering = ['-created_at']


class Jumuiya(models.Model):
    name = models.CharField(max_length=300)
    address = models.TextField(null=True, blank=True)
    jina_kiongozi = models.CharField(max_length=300)
    kanda = models.ForeignKey(Kanda, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    namba_ya_simu = models.CharField(max_length=12, blank=True, null=True)
    location = models.CharField(null=True, blank=True)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Jumuiya: {self.name}"

    class Meta:
        indexes = [
            models.Index(fields=['church', 'name'])
        ]
        ordering = ['-created_at']

class Wahumini(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    user = models.OneToOneField('user_management.User', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='wahumini', help_text='Link to a user if the wahumini is a registered user.')
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_index=True)
    type = models.CharField(max_length=27, default="Mtu mzima" )
    jumuiya = models.ForeignKey(Jumuiya, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    first_name = models.CharField(max_length=100, null=True, blank=True,
                                  help_text='First name for non-registered wahumini.')
    last_name = models.CharField(max_length=100, null=True, blank=True,
                                 help_text='Last name for non-registered wahumini.')
    phone_number = models.CharField(max_length=15, null=True, blank=True,
                                    help_text='Phone number for non-registered wahumini.')
    email = models.EmailField(null=True, blank=True, help_text='Email for non-registered wahumini.')
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    birthdate = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    marital_status = models.CharField(max_length=25)
    has_loin_account = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Wahumini: {self.user.username} (Registered User)"
        return f"Wahumini: {self.first_name} {self.last_name} (Non-Registered)"

    class Meta:
        indexes = [
            models.Index(fields=['church', 'jumuiya', 'phone_number'])
        ]
        ordering = ['-created_at']


class CardsNumber(models.Model):
    BAHASHA_TYPES = (
        ('zaka', 'zaka'),
        ('sadaka', 'sadaka'),
    )
    mhumini = models.ForeignKey(Wahumini, on_delete=models.CASCADE, related_name='nambaza_kadi', db_index=True)
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_index=True)
    card_no = models.CharField(max_length=50, unique=True, help_text='Unique card number for identification.', db_index=True)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    card_status = models.BooleanField(default=True)
    bahasha_type = models.CharField(max_length=10, choices=BAHASHA_TYPES, default='sadaka')

    def __str__(self):
        return f"Nambaza Kadi: {self.card_no} (Wahumini: {self.mhumini.first_name})"

    class Meta:
        indexes = [
            models.Index(fields=['mhumini', 'card_no', 'bahasha_type', 'church'])
        ]
        ordering = ['-created_at']


class PaymentType(models.Model):
    name = models.CharField(max_length=100)
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SadakaTypes(models.Model):
    name = models.CharField(max_length=100)
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Sadaka(models.Model):
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_index=True)
    bahasha = models.ForeignKey(CardsNumber, on_delete=models.CASCADE, null=True, blank=True)
    sadaka_amount = models.DecimalField(max_digits=20, decimal_places=2)
    collected_by = models.CharField(max_length=255)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    sadaka_type = models.ForeignKey(SadakaTypes, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sadaka: {self.sadaka_amount} by {self.collected_by}"

    class Meta:
        indexes = [
            models.Index(fields=['church', 'bahasha', 'sadaka_type'])
        ]
        ordering = ['-inserted_at']


class Zaka(models.Model):
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_index=True)
    bahasha = models.ForeignKey(CardsNumber, on_delete=models.CASCADE, null=True, blank=True)
    zaka_amount = models.DecimalField(max_digits=20, decimal_places=2)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    collected_by = models.CharField(max_length=255)
    date = models.DateField()
    date_received = models.DateField()
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Zakaa: {self.zaka_amount} by {self.collected_by}"

    class Meta:
        indexes = [
            models.Index(fields=['church', 'bahasha', 'payment_type'])
        ]
        ordering = ['-inserted_at']


class PaymentTypeTransfer(models.Model):
    from_payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, related_name='transfers_from')
    to_payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, related_name='transfers_to')
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    transfer_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)


    def __str__(self):
        return f"Transfer of {self.amount} to {self.to_payment_type.name}"

    class Meta:
        indexes = [
            models.Index(fields=['church', 'transfer_date'])
        ]




class Revenue(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_index=True)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    revenue_type = models.CharField(max_length=100)
    revenue_type_record = models.CharField(max_length=100)
    date_received = models.DateField()
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['church', 'date_received'])
        ]


    def __str__(self):
        return f"{self.revenue_type}: {self.amount} on {self.date_received}"



class ExpenseCategory(models.Model):
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=20, decimal_places=4, default=100000.00)
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['church'])
        ]
        ordering = ['-inserted_at']


    def __str__(self):
        return self.category_name


class Expense(models.Model):
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_index=True)
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    date = models.DateField()
    spent_by = models.CharField(max_length=255)
    expense_category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['church', 'expense_category'])
        ]
        ordering = ['-inserted_at']

    def __str__(self):
        return f"Expense: {self.amount} - {self.spent_by}"



class Mchango(models.Model):
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_index=True)
    mchango_name = models.CharField(max_length=255)
    mchango_amount = models.DecimalField(max_digits=20, decimal_places=2)
    mchango_description = models.TextField()
    target_amount = models.DecimalField(max_digits=20, decimal_places=2)
    collected_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    status = models.BooleanField(default=True)
    date = models.DateField()
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['church', 'status'])
        ]
        ordering = ['-inserted_at']

    def __str__(self):
        return f"Mchango: {self.mchango_name} collected {self.collected_amount}"

class MchangoPayments(models.Model):
    mchango = models.ForeignKey(Mchango, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, default=1)
    mhumini = models.ForeignKey(Wahumini, on_delete=models.CASCADE, null=True, blank=True)
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['mchango', 'mhumini'])
        ]
        ordering = ['-inserted_at']



class Ahadi(models.Model):
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_index=True)
    wahumini = models.ForeignKey('Wahumini', on_delete=models.CASCADE, related_name='ahadi', db_index=True)
    mchango = models.ForeignKey('Mchango', on_delete=models.CASCADE, related_name='mchango', null=True, blank=True )
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=20, decimal_places=2)
    date_pledged = models.DateField()
    due_date = models.DateField()
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['wahumini', 'church'])
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Ahadi by {self.wahumini} for {self.mchango} - {self.amount}"


class AhadiPayments(models.Model):
    ahadi = models.ForeignKey(Ahadi, on_delete=models.CASCADE)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, default=1)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    mhumini = models.ForeignKey(Wahumini, on_delete=models.CASCADE, null=True, blank=True)
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['ahadi'])
        ]
        ordering = ['-inserted_at']


class Mavuno(models.Model):
    mavuno_type_options = (
    ("MAVUNO_JIMBO", "MAVUNO_JIMBO"),
    ("MAVUNO_PAROKIA", "MAVUNO_PAROKIA")
    )
    jumuiya = models.ForeignKey(Jumuiya, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=300)
    mavuno_type = models.CharField(max_length=100, choices=mavuno_type_options, default="MAVUNO_PAROKIA")
    description = models.TextField()
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_index=True)
    year_target_amount = models.DecimalField(max_digits=20, decimal_places=2)
    collected_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    status = models.BooleanField(default=True)
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Mavuno by {self.jumuiya.name} for {self.name} - {self.year_target_amount}"


    class Meta:
        indexes = [
            models.Index(fields=['jumuiya', 'church'])
        ]
        ordering = ['-inserted_at']

class MavunoPayments(models.Model):
    mavuno = models.ForeignKey(Mavuno, on_delete=models.CASCADE)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, default=1)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    mhumini = models.ForeignKey(Wahumini, on_delete=models.CASCADE, null=True, blank=True)
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['mavuno', 'payment_type'])
        ]
        ordering = ['-inserted_at']



class SMSQueue(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('WAITING', 'Waiting'),
        ('SUBMITTED', 'Submitted'),
        ('FAILED', 'Failed'),
    ]

    message = models.TextField()
    phone = models.CharField(max_length=20)
    recipient_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    request_id = models.CharField(max_length=50, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    success_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"SMS to {self.phone} - {self.status}"

    def format_phone(self):
        """Format phone number to ensure it starts with country code"""
        phone = str(self.phone).strip()

        # Remove any non-digit characters except +
        phone = ''.join(c for c in phone if c.isdigit() or c == '+')

        # Handle different formats
        if phone.startswith('+255'):
            return phone[1:]  # Remove +
        elif phone.startswith('0'):
            return '255' + phone[1:]  # Replace leading 0 with 255
        elif phone.startswith('255'):
            return phone
        elif len(phone) == 9:  # Assume it's missing country code
            return '255' + phone

        return phone