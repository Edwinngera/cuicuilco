from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import time
import os
import numpy as np
import scipy
import scipy.misc
from skopt import gp_minimize


def expansion_number_to_string(expansion):
    if expansion == 0:
        return "u08"
    elif expansion == 1:
        return "qt"
    elif expansion == 2:
        return "ct"
    elif expansion == 3:
        return "ch3s10qt"
    elif expansion == 4:
        return "ch3s15qt"
    elif expansion == 5:
        return "ch3s20qt"
    elif expansion == 6:
        return "ch3s25qt"
    elif expansion == 7:
        return "ch2s10qt"
    elif expansion == 8:
        return "ch2s15qt"
    elif expansion == 9:
        return "ch2s20qt"
    elif expansion == 10:
        return "ch2s25qt"
    elif expansion == 11:
        return "ch2s30qt"
    elif expansion == 12:
        return "ch2s35qt"
    elif expansion == 13:
        return "ch2s40qt"
    else:
        ex = "invalid expansion number: " + str(expansion)
        raise Exception(ex)


def string_to_expansion_number(string):
    if string == "u08Exp":
        return 0
    elif string == "qtExp":
        return 1
    elif string == "ctExp":
        return 2
    elif string == "ch3s10qtExp":
        return 3
    elif string == "ch3s15qtExp":
        return 4
    elif string == "ch3s20qtExp":
        return 5
    elif string == "ch3s25qtExp":
        return 6
    elif string == "ch2s10qtExp":
        return 7
    elif string == "ch2s15qtExp":
        return 8
    elif string == "ch2s20qtExp":
        return 9
    elif string == "ch2s25qtExp":
        return 10
    elif string == "ch2s30qtExp":
        return 11
    elif string == "ch2s35qtExp":
        return 12
    elif string == "ch2s40qtExp":
        return 13
    else:
        ex = "invalid expansion string: " + string
        raise Exception(ex)


def cuicuilco_f_CE_Gauss(arguments):
    return 1.0 - cuicuilco_evaluation(arguments, measure="CR_Gauss")


def cuicuilco_f_CE_Gauss_soft(arguments):
    return 1.0 - cuicuilco_evaluation(arguments, measure="CR_Gauss_soft")


def cuicuilco_f_CE_Gauss_mix(arguments):
    return 1.0 - cuicuilco_evaluation(arguments, measure="CR_Gauss_mix") 
 

