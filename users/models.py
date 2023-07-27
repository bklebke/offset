from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

# Create your models here.
class CustomUserManager(UserManager):
	pass

class CustomUser(AbstractUser):
	objects = CustomUserManager()
	def __str__(self): 
		return "%s %s" % (self.first_name, self.last_name)

#an account model that holds information related to the item, as defined by Plaid api. May move client, pub ey, and secret key info to settings file down the road.
class Account(models.Model):
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) #sets up the foreign key relationship to users
	client_id = models.TextField(max_length='23', blank=True)
	client_id = '59cd6577bdc6a44745dcf539'
	public_key = models.TextField(max_length='30', blank=True)
	public_key = 'PublicKeyHere'
	secret = models.TextField(max_length='30', blank=True)
	secret = 'SecretKeyHere'
	access_token = models.TextField(max_length='300', blank=True)
	item_id = models.TextField(max_length='300', blank=True)
	public_token = models.TextField(max_length='300', blank=True) #exchanged with server for access_token, filled in by link service on initialization

	def __str__(self):
		return "%s %s" % (self.public_token, self.user)

#to hold the subaccounts for each user account tied to a banking institution (e.g., checking, savings, credit)
class Subaccount(models.Model):
	account = models.ForeignKey(Account, on_delete=models.CASCADE) #sets up the foreign key relationship to users
	plaid_acct_id = models.TextField(max_length='100', blank=True) #account ID in the auth response
	subaccount_type = models.TextField(max_length='50', blank=True) #subtype in the auth response
	subaccount_name = models.TextField(max_length='200', blank=True) #official_name in the auth response

	def __str__(self):
		return "%s %s" % (self.subaccount_type, self.account)
#a transaction model that holds info related to transactions on a given account
class Transaction(models.Model):
	subaccount = models.ForeignKey(Subaccount, on_delete=models.CASCADE) #sets up the foreign key relationship to subaccount
	transaction_date = models.DateField(null=True, blank=True) #transaction date
	transaction_detail = models.TextField(max_length='200', blank=True) #transaction detail
	transaction_amt = models.DecimalField(max_digits=7, decimal_places=2, blank=True) #amount dollars
	transaction_id = models.TextField(max_length='200', blank=True) #transaction ID
	plaid_acct_id = models.TextField(max_length='100', blank=True) #plaid acct id
	category_id = models.TextField(max_length='30', blank=True, null=True) #plaid category id, the ones I want are  18042000 and 22009000 (service oil and gas, and travel, gas stations respectively)
	loc_city = models.TextField(max_length=30, blank=True, null=True) #city location
	loc_zip = models.TextField(max_length=30, blank=True, null=True) #zip location, text to be safe for none
	gas_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) #amount
	gas_amt = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) #amount gas
	co2_amt = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) #amount co2
	co2_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) #amount co2 price
	class Meta:
		ordering = ('-transaction_date', ) # - sign orders in reverse, i.e. newest first

	def __str__(self):
		return "%s on %s for %s with account %s" % (self.transaction_detail, self.transaction_date, self.transaction_amt, self.subaccount)