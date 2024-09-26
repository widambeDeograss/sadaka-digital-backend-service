from django.db import models


class SystemPackage(models.Model):
    package_name = models.CharField(max_length=255)
    package_description = models.TextField()
    package_price = models.CharField(max_length=255)
    package_duration = models.CharField(max_length=255)
    package_status = models.BooleanField(default=True)

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
    package = models.ForeignKey(SystemPackage, on_delete=models.CASCADE)
    church_status = models.BooleanField(default=True)


    def __str__(self):
        return self.church_name
    
    class Meta:
        db_table = 'service_provider_table'


class Wahumini(models.Model):
    user = models.OneToOneField('user_management.User', on_delete=models.CASCADE)
    church = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    user_status = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
    
    class Meta:
        db_table = 'wahumini_table'


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