def cuicuilco_evaluation(arguments, measure="CR_Gauss", verbose=False):
    (L0_pca_out_dim, L0_sfa_out_dim, L1H_sfa_out_dim, L1V_sfa_out_dim, L2H_sfa_out_dim, L2V_sfa_out_dim,
     L3H_sfa_out_dim, L3V_sfa_out_dim, L0_delta_threshold, L1H_delta_threshold, L1V_delta_threshold,
     L2H_delta_threshold, L2V_delta_threshold, L3H_delta_threshold, L3V_delta_threshold, L0_expansion,
     L1H_expansion, L1V_expansion, L2H_expansion, L2V_expansion, L3H_expansion, L3V_expansion,
     L4_degree_QT, L4_degree_CT) = arguments
 
    print("invoking cuicuilco_evaluation with arguments:", arguments)
    
    # Testing whether arguments are compatible
    incompatible = 0
    if L0_pca_out_dim + L0_delta_threshold < L0_sfa_out_dim:
        L0_delta_threshold = L0_sfa_out_dim - L0_pca_out_dim
        print("Attempting to solve incompatibility case 1", L0_pca_out_dim, L0_delta_threshold, L0_sfa_out_dim)
    if L0_delta_threshold < 1 or L0_delta_threshold > 20:
        incompatible = 21

    if 2 * L2H_sfa_out_dim + L2V_delta_threshold < L2V_sfa_out_dim:
        L2V_delta_threshold - 2 * L2H_sfa_out_dim
    if L2V_delta_threshold < 1 or L2V_delta_threshold > 20:
        incompatible = 22

    if L0_pca_out_dim + L0_delta_threshold < L0_sfa_out_dim:
        incompatible = 1
    elif 2 * L0_sfa_out_dim + L1H_delta_threshold < L1H_sfa_out_dim:  # This factor is 2 and not 3 due to overlap
        incompatible = 2
    elif 2 * L1H_sfa_out_dim + L1V_delta_threshold < L1V_sfa_out_dim:  # This factor is 2 and not 3 due to overlap
        incompatible = 3
    elif 2 * L1V_sfa_out_dim + L2H_delta_threshold < L2H_sfa_out_dim:
        incompatible = 4
    elif 2 * L2H_sfa_out_dim + L2V_delta_threshold < L2V_sfa_out_dim:
        incompatible = 5
    elif 2 * L2V_sfa_out_dim + L3H_delta_threshold < L3H_sfa_out_dim:
        incompatible = 6
    elif 2 * L3H_sfa_out_dim + L3V_delta_threshold < L3V_sfa_out_dim:
        incompatible = 7
    if L1H_delta_threshold >  (2 + 3) * L0_sfa_out_dim:
        incompatible = 8
    elif L1V_delta_threshold >  (2 + 3) * L1H_sfa_out_dim:
        incompatible = 9
    elif L2H_delta_threshold >  2 * L1V_sfa_out_dim: # the factor here should be actually 4, right?
        incompatible = 10
    elif L2V_delta_threshold >  2 * L2H_sfa_out_dim:
        incompatible = 11
    elif L3H_delta_threshold >  2 * L2V_sfa_out_dim:
        incompatible = 12
    elif L3V_delta_threshold >  2 * L3H_sfa_out_dim:
        incompatible = 13
    if L0_delta_threshold > L0_sfa_out_dim:
        incompatible = 14
    elif L1H_delta_threshold > L1H_sfa_out_dim:
        incompatible = 15
    elif L1V_delta_threshold > L1V_sfa_out_dim:
        incompatible = 16
    elif L2H_delta_threshold > L2H_sfa_out_dim:
        incompatible = 17
    elif L2V_delta_threshold > L2V_sfa_out_dim:
        incompatible = 18
    elif L3H_delta_threshold > L3H_sfa_out_dim:
        incompatible = 19
    elif L3V_delta_threshold > L3V_sfa_out_dim:
        incompatible = 20

    if incompatible:
        print("Configuration (before fixes):", arguments, " is incompatible (%d) and was skipped" % incompatible)
        return 0.0


    # Update arguments variable
    arguments = (L0_pca_out_dim, L0_sfa_out_dim, L1H_sfa_out_dim, L1V_sfa_out_dim, L2H_sfa_out_dim, L2V_sfa_out_dim,
     L3H_sfa_out_dim, L3V_sfa_out_dim, L0_delta_threshold, L1H_delta_threshold, L1V_delta_threshold,
     L2H_delta_threshold, L2V_delta_threshold, L3H_delta_threshold, L3V_delta_threshold, L0_expansion,
     L1H_expansion, L1V_expansion, L2H_expansion, L2V_expansion, L3H_expansion, L3V_expansion,
     L4_degree_QT, L4_degree_CT)
    print("Creating configuration file ")
    fd = open("MNISTNetwork_24x24_7L_Overlap_config.txt", "w")
    txt = ""
    for entry in arguments:
        txt += str(entry)+ " "
    fd.write(txt)
    fd.close()
    print("created configuration file with contents:", txt)

    cuicuilco_experiment_seeds = [112277, 112288]  # , 112277]
    metrics = []
    for cuicuilco_experiment_seed in cuicuilco_experiment_seeds:  #112233 #np.random.randint(2**25)  #     np.random.randn()
        os.putenv("CUICUILCO_EXPERIMENT_SEED", str(cuicuilco_experiment_seed))
        print("Setting CUICUILCO_EXPERIMENT_SEED: ", str(cuicuilco_experiment_seed))

        output_filename = "hyper_t/MNIST_24x24_7L_L0cloneL_%dPC_%dSF_%sExp_%dF_" + \
                          "L1cloneL_%dSF_%sExp_%dF_L2clone_%dSF_%sExp_%dF_L3cloneL_%dSF_%sExp_%dF_" + \
                          "L4cloneL_%dSF_%sExp_%dF_L5_%dSF_%sExp_%dF_L6_%dSF_%sExp_%dF_NoHead_QT%dAP_CT%dAP_seed%d.txt"
        output_filename = output_filename % (L0_pca_out_dim, L0_delta_threshold, expansion_number_to_string(L0_expansion), L0_sfa_out_dim,
                                L1H_delta_threshold, expansion_number_to_string(L1H_expansion), L1H_sfa_out_dim,
                                L1V_delta_threshold, expansion_number_to_string(L1V_expansion), L1V_sfa_out_dim,
                                L2H_delta_threshold, expansion_number_to_string(L2H_expansion), L2H_sfa_out_dim,
                                L2V_delta_threshold, expansion_number_to_string(L2V_expansion), L2V_sfa_out_dim,
                                L3H_delta_threshold, expansion_number_to_string(L3H_expansion), L3H_sfa_out_dim,
                                L3V_delta_threshold, expansion_number_to_string(L3V_expansion), L3V_sfa_out_dim,
                                L4_degree_QT, L4_degree_CT, cuicuilco_experiment_seed)
        if os.path.isfile(output_filename):
            print("file %s already exists, skipping its computation" % output_filename)
        else:
            command = "time nice -n 19 python -u -m cuicuilco.cuicuilco_run --EnableDisplay=0 --CacheAvailable=0 " + \
                  "--NetworkCacheReadDir=/local/tmp/escalafl/Alberto/SavedNetworks " + \
                  "--NetworkCacheWriteDir=/local/tmp/escalafl/Alberto/SavedNetworks " + \
                  "--NodeCacheReadDir=/local/tmp/escalafl/Alberto/SavedNodes " + \
                  "--NodeCacheWriteDir=/local/tmp/escalafl/Alberto/SavedNodes " + \
                  "--ClassifierCacheWriteDir=/local/tmp/escalafl/Alberto/SavedClassifiers " + \
                  "--SaveSubimagesTraining=0 --SaveAverageSubimageTraining=0 --NumFeaturesSup=9 " + \
                  "--SaveSorted_AE_GaussNewid=0 --SaveSortedIncorrectClassGaussNewid=0 " + \
                  "--ComputeSlowFeaturesNewidAcrossNet=0 --UseFilter=0 --EnableGC=1 --SFAGCReducedDim=0 --EnableKNN=0 " + \
                  "--kNN_k=3 --EnableNCC=0 --EnableSVM=0 --SVM_C=0.125 --SVM_gamma=1.0 --EnableLR=0 " + \
                  "--AskNetworkLoading=0 --LoadNetworkNumber=-1 --NParallel=2 --EnableScheduler=0 " + \
                  "--EstimateExplainedVarWithInverse=0 --EstimateExplainedVarWithKNN_k=0 " + \
                  "--EstimateExplainedVarWithKNNLinApp=0 --EstimateExplainedVarLinGlobal_N=0 --AddNormalizationNode=0 " + \
                  "--MakeLastPCANodeWhithening=0 --FeatureCutOffLevel=-1.0 --ExportDataToLibsvm=0 " + \
                  "--IntegerLabelEstimation=0 --MapDaysToYears=0 --CumulativeScores=0 --DatasetForDisplayNewid=0 " + \
                  "--GraphExactLabelLearning=0 --OutputInsteadOfSVM2=0 --NumberTargetLabels=0 --EnableSVR=0 " + \
                  "--SVR_gamma=0.85 --SVR_C=48.0 --SVR_epsilon=0.075 --SVRInsteadOfSVM2=1 --ObjectiveLabel=0 " + \
                  "--ExperimentalDataset=ParamsMNISTFunc --HierarchicalNetwork=MNISTNetwork_24x24_7L_Overlap_config " + \
                  "--SleepM=0 2>&1 > " + output_filename

            print("excecuting command: ", command)
            os.system(command)

        if verbose:
            print("extracting performance metric from resulting file")
        metric = extract_performance_metric_from_file(output_filename, measure=measure)
        metrics.append(metric)
    return np.array(metric).mean()


