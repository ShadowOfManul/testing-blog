#coding: utf-8
import re
from urlparse import urlparse

allowedTags = ['b','i','u','url','audio','list','le','img']
pairedTags = ['b','i','u','url','audio','list','le']
				#bb  : html
attr_mapping = {'url':'href'}

def validateUrl(url):
	def percent_encode(_url):
		safe_chars = frozenset(u'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-=/&?:%&#')
		
		def replace(c):
			if c not in safe_chars:
				return u"%%%02X" % ord(c)
			else:
				return c
				
		return u"".join([replace(c) for c in _url])
	try:	
		scheme, netloc, path, params, query, fragment = urlparse(url)
		
		if not scheme: #and netloc != "":
			url = u"http://" + url
			scheme, netloc, path, params, query, fragment = urlparse(url)
		
		if scheme.lower() not in [u'http', u'https']:
			return u""
	
		url = percent_encode(url)
	except ValueError:	
		url = u""
	return url

class TagBase:
	'''
		IDcounter - ID нового тэга
		html - аналог в терминах html
		attributes - список аттрибутов, например [url = google.com] 
	google.com - аттрибут url тега url
		re_attributes - regexp с помощью которого будет разобран тэг
	'''
	#IDcounter = 0
	
	html = ''
	allowed_attr = []
	attr_values = {}
	
	#re_attributes = re.compile(r'\[(?!/)(?P<opening>\S*)\s?=?\"?(?P<attr>\S*)\"?\]|\[/(?P<closing>.+?)\]', re.UNICODE)
	
	#понадобится, если будет несколько атрибутов у тега
	#allowed_attributes = None
	#allowed_att_values = None
	
	def __init__(self, name, paired = True):
		# TagBase.IDcounter += 1
		# self.id = TagBase.IDcounter
		
		self.name = name
		self.paired = paired
		
		self.open_pos = None
		self.close_pos = None
		
	def open(self, open_pos):
		self.open_pos = open_pos
	
	def close(self, close_pos):
		self.close_pos = close_pos
		
	def setAttr(self, attr):
		for key in attr.keys():
			self.attr_values[key] = attr[key]
				
	def validateAttr(self):
		pass
			
	def renderOpenHtml(self):
		attr_string = ''
		fin_html = ''
		if self.allowed_attr != [] and self.attr_values != {}:
			fin_html = '<%s %s>'
			for attr in self.attr_values.keys():
				attr_string += '%s=\"%s\" ' % (attr, self.attr_values[attr])
			return fin_html % (self.html, attr_string)
		else:
			fin_html = '<%s>'
			return fin_html % self.html
	
	def renderCloseHtml(self):
		return '</%s>' % self.html
	
	#проверка\возврат аттрибутов
	def isPaired(self):
		return self.paired
		
	def hasPair(self):
		if self.isPaired():
			if self.close_pos != None:
				return True
			else: 
				return False
		else:
			return True
			
	def getOpenPos(self):
		return self.open_pos
		
	def getClosePos(self):
		return self.close_pos
		
	#херня, перерисовать
	def backToBB(self):
		if self.allowed_attr != [] and self.attr_values !={}:
			return '[%s=%s]' % (self.name, self.attr_values[self.allowed_attr[0]])
		else:
			return '[%s]' % self.name
			
class bTag(TagBase):
	html = 'strong'

class uTag(TagBase):
	html = 'u'

class iTag(TagBase):
	html = 'em'
	
class urlTag(TagBase):
	html = 'a'
	allowed_attr = ['href']
	
	def validateAttr(self):	
		self.attr_values['href'] = validateUrl(self.attr_values.get('href'))

class imgTag(TagBase):
	html = 'img'
	allowed_attr = ['src']

	def validateAttr(self):
		img_ext = ['jpeg','jpg','png','gif']
		src = validateUrl(self.attr_values['src'])
		
		if src == "":
			self.attr_values['src'] = ""
		else:
			if src.split('.')[-1] in img_ext:
				self.attr_values['src'] = src
			else:
				self.attr_values['src'] = ""

'''
остальные три зафигачу потом. если понять как делать простые, с этими труда не возникнет
'''	
class audioTag(TagBase):
	html = 'audio'
	allowed_attr = ['src']
	attr_values = {'controls':'true'}
	
	def validateAttr(self):
		audio_ext = ['mp3','ogg']
		src = validateUrl(self.attr_values['src'])
		
		if src == "":
			self.attr_values['src'] = ""
		else:
			if src.split('.')[-1] in audio_ext:
				self.attr_values['src'] = src
			else:
				self.attr_values['src'] = ""

class listTag(TagBase):
	html = 'ul'

class leTag(TagBase):
	html = 'li'

