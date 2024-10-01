from django.db import models


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
    church_name = models.CharField(max_length=255)
    church_location = models.CharField(max_length=255)
    church_email = models.EmailField()
    church_phone = models.CharField(max_length=255)
    church_category = models.CharField(max_length=255)
    church_status = models.BooleanField(default=True)
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.church_name
    
    class Meta:
        db_table = 'service_provider_table'


class Package(models.Model):
    package = models.ForeignKey(SystemPackage, on_delete=models.CASCADE)
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    package_offer = models.ForeignKey(SystemOffer, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    payed_amount = models.IntegerField()
    package_start_date = models.DateTimeField()
    package_end_date = models.DateTimeField()
    inserted_by = models.CharField(max_length=255)
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

class Wahumini(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    user = models.OneToOneField('user_management.User', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='wahumini', help_text='Link to a user if the wahumini is a registered user.')

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
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Wahumini: {self.user.username} (Registered User)"
        return f"Wahumini: {self.first_name} {self.last_name} (Non-Registered)"



class CardsNumber(models.Model):
    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE)
    card_number = models.CharField(max_length=255)
    card_name = models.CharField(max_length=255)
    card_expiry = models.CharField(max_length=255)
    card_cvv = models.CharField(max_length=255)
    card_status = models.BooleanField(default=True)
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.card_number
    
    class Meta:
        db_table = 'cards_number_table'