def extract_performance_metric_from_file(output_filename, measure = "CR_Gauss", verbose=False):
    command_extract = "cat %s | grep New | grep CR_G > del_tmp.txt" % output_filename
    os.system(command_extract)
    fd = open("del_tmp.txt", "r")
    metrics = fd.readline().split(" ")
    fd.close()
    if verbose:
        print("metrics: ", metrics)
    if len(metrics) > 10 and metrics[6] == "CR_Gauss":
        metric_CR_Gauss = float(metrics[7].strip(","))
        metric_CR_Gauss_soft = float(metrics[9].strip(","))
        if np.isnan(metric_CR_Gauss_soft):
            print("warning, nan metric was found and fixed as metric_CR_Gauss - 0.001")
            metric_CR_Gauss_soft = metric_CR_Gauss - 0.001
    else:
        print("unable to find metrics in file (defaulting to 0.95)")
        metric_CR_Gauss = 0.95
        metric_CR_Gauss_soft = 0.95  
    if measure == "CR_Gauss":
        metric = metric_CR_Gauss
    elif measure == "CR_Gauss_soft":
        metric = metric_CR_Gauss_soft
    elif measure == "CR_Gauss_mix":
        metric = 0.5 * (metric_CR_Gauss + metric_CR_Gauss_soft)
    else:
        er = "invalid measure: " +  str(measure)
        raise Exception(er)
    print("metric_CR_Gauss: ", metric_CR_Gauss, " metric_CR_Gauss_soft:", metric_CR_Gauss_soft)

    return metric