class codeTag(TagBase):
	html = 'div'
	allowed_attr = 'lang'
	attr_values = {'class':'code', 
				   'style':'''white-space: pre; font-family: "Courier New",
						      Courier, monospace; font-size: 12px;'''}

	
#заглушка, придумать более адекватный способ
class closingTag():
	def __init__(self, name, open_tag):
		self.name = name
		self.open_tag = open_tag
	def __str__(self):
		return 'CLOSING TAG TO '+self.name+' ON '+str(self.open_tag)

class TagCreator():
	'''
	TagFactory, that's all
	createTag(name) - create tag, that is "name"-tag, for ex: 
	createTag('url') - create an instance of url-tag
	 '''
	def createTag(self, name):
		if	 name == 'b':
			return bTag('b')
		elif name == 'i':
			return iTag('i')
		elif name == 'u':
			return uTag('u')
		elif name == 'url':
			return urlTag('url')
		elif name == 'audio':
			return audioTag('audio')
		elif name == 'list':
			return listTag('list')
		elif name == 'le':
			return leTag('le')
		elif name == 'img':
			return imgTag('img', False)

class Token:

	taglike = re.compile(r'\[/?(?P<name>[\w]*)[\s]?[=]?[\s]?\"?(.*?)\"?\]', re.DOTALL)
	
	def __init__(self, content):
		self.content = content
	
	def isTag(self):
		maybe_tag = Token.taglike.search(self.content)
		if maybe_tag is not None:
			mb_t_name = maybe_tag.group('name')
			if mb_t_name in allowedTags:
				return True
			else:
				return False
		else: 
			return False
					
	def isCloseTag(self):
		if self.isTag() and self.content[1]=='/':
			return True
		else:
			return False
			
	def getContent(self):
		return self.content
		
	def __add__(self, other):
		return Token(self.content + other.content)
		
	def __str__(self):
		return str(self.content)
	
class MultiReplace(object):
    def __init__(self, repl_dict):
        # string to string mapping; use a regular expression
        keys = repl_dict.keys()
        keys.sort(reverse=True) # lexical order
        pattern = u"|".join([re.escape(key) for key in keys])
        self.pattern = re.compile(pattern)
        self.dict = repl_dict
        self.sub = self.pattern.sub

    def replace(self, s):
        # apply replacement dictionary to string
        get = self.dict.get
        def repl(match):
            item = match.group(0)
            return get(item, item)
        return self.sub(repl, s)

    __call__ = replace

	
