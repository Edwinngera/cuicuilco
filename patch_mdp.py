#####################################################################################################################
# patch_mdp: This module adds to MDP the new nodes and functionality of Cuicuilco dynamically                       #
#                                                                                                                   #
#                                                                                                                   #
# By Alberto Escalante. Alberto.Escalante@ini.rub.de                                                                #
# Ruhr-University-Bochum, Institute for Neural Computation, Group of Prof. Dr. Wiskott                              #
#####################################################################################################################

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
import numpy
import sys
import time
import inspect

import mdp
from mdp import numx
from mdp.utils import (mult, pinv)  # , symeig, CovarianceMatrix, SymeigException)

from . import more_nodes
from . import gsfa_nodes
# from .gsfa_nodes import compute_cov_matrix
from . import histogram_equalization
from .sfa_libs import select_rows_from_matrix
from . import inversion
from . import object_cache as misc

mdp.nodes.RandomizedMaskNode = more_nodes.RandomizedMaskNode
mdp.nodes.GeneralExpansionNode = more_nodes.GeneralExpansionNode
mdp.nodes.PointwiseFunctionNode = more_nodes.PointwiseFunctionNode
mdp.nodes.PInvSwitchboard = more_nodes.PInvSwitchboard
mdp.nodes.RandomPermutationNode = more_nodes.RandomPermutationNode
mdp.nodes.HeadNode = more_nodes.HeadNode
# mdp.nodes.SFAPCANode = more_nodes.SFAPCANode
# mdp.nodes.IEVMNode = more_nodes.IEVMNode
# mdp.nodes.IEVMLRecNode = more_nodes.IEVMLRecNode
mdp.nodes.SFAAdaptiveNLNode = more_nodes.SFAAdaptiveNLNode
mdp.nodes.GSFANode = gsfa_nodes.GSFANode
mdp.nodes.iGSFANode = gsfa_nodes.iGSFANode

mdp.nodes.NLIPCANode = histogram_equalization.NLIPCANode
mdp.nodes.NormalizeABNode = histogram_equalization.NormalizeABNode
mdp.nodes.HistogramEqualizationNode = histogram_equalization.HistogramEqualizationNode
mdp.nodes.SFA_GaussianClassifier = more_nodes.SFA_GaussianClassifier
mdp.nodes.BasicAdaptiveCutoffNode = more_nodes.BasicAdaptiveCutoffNode

mdp.Flow.localized_inverse = inversion.localized_inverse

mdp.nodes.SFANode.localized_inverse = inversion.linear_localized_inverse
mdp.nodes.PCANode.localized_inverse = inversion.linear_localized_inverse
mdp.nodes.WhiteningNode.localized_inverse = inversion.linear_localized_inverse

mdp.hinet.Layer.localized_inverse = inversion.layer_localized_inverse

mdp.nodes.GeneralExpansionNode.localized_inverse = inversion.general_expansion_node_localized_inverse

# TODO: DETERMINE IF MDP INDEED NEEDS THIS PATCH!
# The original version disregards output_dim if input_dim is None!!! Correction: ... or self.input_dim is None...
# Apparently, this code is never reached with self.input_dim True
def SFANode__set_range(self):
    if self.output_dim is not None and (self.output_dim <= self.input_dim or self.input_dim is None):
        # The eigenvalues are sorted in ascending order
        rng = (1, self.output_dim)
    else:
        # otherwise, keep all output components
        rng = None
        self.output_dim = self.input_dim
    return rng

# mdp.nodes.SFANode._set_range = SFANode__set_range


def SFANode_inverse(self, y):
    # pseudo-inverse is stored instead of computed everytime
    if "pinv" not in self.__dict__ or self.pinv is None:
        self.pinv = pinv(self.sf)
    return mult(y, self.pinv) + self.avg


# print "Rewritting SFANode methods: _inverse, __init__, _train, _stop_training..."
mdp.nodes.SFANode._inverse = SFANode_inverse

# # TODO: There might be several errors due to incorrect computation of sum_prod_x as mdp.mult(sum_x.T,sum_x)
# # WARNING!!!! CHECK ALL CODE!!!
# def SFANode_train(self, x, block_size=None, train_mode=None, node_weights=None, edge_weights=None):
#     print("obsolete code reached... quitting")

# SFANode is no longer being modified/monkey patched
# mdp.nodes.SFAPCANode.list_train_params = ["scheduler", "n_parallel", "train_mode",
#                                          "block_size"]  # "sfa_expo", "pca_expo", "magnitude_sfa_biasing"
# mdp.nodes.PCANode.list_train_params = ["scheduler", "n_parallel"]
mdp.nodes.GSFANode.list_train_params = ["train_mode", "block_size", "node_weights",
                                        "edge_weights", "verbose"]
mdp.nodes.iGSFANode.list_train_params = ["train_mode", "block_size", "node_weights",
                                         "edge_weights", "verbose"]
mdp.nodes.SFAAdaptiveNLNode.list_train_params = ["scheduler", "n_parallel", "train_mode", "block_size"]
mdp.nodes.NLIPCANode.list_train_params = ["exp_func", "norm_class"]
mdp.nodes.HistogramEqualizationNode.list_train_params = ["num_pivots"]


# It extracts the relevant parameters from params according to Node.list_train_params (if available)
# and passes it to train
def extract_params_relevant_for_node_train(node, params, verbose=False):
    if isinstance(params, list):
        return [extract_params_relevant_for_node_train(node, param, verbose) for param in params]

    if params is None:
        return {}

    if isinstance(node, (mdp.hinet.Layer, mdp.hinet.CloneLayer)):
        add_list_train_params_to_layer_or_node(node, verbose)

    all_params = {}
    if "list_train_params" in dir(node):
        # list_train_params = self.list_train_params
        for par, val in params.items():
            if par in node.list_train_params:
                all_params[par] = val
    if verbose:
        print("node:", node)
        print("all_params extracted:", all_params, "for node:", node, "with params:", params)
    return all_params


def add_list_train_params_to_layer_or_node(node, verbose=False):
    if isinstance(node, mdp.hinet.CloneLayer):
        add_list_train_params_to_layer_or_node(node.nodes[0])
        node.list_train_params = node.nodes[0].list_train_params
    elif isinstance(node, mdp.hinet.Layer):
        list_all_train_params = []
        for node_i in node:
            add_list_train_params_to_layer_or_node(node_i)
            list_all_train_params += node_i.list_train_params
        node.list_train_params = list_all_train_params
    else:  # Not Layer or CloneLayer
        if "list_train_params" not in dir(node):
            if verbose:
                print("list_train_params was not present in node!!!")
            node.list_train_params = []