def load_saved_executions(measure="CR_Gauss", dimensions=None, verbose=False):
    path = "hyper_t"
    only_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    only_files = [f for f in only_files if f.startswith("MNIST_24x24_7L")]
    arguments_list = []
    results_list = []
    for f in only_files:
        print("filename %s was found" % f)
        # MNIST_24x24_7L_L0cloneL_16PC_1SF_qtExp_25F_L1cloneL_1SF_u08Exp_20F_L2clone_30SF_u08Exp_80F_L3cloneL_1SF_u08Exp_100F_L4cloneL_20F_u08Exp_120F_L5_20F_u08Exp_90SF_L6_20F_u08Exp_250SF_NoHead_QT90AP_CT25AP_seed13153651.txt
        vals = f.split("_")
        vals = [val.strip("PCFSseedQTA.txt") for val in vals]
        if verbose or True:
            print("vals=", vals)
        # quit()
        if len(vals) >= 35:
            L0_pca_out_dim = int(vals[4])
            L0_sfa_out_dim = int(vals[7])
            L1H_sfa_out_dim = int(vals[11])
            L1V_sfa_out_dim = int(vals[15]) 
            L2H_sfa_out_dim = int(vals[19])
            L2V_sfa_out_dim = int(vals[23])
            L3H_sfa_out_dim = int(vals[27])
            L3V_sfa_out_dim = int(vals[31])
            L0_delta_threshold = int(vals[5])
            L1H_delta_threshold = int(vals[9])
            L1V_delta_threshold = int(vals[13]) 
            L2H_delta_threshold = int(vals[17])
            L2V_delta_threshold = int(vals[21])
            L3H_delta_threshold = int(vals[25])
            L3V_delta_threshold = int(vals[29])
            L0_expansion = string_to_expansion_number(vals[6])
            L1H_expansion = string_to_expansion_number(vals[10])
            L1V_expansion = string_to_expansion_number(vals[14])
            L2H_expansion = string_to_expansion_number(vals[18])
            L2V_expansion = string_to_expansion_number(vals[22])
            L3H_expansion = string_to_expansion_number(vals[26])
            L3V_expansion = string_to_expansion_number(vals[30])
            L4_degree_QT = int(vals[33])
            L4_degree_CT = int(vals[34])
            seed = int(vals[35])
            arguments = [L0_pca_out_dim, L0_sfa_out_dim, L1H_sfa_out_dim, L1V_sfa_out_dim, L2H_sfa_out_dim, L2V_sfa_out_dim, L3H_sfa_out_dim, L3V_sfa_out_dim, L0_delta_threshold, L1H_delta_threshold, L1V_delta_threshold, L2H_delta_threshold, L2V_delta_threshold, L3H_delta_threshold, L3V_delta_threshold, L0_expansion, L1H_expansion, L1V_expansion, L2H_expansion, L2V_expansion, L3H_expansion, L3V_expansion, L4_degree_QT, L4_degree_CT]
            if verbose:
                print("parsed arguments:", arguments)

            metric = extract_performance_metric_from_file(os.path.join(path, f), measure)
            arguments_list.append(arguments)
            results_list.append(metric)            
        else:
            print("Error parging values", vals)
    if len(arguments_list) > 0:
        results_list = np.array(results_list)
        # arguments_list = np.array(arguments_list, dtype=int)
        ordering = np.argsort(results_list)[::-1]
        results_list = results_list[ordering]
        sorted_arguments_list = []
        for i in range(len(ordering)):
            sorted_arguments_list.append(arguments_list[ordering[i]])
        arguments_list = sorted_arguments_list
        print("ordered results_list: ", results_list)
        print("ordered arguments_list: ")
        for arguments in arguments_list:
            print(arguments)
        if dimensions is not None:
            validity_values = []             
            for i, arguments in enumerate(arguments_list):
                valid = True
                for j, dim in enumerate(dimensions):
                    if len(dim) == 2 and isinstance(dim, tuple):
                        if dim[0] > arguments[j] or dim[1] < arguments[j]:
                            valid = False
                    elif isinstance(dim, list):
                        if arguments[j] not in dim:
                            valid = False
       	        validity_values.append(valid)
            print("validity_values:", validity_values)
            filtered_arguments_list = []
            for i in range(len(validity_values)):
                if validity_values[i]:
                    filtered_arguments_list.append(arguments_list[i])
            arguments_list = filtered_arguments_list    
            results_list = results_list[validity_values]
    # if len(arguments_list) == 0:
    #     arguments_list = None
    #     results_list = None
    print("final ordered results_list: ", results_list)
    print("final ordered arguments_list: ")
    for arguments in arguments_list:
        print(arguments)
        # quit()
    if len(arguments_list) == 0:
        arguments_list = None
        results_list = None


    return arguments_list, results_list

