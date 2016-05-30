class Mapping(object):
	def __init__(self,profileIDs,goals):
		self.profileIDs=profileIDs
		self.mapping=dict()
		self.html=''
		self.convtypes=list()
		self.conv=goals['Conversion'] if 'Conversion' in goals else list() 
		self.rev=goals['Conversion + Revenue'] if 'Conversion + Revenue' in goals else list()
		self.conversion(self.conv+self.rev)
		self.revenue(self.rev)

	def conversion(self,items):
	    if len(items)>0:
	        for i in items:
	            if (i=='transaction'):
	                self.mapping.update({i+'s':'[ecommerce Conv]'})
	                self.convtypes+=['ecommerce']
	            else:
	                self.mapping.update({i+'Completions':'['+i+' Conv]'})
	                self.convtypes+=[i]
	    return self
	def revenue(self,items):
	    if len(items)>0:
	        for i in items:
	            if (i=='transaction'):
	                self.mapping.update({i+'Revenue':'[ecommerce Rev]'})
	            else:
	                self.mapping.update({i+'Value':'['+i+' Conv]'})
	    return self
	def tagging_type(self,html=False):
		raise NotImplementedError

	def metadata(self):
		raise NotImplementedError

	def ismultiprofile(self):
		if len(self.profileIDs)>1:
			return True
		else:
			return False

	def cli_export(self) :
		output='***********\n'
		output+='Mapping name : '+self.metadata()+'\n'
		output+='******\n'
		output+=self.export()+'\n'
		output+='***********\n'
		return output

	def export(self):
		output='profileIds: '+str(self.profileIDs)+'\n'
		output+='mapping: '+str(self.mapping).replace("'",'')+'\n'
		output+=self.tagging_type()
		return output

	def html_export(self):
		self.html='profileIds: '+str(self.profileIDs)+'<br/>'
		self.html+='mapping: '+str(self.mapping).replace("'",'')+'<br/>'
		self.html+=self.tagging_type(html=True)
		return {'mapping':self.html,'conversion_types':self.convtypes,'name':self.metadata(),'profileIDs':self.serialize_profiles()}
	def serialize_profiles(self):
		return '-'.join([str(i) for i in self.profileIDs])


class Autotagging(Mapping):
	def __init__(self,profileIDs,goals):
		Mapping.__init__(self,profileIDs,goals)
	def tagging_type(self,html=False):
		return 'integrationType: AdWords'
	def metadata(self):
		return 'revenue-googleanalytics-autotagging-'+('multiprofile' if self.ismultiprofile() else str(self.profileIDs[0]))

class Manualtagging(Mapping):
	def __init__(self,profileIDs,goals,delim='|',adcontent='classic'):
		Mapping.__init__(self,profileIDs,goals)
		self.delim=delim
		self.adcontent='{1: Keyword ID, 3: Creative ID, 5: Keyword, 7: matchType, 9 : Device}' if adcontent=='classic' else '{1: Keyword ID, 3: Creative ID, 5: Keyword, 7: matchType}'

	def tagging_type(self,html=False):
		adcontent="adContentDelim: '"+self.delim+"' "
		adcontent+='\n' if (html==False) else '<br/>' 
		adcontent+='adContentMapping: '+self.adcontent
		return adcontent

	def metadata(self):
		return 'revenue-googleanalytics-manualtagging-'+('multiprofile' if self.ismultiprofile() else str(self.profileIDs[0]))