#original open-sourced reference code was obtained from "https://bhooi.github.io/"
#loading necessary packages in

from __future__ import division
import math
from operator import itemgetter
import operator
import random
import numpy as np
import sklearn
from sklearn.cluster import KMeans
from scipy.special import gammaln, psi
from preprocess import *
import dill as pickle

# runs bayesian fraud detection; returns vector of suspiciousness
# (in same order as rating_arr)

#adjusting cluster hyperparameter alpha of cluster K to get user behavior distribution
def fit_alpha(D):
	(m, S) = D.shape
	S = int(S)
	if m <= 1: return [1] * S
	alpha = np.array([3] * S)
	alpha_next = np.array([None] * S)
	row_tot = np.sum(D, axis=1)
	MAX_FIT_ITERS = 100
	for it in range(MAX_FIT_ITERS):
		alpha_sum = np.sum(alpha)
		for s in range(S):
			D_col = D[:, s]
			numer = np.sum(D_col / (D_col + (-1 + alpha[s]) * np.ones(m)))
			denom = np.sum(row_tot / (row_tot + (-1 + alpha_sum) * np.ones(m)))
			alpha_next[s] = alpha[s] * numer / denom
		if np.sum(np.abs(alpha - alpha_next)) < 0.01:
			break
		alpha = alpha_next.copy()
	return alpha + 1

#adjusting with respect to another hyperparameter beta
def lbeta(alpha):
    return sum(math.lgamma(a) for a in alpha) - math.lgamma(sum(alpha))

#generating Dirichlet distribution
def ldirichlet_pdf(theta, alpha):
    kernel = sum((a - 1) * math.log(t) for a, t in zip(alpha, theta))
    return kernel - lbeta(alpha)

#Performing argmax for Diritchlet-Multinomail distribution to adjust users' assignments to clusters
def ldirich_multi_pdf(z, alpha):
	npalpha = alpha + z
	return (gammaln(np.sum(alpha)) - gammaln(np.sum(npalpha)) +
		   np.sum(gammaln(npalpha)) - np.sum(gammaln(alpha)))

# denomiator of KL divergence, i.e. E_P 1/log Q(x), where P and Q have Dirich
# params alpha, beta;
# http://bariskurt.com/kullback-leibler-divergence-between-two-dirichlet-and-beta-distributions/
def kl_denom(alpha, beta):

	psi_diff = np.sum(beta * (psi(sum(alpha)) - psi(alpha)))
	return -math.lgamma(np.sum(beta)) + np.sum([math.lgamma(x) for x in np.squeeze(beta)]) + psi_diff

#detecting function
def detect(rating_arr, use_times, K):
	m = rating_arr.shape[0]
	rating_sums = rating_arr.sum(axis=1) + 0.1
	rating_normal = rating_arr / rating_sums[:, np.newaxis]
	user_normal = rating_normal

	#generating K clusters
	est = KMeans(n_clusters=K)
	est.fit(user_normal)
	z = np.array(est.labels_)

	#pi : cluster proportions to be adjusted for each cluster
	pi = [None] * K
	zn = np.array([-1] * m) # z_next
	(m, S1) = rating_arr.shape

	#initial hyperparmeter alpha before fitting
	alpha1 = np.array([[0] * S1 for _ in range(K)], dtype=float)

	NUM_FIT_ITERS = 100
	for it in range(NUM_FIT_ITERS):
		for k in range(K):
			cur_idx = np.array((z == k))
			rating_sub = rating_arr[cur_idx, :]
			n_k = np.sum(cur_idx)
			pi[k] = n_k / m
			if n_k > rating_arr.shape[0]:
				sample_idx = np.array(random.sample(range(n_k), rating_arr.shape[0]))
			else:
				sample_idx = range(n_k)
			rating_sub = rating_sub[sample_idx, :]
			alpha1[k,:] = fit_alpha(rating_sub)

		for i in range(m):
			log_likes = [(ldirich_multi_pdf(rating_arr[i, :], alpha1[k])) for k in range(K)]
			zn[i] = log_likes.index(max(log_likes))
		num_diff = sum(abs(zn - z))
		z = zn
		if num_diff == 0:
			break

	#getting posterior
	post_rating = np.array(rating_arr, dtype='float')
	for i in range(m):
		post_rating[i,:] += alpha1[z[i]]

	#creating array to store suspicion degree
	susp1 = np.zeros(m)
	for i in range(m):
		if i % 100000 == 0: print (i)
		susp1[i] = max([kl_denom(post_rating[i,:], alpha1[k,:]) for k in range(K)])

	#normalizing suspicion
	susp1n = susp1 / np.std(susp1)
	suspn = susp1n
	return suspn
