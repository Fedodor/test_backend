from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import CustomUser, Balance


@receiver(post_save, sender=CustomUser)
def post_save_user(sender, instance: CustomUser, created, **kwargs):
    if created:
        Balance.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_balance(sender, instance: CustomUser, **kwargs):
    instance.balance.save()