def node_train_params(self, data, params=None, verbose=False):
    if isinstance(self, (mdp.hinet.Layer, mdp.hinet.CloneLayer)):
        er = "Should never reach this point, we do not specify here the train_params method for Layers..."
        raise Exception(er)
    elif "list_train_params" in dir(self):
        all_params = extract_params_relevant_for_node_train(self, params, verbose)
        if verbose:
            print("NODE: ", self)
            print("with args: ", inspect.getargspec(self.train))
        # print "and doc:", self.train.__doc__
        # WARNING!!!
        # WARNING, this should be self.train, however an incompatibility was introduced in a newer MDP
        # this var stores at which point in the training sequence we are
        self._train_phase = 0
        # this var is False if the training of the current phase hasn't
        #  started yet, True otherwise
        self._train_phase_started = True
        # this var is False if the complete training is finished
        #        self._training = False
        if verbose:
            # quit()
            print("params=", params)
            print("; list_train_params=", self.list_train_params)
            print("; all_params:", all_params)
        return self._train(data, **all_params)
    else:
        # if isinstance(self, mdp.nodes.SFANode):
        print("Warning, suspicious condition reached: no node.list_train_params found, using default train", dir(self))
        # quit()
        # print(self)
        # print("wrong wrong 2...", dir(self))
        # print("data_tp=", data)
        # quit()
        return self.train(data)  # no Node.train_params found


# Patch all nodes to offer train_params
# Additionally, list_train_params should be added to relevant nodes
print("Adding train_params to all mdp Nodes")
for node_str in dir(mdp.nodes):
    node_class = getattr(mdp.nodes, node_str)
    if inspect.isclass(node_class) and issubclass(node_class, mdp.Node):
        # This assumes that is_trainable() is a class function, however this might be false in some cases
        #        if node_class.is_trainable():
        # print "Adding train_params to mdp.Node: ", node_str
        node_class.train_params = node_train_params

# Do the same with nodes contained in hinet
print("Adding train_params to (hinet) mdp.hinet Nodes")
for node_str in dir(mdp.hinet):
    node_class = getattr(mdp.hinet, node_str)
    if inspect.isclass(node_class) and issubclass(node_class, mdp.Node):
        if not issubclass(node_class, (mdp.hinet.Layer, mdp.hinet.CloneLayer)):
            # This assumes that is_trainable() is a class function, however this might be false in some cases
            #        if node_class.is_trainable():
            # print "Adding train_params to (hinet) mdp.Node: ", node_str
            node_class.train_params = node_train_params


# quit()

# Execute preserving structure of input (data vector) (and in the future passing exec_params)
# Note: exec_params not yet supported
def node_execute_data_vec(self, data_vec, exec_params=None, verbose=False):
    if isinstance(data_vec, numx.ndarray):
        return self.execute(data_vec)  # **exec_params)

    res = []
    if verbose:
        print("data_vect is:", data_vec)
    for i, data in enumerate(data_vec):
        if verbose:
            print("data.shape=", data.shape)
        res.append(self.execute(data))  # **exec_params)
    return res


# Patch all nodes to offer execute_data_vec
print("Adding execute_data_vec to all nodes")
for node_str in dir(mdp.nodes):
    node_class = getattr(mdp.nodes, node_str)
    # print node_class
    if inspect.isclass(node_class) and issubclass(node_class, mdp.Node):
        # print "Adding execute_data_vec to node:", node_str
        node_class.execute_data_vec = node_execute_data_vec
    else:
        pass
        # print "execute_data_vec not added (Not a node)", node_str

print("Adding execute_data_vec to all hinet nodes")
for node_str in dir(mdp.hinet):
    node_class = getattr(mdp.hinet, node_str)
    # print node_class
    if inspect.isclass(node_class) and issubclass(node_class, mdp.Node):
        # print "Adding execute_data_vec to (hinet) node:", node_str
        node_class.execute_data_vec = node_execute_data_vec
    else:
        pass
        # print "Not a node:", node_str


# def PCANode_train_scheduler(self, x, scheduler=None, n_parallel=None):
#     if self.input_dim is None:
#         self.input_dim = x.shape[1]
#         print("YEAHH, CORRECTED TRULY")
#     if scheduler is None or n_parallel is None:
#         # update the covariance matrix
#         self._cov_mtx.update(x)
#     else:
#         num_chunks = n_parallel
#         chunk_size_samples = int(numpy.ceil(x.shape[0] * 1.0 / num_chunks))
#
#         print("%d chunks, of size %d samples" % (num_chunks, chunk_size_samples))
#         for i in range(num_chunks):
#             scheduler.add_task(x[i * chunk_size_samples:(i + 1) * chunk_size_samples], compute_cov_matrix)
#
#         print("Getting results")
#         sys.stdout.flush()
#
#         results = scheduler.get_results()
#         #        print "Shutting down scheduler"
#         sys.stdout.flush()
#
#         if self._cov_mtx._cov_mtx is None:
#             self._cov_mtx._cov_mtx = 0.0
#             self._cov_mtx._avg = 0
#             self._cov_mtx._tlen = 0
#
#         for covmtx in results:
#             self._cov_mtx._cov_mtx += covmtx._cov_mtx
#             self._cov_mtx._avg += covmtx._avg
#             self._cov_mtx._tlen += covmtx._tlen


# mdp.nodes.PCANode._train = PCANode_train_scheduler


# Make switchboard faster!!!
def switchboard_new_execute(self, x):
    return select_rows_from_matrix(x, self.connections)


mdp.hinet.Switchboard._execute = switchboard_new_execute


# print "Fixing GaussianClassifierNode_class_probabilities..."

# Adds verbosity and fixes nan values
def GaussianClassifierNode_class_probabilities(self, x, verbose=True):
    """Return the posterior probability of each class given the input."""
    self._pre_execution_checks(x)

    # compute the probability for each class
    tmp_prob = numpy.zeros((x.shape[0], len(self.labels)),
                           dtype=self.dtype)
    for i in range(len(self.labels)):
        tmp_prob[:, i] = self._gaussian_prob(x, i)
        tmp_prob[:, i] *= self.p[i]

    # normalize to probability 1
    # (not necessary, but sometimes useful)
    tmp_tot = tmp_prob.sum(axis=1)
    tmp_tot = tmp_tot[:, numpy.newaxis]

    # Warning, it can happen that tmp_tot is very small!!!

    probs = tmp_prob / tmp_tot
    uniform_amplitude = 1.0 / probs.shape[1]
    # smallest probability that makes sense for the problem...
    # for the true semantics reverse engineer the semantics of _gaussian_prob()
    smallest_probability = 1e-60
    counter = 0
    for i in range(probs.shape[0]):
        if numpy.isnan(probs[i]).any(): # or tmp_tot[i, 0] < smallest_probability:
            if verbose:
                print("Problematic probs[%d]="%i, probs[i])
                print("Problematic tmp_prob[%d]="%i, tmp_prob[i])
                print("Problematic tmp_tot[%d]="%i, tmp_tot[i])
            # First attempt to fix it, use uniform_amplitude as guess
            probs[i] = uniform_amplitude  # TODO: Use apriori probabilities, not necessarily uniform
            counter += 1
        # Second attempt: Find maximum, and assing 1 to it, otherwise go to previous strategy...
        # Seems like it always fails with nan for all entries, thus first measure is better...
    if verbose:
        print("%d probabilities were fixed" % counter)

    # just in case at this point something still failed... looks impossible though.
    probs = numpy.nan_to_num(probs)

    return probs


