# -*- coding: utf-8 -*- 
from django.db import models


class Article(models.Model):
	title = models.CharField(max_length = 200)
	#description text
	desc_text = models.CharField(max_length = 2000)
	#main content text
	main_text = models.TextField()
	#user's input
	bb_text = models.TextField()
	#publishing date
	pub_date = models.DateTimeField()
	#big (>150 words) or small article
	is_big = models.BooleanField()
	
	def __unicode__(self):
		return self.title
		

