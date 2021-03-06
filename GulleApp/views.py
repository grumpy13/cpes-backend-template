from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import UserSignup, UserLogin, UserForm, MessageForm
from django.contrib import messages
from .models import (Message, Like)
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import JsonResponse

# def home(request):
# 	return render(request, 'home.html')

class Signup(View):

	form_class = UserSignup
	template_name = 'signup.html'

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect("dashboard")

		form = self.form_class()
		return render(request, self.template_name, {'form': form})

	def post(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect("dashboard")

		form = self.form_class(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.set_password(user.password)
			user.save()
			messages.success(request, "You have successfully signed up.")
			login(request, user)
			return redirect("home")
		messages.warning(request, form.errors)
		return redirect("signup")


class Login(View):

	form_class = UserLogin
	template_name = 'login.html'

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect("dashboard")
		form = self.form_class()
		return render(request, self.template_name, {'form': form})

	def post(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect("dashboard")
			
		form = self.form_class(request.POST)
		if form.is_valid():

			username = form.cleaned_data['username']
			password = form.cleaned_data['password']

			auth_user = authenticate(username=username, password=password)
			if auth_user is not None:
				login(request, auth_user)
				messages.success(request, "Welcome Back! " +request.user.username)
				return redirect('home')
			messages.warning(request, "Wrong email/password combination. Please try again.")
			return redirect("login")
		messages.warning(request, form.errors)
		return redirect("login")


class Logout(View):
	def get(self, request, *args, **kwargs):
		logout(request)
		messages.success(request, "You have successfully logged out.")
		return redirect("login")

def no_access(request):
	return render(request, 'no_access.html')

#####################


def profile(request, user_id):

	user = User.objects.get(id=user_id)
	messages = Message.objects.filter(teacher= user)
	context = {
		"user": user,
		"messages": messages,
	}

	return render(request, 'profile.html', context)


def professors_list(request):
	if request.user.is_authenticated:
		return redirect("dashboard")

	professors = User.objects.all()

	if request.GET.get('q'):
		q = request.GET.get('q')
		query = Q(username__contains=q)|Q(first_name__contains=q)|Q(last_name__contains=q)
		professors = User.objects.filter(query)

	context = {
		"professors" : professors
	}

	return render(request, 'home.html', context)

def message_professor(request, professor_id):
	if request.user.is_authenticated:
		return redirect("dashboard")

	professor = User.objects.get(id=professor_id)
	form = MessageForm()

	if request.method == 'POST':
		form = MessageForm(request.POST)
		if form.is_valid():
			message = form.save(commit=False)
			message.teacher = professor
			message.save()

			return redirect("thank-you", professor.id)

	context = {
		"form" : form,
		"professor" : professor
	}

	return render(request, 'sendmessage.html', context)


def thankyou(request, professor_id):
	if request.user.is_authenticated:
		return redirect("dashboard")

	context = {
		"professor_id" : professor_id
	}
	return render(request, 'thankyou.html', context)


def dashboard(request):
	if request.user.is_anonymous:
		return redirect('login')

	liked = request.user.like_set.all().values_list('message', flat=True)
	context = {
		"liked_messages" : liked
	}

	return render(request, 'dashboard.html', context)

def delete_message(request, message_id):
	if request.user.is_anonymous:
		return redirect('login')
		
	Message.objects.get(id=message_id).delete()
	return redirect("dashboard")


def likeMessage(request, message_id):
	if request.user.is_anonymous:
		return redirect('login')

	message = Message.objects.get(id=message_id)
	like, created = Like.objects.get_or_create(professor=request.user, message=message)

	if created:
		action = "like"
	else:
		like.delete()
		action = "unlike"

	response = {
		"action" : action
	}

	return JsonResponse(response, safe=False)

def liked_messages(request):
	if request.user.is_anonymous:
		return redirect('login')

	return render(request, 'fav.html')


def update_profile(request):
	if request.user.is_anonymous:
		return redirect('login')

	form = UserForm()
	if request.method == 'POST':
		form = UserForm(request.POST)
		if form.is_valid:
			form.save()
			return redirect('dashboard')

	context = {
		"form" : form
	}

	return render(request, 'updateprofile.html', context)