def GaussianSoftCR(self, data, true_classes):
    """  Compute an average classification rate based on the 
    estimated class probability for the correct class. 
    This is more informative than taking just the class with 
    maximum a posteriory probability and checking if matches.
    self (mdp node): mdp node providing the class_probabilities function 
    data (2D numpy array): set of samples to do classification 
    true classes (1D numpy array): 
    """
    probabilities = self.class_probabilities(data)
    true_classes = true_classes.flatten().astype(int)

    tot_prob = 0.0
    for i, c in enumerate(true_classes):
        tot_prob += probabilities[i, c]
    tot_prob /= len(true_classes)
    print("In softCR: probabilities[0,:]=", probabilities[0, :])
    return tot_prob


def GaussianRegression(self, data, avg_labels, estimate_std=False):
    """  Use the class probabilities to generate a better label
    If the computation of the class probabilities were perfect,
    and if the Gaussians were just a delta, then the output value
    minimizes the squared error.
    self (mdp node): mdp node providing the class_probabilities function 
    data (2D numpy array): set of samples to do regression on
    avg_labels (1D numpy array): average label for class 0, class 1, ...
    """
    probabilities = self.class_probabilities(data)
    hat_mean = numpy.dot(probabilities, avg_labels)
    hat_mean[numpy.isnan(hat_mean)] = avg_labels.mean()  # TODO:compute real mean of all labels

    if estimate_std:
        hat_std = (numpy.dot(probabilities, avg_labels ** 2) - hat_mean ** 2) ** 0.5

    # print "value.shape=", value.shape
    if not estimate_std:
        return hat_mean
    else:
        return hat_mean, hat_std


def GaussianRegressionMAE(self, data, avg_labels):
    """  Use the class probabilities to generate a better label
    If the computation of the class probabilities were perfect,
    (and if the Gaussians were just a delta???), then the output value
    minimizes the mean average error
    self (mdp node): mdp node providing the class_probabilities function 
    data (2D numpy array): set of samples to do regression on
    avg_labels (1D numpy array): average label for class 0, class 1, ...
    """
    probabilities = self.class_probabilities(data)
    acc_probs = probabilities.cumsum(axis=1)

    print("labels=", self.labels)
    print("acc_probs[0:5]", acc_probs[0:5])

    acc_index = numpy.ones(acc_probs.shape).cumsum(axis=1) - 1
    probability_mask = (acc_probs <= 0.5)
    acc_index[probability_mask] = acc_probs.shape[1] + 100  # mark entries with acc_probs <= 0.5 as a large value.
    best_match = numpy.argmin(acc_index, axis=1)  # making the smallest entry the first one with acc_prob > 0.5

    #    probability_deviation_from_mode = numpy.abs(acc_probs-0.5)
    #    print "probability_deviation_from_mode[0:5]", probability_deviation_from_mode[0:5]
    #    best_match = numpy.argmin(probability_deviation_from_mode, axis=1)
    print("best_match[0:5]", best_match[0:5])
    # print type(best_match)
    # print type(self.labels)
    value = avg_labels[best_match]
    # print "valueMAE.shape=", value.shape
    return value


def GaussianRegressionMAE_uniform_bars(self, data, avg_labels):
    """  Use the class probabilities to generate a better label
    If the computation of the class probabilities were perfect,
    (and if the Gaussians were just a delta???), then the output value
    minimizes the mean average error
    self (mdp node): mdp node providing the class_probabilities function 
    data (2D numpy array): set of samples to do regression on
    avg_labels (1D numpy array): average label for class 0, class 1, ...
    """
    probabilities = self.class_probabilities(data)
    acc_probs = probabilities.cumsum(axis=1)

    print("labels (classes)=", self.labels)
    print("acc_probs[0:5]", acc_probs[0:5])

    acc_index = numpy.ones(acc_probs.shape).cumsum(axis=1) - 1
    probability_mask = (acc_probs <= 0.5)
    acc_index[probability_mask] = acc_probs.shape[1] + 100  # mark entries with acc_probs <= 0.5 as a large value.
    best_match = numpy.argmin(acc_index, axis=1)  # making the smallest entry the first one with acc_prob > 0.5

    print("best_match=", best_match)
    # Compute x0 and x1, assume symetric bars... do this vectorially
    bar_limit_x0 = numpy.zeros(len(avg_labels))
    bar_limit_x0[1:] = (avg_labels[1:] + avg_labels[0:-1]) / 2.0
    bar_limit_x0[0] = avg_labels[0] - (avg_labels[1] - avg_labels[0]) / 2.0

    bar_limit_x1 = numpy.zeros(len(avg_labels))
    bar_limit_x1[:-1] = (avg_labels[:-1] + avg_labels[1:]) / 2.0
    bar_limit_x1[-1] = avg_labels[-1] + (avg_labels[-1] - avg_labels[-2]) / 2.0

    yy = numpy.arange(len(data))
    CP_x0 = acc_probs[yy, best_match - 1]
    mask = (best_match == 0)
    CP_x0[mask] = 0.0
    CP_x1 = acc_probs[yy, best_match]

    x0 = bar_limit_x0[best_match]
    x1 = bar_limit_x1[best_match]

    print("x0.shape=", x0.shape, "x1.shape=", x1.shape, "CP_x0.shape=", CP_x0.shape, "CP_x1.shape=", CP_x1.shape)
    value = x0 + (0.5 - CP_x0) * (x1 - x0) / (CP_x1 - CP_x0)
    print("MAE value=", value)
    #    probability_deviation_from_mode = numpy.abs(acc_probs-0.5)
    #    print "probability_deviation_from_mode[0:5]", probability_deviation_from_mode[0:5]
    #    best_match = numpy.argmin(probability_deviation_from_mode, axis=1)
    #    print "best_match[0:5]",best_match[0:5]
    # print type(best_match)
    # print type(self.labels)
    #    value = avg_labels[best_match]
    # print "valueMAE.shape=", value.shape
    return value


# Do we need this correction? apparently yes! TODO: report to MDP list
print("Fixing GaussianClassifierNode_class_probabilities")
mdp.nodes.GaussianClassifier.class_probabilities = GaussianClassifierNode_class_probabilities
mdp.nodes.GaussianClassifier.regression = GaussianRegression
# Original: mdp.nodes.GaussianClassifier.regressionMAE = GaussianRegressionMAE
# Experimental:
mdp.nodes.GaussianClassifier.regressionMAE = GaussianRegressionMAE  # GaussianRegressionMAE_uniform_bars
mdp.nodes.GaussianClassifier.softCR = GaussianSoftCR


# def switchboard_execute(self, x):
#    return apply_permutation_to_signal(x, self.connections, self.output_dim)
#
# mdp.hinet.Switchboard._execute = switchboard_execute

# print "Adding linear_localized_inverse to RandomPermutationNode..."

def RandomPermutationNode_linear_localized_inverse(self, x, y, y_prime):
    return self.inverse(y_prime)


more_nodes.RandomPermutationNode.linear_localized_inverse = RandomPermutationNode_linear_localized_inverse

# This is not needed, as long as execute is executed for setting such dim sizes
# print "Making IdentityNode trainable (to remember input/output dim sizes)"
# def IdentityNode_is_trainable(self):
#    return True
#
# def IdentityNode_train(self, x):
#    self.output_dim = x.shape[1]
#    
# mdp.nodes.IdentityNode.is_trainable = IdentityNode_is_trainable
# mdp.nodes.IdentityNode._train = IdentityNode_train

