# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import bcrypt, re
from datetime import datetime, date
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.+_-]+\.[a-zA-Z]+$')

class ValidationManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        if len(postData['firstname']) < 1:
            errors["firstname1"] = "First Name cannot be empty/blank"
        if len(postData['firstname']) < 2:
            errors["firstname2"] = "First Name cannot be less than 2 characters"
        if postData['firstname'].isalpha() == False:
            errors["firstname3"] = "First Name must be letters only"
        if len(postData['lastname']) < 1:
            errors["lastname1"] = "Last Name cannot be empty/blank"
        if len(postData['lastname']) < 2:
            errors["lastname2"] = "Last Name cannot be less than 2 characters"
        if postData['lastname'].isalpha() == False:
            errors["lastname3"] = "Last Name must be letters only"
        # Email check if registered below: regemail
        regemail = Users.objects.filter(email__contains=postData["email"])
        if len(regemail) > 0:
            errors["email"] = "Cannot use Email entered. Email already in use"
        if not EMAIL_REGEX.match(postData['email']):
            errors["email"] = "Invalid Email, Re-Enter"
        ##Birthdate Validation
        date = unicode(datetime.now().strftime('%Y-%m-%d'))
        print "date", date
        print "birthdate", postData["birthdate"]
        if postData['birthdate'] >= date:
            errors["birthdate"] = "Birthdate cannot be in the future nor today"
        ##
        if len(postData['password']) < 8:
            errors["password"] = "Password must be at least 8 characters"
        if postData["pw_confirm"] != postData["password"]:
            errors["pw_confirm"] = "Passwords Do Not Match"
        return errors

class LoginValidationManager(models.Manager):
    def login_validator(self, postData):
        loginerrors = {}
        allusers = Users.objects.all()
        if len(allusers) == 0:
            loginerrors["nousers"] = "No Current Users. Please Register"
        loginpassword = Users.objects.filter(email__contains=postData["loginemail"])
        for password in loginpassword:
            if bcrypt.checkpw(postData["loginpassword"].encode(), password.password.encode()) != True:
                loginerrors["loginpassword"] = "Password incorrect"
        loginemail = Users.objects.filter(email__contains=postData["loginemail"])
        for email in loginemail:
            if postData["loginemail"] != email.email:
                loginerrors["loginemail"] = "Email incorrect"
                print loginerrors
        return loginerrors

class Users(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    birthdate = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ValidationManager()
    loginobjects = LoginValidationManager()
    def __repr__(self):
        return "<id={}> firstname={} lastname={} email={} birthdate={} password={}>".format(self.id, self.first_name, self.last_name, self.email, self.birthdate, self.password)

class Authors(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    objects = models.Manager()
    def __repr__(self):
        return "<id={}> name={}>".format(self.id, self.name)

class Books(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    author = models.ForeignKey(Authors, related_name="author")
    objects = models.Manager()
    def __repr__(self):
        return "<id={}> title={}>".format(self.id, self.title)

class Reviews(models.Model):
    rating = models.IntegerField()
    desc = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    user = models.ForeignKey(Users, related_name="reviewer")
    book = models.ForeignKey(Books, related_name="bookreview")
    objects = models.Manager()
    def __repr__(self):
        return "<id={}> title={} desc={} createdat = {} >".format(self.id, self.rating, self.desc, self.created_at)

