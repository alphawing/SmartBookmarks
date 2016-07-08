#load classifier and classes
# predict class for a bookmark
import numpy as np
import urllib2
from BeautifulSoup import BeautifulSoup
import string
punct = set(string.punctuation)
def url_features(url):
	'''gets features from a given url's title'''
	try:
		soup = BeautifulSoup(urllib2.urlopen(url))
		title = soup.title.string
	except :
		print "url not reachable , enter title manually"
		title = str(raw_input())
	a = "".join([title," ",url])
	a = ''.join(x if x not in punct else " " for x in a)
	a = a.lower()
	return a

def predict(clf,vectorizer):
	'''predicts bookmrks based on the tags and url'''
	print "enter url"
	url = str(raw_input())
	a = url_features(url)
	tags = " ".join(a.split())
	print "tags	:",tags
	# vectorize input
	x = vectorizer.transform(np.array([a]))
	# get predicted probabilities
	outputs = clf.predict_proba(x)[0]
	opmap = zip(outputs,clf.classes_)
	opmap.sort(key = lambda a:a[0],reverse = True)
	predicted = clf.predict(x)
	pred_folder = []
	for fld in opmap[1:5]:
		pred_folder.append(fld[1])
	return(predicted,pred_folder)


