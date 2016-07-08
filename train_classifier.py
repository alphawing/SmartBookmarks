#vectorize features in a numpy sparse matrix and classes as numpy arrays 
#train and save classifier
#save vectorizer fo transforming future inputs
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import RidgeClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import Perceptron
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestCentroid
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.extmath import density
from sklearn import metrics
import numpy as np
import random
def train():
	vectorizer = CountVectorizer(min_df=1)
	f = open("./data/bookmark_features","r")
	corpus = np.array(f.read().decode("utf-8").split("\n"))
	X = vectorizer.fit_transform(corpus)
	f = open("./data/bookmark_classes")
	categories = np.array(f.read().split("\n"))
	clf = BernoulliNB(alpha = 0.000000000002).fit(X,categories)
	p = clf.predict(X)
	Training_error = np.mean(p==categories)
	#f = open("./data/classifier.pkl","wb")
	#pickle.dump(clf,f)
	#f = open("./data/vectorizer.pkl","wb")
	#pickle.dump(vectorizer,f)
	return (clf,vectorizer,Training_error)