class Parser:
	_input_bb = ""
	_tokens=[]
	_tag_factory = None

	standard_replace = MultiReplace({ u'<':u'&lt;',
									  u'>':u'&gt;',
									  u'&':u'&amp;',
									  u'\n':u'<br/>',
									  u'\t':u'&nbsp&nbsp&nbsp&nbsp'})

	
	def __init__(self, input):
		self._input_bb = Parser.standard_replace(input)
		self._tag_factory = TagCreator()

	def tokenize(self):
		'''
		с префиксом t_ - перепенные, относящиеся к тексту, чистому от bb разметки
		с префиксом b_ - переменные, относящиеся к bb-тегам
		'''
		input = self._input_bb
		maybe_tag = re.compile(r'\[/?(.*?)\]', re.DOTALL)
		start_pos = 0
		
		tokens = []
		
		def getBbName(token):
			'''принимает строку, содержащую тег и выдает его имя'''
			b_name = re.split('[\s=]',token)[0]
			return b_name
		
		def getBB(piece):
			start_pos = 0
			
			while True:
				mbt = maybe_tag.search(piece, start_pos)
				if mbt is None:
					return -1
				if getBbName(mbt.group(1)) in allowedTags:
					return mbt.span()
				else:	
					start_pos = mbt.span()[0]+1
			
		while True:
			hm = maybe_tag.search(input, start_pos)
			if hm is not None:	
				b_name = getBbName(hm.group(1))
				if b_name in allowedTags:
					t_start_pos = start_pos
					
					b_start_pos = hm.span()[0]
					b_end_pos = hm.span()[1]
					b_tok = Token(input[b_start_pos : b_end_pos])
					t_tok = Token(input[t_start_pos : b_start_pos])
					
					if t_tok.getContent() != '':
						if len(tokens) > 0:
							if not tokens[-1].isTag():
								tokens[-1] += t_tok
							else:
								tokens.append(t_tok)
						else:
							tokens.append(t_tok)
					
					tokens.append(b_tok)
					start_pos = b_end_pos
				else:
					poss = getBB(hm.group(1))
					if poss != -1:
						#добавим все перед тэгом в список токенов и передадим начало тэга наверх
						t_start_pos = start_pos
						t_end_pos = poss[0]
						t_tok = Token(input[t_start_pos : t_end_pos])
						start_pos = poss[1]
					else:
						#добавим весь кусок в список токенов
						t_end = hm.span()[1]
						t_tok = Token(input[start_pos : t_end])
						start_pos = t_end
					
					if len(tokens) > 0:
						if not tokens[-1].isTag():
							tokens[-1] += t_tok
						else:
							tokens.append(t_tok)
					else:
						tokens.append(t_tok)
			else:
				if input[start_pos : ] != "":
					tokens.append(Token(input[start_pos : ]))
				self._tokens = tokens
				return
				
	def buildTags(self):		
		#при расширении придется переносить в тэги, пока так
		re_attributes = re.compile(r'\[(?!/)(?P<name>[\w]*)[\s]?[=]?[\s]?\"?(?P<attr>.*?)\"?\]|\[/(?P<closing>.+?)\]', re.UNICODE)
		
		def getBbName(token):
			'''принимает строку, содержащую тег и выдает его имя'''
			b_name = re.split('[\s=]',token[1:-1])[0]
			return b_name
			
		def findClosing(name, start_pos):
			for idx, tok in enumerate(self._tokens):
				if isinstance(tok,Token):
					if tok.getContent() == "[/%s]" % name and idx > start_pos :
						return idx
			return None	
				
		if self._tokens != []:
			for idx, tok in enumerate(self._tokens):
				if isinstance(tok, Token) and tok.isTag() and not tok.isCloseTag():
					b_name = getBbName(tok.getContent())
					tag_obj = self._tag_factory.createTag(b_name)
					
					#если не получается создать тэг, значит это какая-то хрень и лучше её пропустить
					try:
						tag_obj.open(idx)
					except:
						self._tokens[idx]=Token("")
						continue
					
					#переписать, если будет несколько атрибутов у тега!
					#а они будут, хотя бы для audio
					if tag_obj.allowed_attr != []:
						attr_to_set = {}
						attr = re_attributes.search(tok.getContent()).group('attr')
						attr_to_set[tag_obj.allowed_attr[0]] = attr
						tag_obj.setAttr(attr_to_set)
						tag_obj.validateAttr()
					
					close_pos = findClosing(b_name, idx)

					tag_obj.close(close_pos)

					self._tokens[idx] = tag_obj

					if close_pos is not None:
						self._tokens[close_pos] = closingTag(b_name,idx)					
				else:
					self._tokens[idx] = tok

		else:
			if self._input_bb != '':
				self.tokenize()
				self.buildTags()
			else:
				return
						
	def renderToHtml(self):
		html = ''
		to_rend = range(0,len(self._tokens))
		for idx, tok in enumerate(self._tokens):
			if isinstance(tok, TagBase):
				tag = tok
				open_pos = tag.getOpenPos()
				
				#если открывающий тэг, делаем...
				if tag.isPaired():
					if tag.hasPair():
						to_rend[open_pos] = tag.renderOpenHtml()
						
						close_pos = tag.getClosePos()
						to_rend[close_pos] = tag.renderCloseHtml()
					else:
						#сделать обратный рендер в бб
						#вроде сделан, но looks like shit
						to_rend[open_pos] = tag.backToBB() #"No pair for "+ tag.name+" tag "
				else:
					to_rend[open_pos] = tag.renderOpenHtml()

			elif isinstance(tok, closingTag):
				pass
			else:
				#закрывающих остаться не должно, т.е. это - текст
				#print tok, tok.__class__
				to_rend[idx] = tok.getContent()
		
		html = html.join(to_rend)
		return html
	#функция для отладки
	def getTokens(self):
		return self._tokens
	#исправление невалидного кода, потом
	def validate(self):
		pass



		
def fastParse(input):
	parser = Parser(input)
	parser.tokenize()
	parser.getTokens()
	parser.buildTags()
	return parser.renderToHtml()
	
def test():
	tests = ['[url = "http://www.koko.com"]sffd[/url]',
			 '[url]fdgdfg',
			 '[url]br[b][/i][/b][b][b][][/u][/b]',
			 '[][b][][p]Hello,[p]World',
			 '[url ="http://www.google.com/coop/cse?cx=006850030468302103399%3Amqxv78bdfdo"]CakePHP Google Groups[/url]',
			 '[audio = "www.koko.com/koko.mp3"]Kkokok[/audio]',
			 """['[url = "http://www.koko.com"]sffd[/url]',
			 '[url]fdgdfg',
			 '[url]br[b][/i][/b][b][b][][/u][/b]',
			 '[][b][][p]Hello,[p]World',
			 '[url ="http://www.google.com/coop/cse?cx=006850030468302103399%3Amqxv78bdfdo"]CakePHP Google Groups[/url]',
			 '[audio = "www.koko.com/koko.mp3"]Kkokok[/audio]'
			 ]"""
			 ]
	for test in tests:
		print fastParse(test)
test()