from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, DetailView
from django.utils.decorators import method_decorator
# Create your views here.
from .forms import CustomUserCreationForm, SignUpForm
from . import models
from .models import CustomUser, Account, Subaccount, Transaction

#for the strange simpleisbetterthancomplex implementation (https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html#sign-up-with-extra-fields)

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect



#plaid stuff
import os
import datetime
import plaid
from flask import Flask, render_template, request, jsonify



#class SignUp(generic.CreateView):
#	form_class = CustomUserCreationForm
#	success_url = reverse_lazy('login')
#	template_name = 'signup.html'

def SignUp(request):
	if request.method =='POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('home')
	else:
		form = SignUpForm()
	return render(request, 'signup2.html', {'form': form})

class Profile(LoginRequiredMixin, TemplateView):
	template_name = 'profile.html'
	model = models.CustomUser
	context_object_name = 'accountlist'
	login_url = 'login'
	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		super(Profile, self).dispatch(*args, **kwargs)
		print(self.request.user)
		print(Account.objects.filter(user=self.request.user))
		return super(Profile, self).dispatch(*args, **kwargs)

	def get_context_data(self):
		context = {}
		context['accounts'] = Account.objects.filter(user=self.request.user)
		return context
	#	context['account_list'] = Account.objects.filter(user=self.request.user)
	#	return context



class Success(LoginRequiredMixin, TemplateView):
	template_name = 'success.html'
	model = models.CustomUser
	login_url = 'login'

class Error(TemplateView):
	template_name: 'error.html'
	model = models.CustomUser
	login_url = 'login'

#right now, I import the entire thing into the database from scratch every time this url is called. this is exceptionally poor design, but it works and i'm tired and 
#this is for educational purposes. In the future this should be broken out into helper functions that are called ONCE, during account initialization
@login_required
def AccountOverview(request):
	user = request.user
	account = Account.objects.get(user=user)
	client = plaid.Client(account.client_id, account.secret, account.public_key, 'development')
	authresponse = client.Auth.get(account.access_token)
	for acct in authresponse['accounts']: #iterate thru accounts in auth response
		if acct['subtype'] == 'checking' or acct['subtype'] == 'credit card': # prefilter for debit and credit cards
			all_subaccounts = Subaccount.objects.filter(account=account) #create the queryset for all subaccounts of the active account
			unique = True #assume the best in people
			for e in all_subaccounts: #iterate thru existing subaccounts
				if e.plaid_acct_id == acct['account_id']: #check to see if it's a dupe
					unique = False #if it's a dupe, have your heart broken and your naive trust proven wrong
			if unique:#if you're right, add a new subaccount!
				subaccount = Subaccount(account=account, plaid_acct_id = acct['account_id'], subaccount_type = acct['subtype'], subaccount_name = acct['official_name'])
				subaccount.save()
	all_subaccounts = Subaccount.objects.filter(account=account)
	
	start_date = "{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(-30))
	end_date = "{:%Y-%m-%d}".format(datetime.datetime.now())
	transresponse = client.Transactions.get(account.access_token, start_date, end_date)
	transactions = transresponse['transactions']
	while len(transactions) < transresponse['total_transactions']:
		transresponse = client.Transactions.get(access_token, start_date=start_date, end_date=end_date, offset=len(transactions))
		transactions.extend(transresponse['transactions'])

	all_transactions=[]

	for a in all_subaccounts:
		existing_transactions = Transaction.objects.filter(subaccount=a) #create queryset for existing transactions to check against new ones
		for e in transactions:
			if e['account_id'] == a.plaid_acct_id:
				unique=True #assume the best as above
				for i in existing_transactions: #go thru existing transactions
					if i.transaction_id == e['transaction_id']: #if the transaction id matches...
						unique = False #...be proven wrong
				if unique:
					transaction = Transaction(subaccount=a, plaid_acct_id = e['account_id'], category_id = e['category_id'], transaction_id = e['transaction_id'], transaction_amt=e['amount'], loc_city=e['location']['city'], loc_zip=e['location']['zip'], 
										transaction_detail=e['name'], transaction_date=e['date'])
					transaction.save()
			all_transactions.extend(Transaction.objects.filter(subaccount=a)) # cheating way of filtering on subaccounts, since i'm already iterating thru them
	#catresponse = client.Categories.get() #did this once to get a dump of the categories cause I was lazy, but commenting out now. 
	#print(catresponse)
	#Transaction.objects.all().delete()	#delete database entries when I wasn't checking to see if they already existed
	return render(request, 'users/account_detail.html', {'subaccount': all_subaccounts, }) #'transactions': all_transactions

#initialize the new users with this nifty function that exchanges the temporary public key for the permanent access token
def GetAccessToken(request):
	if request.method == 'POST':
		print(request.user.id)
		user = request.user
		account = Account(public_token=request.POST['public_token'], user=user)
		account.save()
		client = plaid.Client(account.client_id, account.secret, account.public_key, 'development')
		exchange_response = client.Item.public_token.exchange(account.public_token)
		account.access_token = exchange_response['access_token']
		account.item_id = exchange_response['item_id']
		account.save()
		response = client.Auth.get(account.access_token)
		print(response)
		return HttpResponseRedirect(reverse_lazy('home'))
	else:
		return redirect('post_list')
