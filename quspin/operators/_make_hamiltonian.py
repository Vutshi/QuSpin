from __future__ import print_function, division

# the final version the sparse matrices are stored as, good format for dot produces with vectors.
import scipy.sparse as _sp
import warnings
import numpy as _np
from ._functions import function



def test_function(func,func_args):
	t = _np.cos( (_np.pi/_np.exp(0))**( 1.0/_np.euler_gamma ) )
	func_val=func(t,*func_args)
	func_val=_np.array(func_val)
	if func_val.ndim > 0:
		raise ValueError("function must return 0-dim numpy array or scalar value.")




def make_static(basis,static_list,dtype):
	"""
	args:
		static=[[opstr_1,indx_1],...,[opstr_n,indx_n]], list of opstr,indx to add up for static piece of Hamiltonian.
		dtype = the low level C-type which the matrix should store its values with.
	returns:
		H: a csr_matrix representation of the list static

	description:
		this function takes the list static and creates a list of matrix elements is coordinate format. it does
		this by calling the basis method Op which takes a state in the basis, acts with opstr and returns a matrix 
		element and the state which it is connected to. This function is called for every opstr in list static and for every 
		state in the basis until the entire hamiltonian is mapped out. It takes those matrix elements (which need not be 
		sorted or even unique) and creates a coo_matrix from the scipy.sparse library. It then converts this coo_matrix
		to a csr_matrix class which has optimal sparse matrix vector multiplication.
	"""
	Ns=basis.Ns
	H = _sp.csr_matrix((Ns,Ns),dtype=dtype)
	for J,opstr,indx in static_list:
		# print(opstr,bond)
		ME,row,col = basis.Op(opstr,indx,J,dtype)
		Ht=_sp.csr_matrix((ME,(row,col)),shape=(Ns,Ns),dtype=dtype) 
		H=H+Ht
		del Ht
		H.sum_duplicates() # sum duplicate matrix elements
		H.eliminate_zeros() # remove all zero matrix elements
	# print()
	return H 





def make_dynamic(basis,dynamic_list,dtype):
	"""
	args:
	dynamic=[[opstr_1,indx_1,func_1,func_1_args],...,[opstr_n,indx_n,func_n,func_n_args]], list of opstr,indx and functions to drive with
	dtype = the low level C-type which the matrix should store its values with.

	returns:
	tuple((func_1,func_1_args,H_1),...,(func_n_func_n_args,H_n))

	H_i: a csr_matrix representation of opstr_i,indx_i
	func_i: callable function of time which is the drive term in front of H_i

	description:
		This function works the same as static, but instead of adding all of the elements 
		of the dynamic list together, it returns a tuple which contains each individual csr_matrix 
		representation of all the different driven parts. This way one can construct the time dependent 
		Hamiltonian simply by looping over the tuple returned by this function. 
	"""
	Ns=basis.Ns
	dynamic={}
	for J,f,f_args,opstr,indx in dynamic_list:
		if _np.isscalar(f_args): raise TypeError("function arguments must be array type")
		test_function(f,f_args)

		#indx = _np.asarray(indx,_np.int32)
		ME,row,col = basis.Op(opstr,indx,J,dtype)
		Ht =_sp.csr_matrix((ME,(row,col)),shape=(Ns,Ns),dtype=dtype) 

		func = function(f,tuple(f_args))
		if func in dynamic:
			try:
				dynamic[func] += Ht
			except:
				dynamic[func] = dynamic[func] + Ht
		else:
			dynamic[func] = Ht


	return dynamic

