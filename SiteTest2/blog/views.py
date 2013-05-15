# -*- coding: utf-8 -*- 
from blog.models import Article
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django import forms
from bb import fastParse

import re
from postmarkup import render_bbcode

class ArticleForm(forms.ModelForm):		
	class Meta:
		model = Article
		fields = ('title', 'bb_text')
		


#отображает список статей постранично	
def index(request, page_id):
	articles = Article.objects.all()
	articles_number = len(articles)
	if articles_number%5==0 :
		pages_number = articles_number/5
	else:
		pages_number = articles_number/5+1
		
	#т.е. page_id не передался, то нам надо показать список самых последних новостей. а-ля главная страница
	if not page_id:
		articles_to_ret = articles.order_by('-pub_date')[:5]
		prev_page_id = 0
		if pages_number > 1:
			next_page_id = 2
			return render_to_response('article_list.html', 
				{'articles': articles_to_ret, 'prev_page_id': 0, 'next_page_id': 2, 'add_btn_href':'add_article'},
				context_instance=RequestContext(request))
		else:
			return render_to_response('article_list.html',
				{'articles': articles_to_ret, 'prev_page_id': 0, 'next_page_id': 0, 'add_btn_href':'add_article'},
				context_instance=RequestContext(request))
	#ну а если передался, вытаскиваем нужные статьи, и считаем все, что нужно
	else: 
		if page_id > 0:
			articles_to_ret = articles.order_by('-pub_date')[(int(page_id)-1)*5:int(page_id)*5]
			prev_page_id = int(page_id) - 1
			next_page_id = int(page_id) + 1
			if next_page_id <= pages_number:
				return render_to_response('article_list.html', 
					{'articles': articles_to_ret, 'prev_page_id': prev_page_id, 'next_page_id': next_page_id, 'add_btn_href':'add_article'},
					context_instance=RequestContext(request))
			else:
				return render_to_response('article_list.html', 
					{'articles': articles_to_ret, 'prev_page_id': prev_page_id, 'next_page_id': 0, 'add_btn_href':'add_article'},
					context_instance=RequestContext(request))
		
def post(request, post_id):
	article = get_object_or_404(Article, pk = post_id)
	return render_to_response('article_full.html',
		{'article':article},
		context_instance=RequestContext(request))
	
#переписать полностью! добавить адекватства, убрать троеточие, добавить
#логику на отображение "читать дальше" и т.д....
def get_desc(full_text):
	words_number = len(re.split('\s',full_text))
	if words_number < 100:
		desc = ""
		first_words = re.split('\s',full_text)[:100]
		for word in first_words:
			desc += word + ' '
		return desc
	else:
		desc = ""
		first_words = re.split('\s',full_text)[:100]
		for word in first_words:
			desc += word + ' '
		if desc[-2] != '!' or desc[-2] != '?' or desc[-2] != '.':
			desc = desc[:-1] + "..."
		return desc
		
def is_big(full_text):
	words_number = len(re.split('\s',full_text))
	if words_number < 150:
		return False
	else:
		return True

ref_for_article_form = "/"
def dealWithArticle(request, post_id=0):
	'''
	если post_id = 0 => аргумент был не передан и мы создаем статью
	иначе редактируем статью с id = post_id
	надо будет прикрутить куки, чтобы... после редактирования статьи возвращать
	на страницу, откуда статья редактировалась.
	а после создания статьи возвращать страницу новосозданной статьи
	'''
	if post_id == 0:
		#добавление статьи
		mode = 0
	else:
		#редактирование статьи
		mode = 1
	try:
		article = Article.objects.get(pk = post_id)
		article_form = ArticleForm(instance = article)
		article = article_form.save(commit = False)
	except Article.DoesNotExist:
		article = Article()
		
		
	if request.POST:
		post = request.POST.copy()
		new_article_form = ArticleForm(post)
		if new_article_form.is_valid():
			new_article = new_article_form.save(commit = False)
			
			article.title = new_article.title
			article.bb_text = new_article.bb_text
			article.main_text = render_bbcode(new_article.bb_text)
			article.desc_text = render_bbcode(get_desc(new_article.bb_text))
			article.pub_date = timezone.now()
			article.is_big = is_big(article.main_text)
			
			article.save()
			return HttpResponseRedirect(reverse('blog.views.post',kwargs={'post_id':article.id}))
		else:
			return render_to_response('article_form.html',{'article_form': new_article_form, 
														   'mode':mode,
														   'url_ref': ref_for_article_form},
															context_instance=RequestContext(request))
	else:
		#добавляем статью
		if mode == 0:
			article_form = ArticleForm()
			return render_to_response('article_form.html',{'article_form': article_form,
													   'mode':mode,
													   'url_ref': ref_for_article_form},
														context_instance=RequestContext(request))
		if mode == 1:
			return render_to_response('article_form.html',{'article_form': article_form,
														   'mode':mode,
														   'url_ref': ref_for_article_form,
														   'article_id':article.id},
															context_instance=RequestContext(request))

def delete_article(request):
	a = get_object_or_404(Article, pk = request.POST['article_id'])
	a.delete()
	return HttpResponseRedirect('/')


def testView(request):
	if request.GET:
		input = request.GET['input']
		output = fastParse(input)
		return render_to_response('test.html',{'input':input, 'output':output})
	else:
		return render_to_response('test.html')