# PATCH for layer.py
patch_layer = True
if patch_layer:
    def Layer_new__init__(self, nodes, dtype=None, homogeneous=False):
        """Setup the layer with the given list of nodes.
        
        The input and output dimensions for the nodes must be already set 
        (the output dimensions for simplicity reasons). The training phases for 
        the nodes are allowed to differ.
        
        Keyword arguments:
        nodes -- List of the nodes to be used.
        """
        self.nodes = nodes
        # WARNING
        self.homogeneous = homogeneous
        # check nodes properties and get the dtype
        dtype = self._check_props(dtype)
        # calculate the the dimensions
        self.node_input_dims = numx.zeros(len(self.nodes))
        # WARNING: Difference between "==" and "is"???
        if self.homogeneous:
            input_dim = None
            for index, node in enumerate(nodes):
                self.node_input_dims[index] = None
        else:
            input_dim = 0
            for index, node in enumerate(nodes):
                input_dim += node.input_dim
                self.node_input_dims[index] = node.input_dim

        output_dim = self._get_output_dim_from_nodes()

        # set layer state
        nodes_is_training = [node.is_training() for node in nodes]
        if mdp.numx.any(nodes_is_training):
            self._is_trainable = True
            self._training = True
        else:
            self._is_trainable = False
            self._training = False

        super(mdp.hinet.Layer, self).__init__(input_dim=input_dim,
                                              output_dim=output_dim,
                                              dtype=dtype)


    def Layer_new_check_props(self, dtype=None):
        """Check the compatibility of the properties of the internal nodes.
        
        Return the found dtype and check the dimensions.
        
        dtype -- The specified layer dtype.
        """
        dtype_list = []  # the dtypes for all the nodes
        for i, node in enumerate(self.nodes):
            # input_dim for each node must be set
            # WARNING!!!
            if self.homogeneous is False:
                if node.input_dim is None:
                    err = ("input_dim must be set for every node. " +
                           "Node #%d (%s) does not comply." % (i, node))
                    raise mdp.NodeException(err)

            if node.dtype is not None:
                dtype_list.append(node.dtype)
        # check that the dtype is None or the same for every node
        nodes_dtype = None
        nodes_dtypes = set(dtype_list)
        nodes_dtypes.discard(None)
        if len(nodes_dtypes) > 1:
            err = ("All nodes must have the same dtype (found: %s)." %
                   nodes_dtypes)
            raise mdp.NodeException(err)
        elif len(nodes_dtypes) == 1:
            nodes_dtype = list(nodes_dtypes)[0]
        else:
            nodes_dtype = None
        #            er = "Error, no dtypes found!!!"
        #            raise Exception(er)

        # check that the nodes dtype matches the specified dtype
        if nodes_dtype and dtype:
            if not numx.dtype(nodes_dtype) == numx.dtype(dtype):
                err = ("Cannot set dtype to %s: " %
                       numx.dtype(nodes_dtype).name +
                       "an internal node requires %s" % numx.dtype(dtype).name)
                raise mdp.NodeException(err)
        elif nodes_dtype and dtype is None:
            dtype = nodes_dtype
        return dtype


    def Layer_new_train(self, x, scheduler=None, n_parallel=0, immediate_stop_training=False, *args, **kwargs):
        """Perform single training step by training the internal nodes."""
        print("memory efficient layer training that supports a scheduler")
        if self.homogeneous is True:
            layer_input_dim = x.shape[1]
            self.set_input_dim(layer_input_dim)
            num_nodes = len(self.nodes)
            print("Training homogeneous layer with input_dim %d and %d nodes" % (layer_input_dim, num_nodes))
            for node in self.nodes:
                node.set_input_dim(layer_input_dim // num_nodes)
            input_dim = 0
            for index, node in enumerate(self.nodes):
                input_dim += node.input_dim
                self.node_input_dims[index] = node.input_dim
            #           print "input dim is: %d, should be %d"%(input_dim, self.input_dim)

        stop_index = 0
        for node in self.nodes:
            start_index = stop_index
            stop_index += node.input_dim
            #           print "stop_index = ", stop_index
            if node.is_training():
                #if isinstance(node, (mdp.nodes.SFANode, mdp.nodes.PCANode, mdp.nodes.WhiteningNode,
                #                     mdp.hinet.CloneLayer, mdp.hinet.Layer)) and node.input_dim >= 45:
                #    print("Attempting node parallel training in Layer...")
                #    node.train(x[:, start_index: stop_index], scheduler=scheduler, n_parallel=n_parallel, *args,
                #               **kwargs)
                #else:
                node.train(x[:, start_index: stop_index], *args, **kwargs)
                if node.is_training() and immediate_stop_training:
                    node.stop_training()


    def Layer_new_train_params(self, x, immediate_stop_training=False, params=None, verbose=False):
        """Perform single training step by training the internal nodes."""
        if self.homogeneous:
            layer_input_dim = x.shape[1]
            self.set_input_dim(layer_input_dim)
            num_nodes = len(self.nodes)
            print("Training homogeneous layer with input_dim %d and %d nodes" % (layer_input_dim, num_nodes))
            for node in self.nodes:
                node.set_input_dim(layer_input_dim // num_nodes)
            input_dim = 0
            for index, node in enumerate(self.nodes):
                input_dim += node.input_dim
                self.node_input_dims[index] = node.input_dim
            #           print "input dim is: %d, should be %d"%(input_dim, self.input_dim)

        stop_index = 0
        for node in self.nodes:
            start_index = stop_index
            stop_index += node.input_dim
            #           print "stop_index = ", stop_index
            if node.is_training():
                if verbose:
                    print("Layer_new_train_params. params=", params)
                    print("Here computation is fine!!! start_index = ", start_index, "stop_index=", stop_index)
                node.train_params(x[:, start_index: stop_index], params)
                if node.is_training() and immediate_stop_training and not isinstance(self, mdp.hinet.CloneLayer):
                    node.stop_training()
                #                if isinstance(node, (mdp.nodes.SFANode, mdp.nodes.PCANode, mdp.nodes.WhiteningNode,
                # mdp.hinet.CloneLayer, mdp.hinet.Layer)) and node.input_dim >= 45:
                #                    print "Attempting node parallel training in Layer..."
                #                    node.train(x[:, start_index : stop_index], scheduler=scheduler,
                # n_parallel=n_parallel, *args, **kwargs)
                #                else:
                #                    node.train(x[:, start_index : stop_index], *args, **kwargs)
        if isinstance(self, mdp.hinet.CloneLayer) and immediate_stop_training:
            print("layer=", self, "type=", type(self), "layer.homogeneous=", self.homogeneous)
            self.nodes[0].stop_training()


    def Layer_new_pre_execution_checks(self, x):
        """Make sure that output_dim is set and then perform normal checks."""
        if self.output_dim is None:
            # first make sure that the output_dim is set for all nodes

            # Warning!!! add code to support homogeneous input sizes
            if self.homogeneous is True:
                layer_input_dim = x.shape[1]
                self.set_input_dim(layer_input_dim)
                num_nodes = len(self.nodes)

                if verbose:
                    print("Pre_Execution of homogeneous layer with",
                          "input_dim %d and %d nodes" % (layer_input_dim, num_nodes))
                for node in self.nodes:
                    node.set_input_dim(layer_input_dim // num_nodes)
                input_dim = 0
                for index, node in enumerate(self.nodes):
                    input_dim += node.input_dim
                    self.node_input_dims[index] = node.input_dim
                    # print "input dim is: %d, should be %d"%(input_dim, self.input_dim)

            in_stop = 0
            for node in self.nodes:
                in_start = in_stop
                in_stop += node.input_dim
                node._pre_execution_checks(x[:, in_start:in_stop])
            self.output_dim = self._get_output_dim_from_nodes()
            if self.output_dim is None:
                err = "output_dim must be set at this point for all nodes"
                raise mdp.NodeException(err)
        super(mdp.hinet.Layer, self)._pre_execution_checks(x)


    def CloneLayer_new__init__(self, node, n_nodes=1, dtype=None):
        """Setup the layer with the given list of nodes.
        
        Keyword arguments:
        node -- Node to be cloned.
        n_nodes -- Number of repetitions/clones of the given node.
        """
        # WARNING!!!
        super(mdp.hinet.CloneLayer, self).__init__((node,) * n_nodes, dtype=dtype, homogeneous=True)
        self.node = node  # attribute for convenience


    # This is the current MDP _execute method of Layer (CloneLayer is derived from it)

    def CloneLayer_new__execute(self, x, *args, **kwargs):
        n_samples = x.shape[0]
        x = x.reshape(n_samples * x.shape[1] / self.node.input_dim, self.node.input_dim)
        y = self.node.execute(x)
        return y.reshape(n_samples, self.output_dim)

    mdp.hinet.Layer.__init__ = Layer_new__init__
    mdp.hinet.Layer._check_props = Layer_new_check_props

    # ATTENTION, modification for backwards compatibility!!!!!!!
    mdp.hinet.Layer._train = Layer_new_train_params
    # ATTENTION, modification for backwards compatibility!!!!!!!
    # mdp.hinet.Layer._train = Layer_new_train

    # mdp.hinet.Layer.train_params = Layer_new_train_params
    # mdp.hinet.Layer.train_scheduler = Layer_new_train
    mdp.hinet.Layer._pre_execution_checks = Layer_new_pre_execution_checks
    mdp.hinet.CloneLayer.__init__ = CloneLayer_new__init__
    mdp.hinet.CloneLayer._execute = mdp.hinet.Layer._execute
    # print "mdp.Layer was patched"


def HiNetParallelTranslator_translate_layer(self, layer):
    """Replace a Layer with its parallel version."""
    parallel_nodes = super(mdp.parallel.makeparallel.HiNetParallelTranslator,
                           self)._translate_layer(layer)
    # Warning, it was: return parallelhinet.ParallelLayer(parallel_nodes)
    return mdp.parallel.ParallelLayer(parallel_nodes, homogeneous=layer.homogeneous)


# UPDATE WARNING: Is this still needed?
# mdp.parallel.makeparallel.HiNetParallelTranslator._translate_layer = HiNetParallelTranslator_translate_layer

# LINEAR_FLOW FUNCTIONS
# Code courtesy of Alberto Escalante
# improves the training time in a linear factor on the number of nodes
# but is less general than the usual procedure
# Now supporting list based training data for different layers
# not needed now: signal_read_enabled=False, signal_write_enabled=False
patch_flow = True
if patch_flow:
    def flow_special_train_cache_scheduler(self, data, verbose=None, benchmark=None, node_cache_read=None,
                                           signal_cache_read=None, node_cache_write=None, signal_cache_write=None,
                                           scheduler=None, n_parallel=None):
        # train each Node successively
        min_input_size_for_parallel = 45


        if verbose is None:
            verbose = self.verbose

        if verbose:
            print(data.__class__, data.dtype, data.shape)
            print(data)

        data_loaded = True
        for i in range(len(self.flow)):
            trained_node_in_cache = False
            exec_signal_in_cache = False

            if benchmark is not None:
                ttrain0 = time.time()
            if verbose:
                print("*****************************************************************")
                print("Training node #%d (%s)..." % (i, str(self.flow[i])))
                if isinstance(self.flow[i], mdp.hinet.Layer):
                    print("of [%s]" % str(self.flow[i].nodes[0]))
                elif isinstance(self.flow[i], mdp.hinet.CloneLayer):
                    print("of cloned [%s]" % str(self.flow[i].nodes[0]))

            hash_verbose = True  # and False
            if str(self.flow[i]) == "CloneLayer":
                if str(self.flow[i].nodes[0]) == "RandomPermutationNode" and verbose:
                    print("RandomPermutationNode Found")
                    # hash_verbose=False

            if node_cache_write or node_cache_read or signal_cache_write or signal_cache_read:
                untrained_node_hash = misc.hash_object(self.flow[i], verbose=hash_verbose).hexdigest()
                if verbose:
                    print("untrained_node_hash[%d]=" % i, untrained_node_hash)
                node_ndim = str(data.shape[1])
                data_in_hash = misc.hash_object(data).hexdigest()
                if verbose:
                    print("data_in_hash[%d]=" % i, data_in_hash)

            if self.flow[i].is_trainable():
                # look for trained node in cache
                if node_cache_read:
                    node_base_filename = "node_%s_%s_%s" % (node_ndim, untrained_node_hash, data_in_hash)
                    if verbose:
                        print("Searching for Trained Node:", node_base_filename)
                    if node_cache_read.is_file_in_filesystem(base_filename=node_base_filename):
                        if verbose:
                            print("Trained node FOUND in cache...")
                        self.flow[i] = node_cache_read.load_obj_from_cache(base_filename=node_base_filename)
                        trained_node_in_cache = True
                    elif verbose:
                        print("Trained node NOT found in cache...")

                if not trained_node_in_cache:
                    # Not in cache, then train the node
                    if isinstance(self.flow[i], (mdp.hinet.CloneLayer, mdp.hinet.Layer)):
                        # print "Here it should be doing parallel training 1!!!"
                        # WARNING: REMOVED scheduler & n_parallel
                        # self.flow[i].train(data, scheduler=scheduler, n_parallel=n_parallel)
                        self.flow[i].train(data, scheduler=scheduler, n_parallel=n_parallel)
                    # elif isinstance(self.flow[i], (mdp.nodes.SFANode,
                    #                                mdp.nodes.PCANode, mdp.nodes.WhiteningNode)) and \
                    #                 self.flow[i].input_dim >= min_input_size_for_parallel:
                    #     # print "Here it should be doing parallel training 2!!!"
                    #     # WARNING: REMOVED scheduler & n_parallel
                    #     self.flow[i].train(data, scheduler=scheduler, n_parallel=n_parallel)
                    else:
                        if verbose:
                            print("Input_dim was: ", self.flow[i].input_dim,
                                  "or unknown parallel method, thus I didn't go parallel")
                        self.flow[i].train(data)
                    self.flow[i].stop_training()
                    if isinstance(self.flow[i], mdp.nodes.SFANode) and verbose:
                        print("trained SFANode.d is", self.flow[i].d)
            ttrain1 = time.time()

            if node_cache_write or node_cache_read or signal_cache_write or signal_cache_read:
                trained_node_hash = misc.hash_object(self.flow[i], verbose=hash_verbose).hexdigest()
                if verbose:
                    print("trained_node_hash[%d]=" % i, trained_node_hash)

            if verbose:
                print("++++++++++++++++++++++++++++++++++++ Executing...")
            if signal_cache_read:
                signal_base_filename = "signal_%s_%s_%s" % (node_ndim, data_in_hash, trained_node_hash)
                if verbose:
                    print("Searching for Executed Signal: ", signal_base_filename)
                if signal_cache_read.is_splitted_file_in_filesystem(base_filename=signal_base_filename):
                    if verbose:
                        print("Executed signal FOUND in cache...")
                    data = signal_cache_read.load_array_from_cache(base_filename=signal_base_filename, verbose=True)
                    exec_signal_in_cache = True
                elif verbose:
                    print("Executed signal NOT found in cache...")

            if verbose:
                print(data.__class__, data.dtype, data.shape)
                print("supported types:", self.flow[i].get_supported_dtypes())
                print(data)

            if not exec_signal_in_cache:
                data = self.flow[i].execute(data)

            ttrain2 = time.time()
            if verbose:
                print("Training finished in %0.3f s, execution in %0.3f s" % (ttrain1 - ttrain0, ttrain2 - ttrain1))
            if benchmark is not None:
                benchmark.append(("Train node #%d (%s)" % (i, str(self.flow[i])), ttrain1 - ttrain0))
                benchmark.append(("Execute node #%d (%s)" % (i, str(self.flow[i])), ttrain2 - ttrain1))

            # Add to Cache Memory: Executed Signal
            if node_cache_write and not trained_node_in_cache and self.flow[i].is_trainable():
                if verbose:
                    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Caching Trained Node...")
                node_base_filename = "node_%s_%s_%s" % (node_ndim, untrained_node_hash, data_in_hash)
                node_cache_write.update_cache(self.flow[i], base_filename=node_base_filename, overwrite=True,
                                              verbose=True)

            if signal_cache_write and not exec_signal_in_cache:
                if verbose:
                    print("####################################### Caching Executed Signal...")
                data_ndim = node_ndim
                data_base_filename = "signal_%s_%s_%s" % (data_ndim, data_in_hash, trained_node_hash)
                signal_cache_write.update_cache(data, base_filename=data_base_filename, overwrite=True, verbose=True)
        return data


    # The functions generate the training data when executed, while parameters are used for training the
    # corresponding node
    # Function that given a training data description (func and param sets) extracts the relevant function and
    # parameters vector for the given node
    # The catch is that funcs_sets and param_sets are (usually) bidimensional arrays.
    # The first dimension is used for the particular node
    # The second dimension is used in case there is more than one training data set for the node, and mmight be None,
    # which means that the data/parameters from the previous node is used
    # The output is the data functions and parameters needed to train a particular node
    # Add logic for data_params
    def extract_node_funcs(funcs_sets, param_sets, nodenr, verbose=None):
        # print "funcs_sets is:", funcs_sets
        # print "param_sets is:", param_sets
        if isinstance(funcs_sets, list):
            # Find index of last data_vec closer to the requested node
            if nodenr >= len(funcs_sets):
                index = len(funcs_sets) - 1
            else:
                index = nodenr

            # Find index of last data_vec with not None data
            while funcs_sets[index] is None and index > 0:
                index -= 1

            node_funcs = funcs_sets[index]
            if param_sets is None:
                node_params = [None] * len(funcs_sets[index])
                for i in range(len(node_params)):
                    node_params[i] = {}
            else:
                if verbose:
                    print("param_sets =", param_sets)
                node_params = param_sets[index]

            # # TODO: More robust compatibility function required
            # # if len(node_params) != len(node_funcs):
            # #    er = "node_funcs and node_params are not compatible: "+str(node_funcs)+str(node_params)
            # #    raise Exception(er)
            if verbose:
                print("node_funcs and node_params:", node_funcs, node_params)
            return node_funcs, node_params
        else:  # Not a data set, use data itself as training data
            if param_sets is None:
                param_sets = {}
            if verbose:
                print("param_sets =", param_sets)
            return funcs_sets, param_sets

    # If the input is a list of functions, execute them to generate the data_vect, otherwise use node_funcs directly as
    # array data
    def extract_data_from_funcs(node_funcs, verbose=None):
        if verbose:
            print("node_funcs is:", node_funcs)
        if isinstance(node_funcs, list):
            node_data = []
            for func in node_funcs:
                if inspect.isfunction(func):
                    node_data.append(func())
                else:
                    node_data.append(func)
            return node_data
        elif inspect.isfunction(node_funcs):
            return node_funcs()
        else:
            return node_funcs

    # Tells the dimensionality of the data (independent of number of samples or number of data arrays)
    def data_vec_ndim(data_vec):
        if isinstance(data_vec, list):
            return data_vec[0].shape[1]
        else:
            return data_vec.shape[1]

    # As the previous train method, however here shape variable data is allowed
    # Perhaps the data should be loaded dynamically???
    # TODO: find nicer name!
    # In theory, there should  be a data_in_hash for data & another for (data, params), however we only use the last one
    def flow_special_train_cache_scheduler_sets(self, funcs_sets, params_sets=None, verbose=None, very_verbose=False,
                                                benchmark=None, node_cache_read=None, signal_cache_read=None,
                                                node_cache_write=None, signal_cache_write=None, scheduler=None,
                                                n_parallel=None, memory_save=False, immediate_stop_training=False):
        if verbose is None:
            verbose = self.verbose
        # train each Node successively
        # Set smalles dimensionality for which parallel training is worth doing
        min_input_size_for_parallel = 45

        # print data.__class__, data.dtype, data.shape
        # print data
        # print data_params

        # if memory_save:
        #    node_cache_read = None
        #    signal_cache_read = None
        #    node_cache_write = None
        #    signal_cache_write = None
        # indicates whether node_data and node_params are valid
        node_funcs = node_data = node_params = None
        # data_loaded = False
        for i in range(len(self.flow)):
            # indicates whether the node or the exec_signal were loaded from cache
            trained_node_in_cache = False
            exec_signal_in_cache = False

            # Extract data and data_params, integrity check
            # if not data_loaded:
            new_node_funcs, new_node_params = extract_node_funcs(funcs_sets, params_sets, nodenr=i)
            if verbose:
                print("new_node_funcs = ", new_node_funcs)
            # quit()"list_train_params" in dir(self)
            execute_node_data = False
            if isinstance(new_node_funcs, numpy.ndarray):
                # WARNING, this creates a comparisson array!!!!! there should be a more efficient way to compara arrays!
                # HINT: first compare using "x is x", otherwise compare element by element
                comp = (node_funcs != new_node_funcs)
                if isinstance(comp, bool) and (node_funcs != new_node_funcs):
                    execute_node_data = True
                elif isinstance(comp, numpy.ndarray) and (node_funcs != new_node_funcs).any():
                    execute_node_data = True
            else:
                if not (node_funcs == new_node_funcs):  # New data loading needed
                    execute_node_data = True
            # WARNING! am I duplicating the training data for the first node???
            # data should be extracted from new_node_funcs and propagated just before the current node
            if execute_node_data:
                node_data = extract_data_from_funcs(new_node_funcs)
                if verbose:
                    print("node_data is:", node_data)
                data_vec = self.execute_data_vec(node_data, nodenr=i - 1)
                # else:
            # data_vec already contains valid data

            node_funcs = new_node_funcs
            node_params = new_node_params

            if self.flow[i].input_dim is not None and self.flow[i].input_dim >= min_input_size_for_parallel:
                if isinstance(data_vec, list):
                    for j in range(len(data_vec)):
                        new_node_params[j]["scheduler"] = scheduler
                        new_node_params[j]["n_parallel"] = n_parallel
                else:
                    new_node_params["scheduler"] = scheduler
                    new_node_params["n_parallel"] = n_parallel

            # if benchmark is not None:
            ttrain0 = time.time()
            if verbose:
                print("*****************************************************************")
                print("Training node #%d (%s)..." % (i, str(self.flow[i])))
                if isinstance(self.flow[i], mdp.hinet.Layer):
                    print("of [%s]" % str(self.flow[i].nodes[0]))
                elif isinstance(self.flow[i], mdp.hinet.CloneLayer):
                    print("of cloned [%s]" % str(self.flow[i].nodes[0]))

            hash_verbose = False
            if str(self.flow[i]) == "CloneLayer":
                if str(self.flow[i].nodes[0]) == "RandomPermutationNode" and verbose:
                    print("RandomPermutationNode Found")
                    hash_verbose = False

            # Compute hash of Node and Training Data if needed
            # Where to put/hash data_parameters?????? in data "of_course"!
            # Notice, here Data should be taken from appropriate component, and also data_params
            effective_node_params = extract_params_relevant_for_node_train(self.flow[i], node_params)
            if node_cache_write or node_cache_read or signal_cache_write or signal_cache_read:
                untrained_node_hash = misc.hash_object(self.flow[i], verbose=hash_verbose).hexdigest()
                if verbose:
                    print("untrained_node_hash[%d]=" % i, untrained_node_hash)
                node_ndim = str(data_vec_ndim(data_vec))
                # hash data and node parameters for handling the data!
                if verbose:  # and False:
                    print("effective_node_params to be hashed: ", effective_node_params)
                data_in_hash = misc.hash_object((data_vec, effective_node_params)).hexdigest()
                if verbose:
                    print("data_in_hash[%d]=" % i, data_in_hash)

            if self.flow[i].is_trainable():
                # look for trained node in cache
                if node_cache_read:
                    node_base_filename = "node_%s_%s_%s" % (node_ndim, untrained_node_hash, data_in_hash)
                    if verbose:
                        print("Searching for Trained Node:", node_base_filename)
                    if node_cache_read.is_file_in_filesystem(base_filename=node_base_filename):
                        if verbose:
                            print("Trained node FOUND in cache...")
                        self.flow[i] = node_cache_read.load_obj_from_cache(base_filename=node_base_filename)
                        trained_node_in_cache = True
                    elif verbose:
                        print("Trained node NOT found in cache...")
                        # else:
                        # er = "What happened here???"
                        # raise Exception(er)

                # If trained node not found in cache, then train!
                # Here, however, parse data and data_params appropriately!!!!!
                if not trained_node_in_cache:
                    # Not in cache, then train the node
                    if isinstance(self.flow[i], (mdp.hinet.CloneLayer, mdp.hinet.Layer)):
                        # print("First step")
                        if isinstance(data_vec, list):
                            #  print("First step 2")
                            for j, data in enumerate(data_vec):
                                if very_verbose:
                                    print("j=", j)
                                # Here some logic is expected (list of train parameters on each node???)
                                self.flow[i].train(data, params=effective_node_params[j],
                                                   immediate_stop_training=immediate_stop_training)
                        else:
                            if very_verbose:
                                print("PointA")
                            self.flow[i].train(data_vec, params=effective_node_params,
                                               immediate_stop_training=immediate_stop_training)

                    # elif isinstance(self.flow[i], (mdp.nodes.SFANode, mdp.nodes.PCANode, mdp.nodes.WhiteningNode)):
                    #     # print("Second Step")
                    #     if isinstance(data_vec, list):
                    #         for j, data in enumerate(data_vec):
                    #             if verbose and very_verbose:  #
                    #                 print("Parameters used for training node (L)=", effective_node_params)
                    #                 print("Pre self.flow[i].output_dim=", self.flow[i].output_dim)
                    #             self.flow[i].train_params(data, params=effective_node_params[j])
                    #             if verbose:
                    #                 print("Post self.flow[i].output_dim=", self.flow[i].output_dim)
                    #     else:
                    #         if verbose and very_verbose:
                    #             print("Parameters used for training node=", effective_node_params)
                    #         self.flow[i].train_params(data_vec, params=effective_node_params)
                    else:  # Other node which does not have parameters nor parallelization
                        # print "Input_dim ", self.flow[i].input_dim, "<", min_input_size_for_parallel, ",
                        # or unknown parallel method, thus I didn't go parallel"
                        if isinstance(data_vec, list):
                            for j, data in enumerate(data_vec):
                                self.flow[i].train_params(data, params=effective_node_params[j])
                        else:
                            self.flow[i].train_params(data_vec, params=effective_node_params)
                    print("Finishing training of node %d:" % i, self.flow[i])
                    if self.flow[i].is_training():
                        self.flow[i].stop_training()
                    if verbose:
                        print("Post2 self.flow[%d].output_dim=" % i, self.flow[i].output_dim)
                    if isinstance(self.flow[i], mdp.nodes.SFANode) and verbose:
                        print("SFANode.d is ", self.flow[i].d)

            ttrain1 = time.time()

            # is hash of trained node needed??? of course, this is redundant if no training
            if node_cache_write or node_cache_read or signal_cache_write or signal_cache_read:
                trained_node_hash = misc.hash_object(self.flow[i], verbose=hash_verbose).hexdigest()
                if verbose:
                    print("trained_node_hash[%d]=" % i, trained_node_hash)

            if verbose:
                print("++++++++++++++++++++++++++++++++++++ Executing...")
            # Look for excecuted signal in cache
            if signal_cache_read:
                signal_base_filename = "signal_%s_%s_%s" % (node_ndim, data_in_hash, trained_node_hash)
                if verbose:
                    print("Searching for Executed Signal: ", signal_base_filename)
                if signal_cache_read.is_splitted_file_in_filesystem(base_filename=signal_base_filename):
                    if verbose:
                        print("Executed signal FOUND in cache...")
                    data_vec = signal_cache_read.load_array_from_cache(base_filename=signal_base_filename, verbose=True)
                    exec_signal_in_cache = True
                elif verbose:
                    print("Executed signal NOT found in cache...")

            # print data.__class__, data.dtype, data.shape
            # print "supported types:", self.flow[i].get_supported_dtypes()
            # print data

            # However, excecute should preserve shape here!
            if not exec_signal_in_cache:
                data_vec = self.flow[i].execute_data_vec(data_vec)
                if verbose and very_verbose:
                    print("PointB self.flow[%d].output_dim=" % i, self.flow[i].output_dim)
                    print("data_vec:", data_vec)
                    print("len(data_vec):", len(data_vec))
                    print("data_vec[0].shape:", data_vec[0].shape)

            ttrain2 = time.time()
            if verbose:
                print("Training finished in %0.3f s, execution in %0.3f s" % ((ttrain1 - ttrain0), (ttrain2 - ttrain1)))
            if benchmark is not None:
                benchmark.append(("Train node #%d (%s)" % (i, str(self.flow[i])), ttrain1 - ttrain0))
                benchmark.append(("Execute node #%d (%s)" % (i, str(self.flow[i])), ttrain2 - ttrain1))

            # Add to Cache Memory: Trained Node
            if node_cache_write and (not trained_node_in_cache) and self.flow[i].is_trainable():
                if verbose:
                    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Caching Trained Node...")
                node_base_filename = "node_%s_%s_%s" % (node_ndim, untrained_node_hash, data_in_hash)
                node_cache_write.update_cache(self.flow[i], base_filename=node_base_filename, overwrite=True,
                                              verbose=True)

            # Add to Cache Memory: Executed Signal
            if signal_cache_write and (not exec_signal_in_cache):
                # T: Perhaps data should be written based on mdp.array, not on whole data.
                if verbose:
                    print("####################################### Caching Executed Signal...")
                data_ndim = node_ndim
                data_base_filename = "signal_%s_%s_%s" % (data_ndim, data_in_hash, trained_node_hash)
                signal_cache_write.update_cache(data_vec, base_filename=data_base_filename, overwrite=True,
                                                verbose=True)

        if isinstance(data_vec, list):
            return numpy.concatenate(data_vec, axis=0)
        else:
            return data_vec

    # Supports mainly single array data or merges iterator data
    def flow__execute_seq(self, x, nodenr=None, benchmark=None):
        # Filters input data 'x' through the nodes 0..'nodenr' included
        flow = self.flow
        if nodenr is None:
            nodenr = len(flow) - 1

        if benchmark is not None:
            benchmark.update_start_time()

        for i in range(nodenr + 1):
            try:
                x = flow[i].execute(x)
            except Exception as e:
                self._propagate_exception(e, i)
            if benchmark is not None:
                benchmark.add_task_from_previous_time("Execution of node %d" % i)
                # t1 = time.time()
                # benchmark.append(("Node %d (%s)Excecution"%(i,str(flow[i])), t1-t0))
                # t0 = t1
        return x

    # Supports single array data but also iterator
    # However result is concatenated! Not PowerTraining Compatible???
    # Thus this function is usually called for each single chunk
    def flow_execute(self, iterable, nodenr=None, benchmark=None, verbose=None):
        """Process the data through all nodes in the flow.
            
        'iterable' is an iterable or iterator (note that a list is also an
        iterable), which returns data arrays that are used as input to the flow.
        Alternatively, one can specify one data array as input.
            
        If 'nodenr' is specified, the flow is executed only up to
        node nr. 'nodenr'. This is equivalent to 'flow[:nodenr+1](iterable)'.
        """
        # Strange bug when nodenr is None, it seems like None<0 is True!!!
        if nodenr is not None and nodenr < 0:
            return iterable

        if isinstance(iterable, numx.ndarray):
            return self._execute_seq(iterable, nodenr, benchmark)
        res = []
        empty_iterator = True
        for x in iterable:
            empty_iterator = False
            res.append(self._execute_seq(x, nodenr))
        if empty_iterator:
            errstr = "The execute data iterator is empty."
            #        raise mdp.MDPException(errstr)
            raise mdp.linear_flows.FlowException(errstr)
        res = numx.concatenate(res)
        if verbose:
            print("result shape is:", res.shape)
        return numx.concatenate(res)

    # Supports single array data but also iterator/list
    # Small variation over flow_execute: Result has same shape
    def flow_execute_data_vec(self, iterable, nodenr=None, benchmark=None):
        """Process the data through all nodes in the flow.
        keeping the structure
        If 'nodenr' is specified, the flow is executed only up to
        node nr. 'nodenr'. This is equivalent to 'flow[:nodenr+1](iterable)'.
        """
        if isinstance(iterable, numx.ndarray):
            return self._execute_seq(iterable, nodenr, benchmark)
        if nodenr == -1:
            return iterable
        res = []
        empty_iterator = True
        for x in iterable:
            empty_iterator = False
            res.append(self._execute_seq(x, nodenr))
        if empty_iterator:
            errstr = "The execute data iterator is empty."
            #        raise mdp.MDPException(errstr)
            raise mdp.linear_flows.FlowException(errstr)
        return res


    mdp.Flow.special_train_cache_scheduler = flow_special_train_cache_scheduler
    mdp.Flow.special_train_cache_scheduler_sets = flow_special_train_cache_scheduler_sets
    mdp.Flow.execute = flow_execute
    mdp.Flow.execute_data_vec = flow_execute_data_vec
    mdp.Flow._execute_seq = flow__execute_seq

numx_linalg = mdp.numx_linalg

# routines


def KNNClassifier_klabels(self, x):
    """Label the data by comparison with the reference points."""
    square_distances = (x * x).sum(1)[:, numx.newaxis] + (self.samples * self.samples).sum(1)
    square_distances -= 2 * numx.dot(x, self.samples.T)
    min_inds = square_distances.argsort()

    #    print "min_inds[:,0:self.k]", min_inds[:,0:self.k]
    min_inds_sel = min_inds[:, 0:self.k].astype(int)
    #    print "min_inds_sel", min_inds_sel
    my_ordered_labels = numpy.array(self.ordered_labels)
    klabels = my_ordered_labels[min_inds_sel]
    return klabels


def KNNClassifier_klabel_avg(self, x):
    """Label the data by comparison with the reference points."""
    square_distances = (x * x).sum(1)[:, numx.newaxis] + (self.samples * self.samples).sum(1)
    square_distances -= 2 * numx.dot(x, self.samples.T)
    min_inds = square_distances.argsort()

    #    print "min_inds[:,0:self.k]", min_inds[:,0:self.k]
    min_inds_sel = min_inds[:, 0:self.k].astype(int)
    #    print "min_inds_sel", min_inds_sel
    #    klabels = [self.ordered_labels[indices] for indices in min_inds[:,0:self.k]]
    my_ordered_labels = numpy.array(self.ordered_labels)
    klabels = my_ordered_labels[min_inds_sel]
    #    klabels = self.ordered_labels[min_inds_sel]
    #        win_inds = [numx.bincount(self.sample_label_indices[indices[0:self.k]]).
    #                   argmax(0) for indices in min_inds]
    #        labels = [self.ordered_labels[i] for i in win_inds]
    #    print "klabels", klabels
    return klabels.mean(axis=1)

mdp.nodes.KNNClassifier.klabel_avg = KNNClassifier_klabel_avg
mdp.nodes.KNNClassifier.klabels = KNNClassifier_klabels
