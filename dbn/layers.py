"""
Implements different types of layers
- Allows for easy grouping of different types of activation
  functions
- Types:
	- Sigmoid
"""
import theano.tensor as T
import numpy         as np
import utils,theano
from theano.tensor.shared_randomstreams import RandomStreams
NO_UPDATES = theano.OrderedUpdates()
theano_rng = utils.theano_rng
class Linear(object):
	def __init__(self,size):
		self.size = size
	def mean(self,activation_score):
		return activation_score

	def sample(self,activation_score,*args):
		activation_probs = self.mean(activation_score)
		return \
			activation_probs,\
			activation_probs,\
			NO_UPDATES

class Sigmoid(Linear):
	activation = T.nnet.sigmoid
	def mean(self,activation_score):
		activation_probs = self.activation(activation_score)
		return activation_probs

	def sample(self,activation_score,*args):
		activation_probs = self.mean(activation_score)
		return \
			activation_probs,\
			theano_rng.binomial(
				size  = activation_probs.shape,
				n     = 1,
				p     = activation_probs,
				dtype = theano.config.floatX
			),\
			NO_UPDATES

class Softmax(Sigmoid):
	activation = T.nnet.softmax
	def sample(self,activation_score,*args):
		activation_probs = self.mean(activation_score)
		return \
			activation_probs,\
			activation_probs,\
			NO_UPDATES

class OneHotSoftmax(Softmax):
	def sample(self,activation_score,*args):
		activation_probs = self.mean(activation_score)
		return \
			activation_probs,\
			theano_rng.multinomial(
				n     = 1,
				pvals = activation_probs,
				dtype = theano.config.floatX
			),\
			NO_UPDATES



class ReplicatedSoftmax(Softmax):

	def sample_k_times(self,prob,d):
		sample = theano_rng.multinomial(n=d,pvals=prob)
		return sample


	def sample(self,activation_score,data):
		activation_probs = self.mean(activation_score)
		D = T.sum(data,axis=1)
		samples, updates = theano.scan(
				fn=self.sample_k_times,
				sequences=[activation_probs,D]
			)
		return \
			activation_probs,\
			samples,\
			updates