def display_best_arguments(arguments_list, results_list):
    if arguments_list is None:
        print("arguments_list is None")
        return None, None

    arguments_results_dict = {}
    for i, arguments in enumerate(arguments_list):
        arg_tuple = tuple(arguments)
        if arg_tuple in arguments_results_dict:
            arguments_results_dict[arg_tuple].append(results_list[i])
        else:
            arguments_results_dict[arg_tuple] = [results_list[i]]
    # Average all entries with the same key
    averaged_arguments_list = []
    averaged_results_list = []
    results_stds = []
    results_lens = []
    for arg in arguments_results_dict.keys():
        averaged_arguments_list.append(arg)
        averaged_results_list.append(np.array(arguments_results_dict[arg]).mean())
        results_stds.append(np.array(arguments_results_dict[arg]).std())
        results_lens.append(len(arguments_results_dict[arg]))
        # print("std: ", np.array(arguments_results_dict[arg]).std(), " len:", len(arguments_results_dict[arg]))
    # print("averaged_arguments_list=", averaged_arguments_list)
    # print("averaged_results_list=", averaged_results_list)

    # sort
    averaged_results_list = np.array(averaged_results_list)
    results_stds = np.array(results_stds)
    results_lens = np.array(results_lens)
    ordering = np.argsort(averaged_results_list)[::-1]
    averaged_results_list = averaged_results_list[ordering]
    results_stds = results_stds[ordering]
    results_lens = results_lens[ordering]
    averaged_sorted_arguments_list = []
    for i in range(len(ordering)):
        averaged_sorted_arguments_list.append(averaged_arguments_list[ordering[i]])
    averaged_arguments_list = averaged_sorted_arguments_list
    print("averaged ordered results_list: ", averaged_results_list)
    print("results_stds: ", results_stds)
    print("results_lens: ", results_lens)
    print("averaged ordered arguments_list: ")
    for arguments in averaged_arguments_list:
	print("(", end="")
        for arg in arguments:
            print("%3d, "%arg, end="")
        print(")")
        #print(arguments)
    # quit()
    return averaged_arguments_list, averaged_results_list

def progress_callback(res):
    print("C", end="")


#def gp_minimize(func, dimensions, base_estimator=None, n_calls=100, n_random_starts=10, acq_func='gp_hedge',
#                acq_optimizer='auto', x0=None, y0=None, random_state=None, verbose=False, callback=None,
#                n_points=10000, n_restarts_optimizer=5, xi=0.01, kappa=1.96, noise='gaussian', n_jobs=1)

# 13 20 28 50 70 90 120 200 9 19 10 26 6 6 9 0 0 0 0 0 0 0 90 25
range_L0_pca_out_dim = [13]  # (12, 14)  # (10, 16) # 13
range_L0_sfa_out_dim = (15, 18)  # (15, 25) # [20] # (20, 21)
range_L1H_sfa_out_dim = [31, 34]  # (31, 34)  # (20, 36) # [28] # (28, 29)
range_L1V_sfa_out_dim = (55, 65) # [50] # (50, 51)
range_L2H_sfa_out_dim = (75, 95) # [70] # (70, 71)
range_L2V_sfa_out_dim = (73, 95) # [90] # (90, 91)
range_L3H_sfa_out_dim = (84, 102) # [120] # (120, 121)
range_L3V_sfa_out_dim = (139, 173) #[200] # (200, 201)
range_L0_delta_threshold = (10, 16)  # (1, 20) # [9] # #(9, 10) #
range_L1H_delta_threshold = (10, 15) # [19] # (19, 20)
range_L1V_delta_threshold = (10, 20) # [10] # (10, 11)
range_L2H_delta_threshold = (20, 29) # [26] # (26, 27)
range_L2V_delta_threshold = (2, 15) # [6] # (6, 7)
range_L3H_delta_threshold = (0, 9) # [6] # (6, 7)
range_L3V_delta_threshold = (0, 9)  # (3, 5) # [9] # (9, 10)
# WARNING two categories cannot be expressed as [n1, n2], instead use e.g., [n1, n1, n2]
#         otherwise interval (n1, n2) is assumed
range_L0_expansion = [0, 1] # [0] # (0, 1)
range_L1H_expansion = [0] # TRY ALSO 3 [0, 0, 3] # (0, 1)
range_L1V_expansion = [0, 3, 4] # (0, 1)
range_L2H_expansion = [0, ] # (0, 1)
range_L2V_expansion = [0, 0, 3] # (0, 1)
range_L3H_expansion = [0, 7, 8, 9, 10] # (0, 0)
range_L3V_expansion = [0, 7, 8, 9, 10, 11, 12, 13] # [0, 7, 8, 9] (0, 0)
range_L4_degree_QT = (60, 89) # [90] # (90, 90)
range_L4_degree_CT = (20, 21, 22, 23, 24) # [25] # (25, 25)
cuicuilco_dimensions = (range_L0_pca_out_dim, range_L0_sfa_out_dim, range_L1H_sfa_out_dim, range_L1V_sfa_out_dim, range_L2H_sfa_out_dim, range_L2V_sfa_out_dim, range_L3H_sfa_out_dim, range_L3V_sfa_out_dim, range_L0_delta_threshold, range_L1H_delta_threshold, range_L1V_delta_threshold, range_L2H_delta_threshold, range_L2V_delta_threshold, range_L3H_delta_threshold, range_L3V_delta_threshold, range_L0_expansion, range_L1H_expansion, range_L1V_expansion, range_L2H_expansion, range_L2V_expansion, range_L3H_expansion, range_L3V_expansion, range_L4_degree_QT, range_L4_degree_CT) # tuple or list? 

print("cuicuilco_dimensions:", cuicuilco_dimensions)

#TODO: load previously computed results from saved files

# np.random.seed(1234) # use a new random seed each time to allow combination of executions on different systems

argument_list, results_list = load_saved_executions(measure="CR_Gauss_mix", dimensions=cuicuilco_dimensions)
display_best_arguments(argument_list, results_list)
#argument_list = None
#results_list = None
#quit()

if results_list is not None:
    results_list = [1.0 - result for result in results_list]

print("cuicuilco_dimensions:", cuicuilco_dimensions)
t0 = time.time()
res = gp_minimize(func=cuicuilco_f_CE_Gauss_mix, dimensions=cuicuilco_dimensions, base_estimator=None, n_calls=40, n_random_starts=40,  # 20 10
                  acq_func='gp_hedge', acq_optimizer='auto', x0=argument_list, y0=results_list, random_state=None, verbose=False,
                  callback=progress_callback, n_points=100*10000, n_restarts_optimizer=5,   # n_points=10000
                  xi=0.01, kappa=1.96, noise='gaussian', n_jobs=1)
t1 = time.time()

print("res:", res)
print("Execution time: %0.3f s" % (t1 - t0))

