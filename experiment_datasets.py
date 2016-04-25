import SystemParameters
from SystemParameters import load_data_from_sSeq
import numpy
import scipy
import mdp
import sfa_libs 
import more_nodes
import more_nodes as he
import patch_mdp
import imageLoader
from nonlinear_expansion import *
import lattice
import PIL
from PIL import Image
import copy
import os
import string

DAYS_IN_A_YEAR = 365.242

experiment_seed = os.getenv("CUICUILCO_EXPERIMENT_SEED") #1112223339 #1112223339
if experiment_seed:
    experiment_seed = int(experiment_seed)
else:
    experiment_seed = 1112223334 #111222333
    ex = "CUICUILCO_EXPERIMENT_SEED unset"
    raise Exception(ex)
print "PosXseed. experiment_seed=", experiment_seed
numpy.random.seed(experiment_seed) #seed|-5789
print "experiment_seed=", experiment_seed




import os

on_lok21 = os.path.lexists("/local2/tmp/escalafl/")
on_zappa01 = os.path.lexists("/local/escalafl/on_zappa01")
on_lok09 = os.path.lexists("/local/escalafl/on_lok09/")
on_lok10 = os.path.lexists("/local/escalafl/on_lok10")
local_available = os.path.lexists("/local/escalafl/")
if on_lok21:
    user_base_dir = "/local2/tmp/escalafl/"
    frgc_normalized_base_dir = "/local2/tmp/escalafl/Alberto/FRGC_Normalized"
    frgc_noface_base_dir = "/local/escalafl/Alberto/FRGC_NoFace"
    alldb_noface_base_dir = "/local/escalafl/Alberto/AllDB_NoFace"
    frgc_eyeL_normalized_base_dir = "/local/escalafl/Alberto/FRGC_EyeL"
    print "Running on Lok21"
elif on_lok09 or on_lok10:
    user_base_dir = "/local/escalafl/"
    frgc_normalized_base_dir = "/local/escalafl/Alberto/FRGC_Normalized"
    frgc_noface_base_dir = "/local/escalafl/Alberto/FRGC_NoFace"
    alldb_noface_base_dir = "/local/escalafl/Alberto/AllDB_NoFace"
    alldbnormalized_base_dir = "/local/escalafl/Alberto/AllDBNormalized"    
    frgc_eyeL_normalized_base_dir = "/local/escalafl/Alberto/FRGC_EyeL"
    #age_eyes_normalized_base_dir =  "/local/escalafl/Alberto/MORPH_normalizedEyesZByAge"
    print "Running on Lok09 or Lok10"
elif local_available:
    user_base_dir = "/local/escalafl/"
    frgc_normalized_base_dir = "/local/escalafl/Alberto/FRGC_Normalized"
    frgc_noface_base_dir = "/local/escalafl/Alberto/FRGC_NoFace"
    alldb_noface_base_dir = "/local/escalafl/Alberto/AllDB_NoFace"
    alldbnormalized_base_dir = "/local/escalafl/Alberto/AllDBNormalized"
    frgc_eyeL_normalized_base_dir = "/local/escalafl/Alberto/FRGC_EyeL"
    #age_eyes_normalized_base_dir =  "/local/escalafl/Alberto/MORPH_normalizedEyesZByAge"
    print "Unknown host, but /local/escalafl available"
else:
    user_base_dir = "/local/tmp/escalafl/"
    frgc_normalized_base_dir ="/local/tmp/escalafl/Alberto/FRGC_Normalized"    
    frgc_noface_base_dir = "/local/escalafl/Alberto/FRGC_NoFace"
    alldb_noface_base_dir = "/local/escalafl/Alberto/AllDB_NoFace"
    alldbnormalized_base_dir = "/local/escalafl/Alberto/AllDBNormalized"
    frgc_eyeL_normalized_base_dir = "/local/escalafl/Alberto/FRGC_EyeL"
    print "Running on unknown host"
    quit()

def repeat_list_elements(lista, rep):
    return [element for it in range(rep) for element in lista]

print "******** Setting Training Information Parameters for Gender (simulated faces) **********"
def iSeqCreateGender(first_id = 0, num_ids = 25, user_base_dir=user_base_dir, data_dir="Alberto/RenderingsGender60x200", gender_continuous=True, seed=None):
    if seed >= 0 or seed is None:
        numpy.random.seed(seed)
        print "Gender. Using seed", seed

    print "******** Setting Training Information Parameters for Gender **********"
    iSeq = SystemParameters.ParamsInput()
        
    iSeq.name = "Gender60x200"

    iSeq.gender_continuous = gender_continuous     
    iSeq.data_base_dir = user_base_dir + data_dir
    iSeq.ids = numpy.arange(first_id,first_id+num_ids) #160, but 180 for paper!
    iSeq.ages = [999]
    iSeq.MIN_GENDER = -3
    iSeq.MAX_GENDER = 3
    iSeq.GENDER_STEP = 0.10000 #01. 0.20025 default. 0.4 fails, use 0.4005, 0.80075, 0.9005
    #iSeq.GENDER_STEP = 0.80075 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
    iSeq.real_genders = numpy.arange(iSeq.MIN_GENDER, iSeq.MAX_GENDER, iSeq.GENDER_STEP)
    iSeq.genders = map(imageLoader.code_gender, iSeq.real_genders)
    iSeq.racetweens = [999]
    iSeq.expressions = [0]
    iSeq.morphs = [0]
    iSeq.poses = [0]
    iSeq.lightings = [0]
    iSeq.slow_signal = 2
    iSeq.step = 1
    iSeq.offset = 0
    iSeq.input_files = imageLoader.create_image_filenames2(iSeq.data_base_dir, iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                                    iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                                    iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset)
    iSeq.num_images = len(iSeq.input_files)
    iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                          iSeq.morphs, iSeq.poses, iSeq.lightings]
        
    if iSeq.gender_continuous:
        iSeq.block_size = iSeq.num_images / len(iSeq.params[iSeq.slow_signal])  
        iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.real_genders, iSeq.block_size)
        iSeq.correct_classes = sfa_libs.wider_1Darray(iSeq.real_genders, iSeq.block_size)
    else:
        bs = iSeq.num_images / len(iSeq.params[iSeq.slow_signal])
        bs1 = len(iSeq.real_genders[iSeq.real_genders<0]) * bs
        bs2 = len(iSeq.real_genders[iSeq.real_genders>=0]) * bs
            
        iSeq.block_size = numpy.array([bs1, bs2])
        iSeq.correct_labels = numpy.array([-1]*bs1 + [1]*bs2)
        #iSeq.correct_classes = sfa_libs.wider_1Darray(iSeq.real_genders, iSeq.block_size)
        iSeq.correct_classes = numpy.array([-1]*bs1 + [1]*bs2)
            
    SystemParameters.test_object_contents(iSeq)
    return iSeq

def sSeqCreateGender(iSeq, contrast_enhance, seed=-1):
    if seed >= 0 or seed is None: 
        numpy.random.seed(seed)
    
    if iSeq==None:
        print "Gender: iSeq was None, this might be an indication that the data is not available"
        sSeq = SystemParameters.ParamsDataLoading()
        return sSeq
    
    print "******** Setting Training Data Parameters for Gender  ****************"
    sSeq = SystemParameters.ParamsDataLoading()
    sSeq.input_files = iSeq.input_files
    sSeq.num_images = iSeq.num_images
    sSeq.block_size = iSeq.block_size
    sSeq.image_width = 256
    sSeq.image_height = 192
    sSeq.subimage_width = 135
    sSeq.subimage_height = 135 
    sSeq.pixelsampling_x = 1
    sSeq.pixelsampling_y =  1
    sSeq.subimage_pixelsampling = 2
    sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2
    sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
    sSeq.add_noise_L0 = True
    sSeq.convert_format = "L"
    sSeq.background_type = "black"
    sSeq.contrast_enhance = contrast_enhance
    sSeq.translation = 2
    sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)
    sSeq.translations_y = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)
    sSeq.trans_sampled = False
    if iSeq.gender_continuous:
        sSeq.train_mode = 'serial' # ('mixed' for paper) regular, 'serial'
    else:
        sSeq.train_mode = 'clustered'
    sSeq.load_data = load_data_from_sSeq
    SystemParameters.test_object_contents(sSeq)
    return sSeq

# # print "******** Setting Training Information Parameters for Gender **********"
# # gender_continuous = True #and False 
# # 
# # iTrainGender = SystemParameters.ParamsInput()
# # iTrainGender.name = "Gender60x200"
# # iTrainGender.data_base_dir = user_base_dir + "Alberto/RenderingsGender60x200"
# # iTrainGender.ids = numpy.arange(0,25) #160, but 180 for paper!
# # iTrainGender.ages = [999]
# # iTrainGender.MIN_GENDER = -3
# # iTrainGender.MAX_GENDER = 3
# # iTrainGender.GENDER_STEP = 0.10000 #01. 0.20025 default. 0.4 fails, use 0.4005, 0.80075, 0.9005
# # #iTrainGender.GENDER_STEP = 0.80075 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
# # iTrainGender.real_genders = numpy.arange(iTrainGender.MIN_GENDER, iTrainGender.MAX_GENDER, iTrainGender.GENDER_STEP)
# # iTrainGender.genders = map(imageLoader.code_gender, iTrainGender.real_genders)
# # iTrainGender.racetweens = [999]
# # iTrainGender.expressions = [0]
# # iTrainGender.morphs = [0]
# # iTrainGender.poses = [0]
# # iTrainGender.lightings = [0]
# # iTrainGender.slow_signal = 2
# # iTrainGender.step = 1
# # iTrainGender.offset = 0
# # iTrainGender.input_files = imageLoader.create_image_filenames2(iTrainGender.data_base_dir, iTrainGender.slow_signal, iTrainGender.ids, iTrainGender.ages, \
# #                                             iTrainGender.genders, iTrainGender.racetweens, iTrainGender.expressions, iTrainGender.morphs, \
# #                                             iTrainGender.poses, iTrainGender.lightings, iTrainGender.step, iTrainGender.offset)
# # #MEGAWARNING!!!!
# # #numpy.random.shuffle(iTrainGender.input_files)  
# # #numpy.random.shuffle(iTrainGender.input_files)  
# # 
# # iTrainGender.num_images = len(iTrainGender.input_files)
# # #iTrainGender.params = [ids, expressions, morphs, poses, lightings]
# # iTrainGender.params = [iTrainGender.ids, iTrainGender.ages, iTrainGender.genders, iTrainGender.racetweens, iTrainGender.expressions, \
# #                   iTrainGender.morphs, iTrainGender.poses, iTrainGender.lightings]
# # 
# # if gender_continuous:
# #     iTrainGender.block_size = iTrainGender.num_images / len(iTrainGender.params[iTrainGender.slow_signal])  
# #     iTrainGender.correct_labels = sfa_libs.wider_1Darray(iTrainGender.real_genders, iTrainGender.block_size)
# #     iTrainGender.correct_classes = sfa_libs.widees ist nicht zu kompliziertr_1Darray(iTrainGender.real_genders, iTrainGender.block_size)
# # else:
# #     bs = iTrainGender.num_images / len(iTrainGender.params[iTrainGender.slow_signal])
# #     bs1 = len(iTrainGender.real_genders[iTrainGender.real_genders<0]) * bs
# #     bs2 = len(iTrainGender.real_genders[iTrainGender.real_genders>=0]) * bs
# #     
# #     iTrainGender.block_size = numpy.array([bs1, bs2])
# #     iTrainGender.correct_labels = numpy.array([-1]*bs1 + [1]*bs2)
# #     #iTrainGender.correct_classes = sfa_libs.wider_1Darray(iTrainGender.real_genders, iTrainGender.block_size)
# #     iTrainGender.correct_classes = numpy.array([-1]*bs1 + [1]*bs2)
# #     
# # SystemParameters.test_object_contents(iTrainGender)
# # 
# # #iTrainGender.correct_classes = sfa_libs.wider_1Darray(numpy.arange(iTrainGender.num_images / iTrainGender.block_size), iTrainGender.block_size)
# # 
# # print "******** Setting Training Data Parameters for Gender  ****************"
# # sTrainGender = SystemParameters.ParamsDataLoading()
# # sTrainGender.input_files = iTrainGender.input_files
# # sTrainGender.num_images = iTrainGender.num_images
# # sTrainGender.block_size = iTrainGender.block_size
# # sTrainGender.image_width = 256
# # sTrainGender.image_height = 192
# # sTrainGender.subimage_width = 135
# # sTrainGender.subimage_height = 135 
# # sTrainGender.pixelsampling_x = 1
# # sTrainGender.pixelsampling_y =  1
# # sTrainGender.subimage_pixelsampling = 2
# # sTrainGender.subimage_first_row =  sTrainGender.image_height/2-sTrainGender.subimage_height*sTrainGender.pixelsampling_y/2
# # sTrainGender.subimage_first_column = sTrainGender.image_width/2-sTrainGender.subimage_width*sTrainGender.pixelsampling_x/2+ 5*sTrainGender.pixelsampling_x
# # sTrainGender.add_noise_L0 = True
# # sTrainGender.convert_format = "L"
# # sTrainGender.background_type = "black"
# # sTrainGender.translation = 2
# # sTrainGender.translations_x = numpy.random.random_integers(-sTrainGender.translation, sTrainGender.translation, sTrainGender.num_images)
# # sTrainGender.translations_y = numpy.random.random_integers(-sTrainGender.translation, sTrainGender.translation, sTrainGender.num_images)
# # sTrainGender.trans_sampled = False
# # if gender_continuous:
# #     sTrainGender.train_mode = 'serial' # ('mixed' for paper)
# # else:
# #     sTrainGender.train_mode = 'clustered'
# # SystemParameters.test_object_contents(sTrainGender)
# # 
# # print "****** Setting Seen Id Test Information Parameters for Gender ********"
# # iSeenidGender = SystemParameters.ParamsInput()
# # iSeenidGender.name = "Gender60x200Seenid"
# # iSeenidGender.data_base_dir =user_base_dir + "Alberto/RenderingsGender60x200"
# # iSeenidGender.ids = numpy.arange(0,180) # #160, (0,180) for paper!
# # iSeenidGender.ages = [999]
# # iSeenidGender.MIN_GENDER = -3
# # iSeenidGender.MAX_GENDER = 3
# # iSeenidGender.GENDER_STEP = 0.10000 #01. defaultes ist nicht zu kompliziert. 0.4 fails, use 0.4005, 0.80075, 0.9005
# # #iSeenidGender.GENDER_STEP = 0.80075 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
# # iSeenidGender.real_genders = numpy.arange(iSeenidGender.MIN_GENDER, iSeenidGender.MAX_GENDER, iSeenidGender.GENDER_STEP)
# # iSeenidGender.genders = map(imageLoader.code_gender, iSeenidGender.real_genders)
# # iSeenidGender.racetweens = [999]
# # iSeenidGender.expressions = [0]
# # iSeenidGender.morphs = [0]
# # iSeenidGender.poses = [0]
# # iSeenidGender.lightings = [0]
# # iSeenidGender.slow_signal = 2
# # iSeenidGender.step = 1
# # iSeenidGender.offset = 0                             
# # iSeenidGender.input_files = imageLoader.create_image_filenames2(iSeenidGender.data_base_dir, iSeenidGender.slow_signal, iSeenidGender.ids, iSeenidGender.ages, \
# #                                             iSeenidGender.genders, iSeenidGender.racetweens, iSeenidGender.expressions, iSeenidGender.morphs, \
# #                                             iSeenidGender.poses, iSeenidGender.lightings, iSeenidGender.step, iSeenidGender.offset)  
# # iSeenidGender.num_images = len(iSeenidGender.input_files)
# # #iSeenidGender.params = [ids, expressions, morphs, poses, lightings]
# # iSeenidGender.params = [iSeenidGender.ids, iSeenidGender.ages, iSeenidGender.genders, iSeenidGender.racetweens, iSeenidGender.expressions, \
# #                   iSeenidGender.morphs, iSeenidGender.poses, iSeenidGender.lightings]
# # if gender_continuous:
# #     iSeenidGender.block_size = iSeenidGender.num_images / len(iSeenidGender.params[iSeenidGender.slow_signal])
# #     iSeenidGender.correct_labels = sfa_libs.wider_1Darray(iSeenidGender.real_genders, iSeenidGender.block_size)
# #     iSeenidGender.correct_classes = sfa_libs.wider_1Darray(iSeenidGender.real_genders, iSeenidGender.block_size)
# # else:
# #     bs = iSeenidGender.num_images / len(iSeenidGender.params[iSeenidGender.slow_signal])
# #     bs1 = len(iSeenidGender.real_genders[iSeenidGender.real_genders<0]) * bs
# #     bs2 = len(iSeenidGender.real_genders[iSeenidGender.real_genders>=0]) * bs
# #     iSeenidGender.block_size = numpy.array([bs1, bs2])
# #     iSeenidGender.correct_labels = numpy.array([-1]*bs1 + [1]*bs2)
# #     iSeenidGender.correct_classes = numpy.array([-1]*bs1 + [1]*bs2)
# # 
# # SystemParameters.test_object_contents(iSeenidGender)
# # 
# # 
# # print "***** Setting Seen Id Sequence Parameters for Gender ****************"
# # sSeenidGender = SystemParameters.ParamsDataLoading()
# # sSeenidGender.input_files = iSeenidGender.input_files
# # sSeenidGender.num_images = iSeenidGender.num_images
# # sSeenidGender.image_width = 256
# # sSeenidGender.image_height = 192
# # sSeenidGender.subimage_width = 135
# # sSeenidGender.subimage_height = 135 
# # sSeenidGender.pixelsampling_x = 1
# # sSeenidGender.pixelsampling_y =  1
# # sSeenidGender.subimage_pixelsampling = 2
# # sSeenidGender.subimage_first_row =  sSeenidGender.image_height/2-sSeenidGender.subimage_height*sSeenidGender.pixelsampling_y/2
# # sSeenidGender.subimage_first_column = sSeenidGender.image_width/2-sSeenidGender.subimage_width*sSeenidGender.pixelsampling_x/2+ 5*sSeenidGender.pixelsampling_x
# # sSeenidGender.add_noise_L0 = True
# # sSeenidGender.convert_format = "L"
# # sSeenidGender.background_type = "black"
# # sSeenidGender.translation = 2
# # sSeenidGender.translations_x = numpy.random.random_integers(-sSeenidGender.translation, sSeenidGender.translation, sSeenidGender.num_images)
# # sSeenidGender.translations_y = numpy.random.random_integers(-sSeenidGender.translation, sSeenidGender.translation, sSeenidGender.num_images)
# # sSeenidGender.trans_sampled = False
# # sSeenidGender.load_data = load_data_from_sSeqes ist nicht zu kompliziert
# # SystemParameters.test_object_contents(sSeenidGender)
# # 
# # 0
# # print "** Setting New Id Test Information Parameters for Gender **********"
# # iNewidGender = SystemParameters.ParamsInput()
# # iNewidGender.name = "Gender60x200Newid"
# # iNewidGender.data_base_dir =user_base_dir + "Alberto/RenderingsGender60x200"
# # iNewidGender.ids = range(180,200)#160,200, 180-200 for paper!
# # iNewidGender.ages = [999]
# # iNewidGender.MIN_GENDER = -3
# # iNewidGender.MAX_GENDER = 3
# # iNewidGender.GENDER_STEP = 0.10000 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
# # #iSeenidGender.GENDER_STEP = 0.80075 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
# # iNewidGender.real_genders = numpy.arange(iNewidGender.MIN_GENDER, iNewidGender.MAX_GENDER, iNewidGender.GENDER_STEP)
# # iNewidGender.genders = map(imageLoader.code_gender, iNewidGender.real_genders)
# # iNewidGender.racetweens = [999]
# # iNewidGender.expressions = [0]
# # iNewidGender.morphs = [0]
# # iNewidGender.poses = [0]
# # iNewidGender.lightings = [0]
# # iNewidGender.slow_signal = 2
# # iNewidGender.step = 1
# # iNewidGender.offset = 0                             
# # iNewidGender.input_files = imageLoader.create_image_filenames2(iNewidGender.data_base_dir, iNewidGender.slow_signal, iNewidGender.ids, iNewidGender.ages, \
# #                                             iNewidGender.genders, iNewidGender.racetweens, iNewidGender.expressions, iNewidGender.morphs, \
# #                                             iNewidGender.poses, iNewidGender.lightings, iNewidGender.step, iNewidGender.offset)  
# # iNewidGender.num_images = len(iNewidGender.inputes ist nicht zu kompliziert_files)
# # #iNewidGender.params = [ids, expressions, morphs, poses, lightings]
# # iNewidGender.params = [iNewidGender.ids, iNewidGender.ages, iNewidGender.genders, iNewidGender.racetweens, iNewidGender.expressions, \
# #                   iNewidGender.morphs, iNewidGender.poses, iNewidGender.lightings]
# # iNewidGender.block_size = iNewidGender.num_images / len(iNewidGender.params[iNewidGender.slow_signal])
# # 
# # iNewidGender.correct_labels = sfa_libs.wider_1Darray(iNewidGender.real_genders, iNewidGender.block_size)
# # iNewidGender.correct_classes = sfa_libs.wider_1Darray(iNewidGender.real_genders, iNewidGender.block_size)
# # #iNewidGender.correct_classes = sfa_libs.wider_1Darray(numpy.arange(iNewidGender.num_images / iNewidGender.block_size), iNewidGender.block_size)
# # 
# # if gender_continuous:
# #     iNewidGender.block_size = iNewidGender.num_images / len(iNewidGender.params[iNewidGender.slow_signal])
# #     iNewidGender.correct_labels = sfa_libs.wider_1Darray(iNewidGender.real_genders, iNewidGender.block_size)
# #     iNewidGender.correct_classes = sfa_libs.wider_1Darray(iNewidGender.real_genders, iNewidGender.block_size)
# # else:
# #     bs = iNewidGender.num_images / len(iNewidGender.params[iNewidGender.slow_signal])
# #     bs1 = len(iNewidGender.real_genders[iNewidGender.real_genders<0]) * bs
# #     bs2 = len(iNewidGender.real_genders[iNewidGender.real_genders>=0]) * bs
# #     iNewidGender.block_size = numpy.array([bs1, bs2])
# #     iNewidGender.correct_labels = numpy.array([-1]*bs1 + [1]*bs2)
# #     iNewidGender.correct_classes = numpy.array( [-1]*bs1 + [1]*bs2)
# # 
# # SystemParameters.test_object_contents(iNewidGendes ist nicht zu komplizierter)
# # 
# # 
# # print "******** Setting New Id Data Parameters ******************************"
# # sNewidGender = SystemParameters.ParamsDataLoading()
# # sNewidGender.input_files = iNewidGender.input_files
# # sNewidGender.num_images = iNewidGender.num_images
# # sNewidGender.image_width = 256
# # sNewidGender.image_height = 192
# # sNewidGender.subimage_width = 135
# # sNewidGender.subimage_height = 135 
# # sNewidGender.pixelsampling_x = 1
# # sNewidGender.pixelsampling_y =  1
# # sNewidGender.subimage_pixelsampling = 2
# # sNewidGender.subimage_first_row =  sNewidGender.image_height/2-sNewidGender.subimage_height*sNewidGender.pixelsampling_y/2
# # sNewidGender.subimage_first_column = sNewidGender.image_width/2-sNewidGender.subimage_width*sNewidGender.pixelsampling_x/2+ 5*sNewidGender.pixelsampling_x
# # sNewidGender.add_noise_L0 = True
# # sNewidGender.convert_format = "L"
# # sNewidGender.background_type = "black"
# # sNewidGender.translation = 2
# # sNewidGender.translations_x = numpy.random.random_integers(-sNewidGender.translation, sNewidGender.translation, sNewidGender.num_images)
# # sNewidGender.translations_y = numpy.random.random_integers(-sNewidGender.translation, sNewidGender.translation, sNewidGender.num_images)
# # sNewidGender.trans_sampled = False
# # sNewidGender.load_data = load_data_from_sSeq
# # SystemParameters.test_object_contents(sNewidGender)

numpy.random.seed(experiment_seed+987987987)
contrast_enhance = "ContrastGenderMultiply"
#WARNING!!!
#iTrainGender0 = iSeqCreateGender(first_id = 0, num_ids = 180, user_base_dir=user_base_dir, data_dir="Alberto/RenderingsGender60x200", gender_continuous=True, seed=-1)
iTrainGender0 = iSeqCreateGender(first_id = 0, num_ids = 180, user_base_dir=user_base_dir, data_dir="Alberto/RenderingsGender60x200", gender_continuous=True, seed=-1)
sTrainGender0 = sSeqCreateGender(iTrainGender0, contrast_enhance, seed=-1)

iTrainGender1 = iSeqCreateGender(first_id = 0, num_ids = 10, user_base_dir=user_base_dir, data_dir="Alberto/RenderingsGender60x200", gender_continuous=True, seed=-1)
sTrainGender1 = sSeqCreateGender(iTrainGender1, contrast_enhance, seed=-1)

#iTrainGender2 = iSeqCreateGender(first_id = 40, num_ids = 150, user_base_dir=user_base_dir, data_dir="Alberto/RenderingsGender60x200", gender_continuous=True, seed=-1)
#sTrainGender2 = sSeqCreateGender(iTrainGender2, seed=-1)
#sTrainGender2.train_mode = "ignore_data"

#iSeenidGender = iSeqCreateGender(first_id = 0, num_ids = 180, user_base_dir=user_base_dir, data_dir="Alberto/RenderingsGender60x200", gender_continuous=True, seed=-1)
iSeenidGender = iSeqCreateGender(first_id = 0, num_ids = 180, user_base_dir=user_base_dir, data_dir="Alberto/RenderingsGender60x200", gender_continuous=True, seed=-1)
sSeenidGender = sSeqCreateGender(iSeenidGender, contrast_enhance, seed=-1)

iNewidGender = iSeqCreateGender(first_id = 180, num_ids = 20, user_base_dir=user_base_dir, data_dir="Alberto/RenderingsGender60x200", gender_continuous=True, seed=-1)
sNewidGender = sSeqCreateGender(iNewidGender, contrast_enhance, seed=-1)

#LABEL TRANSFORMATIONS FOR EXACT LABEL LEARNING
random_labels = True and False
discontinuous_labels = True and False
if random_labels or discontinuous_labels:
    labels = numpy.sort(list(set(iTrainGender0.correct_labels)))

    if discontinuous_labels:
        random_labels = (numpy.arange(-3,3,0.1)+3)%3 - 6
    else:
        random_labels = numpy.random.normal(size = len(labels))
        random_labels = numpy.abs(numpy.random.normal(size = len(labels))).cumsum()
    
    print "labels =", labels
    print "random_labels = ", random_labels
    for i, label_val in enumerate(labels):
        for correct_labels in (iTrainGender0.correct_labels, iTrainGender1.correct_labels, iSeenidGender.correct_labels, iNewidGender.correct_labels): #
            correct_labels[correct_labels == label_val] = random_labels[i]
else: #regular labels    
    power = 1.0 #2.0 # 3.0 1.0
    offset = 0.0 #3.0 # 0.0, 3.0
    if power==2:
        iTrainGender0.correct_labels = iTrainGender0.correct_labels ** power
        iSeenidGender.correct_labels = iSeenidGender.correct_labels ** power
        iNewidGender.correct_labels =  iNewidGender.correct_labels ** power
    elif power==3 or power==1:
        iTrainGender0.correct_labels = sgn_expo(iTrainGender0.correct_labels+offset, power) 
        iTrainGender1.correct_labels = sgn_expo(iTrainGender1.correct_labels+offset, power) 
        #iTrainGender2.correct_labels = sgn_expo(iTrainGender2.correct_labels, 1.0) 
        iSeenidGender.correct_labels =  sgn_expo(iSeenidGender.correct_labels+offset, power)
        iNewidGender.correct_labels = sgn_expo(iNewidGender.correct_labels+offset, power)
    else:
        er = "Dont know how to handle power properly, power=", power
        raise Exception(er)

def extract_gender_from_filename(filename):
    if "M" in filename:
        return -1
    elif "F" in filename:
        return 1
    else:
        print "gender from filename %s not recognized"%filename
    quit()


def load_GT_labels(labels_filename, age_included=True, rAge_included=False, gender_included=True, race_included=False, avgColor_included=False):
    fd = open(labels_filename, 'r')

    c_age = 1
    if age_included:
        c_rAge = c_age + 1
    else:
        c_rAge = c_age
    if rAge_included:
        c_gender = c_rAge + 1
    else:
        c_gender = c_rAge
    if gender_included:
        c_race = c_gender + 1
    else:
        c_race = c_gender
    if race_included:
        c_avgColor = c_race + 1
    else:
        c_avgColor = c_race
    
    labels = {}
    for line in fd.readlines():
        all_labels = string.split(line, " ")
        filename = all_labels[0]        
        this_labels = []
        if age_included:
            age = float(all_labels[c_age])
            this_labels.append(age)
        if rAge_included:
            rAge = float(all_labels[c_rAge])
            this_labels.append(rAge)
        if gender_included:
            gender = all_labels[c_gender][0]
            if gender == "M":
                gender = -1
            elif gender == "F":                
                gender = 1
            else:
                er = "Gender *%s* not recognized"%str(gender)
                raise Exception(er)
            this_labels.append(gender)
        if race_included:
            race = all_labels[c_race][0]
            if race == "B":
                race = -2
            elif race == "O":
                race = -1
            elif race == "A":
                race = 0
            elif race == "H":
                race = 1
            elif race == "W":
                race = 2
            else:
                er = "Race *%s* not recognized"%str(race)
                raise Exception(er)
            this_labels.append(race)
        if avgColor_included:
            avgColor = float(all_labels[c_avgColor])
            this_labels.append(avgColor)       
        labels[filename] = this_labels
    fd.close()
    return labels
    
add_skin_color_label_classes = True and False
multiple_labels = add_skin_color_label_classes and False 
first_gender_label = True #and False
sampled_by_gender = True #and False

#True, False, False, False => learn only skin color
#True, True, True, True  => learn both gender and skin color, gender is first label and determines ordering
#True, True, True, False => learn both gender and skin color, gender is first label but skin color determines ordering
#False, False, True, True => learn only gender 

if add_skin_color_label_classes:
    skin_color_labels_map = load_GT_labels(user_base_dir+"Alberto/RenderingsGender60x200"+"/GT_average_color_labels.txt", age_included=False, rAge_included=False, gender_included=False, race_included=False, avgColor_included=True)
    
    example_filename = "output133_a999_g362_rt999_e0_c0_p0_i0.tif"
    filename_len = len(example_filename)
    
    skin_color_labels_TrainGender0 =[]   
    for input_file in iTrainGender0.input_files:
        input_file_short =  input_file[-filename_len:]
        skin_color_labels_TrainGender0.append(skin_color_labels_map[input_file_short])  
    skin_color_labels_TrainGender0 = numpy.array(skin_color_labels_TrainGender0).reshape((-1,1))
    
    skin_color_labels_SeenidGender =[]   
    for input_file in iSeenidGender.input_files:
        input_file_short =  input_file[-filename_len:]
        skin_color_labels_SeenidGender.append(skin_color_labels_map[input_file_short])
    skin_color_labels_SeenidGender = numpy.array(skin_color_labels_SeenidGender).reshape((-1,1))

    skin_color_labels_NewidGender =[]   
    for input_file in iNewidGender.input_files:
        input_file_short =  input_file[-filename_len:]
        skin_color_labels_NewidGender.append(skin_color_labels_map[input_file_short])
    skin_color_labels_NewidGender = numpy.array(skin_color_labels_NewidGender).reshape((-1,1))

    skin_color_labels = skin_color_labels_SeenidGender.flatten()
    sorting = numpy.argsort(skin_color_labels)
    num_classes = 60
    skin_color_classes_SeenidGender = numpy.zeros(iSeenidGender.num_images)
    skin_color_classes_SeenidGender[sorting] = numpy.arange(iSeenidGender.num_images)*num_classes/iSeenidGender.num_images
    avg_labels = more_nodes.compute_average_labels_for_each_class(skin_color_classes_SeenidGender, skin_color_labels)
    all_classes = numpy.unique(skin_color_classes_SeenidGender)
    print "skin color avg_labels=", avg_labels 
    skin_color_classes_TrainGender0 = more_nodes.map_labels_to_class_number(all_classes, avg_labels, skin_color_labels_TrainGender0.flatten())
    skin_color_classes_NewidGender = more_nodes.map_labels_to_class_number(all_classes, avg_labels, skin_color_labels_NewidGender.flatten())

    skin_color_classes_TrainGender0 = skin_color_classes_TrainGender0.reshape((-1,1))
    skin_color_classes_SeenidGender = skin_color_classes_SeenidGender.reshape((-1,1))
    skin_color_classes_NewidGender = skin_color_classes_NewidGender.reshape((-1,1))

if multiple_labels==True:
    if first_gender_label == True:
        print "Learning both skin color and gender, gender is first label"
        iTrainGender0.correct_labels = numpy.concatenate((iTrainGender0.correct_labels.reshape(-1,1), skin_color_labels_TrainGender0), axis=1)
        iSeenidGender.correct_labels = numpy.concatenate((iSeenidGender.correct_labels.reshape(-1,1), skin_color_labels_SeenidGender), axis=1)
        iNewidGender.correct_labels = numpy.concatenate((iNewidGender.correct_labels.reshape(-1,1), skin_color_labels_NewidGender), axis=1)
    
        iTrainGender0.correct_classes = numpy.concatenate((iTrainGender0.correct_classes.reshape(-1,1), skin_color_classes_TrainGender0), axis=1)
        iSeenidGender.correct_classes = numpy.concatenate((iSeenidGender.correct_classes.reshape(-1,1), skin_color_classes_SeenidGender), axis=1)
        iNewidGender.correct_classes = numpy.concatenate((iNewidGender.correct_classes.reshape(-1,1), skin_color_classes_NewidGender), axis=1)
    else:
        print "Learning both skin color and gender, color is first label"
        iTrainGender0.correct_labels = numpy.concatenate((skin_color_labels_TrainGender0, iTrainGender0.correct_labels.reshape(-1,1)), axis=1)
        iSeenidGender.correct_labels = numpy.concatenate((skin_color_labels_SeenidGender, iSeenidGender.correct_labels.reshape(-1,1)), axis=1)
        iNewidGender.correct_labels = numpy.concatenate((skin_color_labels_NewidGender, iNewidGender.correct_labels.reshape(-1,1)), axis=1)
    
        iTrainGender0.correct_classes = numpy.concatenate((skin_color_classes_TrainGender0, iTrainGender0.correct_classes.reshape(-1,1)), axis=1)
        iSeenidGender.correct_classes = numpy.concatenate((skin_color_classes_SeenidGender, iSeenidGender.correct_classes.reshape(-1,1)), axis=1)
        iNewidGender.correct_classes = numpy.concatenate((skin_color_classes_NewidGender, iNewidGender.correct_classes.reshape(-1,1)), axis=1)
else:
    if add_skin_color_label_classes:
        print "Learning skin color instead of gender"
        iTrainGender0.correct_labels = skin_color_labels_TrainGender0.flatten()
        iSeenidGender.correct_labels = skin_color_labels_SeenidGender.flatten()
        iNewidGender.correct_labels = skin_color_labels_NewidGender.flatten()
        iTrainGender0.correct_classes = skin_color_classes_TrainGender0.flatten()
        iSeenidGender.correct_classes = skin_color_classes_SeenidGender.flatten()
        iNewidGender.correct_classes = skin_color_classes_NewidGender.flatten()
    else:
        print "Learning gender only"

if sampled_by_gender == False:
    print "reordering by increasing skin color label"
    for (iSeq, labels) in ((iTrainGender0, skin_color_labels_TrainGender0), 
                           (iSeenidGender, skin_color_labels_SeenidGender), 
                            (iNewidGender, skin_color_labels_NewidGender)):    
        all_labels = labels.flatten()
        reordering = numpy.argsort(all_labels)
        if multiple_labels:
            iSeq.correct_labels = iSeq.correct_labels[reordering,:]
            iSeq.correct_classes = iSeq.correct_classes[reordering,:]
        else:
            iSeq.correct_labels = iSeq.correct_labels[reordering]
            iSeq.correct_classes = iSeq.correct_classes[reordering]            
        reordered_files = []
        for i in range(len(iSeq.input_files)):
            reordered_files.append(iSeq.input_files[reordering[i]])
        iSeq.input_files = reordered_files
        #print "reordered_files=", reordered_files
    print "labels/classes reordered, skin color is the first one"





####################################################################
###########        SYSTEM FOR GENDER ESTIMATION         ############
####################################################################  
ParamsGender = SystemParameters.ParamsSystem()
ParamsGender.name = "Network that extracts gender information"
ParamsGender.network = None
semi_supervised_learning = False
if semi_supervised_learning:
    ParamsGender.iTrain = [[iTrainGender0], [iTrainGender1,]] #[]
    ParamsGender.sTrain = [[sTrainGender0], [sTrainGender1,]] #[]
else:
    ParamsGender.iTrain = [[iTrainGender0]] #[]
    ParamsGender.sTrain = [[sTrainGender0]] #[]    
ParamsGender.iSeenid = iSeenidGender
ParamsGender.sSeenid = sSeenidGender
ParamsGender.iNewid = [[iNewidGender]] #[]
ParamsGender.sNewid = [[sNewidGender]] #[]

# ParamsGender.block_size = iTrainGender1.block_size
# if gender_continuous:
#     ParamsGender.train_mode = 'mixed'
# else:
#     ParamsGender.train_mode = 'clustered'
    
ParamsGender.analysis = None
ParamsGender.enable_reduced_image_sizes = True #(False paper)
ParamsGender.reduction_factor = 2.0 # 8.0 # 2.0 #1.0 #(1.0 paper)
ParamsGender.hack_image_size  = 64  # 16 # 64 #128 #(128 paper)
ParamsGender.enable_hack_image_size = True

print "******** Setting Train Information Parameters for Identity ***********"
iTrainIdentity = SystemParameters.ParamsInput()
iTrainIdentity.name = "Identities20x500"
iTrainIdentity.data_base_dir =user_base_dir + "Alberto/Renderings20x500"
iTrainIdentity.ids = numpy.arange(0,18)
iTrainIdentity.ages = [999]
#iTrainIdentity.MIN_GENDER = -3
#iTrainIdentity.MAX_GENDER = 3
#iTrainIdentity.GENDER_STEP = 0.10000 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
#iTrainIdentity.GENDER_STEP = 0.80075 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
#iTrainIdentity.genders = map(imageLoader.code_gender, numpy.arange(iTrainIdentity.MIN_GENDER, iTrainIdentity.MAX_GENDER, iTrainIdentity.GENDER_STEP))
iTrainIdentity.genders = [999]
iTrainIdentity.racetweens = [999]
iTrainIdentity.expressions = [0]
iTrainIdentity.morphs = [0]
iTrainIdentity.poses = range(0,500)
iTrainIdentity.lightings = [0]
iTrainIdentity.slow_signal = 0
iTrainIdentity.step = 2
iTrainIdentity.offset = 0     

iTrainIdentity.input_files = imageLoader.create_image_filenames(iTrainIdentity.data_base_dir, iTrainIdentity.slow_signal, iTrainIdentity.ids, iTrainIdentity.expressions, iTrainIdentity.morphs, iTrainIdentity.poses, iTrainIdentity.lightings, iTrainIdentity.step, iTrainIdentity.offset)
iTrainIdentity.num_images = len(iTrainIdentity.input_files)
iTrainIdentity.params = [iTrainIdentity.ids, iTrainIdentity.expressions, iTrainIdentity.morphs, iTrainIdentity.poses, iTrainIdentity.lightings]
iTrainIdentity.block_size= iTrainIdentity.num_images / len(iTrainIdentity.params[iTrainIdentity.slow_signal])

iTrainIdentity.correct_classes = sfa_libs.wider_1Darray(iTrainIdentity.ids, iTrainIdentity.block_size)
iTrainIdentity.correct_labels = sfa_libs.wider_1Darray(iTrainIdentity.ids, iTrainIdentity.block_size)

SystemParameters.test_object_contents(iTrainIdentity)

print "***** Setting Train Sequence Parameters for Identity *****************"
sTrainIdentity = SystemParameters.ParamsDataLoading()
sTrainIdentity.input_files = iTrainIdentity.input_files
sTrainIdentity.num_images = iTrainIdentity.num_images
sTrainIdentity.image_width = 640
sTrainIdentity.image_height = 480
sTrainIdentity.subimage_width = 135
sTrainIdentity.subimage_height = 135 
sTrainIdentity.pixelsampling_x = 2
sTrainIdentity.pixelsampling_y =  2
sTrainIdentity.subimage_pixelsampling = 2
sTrainIdentity.subimage_first_row =  sTrainIdentity.image_height/2-sTrainIdentity.subimage_height*sTrainIdentity.pixelsampling_y/2
sTrainIdentity.subimage_first_column = sTrainIdentity.image_width/2-sTrainIdentity.subimage_width*sTrainIdentity.pixelsampling_x/2+ 5*sTrainIdentity.pixelsampling_x
sTrainIdentity.add_noise_L0 = False
sTrainIdentity.convert_format = "L"
sTrainIdentity.background_type = "black"
sTrainIdentity.translation = 0
sTrainIdentity.translations_x = numpy.random.random_integers(-sTrainIdentity.translation, sTrainIdentity.translation, sTrainIdentity.num_images)
sTrainIdentity.translations_y = numpy.random.random_integers(-sTrainIdentity.translation, sTrainIdentity.translation, sTrainIdentity.num_images)
sTrainIdentity.trans_sampled = False
SystemParameters.test_object_contents(sTrainIdentity)


print "******** Setting Seen Id Information Parameters for Identity *********"
iSeenidIdentity = SystemParameters.ParamsInput()
iSeenidIdentity.name = "Identities20x500"
iSeenidIdentity.data_base_dir =user_base_dir + "Alberto/Renderings20x500"
iSeenidIdentity.ids = numpy.arange(0,18)
iSeenidIdentity.ages = [999]
iSeenidIdentity.MIN_GENDER = -3
iSeenidIdentity.MAX_GENDER = 3
iSeenidIdentity.GENDER_STEP = 0.10000 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
#iSeenidIdentity.GENDER_STEP = 0.80075 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
iSeenidIdentity.genders = map(imageLoader.code_gender, numpy.arange(iSeenidIdentity.MIN_GENDER, iSeenidIdentity.MAX_GENDER, iSeenidIdentity.GENDER_STEP))
iSeenidIdentity.racetweens = [999]
iSeenidIdentity.expressions = [0]
iSeenidIdentity.morphs = [0]
iSeenidIdentity.poses = range(0,500)
iSeenidIdentity.lightings = [0]
iSeenidIdentity.slow_signal = 0
iSeenidIdentity.step = 2
iSeenidIdentity.offset = 1    

iSeenidIdentity.input_files = imageLoader.create_image_filenames(iSeenidIdentity.data_base_dir, iSeenidIdentity.slow_signal, iSeenidIdentity.ids, iSeenidIdentity.expressions, iSeenidIdentity.morphs, iSeenidIdentity.poses, iSeenidIdentity.lightings, iSeenidIdentity.step, iSeenidIdentity.offset)
iSeenidIdentity.num_images = len(iSeenidIdentity.input_files)
iSeenidIdentity.params = [iSeenidIdentity.ids, iSeenidIdentity.expressions, iSeenidIdentity.morphs, iSeenidIdentity.poses, iSeenidIdentity.lightings]
iSeenidIdentity.block_size= iSeenidIdentity.num_images / len(iSeenidIdentity.params[iSeenidIdentity.slow_signal])

iSeenidIdentity.correct_classes = sfa_libs.wider_1Darray(iSeenidIdentity.ids, iSeenidIdentity.block_size)
iSeenidIdentity.correct_labels = sfa_libs.wider_1Darray(iSeenidIdentity.ids, iSeenidIdentity.block_size)

SystemParameters.test_object_contents(iSeenidIdentity)

print "******** Setting Seen Id Sequence Parameters for Identity ************"
sSeenidIdentity = SystemParameters.ParamsDataLoading()
sSeenidIdentity.input_files = iSeenidIdentity.input_files
sSeenidIdentity.num_images = iSeenidIdentity.num_images
sSeenidIdentity.image_width = 640
sSeenidIdentity.image_height = 480
sSeenidIdentity.subimage_width = 135
sSeenidIdentity.subimage_height = 135 
sSeenidIdentity.pixelsampling_x = 2
sSeenidIdentity.pixelsampling_y =  2
sSeenidIdentity.subimage_pixelsampling = 2
sSeenidIdentity.subimage_first_row =  sSeenidIdentity.image_height/2-sSeenidIdentity.subimage_height*sSeenidIdentity.pixelsampling_y/2
sSeenidIdentity.subimage_first_column = sSeenidIdentity.image_width/2-sSeenidIdentity.subimage_width*sSeenidIdentity.pixelsampling_x/2+ 5*sSeenidIdentity.pixelsampling_x
sSeenidIdentity.add_noise_L0 = False
sSeenidIdentity.convert_format = "L"
sSeenidIdentity.background_type = "black"
sSeenidIdentity.translation = 0
sSeenidIdentity.translations_x = numpy.random.random_integers(-sSeenidIdentity.translation, sSeenidIdentity.translation, sSeenidIdentity.num_images)
sSeenidIdentity.translations_y = numpy.random.random_integers(-sSeenidIdentity.translation, sSeenidIdentity.translation, sSeenidIdentity.num_images)
sSeenidIdentity.trans_sampled = False
SystemParameters.test_object_contents(sSeenidIdentity)


print "******** Setting New Id Information Parameters for Identity **********"
iNewidIdentity = SystemParameters.ParamsInput()
iNewidIdentity.name = "Identities20x500"
iNewidIdentity.data_base_dir =user_base_dir + "Alberto/Renderings20x500"
iNewidIdentity.ids = numpy.arange(18,20, dtype="int")
iNewidIdentity.ages = [999]
iNewidIdentity.MIN_GENDER = -3
iNewidIdentity.MAX_GENDER = 3
iNewidIdentity.GENDER_STEP = 0.10000 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
#iNewidIdentity.GENDER_STEP = 0.80075 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
iNewidIdentity.genders = map(imageLoader.code_gender, numpy.arange(iNewidIdentity.MIN_GENDER, iNewidIdentity.MAX_GENDER, iNewidIdentity.GENDER_STEP))
iNewidIdentity.racetweens = [999]
iNewidIdentity.expressions = [0]
iNewidIdentity.morphs = [0]
iNewidIdentity.poses = range(0,500)
iNewidIdentity.lightings = [0]
iNewidIdentity.slow_signal = 0
iNewidIdentity.step = 1
iNewidIdentity.offset = 0     

iNewidIdentity.input_files = imageLoader.create_image_filenames(iNewidIdentity.data_base_dir, iNewidIdentity.slow_signal, iNewidIdentity.ids, iNewidIdentity.expressions, iNewidIdentity.morphs, iNewidIdentity.poses, iNewidIdentity.lightings, iNewidIdentity.step, iNewidIdentity.offset)
iNewidIdentity.num_images = len(iNewidIdentity.input_files)
iNewidIdentity.params = [iNewidIdentity.ids, iNewidIdentity.expressions, iNewidIdentity.morphs, iNewidIdentity.poses, iNewidIdentity.lightings]
iNewidIdentity.block_size= iNewidIdentity.num_images / len(iNewidIdentity.params[iNewidIdentity.slow_signal])

iNewidIdentity.correct_classes = sfa_libs.wider_1Darray(iNewidIdentity.ids, iNewidIdentity.block_size)
iNewidIdentity.correct_labels = sfa_libs.wider_1Darray(iNewidIdentity.ids, iNewidIdentity.block_size)

SystemParameters.test_object_contents(iNewidIdentity)

print "******** Setting New Id Sequence Parameters for Identity *************"
sNewidIdentity = SystemParameters.ParamsDataLoading()
sNewidIdentity.input_files = iNewidIdentity.input_files
sNewidIdentity.num_images = iNewidIdentity.num_images
sNewidIdentity.image_width = 640
sNewidIdentity.image_height = 480
sNewidIdentity.subimage_width = 135
sNewidIdentity.subimage_height = 135 
sNewidIdentity.pixelsampling_x = 2
sNewidIdentity.pixelsampling_y =  2
sNewidIdentity.subimage_pixelsampling = 2
sNewidIdentity.subimage_first_row =  sNewidIdentity.image_height/2-sNewidIdentity.subimage_height*sNewidIdentity.pixelsampling_y/2
sNewidIdentity.subimage_first_column = sNewidIdentity.image_width/2-sNewidIdentity.subimage_width*sNewidIdentity.pixelsampling_x/2+ 5*sNewidIdentity.pixelsampling_x
sNewidIdentity.add_noise_L0 = False
sNewidIdentity.convert_format = "L"
sNewidIdentity.background_type = "black"
sNewidIdentity.translation = 0
sNewidIdentity.translations_x = numpy.random.random_integers(-sNewidIdentity.translation, sNewidIdentity.translation, sNewidIdentity.num_images)
sNewidIdentity.translations_y = numpy.random.random_integers(-sNewidIdentity.translation, sNewidIdentity.translation, sNewidIdentity.num_images)
sNewidIdentity.trans_sampled = False
SystemParameters.test_object_contents(sNewidIdentity)



####################################################################
###########        SYSTEM FOR IDENTITY RECOGNITION      ############
####################################################################  
ParamsIdentity = SystemParameters.ParamsSystem()
ParamsIdentity.name = "Network that extracts identity information"
ParamsIdentity.network = "linearNetwork4L"
ParamsIdentity.iTrain = iTrainIdentity
ParamsIdentity.sTrain = sTrainIdentity
ParamsIdentity.iSeenid = iSeenidIdentity
ParamsIdentity.sSeenid = sSeenidIdentity
ParamsIdentity.iNewid = iNewidIdentity
ParamsIdentity.sNewid = sNewidIdentity
ParamsIdentity.block_size = iTrainIdentity.block_size
ParamsIdentity.train_mode = 'clustered'
ParamsIdentity.analysis = None
        

print "******** Setting Train Information Parameters for Angle **************"
iTrainAngle = SystemParameters.ParamsInput()
iTrainAngle.name = "Angle20x500"
iTrainAngle.data_base_dir =user_base_dir + "Alberto/Renderings20x500"
iTrainAngle.ids = numpy.arange(0,18)
iTrainAngle.ages = [999]
#iTrainAngle.MIN_GENDER = -3
#iTrainAngle.MAX_GENDER = 3
#iTrainAngle.GENDER_STEP = 0.10000 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
#iTrainAngle.GENDER_STEP = 0.80075 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
#iTrainAngle.genders = map(imageLoader.code_gender, numpy.arange(iTrainAngle.MIN_GENDER, iTrainAngle.MAX_GENDER, iTrainAngle.GENDER_STEP))
iTrainAngle.genders = [999]
iTrainAngle.racetweens = [999]
iTrainAngle.expressions = [0]
iTrainAngle.morphs = [0]
iTrainAngle.real_poses = numpy.linspace(0, 90.0, 125) #0,90,500
iTrainAngle.poses = numpy.arange(0,500,4) #0,500
iTrainAngle.lightings = [0]
iTrainAngle.slow_signal = 3
iTrainAngle.step = 1 # 1
iTrainAngle.offset = 0     

iTrainAngle.input_files = imageLoader.create_image_filenames(iTrainAngle.data_base_dir, iTrainAngle.slow_signal, iTrainAngle.ids, iTrainAngle.expressions, iTrainAngle.morphs, iTrainAngle.poses, iTrainAngle.lightings, iTrainAngle.step, iTrainAngle.offset)
iTrainAngle.num_images = len(iTrainAngle.input_files)
iTrainAngle.params = [iTrainAngle.ids, iTrainAngle.expressions, iTrainAngle.morphs, iTrainAngle.poses, iTrainAngle.lightings]
iTrainAngle.block_size= iTrainAngle.num_images / len(iTrainAngle.params[iTrainAngle.slow_signal])

iTrainAngle.correct_classes = sfa_libs.wider_1Darray(iTrainAngle.poses, iTrainAngle.block_size)
iTrainAngle.correct_labels = sfa_libs.wider_1Darray(iTrainAngle.real_poses, iTrainAngle.block_size)

SystemParameters.test_object_contents(iTrainAngle)

print "***** Setting Train Sequence Parameters for Angle ********************"
sTrainAngle = SystemParameters.ParamsDataLoading()
sTrainAngle.input_files = iTrainAngle.input_files
sTrainAngle.num_images = iTrainAngle.num_images
sTrainAngle.image_width = 640
sTrainAngle.image_height = 480
sTrainAngle.subimage_width = 135
sTrainAngle.subimage_height = 135 
sTrainAngle.pixelsampling_x = 2
sTrainAngle.pixelsampling_y =  2
sTrainAngle.subimage_pixelsampling = 2
sTrainAngle.subimage_first_row =  sTrainAngle.image_height/2-sTrainAngle.subimage_height*sTrainAngle.pixelsampling_y/2
sTrainAngle.subimage_first_column = sTrainAngle.image_width/2-sTrainAngle.subimage_width*sTrainAngle.pixelsampling_x/2+ 5*sTrainAngle.pixelsampling_x
sTrainAngle.add_noise_L0 = False
sTrainAngle.convert_format = "L"
sTrainAngle.background_type = "black"
sTrainAngle.translation = 1
sTrainAngle.translations_x = numpy.random.random_integers(-sTrainAngle.translation, sTrainAngle.translation, sTrainAngle.num_images)
sTrainAngle.translations_y = numpy.random.random_integers(-sTrainAngle.translation, sTrainAngle.translation, sTrainAngle.num_images)
sTrainAngle.trans_sampled = False
SystemParameters.test_object_contents(sTrainAngle)


print "******** Setting Seen Id Information Parameters for Angle ************"
iSeenidAngle = SystemParameters.ParamsInput()
iSeenidAngle.name = "Angle20x500"
iSeenidAngle.data_base_dir =user_base_dir + "Alberto/Renderings20x500"
iSeenidAngle.ids = numpy.arange(0,18)
iSeenidAngle.ages = [999]
iSeenidAngle.MIN_GENDER = -3
iSeenidAngle.MAX_GENDER = 3
iSeenidAngle.GENDER_STEP = 0.10000 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
#iSeenidAngle.GENDER_STEP = 0.80075 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
iSeenidAngle.genders = map(imageLoader.code_gender, numpy.arange(iSeenidAngle.MIN_GENDER, iSeenidAngle.MAX_GENDER, iSeenidAngle.GENDER_STEP))
iSeenidAngle.racetweens = [999]
iSeenidAngle.expressions = [0]
iSeenidAngle.morphs = [0]
iSeenidAngle.real_poses = numpy.linspace(0,90.0,125) #0,90,500
iSeenidAngle.poses = numpy.arange(0,500, 4) #0,500
iSeenidAngle.lightings = [0]
iSeenidAngle.slow_signal = 3
iSeenidAngle.step = 1 # 1
iSeenidAngle.offset = 0

iSeenidAngle.input_files = imageLoader.create_image_filenames(iSeenidAngle.data_base_dir, iSeenidAngle.slow_signal, iSeenidAngle.ids, iSeenidAngle.expressions, iSeenidAngle.morphs, iSeenidAngle.poses, iSeenidAngle.lightings, iSeenidAngle.step, iSeenidAngle.offset)
iSeenidAngle.num_images = len(iSeenidAngle.input_files)
iSeenidAngle.params = [iSeenidAngle.ids, iSeenidAngle.expressions, iSeenidAngle.morphs, iSeenidAngle.poses, iSeenidAngle.lightings]
iSeenidAngle.block_size= iSeenidAngle.num_images / len(iSeenidAngle.params[iSeenidAngle.slow_signal])

iSeenidAngle.correct_classes = sfa_libs.wider_1Darray(iSeenidAngle.poses, iSeenidAngle.block_size)
iSeenidAngle.correct_labels = sfa_libs.wider_1Darray(iSeenidAngle.real_poses, iSeenidAngle.block_size)

SystemParameters.test_object_contents(iSeenidAngle)

print "******** Setting Seen Id Sequence Parameters for Angle ***************"
sSeenidAngle = SystemParameters.ParamsDataLoading()
sSeenidAngle.input_files = iSeenidAngle.input_files
sSeenidAngle.num_images = iSeenidAngle.num_images
sSeenidAngle.image_width = 640
sSeenidAngle.image_height = 480
sSeenidAngle.subimage_width = 135
sSeenidAngle.subimage_height = 135 
sSeenidAngle.pixelsampling_x = 2
sSeenidAngle.pixelsampling_y =  2
sSeenidAngle.subimage_pixelsampling = 2
sSeenidAngle.subimage_first_row =  sSeenidAngle.image_height/2-sSeenidAngle.subimage_height*sSeenidAngle.pixelsampling_y/2
sSeenidAngle.subimage_first_column = sSeenidAngle.image_width/2-sSeenidAngle.subimage_width*sSeenidAngle.pixelsampling_x/2+ 5*sSeenidAngle.pixelsampling_x
sSeenidAngle.add_noise_L0 = False
sSeenidAngle.convert_format = "L"
sSeenidAngle.background_type = "black"
sSeenidAngle.translation = 1
sSeenidAngle.translations_x = numpy.random.random_integers(-sSeenidAngle.translation, sSeenidAngle.translation, sSeenidAngle.num_images)
sSeenidAngle.translations_y = numpy.random.random_integers(-sSeenidAngle.translation, sSeenidAngle.translation, sSeenidAngle.num_images)
sSeenidAngle.trans_sampled = False
SystemParameters.test_object_contents(sSeenidAngle)


print "******** Setting New Id Information Parameters for Angle *************"
iNewidAngle = SystemParameters.ParamsInput()
iNewidAngle.name = "Angle20x500"
iNewidAngle.data_base_dir =user_base_dir + "Alberto/Renderings20x500"
iNewidAngle.ids = numpy.arange(18,20)
iNewidAngle.ages = [999]
iNewidAngle.MIN_GENDER = -3
iNewidAngle.MAX_GENDER = 3
iNewidAngle.GENDER_STEP = 0.10000 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
#iNewidAngle.GENDER_STEP = 0.80075 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
iNewidAngle.genders = map(imageLoader.code_gender, numpy.arange(iNewidAngle.MIN_GENDER, iNewidAngle.MAX_GENDER, iNewidAngle.GENDER_STEP))
iNewidAngle.racetweens = [999]
iNewidAngle.expressions = [0]
iNewidAngle.morphs = [0]
iNewidAngle.real_poses = numpy.linspace(0,90.0,500)
iNewidAngle.poses = numpy.arange(0,500)
iNewidAngle.lightings = [0]
iNewidAngle.slow_signal = 3
iNewidAngle.step = 1
iNewidAngle.offset = 0     

iNewidAngle.input_files = imageLoader.create_image_filenames(iNewidAngle.data_base_dir, iNewidAngle.slow_signal, iNewidAngle.ids, iNewidAngle.expressions, iNewidAngle.morphs, iNewidAngle.poses, iNewidAngle.lightings, iNewidAngle.step, iNewidAngle.offset)
iNewidAngle.num_images = len(iNewidAngle.input_files)
iNewidAngle.params = [iNewidAngle.ids, iNewidAngle.expressions, iNewidAngle.morphs, iNewidAngle.poses, iNewidAngle.lightings]
iNewidAngle.block_size= iNewidAngle.num_images / len(iNewidAngle.params[iNewidAngle.slow_signal])

iNewidAngle.correct_classes = sfa_libs.wider_1Darray(iNewidAngle.poses, iNewidAngle.block_size)
iNewidAngle.correct_labels = sfa_libs.wider_1Darray(iNewidAngle.real_poses, iNewidAngle.block_size)

SystemParameters.test_object_contents(iNewidAngle)

print "******** Setting New Id Sequence Parameters for Angle ****************"
sNewidAngle = SystemParameters.ParamsDataLoading()
sNewidAngle.input_files = iNewidAngle.input_files
sNewidAngle.num_images = iNewidAngle.num_images
sNewidAngle.image_width = 640
sNewidAngle.image_height = 480
sNewidAngle.subimage_width = 135
sNewidAngle.subimage_height = 135 
sNewidAngle.pixelsampling_x = 2
sNewidAngle.pixelsampling_y =  2
sNewidAngle.subimage_pixelsampling = 2
sNewidAngle.subimage_first_row =  sNewidAngle.image_height/2-sNewidAngle.subimage_height*sNewidAngle.pixelsampling_y/2
sNewidAngle.subimage_first_column = sNewidAngle.image_width/2-sNewidAngle.subimage_width*sNewidAngle.pixelsampling_x/2+ 5*sNewidAngle.pixelsampling_x
sNewidAngle.add_noise_L0 = False
sNewidAngle.convert_format = "L"
sNewidAngle.background_type = "black"
sNewidAngle.translation = 1
sNewidAngle.translations_x = numpy.random.random_integers(-sNewidAngle.translation, sNewidAngle.translation, sNewidAngle.num_images)
sNewidAngle.translations_y = numpy.random.random_integers(-sNewidAngle.translation, sNewidAngle.translation, sNewidAngle.num_images)
sNewidAngle.trans_sampled = False
SystemParameters.test_object_contents(sNewidAngle)



####################################################################
###########        SYSTEM FOR ANGLE RECOGNITION      ############
####################################################################  
ParamsAngle = SystemParameters.ParamsSystem()
ParamsAngle.name = "Network that extracts Angle information"
ParamsAngle.network = "linearNetwork4L"
ParamsAngle.iTrain = iTrainAngle
ParamsAngle.sTrain = sTrainAngle
ParamsAngle.iSeenid = iSeenidAngle
ParamsAngle.sSeenid = sSeenidAngle
ParamsAngle.iNewid = iNewidAngle
ParamsAngle.sNewid = sNewidAngle
ParamsAngle.block_size = iTrainAngle.block_size
ParamsAngle.train_mode = 'mixed'
ParamsAngle.analysis = None





print "***** Setting Training Information Parameters for Translation X ******"
iTrainTransX = SystemParameters.ParamsInput()
iTrainTransX.name = "Translation X: 60Genders x 200 identities"
iTrainTransX.data_base_dir = user_base_dir + "Alberto/RenderingsGender60x200"
iTrainTransX.ids = numpy.arange(0,150) # 160
iTrainTransX.trans = numpy.arange(-50, 50, 2)
if len(iTrainTransX.ids) % len(iTrainTransX.trans) != 0:
    ex="Here the number of translations must be a divisor of the number of identities"
    raise Exception(ex)
iTrainTransX.ages = [999]
iTrainTransX.MIN_GENDER= -3
iTrainTransX.MAX_GENDER = 3
iTrainTransX.GENDER_STEP = 0.10000 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
#iTrainTransX.TransX_STEP = 0.80075 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
iTrainTransX.real_genders = numpy.arange(iTrainTransX.MIN_GENDER, iTrainTransX.MAX_GENDER, iTrainTransX.GENDER_STEP)
iTrainTransX.genders = map(imageLoader.code_gender, iTrainTransX.real_genders)
iTrainTransX.racetweens = [999]
iTrainTransX.expressions = [0]
iTrainTransX.morphs = [0]
iTrainTransX.poses = [0]
iTrainTransX.lightings = [0]
iTrainTransX.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iTrainTransX.step = 1
iTrainTransX.offset = 0
iTrainTransX.input_files = imageLoader.create_image_filenames2(iTrainTransX.data_base_dir, iTrainTransX.slow_signal, iTrainTransX.ids, iTrainTransX.ages, \
                                            iTrainTransX.genders, iTrainTransX.racetweens, iTrainTransX.expressions, iTrainTransX.morphs, \
                                            iTrainTransX.poses, iTrainTransX.lightings, iTrainTransX.step, iTrainTransX.offset)
#MEGAWARNING!!!!
#iTrainTransX.input_files = iTrainTransX.input_files
#numpy.random.shuffle(iTrainTransX.input_files)  
#numpy.random.shuffle(iTrainTransX.input_files)  

iTrainTransX.num_images = len(iTrainTransX.input_files)
#iTrainTransX.params = [ids, expressions, morphs, poses, lightings]
iTrainTransX.params = [iTrainTransX.ids, iTrainTransX.ages, iTrainTransX.genders, iTrainTransX.racetweens, iTrainTransX.expressions, \
                  iTrainTransX.morphs, iTrainTransX.poses, iTrainTransX.lightings]
iTrainTransX.block_size = iTrainTransX.num_images / len (iTrainTransX.trans)
#print "Blocksize = ", iTrainTransX.block_size
#quit()

iTrainTransX.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iTrainTransX.trans)), iTrainTransX.block_size)
iTrainTransX.correct_labels = sfa_libs.wider_1Darray(iTrainTransX.trans, iTrainTransX.block_size)

SystemParameters.test_object_contents(iTrainTransX)

print "******** Setting Training Data Parameters for TransX  ****************"
sTrainTransX = SystemParameters.ParamsDataLoading()
sTrainTransX.input_files = iTrainTransX.input_files
sTrainTransX.num_images = iTrainTransX.num_images
sTrainTransX.block_size = iTrainTransX.block_size
sTrainTransX.image_width = 256
sTrainTransX.image_height = 192
sTrainTransX.subimage_width = 135
sTrainTransX.subimage_height = 135 
sTrainTransX.pixelsampling_x = 1
sTrainTransX.pixelsampling_y =  1
sTrainTransX.subimage_pixelsampling = 2
sTrainTransX.subimage_first_row =  sTrainTransX.image_height/2-sTrainTransX.subimage_height*sTrainTransX.pixelsampling_y/2
sTrainTransX.subimage_first_column = sTrainTransX.image_width/2-sTrainTransX.subimage_width*sTrainTransX.pixelsampling_x/2
#sTrainTransX.subimage_first_column = sTrainTransX.image_width/2-sTrainTransX.subimage_width*sTrainTransX.pixelsampling_x/2+ 5*sTrainTransX.pixelsampling_x
sTrainTransX.add_noise_L0 = True
sTrainTransX.convert_format = "L"
sTrainTransX.background_type = "black"
sTrainTransX.translation = 25
#sTrainTransX.translations_x = numpy.random.random_integers(-sTrainTransX.translation, sTrainTransX.translation, sTrainTransX.num_images)                                                           
sTrainTransX.translations_x = sfa_libs.wider_1Darray(iTrainTransX.trans, iTrainTransX.block_size)
sTrainTransX.translations_y = numpy.random.random_integers(-sTrainTransX.translation, sTrainTransX.translation, sTrainTransX.num_images)
sTrainTransX.trans_sampled = False
SystemParameters.test_object_contents(sTrainTransX)

print "***** Setting Seen ID Information Parameters for Translation X *******"
iSeenidTransX = SystemParameters.ParamsInput()
iSeenidTransX.name = "Test Translation X: 60Genders x 200 identities, dx = 1 pixel"
iSeenidTransX.data_base_dir = user_base_dir + "Alberto/RenderingsGender60x200"
iSeenidTransX.ids = numpy.arange(0,50) # 160
iSeenidTransX.trans = iTrainTransX.trans + 1
if len(iSeenidTransX.ids) % len(iSeenidTransX.trans) != 0:
    ex="Here the number of translations must be a divisor of the number of identities"
    raise Exception(ex)
iSeenidTransX.ages = [999]
iSeenidTransX.MIN_GENDER= -3
iSeenidTransX.MAX_GENDER = 3
iSeenidTransX.GENDER_STEP = 0.10000 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
#iSeenidTransX.TransX_STEP = 0.80075 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
iSeenidTransX.real_genders = numpy.arange(iSeenidTransX.MIN_GENDER, iSeenidTransX.MAX_GENDER, iSeenidTransX.GENDER_STEP)
iSeenidTransX.genders = map(imageLoader.code_gender, iSeenidTransX.real_genders)
iSeenidTransX.racetweens = [999]
iSeenidTransX.expressions = [0]
iSeenidTransX.morphs = [0]
iSeenidTransX.poses = [0]
iSeenidTransX.lightings = [0]
iSeenidTransX.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iSeenidTransX.step = 1
iSeenidTransX.offset = 0
iSeenidTransX.input_files = imageLoader.create_image_filenames2(iSeenidTransX.data_base_dir, iSeenidTransX.slow_signal, iSeenidTransX.ids, iSeenidTransX.ages, \
                                            iSeenidTransX.genders, iSeenidTransX.racetweens, iSeenidTransX.expressions, iSeenidTransX.morphs, \
                                            iSeenidTransX.poses, iSeenidTransX.lightings, iSeenidTransX.step, iSeenidTransX.offset)
#MEGAWARNING!!!!
#numpy.random.shuffle(iSeenidTransX.input_files)  
#numpy.random.shuffle(iSeenidTransX.input_files)  

iSeenidTransX.num_images = len(iSeenidTransX.input_files)
#iSeenidTransX.params = [ids, expressions, morphs, poses, lightings]
iSeenidTransX.params = [iSeenidTransX.ids, iSeenidTransX.ages, iSeenidTransX.genders, iSeenidTransX.racetweens, iSeenidTransX.expressions, \
                  iSeenidTransX.morphs, iSeenidTransX.poses, iSeenidTransX.lightings]
iSeenidTransX.block_size = iSeenidTransX.num_images / len (iSeenidTransX.trans)

iSeenidTransX.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeenidTransX.trans)), iSeenidTransX.block_size)
iSeenidTransX.correct_labels = sfa_libs.wider_1Darray(iSeenidTransX.trans, iSeenidTransX.block_size)

SystemParameters.test_object_contents(iSeenidTransX)

print "******** Setting Seen Id Data Parameters for TransX  *****************"
sSeenidTransX = SystemParameters.ParamsDataLoading()
sSeenidTransX.input_files = iSeenidTransX.input_files
sSeenidTransX.num_images = iSeenidTransX.num_images
sSeenidTransX.block_size = iSeenidTransX.block_size
sSeenidTransX.image_width = 256
sSeenidTransX.image_height = 192
sSeenidTransX.subimage_width = 135
sSeenidTransX.subimage_height = 135 
sSeenidTransX.pixelsampling_x = 1
sSeenidTransX.pixelsampling_y =  1
sSeenidTransX.subimage_pixelsampling = 2
sSeenidTransX.subimage_first_row =  sSeenidTransX.image_height/2-sSeenidTransX.subimage_height*sSeenidTransX.pixelsampling_y/2
sSeenidTransX.subimage_first_column = sSeenidTransX.image_width/2-sSeenidTransX.subimage_width*sSeenidTransX.pixelsampling_x/2
#sSeenidTransX.subimage_first_column = sSeenidTransX.image_width/2-sSeenidTransX.subimage_width*sSeenidTransX.pixelsampling_x/2+ 5*sSeenidTransX.pixelsampling_x
sSeenidTransX.add_noise_L0 = True
sSeenidTransX.convert_format = "L"
sSeenidTransX.background_type = "black"
sSeenidTransX.translation = 20
#sSeenidTransX.translations_x = numpy.random.random_integers(-sSeenidTransX.translation, sSeenidTransX.translation, sSeenidTransX.num_images)                                                           
sSeenidTransX.translations_x = sfa_libs.wider_1Darray(iSeenidTransX.trans, iSeenidTransX.block_size)
sSeenidTransX.translations_y = numpy.random.random_integers(-sSeenidTransX.translation, sSeenidTransX.translation, sSeenidTransX.num_images)
sSeenidTransX.trans_sampled = False
SystemParameters.test_object_contents(sSeenidTransX)


print "******** Setting New Id Information Parameters for Translation X *****"
iNewidTransX = SystemParameters.ParamsInput()
iNewidTransX.name = "New ID Translation X: 60Genders x 200 identities, dx = 1 pixel"
iNewidTransX.data_base_dir =user_base_dir + "Alberto/RenderingsGender60x200"
iNewidTransX.ids = numpy.arange(150,200) # 160
iNewidTransX.trans = numpy.arange(-50,50,2)
if len(iNewidTransX.ids) % len(iNewidTransX.trans) != 0:
    ex="Here the number of translations must be a divisor of the number of identities"
    raise Exception(ex)
iNewidTransX.ages = [999]
iNewidTransX.MIN_GENDER= -3
iNewidTransX.MAX_GENDER = 3
iNewidTransX.GENDER_STEP = 0.10000 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
#iNewidTransX.TransX_STEP = 0.80075 #01. default. 0.4 fails, use 0.4005, 0.80075, 0.9005
iNewidTransX.real_genders = numpy.arange(iNewidTransX.MIN_GENDER, iNewidTransX.MAX_GENDER, iNewidTransX.GENDER_STEP)
iNewidTransX.genders = map(imageLoader.code_gender, iNewidTransX.real_genders)
iNewidTransX.racetweens = [999]
iNewidTransX.expressions = [0]
iNewidTransX.morphs = [0]
iNewidTransX.poses = [0]
iNewidTransX.lightings = [0]
iNewidTransX.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iNewidTransX.step = 1
iNewidTransX.offset = 0
iNewidTransX.input_files = imageLoader.create_image_filenames2(iNewidTransX.data_base_dir, iNewidTransX.slow_signal, iNewidTransX.ids, iNewidTransX.ages, \
                                            iNewidTransX.genders, iNewidTransX.racetweens, iNewidTransX.expressions, iNewidTransX.morphs, \
                                            iNewidTransX.poses, iNewidTransX.lightings, iNewidTransX.step, iNewidTransX.offset)
#MEGAWARNING!!!!
#iNewidTransX.input_files = iNewidTransX.input_files
#numpy.random.shuffle(iNewidTransX.input_files)  
#numpy.random.shuffle(iNewidTransX.input_files)  

iNewidTransX.num_images = len(iNewidTransX.input_files)
#iNewidTransX.params = [ids, expressions, morphs, poses, lightings]
iNewidTransX.params = [iNewidTransX.ids, iNewidTransX.ages, iNewidTransX.genders, iNewidTransX.racetweens, iNewidTransX.expressions, \
                  iNewidTransX.morphs, iNewidTransX.poses, iNewidTransX.lightings]
iNewidTransX.block_size = iNewidTransX.num_images / len (iNewidTransX.trans)

iNewidTransX.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iNewidTransX.trans)), iNewidTransX.block_size)
iNewidTransX.correct_labels = sfa_libs.wider_1Darray(iNewidTransX.trans, iNewidTransX.block_size)

SystemParameters.test_object_contents(iNewidTransX)

print "******** Setting Seen Id Data Parameters for TransX  *****************"
sNewidTransX = SystemParameters.ParamsDataLoading()
sNewidTransX.input_files = iNewidTransX.input_files
sNewidTransX.num_images = iNewidTransX.num_images
sNewidTransX.block_size = iNewidTransX.block_size
sNewidTransX.image_width = 256
sNewidTransX.image_height = 192
sNewidTransX.subimage_width = 135
sNewidTransX.subimage_height = 135 
sNewidTransX.pixelsampling_x = 1
sNewidTransX.pixelsampling_y =  1
sNewidTransX.subimage_pixelsampling = 2
sNewidTransX.subimage_first_row =  sNewidTransX.image_height/2-sNewidTransX.subimage_height*sNewidTransX.pixelsampling_y/2
sNewidTransX.subimage_first_column = sNewidTransX.image_width/2-sNewidTransX.subimage_width*sNewidTransX.pixelsampling_x/2
#sNewidTransX.subimage_first_column = sNewidTransX.image_width/2-sNewidTransX.subimage_width*sNewidTransX.pixelsampling_x/2+ 5*sNewidTransX.pixelsampling_x
sNewidTransX.add_noise_L0 = True
sNewidTransX.convert_format = "L"
sNewidTransX.background_type = "black"
sNewidTransX.translation = 25 #20
#sNewidTransX.translations_x = numpy.random.random_integers(-sNewidTransX.translation, sNewidTransX.translation, sNewidTransX.num_images)                                                           
sNewidTransX.translations_x = sfa_libs.wider_1Darray(iNewidTransX.trans, iNewidTransX.block_size)
sNewidTransX.translations_y = numpy.random.random_integers(-sNewidTransX.translation, sNewidTransX.translation, sNewidTransX.num_images)
sNewidTransX.trans_sampled = False
SystemParameters.test_object_contents(sNewidTransX)


####################################################################
###########    SYSTEM FOR TRANSLATION_X EXTRACTION      ############
####################################################################  
ParamsTransX = SystemParameters.ParamsSystem()
ParamsTransX.name = "Network that extracts TransX information"
ParamsTransX.network = "linearNetwork4L"
ParamsTransX.iTrain = iTrainTransX
ParamsTransX.sTrain = sTrainTransX
ParamsTransX.iSeenid = iSeenidTransX
ParamsTransX.sSeenid = sSeenidTransX
ParamsTransX.iNewid = iNewidTransX
ParamsTransX.sNewid = sNewidTransX
ParamsTransX.block_size = iTrainTransX.block_size
ParamsTransX.train_mode = 'mixed'
ParamsTransX.analysis = None




print "***** Setting Training Information Parameters for Age (simulated faces) ******"
iTrainAge = SystemParameters.ParamsInput()
iTrainAge.name = "Age: 23 Ages x 200 identities"
iTrainAge.data_base_dir =user_base_dir + "Alberto/RendersAge200x23"
iTrainAge.im_base_name = "age"
iTrainAge.ids = numpy.arange(0,180) # 180, warning speeding up
#Available ages: iTrainAge.ages = [15, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 35, 36, 40, 42, 44, 45, 46, 48, 50, 55, 60, 65]
iTrainAge.ages = numpy.array([15, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 35, 36, 40, 42, 44, 45, 46, 48, 50, 55, 60, 65])
#iTrainAge.ages = numpy.array([15, 20, 24, 30, 35, 40, 45, 50, 55, 60, 65])
iTrainAge.genders = [None]
iTrainAge.racetweens = [None]
iTrainAge.expressions = [0]
iTrainAge.morphs = [0]
iTrainAge.poses = [0]
iTrainAge.lightings = [0]
iTrainAge.slow_signal = 1 
iTrainAge.step = 1 
iTrainAge.offset = 0
iTrainAge.input_files = imageLoader.create_image_filenames3(iTrainAge.data_base_dir, iTrainAge.im_base_name, iTrainAge.slow_signal, iTrainAge.ids, iTrainAge.ages, \
                                            iTrainAge.genders, iTrainAge.racetweens, iTrainAge.expressions, iTrainAge.morphs, \
                                            iTrainAge.poses, iTrainAge.lightings, iTrainAge.step, iTrainAge.offset, verbose=False)

#print "Filenames = ", iTrainAge.input_files
iTrainAge.num_images = len(iTrainAge.input_files)
#print "Num Images = ", iTrainAge.num_images
#iTrainAge.params = [ids, expressions, morphs, poses, lightings]
iTrainAge.params = [iTrainAge.ids, iTrainAge.ages, iTrainAge.genders, iTrainAge.racetweens, iTrainAge.expressions, \
                  iTrainAge.morphs, iTrainAge.poses, iTrainAge.lightings]
iTrainAge.block_size = iTrainAge.num_images / len (iTrainAge.ages)

iTrainAge.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iTrainAge.ages)), iTrainAge.block_size)
iTrainAge.correct_labels = sfa_libs.wider_1Darray(iTrainAge.ages, iTrainAge.block_size)

SystemParameters.test_object_contents(iTrainAge)

print "******** Setting Training Data Parameters for Age  ****************"
sTrainAge = SystemParameters.ParamsDataLoading()
sTrainAge.input_files = iTrainAge.input_files
sTrainAge.num_images = iTrainAge.num_images
sTrainAge.block_size = iTrainAge.block_size
sTrainAge.image_width = 256
sTrainAge.image_height = 192
sTrainAge.subimage_width = 135
sTrainAge.subimage_height = 135 
sTrainAge.pixelsampling_x = 1
sTrainAge.pixelsampling_y =  1
sTrainAge.subimage_pixelsampling = 2
sTrainAge.subimage_first_row =  sTrainAge.image_height/2-sTrainAge.subimage_height*sTrainAge.pixelsampling_y/2
sTrainAge.subimage_first_column = sTrainAge.image_width/2-sTrainAge.subimage_width*sTrainAge.pixelsampling_x/2
#sTrainAge.subimage_first_column = sTrainAge.image_width/2-sTrainAge.subimage_width*sTrainAge.pixelsampling_x/2+ 5*sTrainAge.pixelsampling_x
sTrainAge.add_noise_L0 = True
sTrainAge.convert_format = "L"
sTrainAge.background_type = "blue"
sTrainAge.translation = 1
#sTrainAge.translations_x = numpy.random.random_integers(-sTrainAge.translation, sTrainAge.translation, sTrainAge.num_images)                                                           
sTrainAge.translations_x = numpy.random.random_integers(-sTrainAge.translation, sTrainAge.translation, sTrainAge.num_images)
sTrainAge.translations_y = numpy.random.random_integers(-sTrainAge.translation, sTrainAge.translation, sTrainAge.num_images)
sTrainAge.trans_sampled = False
sTrainAge.train_mode = 'mixed'
sTrainAge.name = iTrainAge.name
sTrainAge.load_data = load_data_from_sSeq
SystemParameters.test_object_contents(sTrainAge)


print "***** Setting Seen Id Test Information Parameters for Age ******"
iSeenidAge = SystemParameters.ParamsInput()
iSeenidAge.name = "Age: 23 Ages x 200 identities"
iSeenidAge.data_base_dir =user_base_dir + "Alberto/RendersAge200x23"
iSeenidAge.im_base_name = "age"
iSeenidAge.ids = numpy.arange(0,180) # 180
#Available ages: iSeenidAge.ages = numpy.array([15, 16, 18, 20, 22, 24, 25, 26, 28, 30, 32, 34, 35, 36, 40, 42, 44, 45, 46, 48, 50, 55, 60, 65])
iSeenidAge.ages = numpy.array([15, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 35, 36, 40, 42, 44, 45, 46, 48, 50, 55, 60, 65])
#iSeenidAge.ages = numpy.array([15, 20, 24, 30, 35, 40, 45, 50, 55, 60, 65])
iSeenidAge.genders = [None]
iSeenidAge.racetweens = [None]
iSeenidAge.expressions = [0]
iSeenidAge.morphs = [0]
iSeenidAge.poses = [0]
iSeenidAge.lightings = [0]
iSeenidAge.slow_signal = 1 
iSeenidAge.step = 1
iSeenidAge.offset = 0
iSeenidAge.input_files = imageLoader.create_image_filenames3(iSeenidAge.data_base_dir, iSeenidAge.im_base_name, iSeenidAge.slow_signal, iSeenidAge.ids, iSeenidAge.ages, \
                                            iSeenidAge.genders, iSeenidAge.racetweens, iSeenidAge.expressions, iSeenidAge.morphs, \
                                            iSeenidAge.poses, iSeenidAge.lightings, iSeenidAge.step, iSeenidAge.offset)

iSeenidAge.num_images = len(iSeenidAge.input_files)
#iSeenidAge.params = [ids, expressions, morphs, poses, lightings]
iSeenidAge.params = [iSeenidAge.ids, iSeenidAge.ages, iSeenidAge.genders, iSeenidAge.racetweens, iSeenidAge.expressions, \
                  iSeenidAge.morphs, iSeenidAge.poses, iSeenidAge.lightings]
iSeenidAge.block_size = iSeenidAge.num_images / len (iSeenidAge.ages)

iSeenidAge.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeenidAge.ages)), iSeenidAge.block_size)
iSeenidAge.correct_labels = sfa_libs.wider_1Darray(iSeenidAge.ages, iSeenidAge.block_size)

SystemParameters.test_object_contents(iSeenidAge)

print "******** Setting Seen Id Data Parameters for Age  ****************"
sSeenidAge = SystemParameters.ParamsDataLoading()
sSeenidAge.input_files = iSeenidAge.input_files
sSeenidAge.num_images = iSeenidAge.num_images
sSeenidAge.block_size = iSeenidAge.block_size
sSeenidAge.image_width = 256
sSeenidAge.image_height = 192
sSeenidAge.subimage_width = 135
sSeenidAge.subimage_height = 135 
sSeenidAge.pixelsampling_x = 1
sSeenidAge.pixelsampling_y =  1
sSeenidAge.subimage_pixelsampling = 2
sSeenidAge.subimage_first_row =  sSeenidAge.image_height/2-sSeenidAge.subimage_height*sSeenidAge.pixelsampling_y/2
sSeenidAge.subimage_first_column = sSeenidAge.image_width/2-sSeenidAge.subimage_width*sSeenidAge.pixelsampling_x/2
#sSeenidAge.subimage_first_column = sSeenidAge.image_width/2-sSeenidAge.subimage_width*sSeenidAge.pixelsampling_x/2+ 5*sSeenidAge.pixelsampling_x
sSeenidAge.add_noise_L0 = True
sSeenidAge.convert_format = "L"
sSeenidAge.background_type = "blue"
sSeenidAge.translation = 1
#sSeenidAge.translations_x = numpy.random.random_integers(-sSeenidAge.translation, sSeenidAge.translation, sSeenidAge.num_images)                                                           
sSeenidAge.translations_x = numpy.random.random_integers(-sSeenidAge.translation, sSeenidAge.translation, sSeenidAge.num_images)
sSeenidAge.translations_y = numpy.random.random_integers(-sSeenidAge.translation, sSeenidAge.translation, sSeenidAge.num_images)
sSeenidAge.trans_sampled = False
sSeenidAge.name = iSeenidAge.name
sSeenidAge.load_data = load_data_from_sSeq
SystemParameters.test_object_contents(sSeenidAge)


print "***** Setting New Id Test Information Parameters for Age ******"
iNewidAge = SystemParameters.ParamsInput()
iNewidAge.name = "Age: 23 Ages x 200 identities"
iNewidAge.data_base_dir =user_base_dir + "Alberto/RendersAge200x23"
iNewidAge.im_base_name = "age"
iNewidAge.ids = numpy.arange(180,200) # 180,200
#Available ages: iNewidAge.ages = numpy.array([15, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 35, 36, 40, 42, 44, 45, 46, 48, 50, 55, 60, 65])
iNewidAge.ages = numpy.array([15, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 35, 36, 40, 42, 44, 45, 46, 48, 50, 55, 60, 65])
#iNewidAge.ages = numpy.array([15, 20, 24, 30, 35, 40, 45, 50, 55, 60, 65])
iNewidAge.genders = [None]
iNewidAge.racetweens = [None]
iNewidAge.expressions = [0]
iNewidAge.morphs = [0]
iNewidAge.poses = [0]
iNewidAge.lightings = [0]
iNewidAge.slow_signal = 1 
iNewidAge.step = 1
iNewidAge.offset = 0
iNewidAge.input_files = imageLoader.create_image_filenames3(iNewidAge.data_base_dir, iNewidAge.im_base_name, iNewidAge.slow_signal, iNewidAge.ids, iNewidAge.ages, \
                                            iNewidAge.genders, iNewidAge.racetweens, iNewidAge.expressions, iNewidAge.morphs, \
                                            iNewidAge.poses, iNewidAge.lightings, iNewidAge.step, iNewidAge.offset)

iNewidAge.num_images = len(iNewidAge.input_files)
#iNewidAge.params = [ids, expressions, morphs, poses, lightings]
iNewidAge.params = [iNewidAge.ids, iNewidAge.ages, iNewidAge.genders, iNewidAge.racetweens, iNewidAge.expressions, \
                  iNewidAge.morphs, iNewidAge.poses, iNewidAge.lightings]
iNewidAge.block_size = iNewidAge.num_images / len (iNewidAge.ages)

iNewidAge.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iNewidAge.ages)), iNewidAge.block_size)
iNewidAge.correct_labels = sfa_libs.wider_1Darray(iNewidAge.ages, iNewidAge.block_size)

SystemParameters.test_object_contents(iNewidAge)

print "******** Setting Training Data Parameters for Age  ****************"
sNewidAge = SystemParameters.ParamsDataLoading()
sNewidAge.input_files = iNewidAge.input_files
sNewidAge.num_images = iNewidAge.num_images
sNewidAge.block_size = iNewidAge.block_size
sNewidAge.image_width = 256
sNewidAge.image_height = 192
sNewidAge.subimage_width = 135
sNewidAge.subimage_height = 135 
sNewidAge.pixelsampling_x = 1
sNewidAge.pixelsampling_y =  1
sNewidAge.subimage_pixelsampling = 2
sNewidAge.subimage_first_row =  sNewidAge.image_height/2-sNewidAge.subimage_height*sNewidAge.pixelsampling_y/2
sNewidAge.subimage_first_column = sNewidAge.image_width/2-sNewidAge.subimage_width*sNewidAge.pixelsampling_x/2
#sNewidAge.subimage_first_column = sNewidAge.image_width/2-sNewidAge.subimage_width*sNewidAge.pixelsampling_x/2+ 5*sNewidAge.pixelsampling_x
sNewidAge.add_noise_L0 = True
sNewidAge.convert_format = "L"
sNewidAge.background_type = "blue"
sNewidAge.translation = 1
#sNewidAge.translations_x = numpy.random.random_integers(-sNewidAge.translation, sNewidAge.translation, sNewidAge.num_images)                                                           
sNewidAge.translations_x = numpy.random.random_integers(-sNewidAge.translation, sNewidAge.translation, sNewidAge.num_images)
sNewidAge.translations_y = numpy.random.random_integers(-sNewidAge.translation, sNewidAge.translation, sNewidAge.num_images)
sNewidAge.trans_sampled = False
sNewidAge.name = iNewidAge.name
sNewidAge.load_data = load_data_from_sSeq
SystemParameters.test_object_contents(sNewidAge)


####################################################################
###########    SYSTEM FOR AGE EXTRACTION      ############
####################################################################  
ParamsAge = SystemParameters.ParamsSystem()
ParamsAge.name = "Network that extracts Age information"
ParamsAge.network = "linearNetwork4L"
ParamsAge.iTrain = [[iTrainAge]]
ParamsAge.sTrain = [[sTrainAge]]
ParamsAge.iSeenid = iSeenidAge
ParamsAge.sSeenid = sSeenidAge
ParamsAge.iNewid = [[iNewidAge]]
ParamsAge.sNewid = [[sNewidAge]]
ParamsAge.block_size = iTrainAge.block_size
ParamsAge.train_mode = 'mixed'
ParamsAge.analysis = None
ParamsAge.enable_reduced_image_sizes = False
ParamsAge.reduction_factor = 1.0
ParamsAge.hack_image_size = 128
ParamsAge.enable_hack_image_size = True


#PIPELINE FOR FACE DETECTION:
#Orig=TX: DX0=+/- 45, DY0=+/- 20, DS0= 0.55-1.1
#TY: DX1=+/- 20, DY0=+/- 20, DS0= 0.55-1.1
#S: DX1=+/- 20, DY1=+/- 10, DS0= 0.55-1.1
#TMX: DX1=+/- 20, DY1=+/- 10, DS1= 0.775-1.05
#TMY: DX2=+/- 10, DY1=+/- 10, DS1= 0.775-1.05
#MS: DX2=+/- 10, DY2=+/- 5, DS1= 0.775-1.05
#Out About: DX2=+/- 10, DY2=+/- 5, DS2= 0.8875-1.025
#notice: for dx* and dy* intervals are open, while for smin and smax intervals are closed
pipeline_fd = dict(dx0 = 45, dy0 = 20, smin0 = 0.55, smax0 = 1.1,
                dx1 = 20, dy1 = 10, smin1 = 0.775, smax1 = 1.05)
#Pipeline actually supports inputs in: [-dx0, dx0-2] [-dy0, dy0-2] [smin0, smax0] 
#Remember these values are before image resizing

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#This network actually supports images in the closed intervals: [smin0, smax0] [-dy0, dy0]
#but halb-open [-dx0, dx0) 
print "***** Setting Training Information Parameters for Real Translation X ******"
iSeq = iTrainRTransX = SystemParameters.ParamsInput()
iSeq.name = "Real Translation X: (-45, 45, 2) translation and y 40"
iSeq.data_base_dir = frgc_normalized_base_dir
iSeq.ids = numpy.arange(0,7965) # 8000, 7965

iSeq.trans = numpy.arange(-1 * pipeline_fd['dx0'], pipeline_fd['dx0'], 2) # (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.trans) != 0:
    ex="Here the number of translations must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=4, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * 4 # warning!!! 4, 8
#To avoid grouping similar images next to one other
numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.trans)
print "BLOCK SIZE =", iSeq.block_size 
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.trans)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Real TransX  ****************"
sSeq = sTrainRTransX = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 128
sSeq.subimage_height = 128 


sSeq.trans_x_max = pipeline_fd['dx0']
sSeq.trans_x_min = -1 * pipeline_fd['dx0']

#WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
sSeq.trans_y_max = pipeline_fd['dy0']
sSeq.trans_y_min = -1 * sSeq.trans_y_max

#iSeq.scales = numpy.linspace(0.5, 1.30, 16) # (-50, 50, 2)
sSeq.min_sampling = pipeline_fd['smin0']
sSeq.max_sampling = pipeline_fd['smax0']

sSeq.pixelsampling_x = sSeq.pixelsampling_y = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
#sSeq.subimage_pixelsampling = 2
sSeq.subimage_first_row =  sSeq.image_height/2.0-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2.0-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coordinate
#sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
#sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)                                                           
sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.translations_y = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, sSeq.num_images)
sSeq.trans_sampled = True
sSeq.name = "RTans X Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
SystemParameters.test_object_contents(sSeq)

print "***** Setting Seen ID Information Parameters for Real Translation X *******"
iSeq = sSeq = None
iSeq = iSeenidRTransX = SystemParameters.ParamsInput()
iSeq.name = "Test Real Translation X: (-45, 45, 2) translation"
iSeq.data_base_dir = frgc_normalized_base_dir
iSeq.ids = numpy.arange(8000,8990) # WARNING 8900
iSeq.trans = numpy.arange(sTrainRTransX.trans_x_min, sTrainRTransX.trans_x_max, 2) #WARNING!!!! (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.trans) != 0:
    ex="Here the number of translations must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=4, image_postfix=".jpg")

iSeq.input_files = iSeq.input_files * 16 # Warning!!! 16, 32
numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.trans)

iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.trans)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Seen Id Data Parameters for Real TransX  ****************"
sSeq = sSeenidRTransX = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 128
sSeq.subimage_height = 128 
sSeq.trans_x_max = sTrainRTransX.trans_x_max
sSeq.trans_x_min = sTrainRTransX.trans_x_min
sSeq.trans_y_max = sTrainRTransX.trans_y_max
sSeq.trans_y_min = sTrainRTransX.trans_y_min
#iSeq.scales = numpy.linspace(0.5, 1.30, 16) # (-50, 50, 2)
sSeq.min_sampling = sTrainRTransX.min_sampling
sSeq.max_sampling = sTrainRTransX.max_sampling
sSeq.pixelsampling_x = sSeq.pixelsampling_y = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
#sSeq.subimage_pixelsampling = 2
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coordinate
#sSeq.translation = 20 #25, 20, WARNING!!!!!!!
#sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)                                                           
sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.translations_y = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, sSeq.num_images)
sSeq.trans_sampled = True
sSeq.name = "RTans X Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
SystemParameters.test_object_contents(sSeq)


print "******** Setting New Id Information Parameters for Real Translation X *****"
iSeq = sSeq = None
iSeq = iNewidRTransX = SystemParameters.ParamsInput()
iSeq.name = "New ID Real Translation X: (-45, 45, 2) translation"
iSeq.data_base_dir = frgc_normalized_base_dir
iSeq.ids = numpy.arange(9000,9990) # 8000, 10000
iSeq.trans = numpy.arange(sTrainRTransX.trans_x_min, sTrainRTransX.trans_x_max, 2) # (-45, 45, 2)
if len(iSeq.ids) % len(iSeq.trans) != 0:
    ex="Here the number of translations must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=4, image_postfix=".jpg")
 
#MEGAWARNING!!!!
iSeq.input_files = iSeq.input_files * 4 #warning * 4
numpy.random.shuffle(iSeq.input_files)  
iSeq.num_images = len(iSeq.input_files)
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.trans)

iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.trans)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting New ID Data Parameters for Real TransX  ****************"
sSeq = sNewidRTransX = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 128
sSeq.subimage_height = 128 
sSeq.trans_x_max = sTrainRTransX.trans_x_max
sSeq.trans_x_min = sTrainRTransX.trans_x_min
sSeq.trans_y_max = sTrainRTransX.trans_y_max
sSeq.trans_y_min = sTrainRTransX.trans_y_min
#iSeq.scales = numpy.linspace(0.5, 1.30, 16) # (-50, 50, 2)
sSeq.min_sampling = sTrainRTransX.min_sampling
sSeq.max_sampling = sTrainRTransX.max_sampling
sSeq.pixelsampling_x = sSeq.pixelsampling_y = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
sSeq.subimage_pixelsampling = 2
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coordinate
sSeq.translation = 20 #20
#sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)                                                           
sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.translations_y = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, sSeq.num_images)
sSeq.trans_sampled = True
sSeq.name = "RTans X Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
SystemParameters.test_object_contents(sSeq)


####################################################################
###########    SYSTEM FOR REAL_TRANSLATION_X EXTRACTION      ############
####################################################################  
ParamsRTransX = SystemParameters.ParamsSystem()
ParamsRTransX.name = sTrainRTransX.name
ParamsRTransX.network = "linearNetwork4L"
ParamsRTransX.iTrain = iTrainRTransX
ParamsRTransX.sTrain = sTrainRTransX
ParamsRTransX.iSeenid = iSeenidRTransX
ParamsRTransX.sSeenid = sSeenidRTransX
ParamsRTransX.iNewid = iNewidRTransX
ParamsRTransX.sNewid = sNewidRTransX
##MEGAWARNING!!!!
#ParamsRTransX.iNewid = iNewidTransX
#ParamsRTransX.sNewid = sNewidTransX
#ParamsRTransX.sNewid.translations_y = ParamsRTransX.sNewid.translations_y * 0.0 + 8.0

ParamsRTransX.block_size = iTrainRTransX.block_size
ParamsRTransX.train_mode = 'mixed'
ParamsRTransX.analysis = None

ParamsRTransX.enable_reduced_image_sizes = True
ParamsRTransX.reduction_factor = 2.0
ParamsRTransX.hack_image_size = 64
ParamsRTransX.enable_hack_image_size = True


#GC / 17 signals, mse=11.5



# YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYyYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
#This network actually supports images in the closed intervals: [-dx1, dx1], [smin0, smax0]
#but halb-open [-dy0, dy0)
print "***** Setting Training Information Parameters for Real Translation Y ******"
iSeq = iTrainRTransY = SystemParameters.ParamsInput()
iSeq.name = "Real Translation Y: Y(-20, 20, 1) translation and dx 20"
iSeq.data_base_dir = frgc_normalized_base_dir
iSeq.ids = numpy.arange(0,8000) # 8000, 7965

iSeq.trans = numpy.arange(-1 * pipeline_fd['dy0'], pipeline_fd['dy0'], 1) # (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.trans) != 0:
    ex="Here the number of translations must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=4, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * 4 # warning!!! 4, 8
#To avoid grouping similar images next to one other
numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.trans)
print "BLOCK SIZE =", iSeq.block_size 
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.trans)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Real TransY  ****************"
sSeq = sTrainRTransY = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 128
sSeq.subimage_height = 128 


sSeq.trans_x_max = pipeline_fd['dx1']
sSeq.trans_x_min = -1 * pipeline_fd['dx1']

sSeq.trans_y_max = pipeline_fd['dy0']
sSeq.trans_y_min = -1 * sSeq.trans_y_max

#iSeq.scales = numpy.linspace(0.5, 1.30, 16) # (-50, 50, 2)
sSeq.min_sampling = pipeline_fd['smin0']
sSeq.max_sampling = pipeline_fd['smax0']

sSeq.pixelsampling_x = sSeq.pixelsampling_y = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
#sSeq.subimage_pixelsampling = 2
sSeq.subimage_first_row =  sSeq.image_height/2.0-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2.0-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coordinate
#sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
#sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)                                                           
sSeq.translations_x = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images)
sSeq.translations_y = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)

sSeq.trans_sampled = True
sSeq.name = "RTans Y Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)

print "***** Setting Seen ID Information Parameters for Real Translation Y *******"
iSeq = sSeq = None
iSeq = iSeenidRTransY = SystemParameters.ParamsInput()
iSeq.name = "Test Real Translation Y: (-20, 20, 1) translation"
iSeq.data_base_dir = frgc_normalized_base_dir
iSeq.ids = numpy.arange(8000,9000) # WARNING 8900
iSeq.trans = numpy.arange(sTrainRTransY.trans_y_min, sTrainRTransY.trans_y_max, 1) #WARNING!!!! (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.trans) != 0:
    ex="Here the number of translations must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=4, image_postfix=".jpg")

iSeq.input_files = iSeq.input_files * 16 # Warning!!! 16
numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.trans)

iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.trans)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Seen Id Data Parameters for Real TransY  ****************"
sSeq = sSeenidRTransY = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 128
sSeq.subimage_height = 128 
sSeq.trans_x_max = sTrainRTransY.trans_x_max
sSeq.trans_x_min = sTrainRTransY.trans_x_min
sSeq.trans_y_max = sTrainRTransY.trans_y_max
sSeq.trans_y_min = sTrainRTransY.trans_y_min
#iSeq.scales = numpy.linspace(0.5, 1.30, 16) # (-50, 50, 2)
sSeq.min_sampling = sTrainRTransY.min_sampling
sSeq.max_sampling = sTrainRTransY.max_sampling
sSeq.pixelsampling_x = sSeq.pixelsampling_y = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
#sSeq.subimage_pixelsampling = 2
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coordinate
#sSeq.translation = 20 #25, 20, WARNING!!!!!!!
#sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)                                                           
sSeq.translations_x = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images)
sSeq.translations_y = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.trans_sampled = True
sSeq.name = "RTans Y Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)


print "******** Setting New Id Information Parameters for Real Translation Y *****"
iSeq = sSeq = None
iSeq = iNewidRTransY = SystemParameters.ParamsInput()
iSeq.name = "New ID Real Translation Y: (-20, 20, 1) translation"
iSeq.data_base_dir = frgc_normalized_base_dir
iSeq.ids = numpy.arange(9000,10000) # 8000, 10000
iSeq.trans = numpy.arange(sTrainRTransY.trans_y_min, sTrainRTransY.trans_y_max, 1) # (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.trans) != 0:
    ex="Here the number of translations must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=4, image_postfix=".jpg")
 
#MEGAWARNING!!!!
iSeq.input_files = iSeq.input_files * 4 #warning * 4
numpy.random.shuffle(iSeq.input_files)  
iSeq.num_images = len(iSeq.input_files)
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.trans)

iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.trans)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting New ID Data Parameters for Real TransY  ****************"
sSeq = sNewidRTransY = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 128
sSeq.subimage_height = 128 
sSeq.trans_x_max = sTrainRTransY.trans_x_max
sSeq.trans_x_min = sTrainRTransY.trans_x_min
sSeq.trans_y_max = sTrainRTransY.trans_y_max
sSeq.trans_y_min = -1 * sTrainRTransY.trans_y_min
#iSeq.scales = numpy.linspace(0.5, 1.30, 16) # (-50, 50, 2)
sSeq.min_sampling = sTrainRTransY.min_sampling
sSeq.max_sampling = sTrainRTransY.max_sampling
sSeq.pixelsampling_x = sSeq.pixelsampling_y = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
sSeq.subimage_pixelsampling = 2
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coordinate
sSeq.translation = 20 #20
#sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)                                                           
sSeq.translations_x = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images)
sSeq.translations_y = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.trans_sampled = True
sSeq.name = "RTans Y Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)


####################################################################
###########    SYSTEM FOR REAL_TRANSLATION_Y EXTRACTION      ############
####################################################################  
ParamsRTransY = SystemParameters.ParamsSystem()
ParamsRTransY.name = sTrainRTransY.name
ParamsRTransY.network = "linearNetwork4L"
ParamsRTransY.iTrain = iTrainRTransY
ParamsRTransY.sTrain = sTrainRTransY
ParamsRTransY.iSeenid = iSeenidRTransY
ParamsRTransY.sSeenid = sSeenidRTransY
ParamsRTransY.iNewid = iNewidRTransY
ParamsRTransY.sNewid = sNewidRTransY
##MEGAWARNING!!!!
#ParamsRTransY.iNewid = iNewidTransY
#ParamsRTransY.sNewid = sNewidTransY
#ParamsRTransY.sNewid.translations_y = ParamsRTransY.sNewid.translations_y * 0.0 + 8.0

ParamsRTransY.block_size = iTrainRTransY.block_size
ParamsRTransY.train_mode = 'mixed'
ParamsRTransY.analysis = None
#Gaussian classifier:
#7 => 6.81
#10 => 6.64
#12 => 6.68
#15 =>
#17 => 6.68




#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
#This network actually supports images in the closed intervals: [-dx1, dx1], [-dy1, dy1], [smin, smax]
print "Studienprojekt. Scale estimation datasets. By Jan, Stephan and Alberto "
print "***** Setting Training Information Parameters for Scale ******"
iSeq = iTrainRScale = SystemParameters.ParamsInput()
iSeq.name = "Real Scale: (0.55, 1.1,  50)"

iSeq.data_base_dir = alldbnormalized_base_dir
alldbnormalized_available_images = numpy.arange(0,55000)
numpy.random.shuffle(alldbnormalized_available_images)

iSeq.ids = alldbnormalized_available_images[0:30000]

iSeq.scales = numpy.linspace(pipeline_fd['smin0'], pipeline_fd['smax0'], 50) # (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.scales) != 0:
    ex="Here the number of scales must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * 2 # 2, 10
#To avoid grouping similar images next to one other
numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.scales)
print "BLOCK SIZE =", iSeq.block_size 
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.scales)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.scales, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Real Scale  ****************"
sSeq = sTrainRScale = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 135
sSeq.subimage_height = 135

sSeq.trans_x_max = pipeline_fd['dx1']
sSeq.trans_x_min = -1 * pipeline_fd['dx1']
sSeq.trans_y_max = pipeline_fd['dy1']
sSeq.trans_y_min = -1 * pipeline_fd['dy1']
sSeq.min_sampling = pipeline_fd['smin0']
sSeq.max_sampling = pipeline_fd['smax0']
 
sSeq.pixelsampling_x = sfa_libs.wider_1Darray(iSeq.scales,  iSeq.block_size)
sSeq.pixelsampling_y =  sfa_libs.wider_1Darray(iSeq.scales,  iSeq.block_size)
sSeq.subimage_pixelsampling = 2
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None

#random translation for th w coordinate
sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images)
sSeq.translations_y = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, sSeq.num_images)

sSeq.trans_sampled = True
sSeq.name = "Scale. Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f, 50)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)


print "***** Setting SeenId Information Parameters for Scale ******"
iSeq = iSeenidRScale = SystemParameters.ParamsInput()
iSeq.name = "Real Scale: (0.55, 1.1 / 50)"
iSeq.data_base_dir = alldbnormalized_base_dir
iSeq.ids = alldbnormalized_available_images[30000:45000]

iSeq.scales = numpy.linspace(sTrainRScale.min_sampling, sTrainRScale.max_sampling, 50) # (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.scales) != 0:
    ex="Here the number of scales must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * 2 # 3 Warning, 20, 32
#To avoid grouping similar images next to one other
numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.scales)
print "BLOCK SIZE =", iSeq.block_size 
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.scales)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.scales, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting SeenId Data Parameters for Real Scale  ****************"
sSeq = sSeenidRScale = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 135
sSeq.subimage_height = 135 

sSeq.trans_x_max = sTrainRScale.trans_x_max
sSeq.trans_x_min = sTrainRScale.trans_x_min
sSeq.trans_y_max = sTrainRScale.trans_y_max
sSeq.trans_y_min = sTrainRScale.trans_y_min
sSeq.min_sampling = sTrainRScale.min_sampling
sSeq.max_sampling = sTrainRScale.max_sampling

sSeq.pixelsampling_x = sfa_libs.wider_1Darray(iSeq.scales,  iSeq.block_size)
sSeq.pixelsampling_y =  sfa_libs.wider_1Darray(iSeq.scales,  iSeq.block_size)
sSeq.subimage_pixelsampling = 2
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coo8rdinate
sSeq.translation = 8 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images)
sSeq.translations_y = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, sSeq.num_images)

sSeq.trans_sampled = True
sSeq.name = "Scale. Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f, 50)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)

print "***** Setting NewId Information Parameters for Scale ******"
iSeq = iNewidRScale = SystemParameters.ParamsInput()
iSeq.name = "Real Scale: (0.5, 1, 50)"
iSeq.data_base_dir = alldbnormalized_base_dir
iSeq.ids = alldbnormalized_available_images[45000:55000]
iSeq.scales = numpy.linspace(sTrainRScale.min_sampling, sTrainRScale.max_sampling, 50) # (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.scales) != 0:
    ex="Here the number of scales must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * 1 #8
#To avoid grouping similar images next to one other
numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.scales)
print "BLOCK SIZE =", iSeq.block_size 
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.scales)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.scales, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting NewId Data Parameters for Real Scale  ****************"
sSeq = sNewidRScale = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 135
sSeq.subimage_height = 135 

sSeq.trans_x_max = sTrainRScale.trans_x_max
sSeq.trans_x_min = sTrainRScale.trans_x_min
sSeq.trans_y_max = sTrainRScale.trans_y_max
sSeq.trans_y_min = sTrainRScale.trans_y_min
sSeq.min_sampling = sTrainRScale.min_sampling
sSeq.max_sampling = sTrainRScale.max_sampling

sSeq.pixelsampling_x = sfa_libs.wider_1Darray(iSeq.scales,  iSeq.block_size)
sSeq.pixelsampling_y =  sfa_libs.wider_1Darray(iSeq.scales,  iSeq.block_size)
sSeq.subimage_pixelsampling = 2
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coordinate
sSeq.translation = 8 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images)
sSeq.translations_y = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, sSeq.num_images)

sSeq.trans_sampled = True
sSeq.name = "Scale. Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f, 50)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)

####################################################################
###########    SYSTEM FOR REAL_SCALE EXTRACTION      ############
####################################################################  
ParamsRScale = SystemParameters.ParamsSystem()
ParamsRScale.name = sTrainRScale.name
ParamsRScale.network = "linearNetwork4L"
ParamsRScale.iTrain = iTrainRScale
ParamsRScale.sTrain = sTrainRScale
ParamsRScale.iSeenid = iSeenidRScale
ParamsRScale.sSeenid = sSeenidRScale
ParamsRScale.iNewid = iNewidRScale
ParamsRScale.sNewid = sNewidRScale
##MEGAWARNING!!!!
#ParamsRScale.iNewid = iNewidScale
#ParamsRScale.sNewid = sNewidScale
#ParamsRScale.sNewid.translations_y = ParamsRScale.sNewid.translations_y * 0.0 + 8.0

ParamsRScale.block_size = iTrainRScale.block_size
ParamsRScale.train_mode = 'mixed'
ParamsRScale.analysis = None
ParamsRScale.enable_reduced_image_sizes = True
ParamsRScale.reduction_factor = 2.0 # WARNING 2, 4
ParamsRScale.hack_image_size = 64 # WARNING 64, 32
ParamsRScale.enable_hack_image_size = True


#GC (see text file)
# 4 => 0.00406
# 5 => 0.004042
# 15 => 0.00315

#b=[]
#flow, layers, benchmark = CreateNetwork(linearNetworkT6L, 128, 128, 100, 'mixed', b)


print "Studienprojekt. Illumination estimation datasets. By Jan and Stephan and Alberto "
print "***** Setting Training Information Parameters for Illumination ******"
iSeq = iTrainRIllumination = SystemParameters.ParamsInput()
iSeq.name = "Real Illumination:"
on_Jan = os.path.lexists("/home/jan")
if on_lok21:
    pathIllumination = "/local2/escalafl/Alberto/Erg"
if on_Jan:
    pathIllumination = "/home/jan/Dokumente/Studienprojekt/Pictures Illumination Cars/NewImages"
elif on_zappa01:
    pathIllumination = "/local/escalafl/Alberto/NewImages"
else:
    pathIllumination = "/local/escalafl/Alberto/Erg"

available_cars = numpy.arange(1,32)
numpy.random.shuffle(available_cars)

iSeq.data_base_dir = pathIllumination
iSeq.ids = available_cars[0:22]
iSeq.illumination = numpy.arange(0,870)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = iSeq.illumination
iSeq.slow_signal = 7 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "car", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=3, image_postfix=".bmp")
iSeq.input_files = iSeq.input_files * 1
#To avoid grouping similar images next to one other
#numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = 10*iSeq.num_images / len (iSeq.lightings)
print "BLOCK SIZE =", iSeq.block_size 
#print iSeq.block_size
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.lightings)/10), iSeq.block_size)
#print len(iSeq.correct_classes)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.lightings/10, iSeq.block_size/10)
#print len(iSeq.correct_labels)


SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Real Illumination  ****************"
sSeq = sTrainRIllumination = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 150
sSeq.image_height = 150
sSeq.subimage_width = 64
sSeq.subimage_height = 64
sSeq.min_sampling = 1.7
sSeq.max_sampling = 1.8
sSeq.pixelsampling_y = sSeq.pixelsampling_x = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, sSeq.num_images)
sSeq.subimage_pixelsampling = 1
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coordinate
sSeq.translation = 3 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)          
#sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.translations_y = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)
sSeq.trans_sampled = False
SystemParameters.test_object_contents(sSeq)


iSeq = iSeenidRIllumination = SystemParameters.ParamsInput()
iSeq.name = "Real Illumination: "
iSeq.data_base_dir = pathIllumination
iSeq.ids = available_cars[22:27]
iSeq.illumination = numpy.arange(0,870)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = iSeq.illumination
iSeq.slow_signal = 7 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "car", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=3, image_postfix=".bmp")
iSeq.input_files = iSeq.input_files * 1
#To avoid grouping similar images next to one other
#numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = 10*iSeq.num_images / len (iSeq.lightings)
print "BLOCK SIZE =", iSeq.block_size 
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.lightings)/10), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.lightings/10, iSeq.block_size/10)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Real Illumination  ****************"
sSeq = sSeenidRIllumination = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 150
sSeq.image_height = 150
sSeq.subimage_width = 64
sSeq.subimage_height = 64
sSeq.min_sampling = 1.7
sSeq.max_sampling = 1.8
sSeq.pixelsampling_y = sSeq.pixelsampling_x = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, sSeq.num_images)
sSeq.subimage_pixelsampling = 1
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coordinate
sSeq.translation = 3 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)          
#sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.translations_y = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)
sSeq.trans_sampled = False
SystemParameters.test_object_contents(sSeq)


iSeq = iNewidRIllumination = SystemParameters.ParamsInput()
iSeq.name = "Real Illumination: "
iSeq.data_base_dir = pathIllumination
iSeq.ids = available_cars[27:32]
iSeq.illumination = numpy.arange(0,870)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = iSeq.illumination
iSeq.slow_signal = 7 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "car", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=3, image_postfix=".bmp")
iSeq.input_files = iSeq.input_files * 1
#To avoid grouping similar images next to one other
#numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = 10*iSeq.num_images / len (iSeq.lightings)
print "BLOCK SIZE =", iSeq.block_size 
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.lightings)/10), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.lightings/10, iSeq.block_size/10)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Testing Data Parameters for Real Illumination  ****************"
sSeq = sNewidRIllumination = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 150
sSeq.image_height = 150
sSeq.subimage_width = 64
sSeq.subimage_height = 64
sSeq.min_sampling = 1.7
sSeq.max_sampling = 1.8
sSeq.pixelsampling_y = sSeq.pixelsampling_x = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, sSeq.num_images)
sSeq.subimage_pixelsampling = 1
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coordinate
sSeq.translation = 3 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)          
#sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.translations_y = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)
sSeq.trans_sampled = False
SystemParameters.test_object_contents(sSeq)

####################################################################
###########    SYSTEM FOR REAL_TRANSLATION_X EXTRACTION      ############
####################################################################  
ParamsRIllumination = SystemParameters.ParamsSystem()
ParamsRIllumination.name = "Network that extracts Real Translation X information"
ParamsRIllumination.network = "linearNetwork4L"
ParamsRIllumination.iTrain = iTrainRIllumination
ParamsRIllumination.sTrain = sTrainRIllumination
ParamsRIllumination.iSeenid = iSeenidRIllumination
ParamsRIllumination.sSeenid = sSeenidRIllumination
ParamsRIllumination.iNewid = iNewidRIllumination
ParamsRIllumination.sNewid = sNewidRIllumination
##MEGAWARNING!!!!
#ParamsRIllumination.iNewid = iNewidIllumination
#ParamsRIllumination.sNewid = sNewidIllumination
#ParamsRIllumination.sNewid.translations_y = ParamsRIllumination.sNewid.translations_y * 0.0 + 8.0

ParamsRIllumination.block_size = iTrainRIllumination.block_size
ParamsRIllumination.train_mode = 'mixed'
ParamsRIllumination.analysis = None

#b=[]
#flow, layers, benchmark = CreateNetwork(linearNetworkT6L, 128, 128, 100, 'mixed', b)


print "Studienprojekt. Rotation estimation datasets. By Jan and Stephan and Alberto "
print "***** Setting Training Information Parameters for Rotation ******"
iSeq = iTrainRRotation = SystemParameters.ParamsInput()
iSeq.name = "Real Rotation: "
on_Jan = os.path.lexists("/home/jan")
if on_lok21:
    pathRotation = "/local2/escalafl/Alberto/Erg"
if on_Jan:
    pathRotation = "/media/7270C6F570C6BF5B/Pictures Rotation/Single Pictures"
else:
    pathRotation = "/home/Stephan/Erg"
available_cars = numpy.arange(1,40)
numpy.random.shuffle(available_cars)

iSeq.data_base_dir = pathRotation
iSeq.ids = available_cars[0:28]
iSeq.illumination = numpy.arange(0,500)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = iSeq.illumination
iSeq.slow_signal = 7 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "car", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=3, image_postfix=".bmp")
iSeq.input_files = iSeq.input_files * 1 

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = 10*iSeq.num_images / len (iSeq.lightings)
print "BLOCK SIZE =", iSeq.block_size 
#print iSeq.block_size
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.lightings)/10), iSeq.block_size)
#print len(iSeq.correct_classes)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.lightings/10, iSeq.block_size/10)
#print len(iSeq.correct_labels)
SystemParameters.test_object_contents(iSeq)


print "******** Setting Training Data Parameters for Real Rotation  ****************"
sSeq = sTrainRRotation = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 80
sSeq.image_height = 80
sSeq.subimage_width = 64
sSeq.subimage_height = 64
sSeq.min_sampling = 1.0
sSeq.max_sampling = 1.0
sSeq.pixelsampling_y = sSeq.pixelsampling_x = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, sSeq.num_images)
sSeq.subimage_pixelsampling = 1
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coordinate
sSeq.translation = 3 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)          
#sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.translations_y = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)
sSeq.trans_sampled = False
SystemParameters.test_object_contents(sSeq)


iSeq = iSeenidRRotation = SystemParameters.ParamsInput()
iSeq.name = "Real Rotation: "
iSeq.data_base_dir = pathRotation
iSeq.ids = available_cars[28:34]
iSeq.illumination = numpy.arange(0,500)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = iSeq.illumination
iSeq.slow_signal = 7 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "car", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=3, image_postfix=".bmp")
iSeq.input_files = iSeq.input_files * 1
#To avoid grouping similar images next to one other
#numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = 10*iSeq.num_images / len (iSeq.lightings)
print "BLOCK SIZE =", iSeq.block_size 
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.lightings)/10), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.lightings/10, iSeq.block_size/10)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Real Rotation  ****************"
sSeq = sSeenidRRotation = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 80
sSeq.image_height = 80
sSeq.subimage_width = 64
sSeq.subimage_height = 64
sSeq.min_sampling = 1.0
sSeq.max_sampling = 1.0
sSeq.pixelsampling_y = sSeq.pixelsampling_x = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, sSeq.num_images)
sSeq.subimage_pixelsampling = 1
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coordinate
sSeq.translation = 3 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)          
#sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.translations_y = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)
sSeq.trans_sampled = False
SystemParameters.test_object_contents(sSeq)


iSeq = iNewidRRotation = SystemParameters.ParamsInput()
iSeq.name = "Real Rotation: "
iSeq.data_base_dir = pathRotation
iSeq.ids = available_cars[34:40]
iSeq.illumination = numpy.arange(0,500)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = iSeq.illumination
iSeq.slow_signal = 7 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "car", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=3, image_postfix=".bmp")
iSeq.input_files = iSeq.input_files * 1
#To avoid grouping similar images next to one other
#numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = 10*iSeq.num_images / len (iSeq.lightings)
print "BLOCK SIZE =", iSeq.block_size 
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.lightings)/10), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.lightings/10, iSeq.block_size/10)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Testing Data Parameters for Real Illumination  ****************"
sSeq = sNewidRRotation = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 80
sSeq.image_height = 80
sSeq.subimage_width = 64
sSeq.subimage_height = 64
sSeq.min_sampling = 1.0
sSeq.max_sampling = 1.0
sSeq.pixelsampling_y = sSeq.pixelsampling_x = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, sSeq.num_images)
sSeq.subimage_pixelsampling = 1
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
#random translation for th w coordinate
sSeq.translation = 3 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)          
#sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.translations_y = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)
sSeq.trans_sampled = False
SystemParameters.test_object_contents(sSeq)

####################################################################
###########    SYSTEM FOR REAL_TRANSLATION_X EXTRACTION      ############
####################################################################  
ParamsRRotation = SystemParameters.ParamsSystem()
ParamsRRotation.name = "Network that extracts Real Translation X information"
ParamsRRotation.network = "linearNetwork4L"
ParamsRRotation.iTrain = iTrainRRotation
ParamsRRotation.sTrain = sTrainRRotation
ParamsRRotation.iSeenid = iSeenidRRotation
ParamsRRotation.sSeenid = sSeenidRRotation
ParamsRRotation.iNewid = iNewidRRotation
ParamsRRotation.sNewid = sNewidRRotation
ParamsRRotation.block_size = iTrainRRotation.block_size
ParamsRRotation.train_mode = 'mixed'
ParamsRRotation.analysis = None


def double_uniform(min1, max1, min2, max2, size, p2):
    prob = numpy.random.uniform(0.0, 1.0, size)
    u1 = numpy.random.uniform(min1, max1, size)
    u2 = numpy.random.uniform(min2, max2, size)
    
    res = u1
    mask = (prob <= p2) #then take it from u2
    res[mask] = u2[mask]
    return res

#TODO: code is slow, improve
#Box is a list of pairs. Pair i contains the smallest and largest value for coordinate i
def box_sampling(box, num_samples=1):
    num_dimensions = len(box)
    output = numpy.zeros((num_samples, num_dimensions))
    for i in range(num_dimensions):
        output[:,i] = numpy.random.uniform(box[i][0], box[i][1], size=num_samples)
    return output

#x must be a two-dimensional array
def inside_box(x, box, num_dim):
    num_samples = len(x)
    inside = numpy.ones(num_samples, dtype="bool")
    for i in range(num_dim):
        inside = inside & (x[:, i] > box[i][0]) & (x[:, i] < box[i][1])    
    return inside
        
#TODO: code is slow, improve   
def sub_box_sampling(box_in, box_ext, num_samples=1):
    num_dimensions = len(box_in)
    if num_dimensions != len(box_ext):
        err = "Exterion and interior boxes have a different numbe of dimensions!!!"
        raise Exception(err)
    output = numpy.zeros((num_samples, num_dimensions))
    incorrect = numpy.ones(num_samples, dtype="bool")
    while incorrect.sum()>0:
#        print "incorrect.sum()=",incorrect.sum()
        new_candidates = box_sampling(box_ext, incorrect.sum()) 
        output[incorrect] = new_candidates       
        incorrect = inside_box(output, box_in, num_dimensions)        
    return output

#FACE / NO-FACE FACE / NO-FACE FACE / NO-FACE FACE / NO-FACE FACE / NO-FACE FACE / NO-FACE FACE / NO-FACE FACE / NO-FACE
#Attempt to distinguish between faces and no-faces
print "***** Setting Training Information Parameters for Face ******"
iSeq = iTrainRFace = SystemParameters.ParamsInput()
# (0.55+1.1)/2 = 0.825, 0.55/2 = 0.275, 0.55/4 = 0.1375, .825 + .1375 = .9625, .825 - .55/4 = .6875
iSeq.name = "Real FACE (Centered / Decentered)"

iSeq.data_base_dir = frgc_normalized_base_dir
iSeq.ids = numpy.arange(0,6000) # 6000
iSeq.faces = numpy.arange(0,2) # 0=centered normalized face, 1=not centered normalized face

#iSeq.scales = numpy.linspace(pipeline_fd['smin0'], pipeline_fd['smax0'], 50) # (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.faces) != 0:
    ex="Here the number of scales must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is whether there is a centered or descentered face
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=4, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * 4 #4 was overfitting non linear sfa slightly
#To avoid grouping similar images next to one other
numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.faces)
print "BLOCK SIZE =", iSeq.block_size 

iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.faces*2-1, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Real Face  ****************"
sSeq = sTrainRFace = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 135
sSeq.subimage_height = 135

sSeq.trans_x_max = pipeline_fd['dx1']
sSeq.trans_x_min = -1 * pipeline_fd['dx1']
sSeq.trans_y_max = pipeline_fd['dy1']
sSeq.trans_y_min = -1 * pipeline_fd['dy1']
sSeq.min_sampling = pipeline_fd['smin1']
sSeq.max_sampling = pipeline_fd['smax1']

sSeq.noface_trans_x_max = 45
sSeq.noface_trans_x_min = -45
sSeq.noface_trans_y_max = 19
sSeq.noface_trans_y_min = -19
sSeq.noface_min_sampling = 0.55
sSeq.noface_max_sampling = 1.1
 

sSeq.pixelsampling_x = numpy.zeros(sSeq.num_images)
sSeq.pixelsampling_y = numpy.zeros(sSeq.num_images) 

#Centered Face
sSeq.pixelsampling_x[0:iSeq.block_size] = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, size=iSeq.block_size)
sSeq.pixelsampling_y[0:iSeq.block_size] = sSeq.pixelsampling_x[0:iSeq.block_size] + 0.0 #MUST BE A DIFFERENT OBJECT
#sSeq.pixelsampling_x[iSeq.block_size:] = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, size=iSeq.block_size)
#sSeq.pixelsampling_y[iSeq.block_size:] = sSeq.pixelsampling_x[iSeq.block_size:] + 0.0
#Decentered Face, using different x and y samplings
sSeq.pixelsampling_x[iSeq.block_size:] = double_uniform(sSeq.noface_min_sampling, sSeq.min_sampling, sSeq.max_sampling, sSeq.noface_max_sampling , size=iSeq.block_size,   p2=0.5)
sSeq.pixelsampling_y[iSeq.block_size:] = double_uniform(sSeq.noface_min_sampling, sSeq.min_sampling, sSeq.max_sampling, sSeq.noface_max_sampling , size=iSeq.block_size,   p2=0.5)

sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None

#random translation for th w coordinate
#sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.zeros(sSeq.num_images)
sSeq.translations_y = numpy.zeros(sSeq.num_images)
#Centered Face
sSeq.translations_x[0:iSeq.block_size] = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, iSeq.block_size)
sSeq.translations_y[0:iSeq.block_size] = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, iSeq.block_size)
#sSeq.translations_x[iSeq.block_size:] = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, iSeq.block_size)
#sSeq.translations_y[iSeq.block_size:] = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, iSeq.block_size)
#Decentered Face
sSeq.translations_x[iSeq.block_size:] = double_uniform(sSeq.noface_trans_x_min, sSeq.trans_x_min, sSeq.trans_x_max, sSeq.noface_trans_x_max, size=iSeq.block_size, p2=0.5)
sSeq.translations_y[iSeq.block_size:] = double_uniform(sSeq.noface_trans_y_min, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.noface_trans_y_max, size=iSeq.block_size, p2=0.5)

sSeq.trans_sampled = True
sSeq.name = "Face. Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f, 50)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, int(sSeq.min_sampling*1000), int(sSeq.max_sampling*1000))


print " sSeq.subimage_first_row =", sSeq.subimage_first_row
print "sSeq.pixelsampling_x", sSeq.pixelsampling_x
print "sSeq.translations_x", sSeq.translations_x

iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)



print "***** Setting Seenid Information Parameters for Face ******"
iSeq = iSeenidRFace = SystemParameters.ParamsInput()
# (0.55+1.1)/2 = 0.825, 0.55/2 = 0.275, 0.55/4 = 0.1375, .825 + .1375 = .9625, .825 - .55/4 = .6875
iSeq.name = "Real FACE (Centered / Decentered)"

iSeq.data_base_dir = frgc_normalized_base_dir
iSeq.ids = numpy.arange(6000,8000) # 8000
iSeq.faces = numpy.arange(0,2) # 0=centered normalized face, 1=not centered normalized face

#iSeq.scales = numpy.linspace(pipeline_fd['smin0'], pipeline_fd['smax0'], 50) # (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.faces) != 0:
    ex="Here the number of scales must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is whether there is a centered or descentered face
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=4, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * 8
#To avoid grouping similar images next to one other
numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.faces)
print "BLOCK SIZE =", iSeq.block_size 

iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.faces*2-1, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting SeenID Data Parameters for Real Face  ****************"
sSeq = sSeenidRFace = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 135
sSeq.subimage_height = 135

sSeq.trans_x_max = pipeline_fd['dx1']
sSeq.trans_x_min = -1 * pipeline_fd['dx1']
sSeq.trans_y_max = pipeline_fd['dy1']
sSeq.trans_y_min = -1 * pipeline_fd['dy1']
sSeq.min_sampling = pipeline_fd['smin1']
sSeq.max_sampling = pipeline_fd['smax1']

sSeq.noface_trans_x_max = 45
sSeq.noface_trans_x_min = -45
sSeq.noface_trans_y_max = 19
sSeq.noface_trans_y_min = -19
sSeq.noface_min_sampling = 0.55
sSeq.noface_max_sampling = 1.1
 

sSeq.pixelsampling_x = numpy.zeros(sSeq.num_images)
sSeq.pixelsampling_y = numpy.zeros(sSeq.num_images) 

#Centered Face
sSeq.pixelsampling_x[0:iSeq.block_size] = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, size=iSeq.block_size)
sSeq.pixelsampling_y[0:iSeq.block_size] = sSeq.pixelsampling_x[0:iSeq.block_size] + 0.0 #MUST BE A DIFFERENT OBJECT
#sSeq.pixelsampling_x[iSeq.block_size:] = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, size=iSeq.block_size)
#sSeq.pixelsampling_y[iSeq.block_size:] = sSeq.pixelsampling_x[iSeq.block_size:] + 0.0
#Decentered Face, using different x and y samplings
sSeq.pixelsampling_x[iSeq.block_size:] = double_uniform(sSeq.noface_min_sampling, sSeq.min_sampling, sSeq.max_sampling, sSeq.noface_max_sampling , size=iSeq.block_size,   p2=0.5)
sSeq.pixelsampling_y[iSeq.block_size:] = double_uniform(sSeq.noface_min_sampling, sSeq.min_sampling, sSeq.max_sampling, sSeq.noface_max_sampling , size=iSeq.block_size,   p2=0.5)

sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None

#random translation for th w coordinate
#sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.zeros(sSeq.num_images)
sSeq.translations_y = numpy.zeros(sSeq.num_images)
#Centered Face
sSeq.translations_x[0:iSeq.block_size] = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, iSeq.block_size)
sSeq.translations_y[0:iSeq.block_size] = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, iSeq.block_size)
#Decentered Face
sSeq.translations_x[iSeq.block_size:] = double_uniform(sSeq.noface_trans_x_min, sSeq.trans_x_min, sSeq.trans_x_max, sSeq.noface_trans_x_max, size=iSeq.block_size, p2=0.5)
sSeq.translations_y[iSeq.block_size:] = double_uniform(sSeq.noface_trans_y_min, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.noface_trans_y_max, size=iSeq.block_size, p2=0.5)

sSeq.trans_sampled = True
sSeq.name = "Face. Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f, 50)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, int(sSeq.min_sampling*1000), int(sSeq.max_sampling*1000))

iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)


print "***** Setting Newid Information Parameters for Face ******"
iSeq = iNewidRFace = SystemParameters.ParamsInput()
# (0.55+1.1)/2 = 0.825, 0.55/2 = 0.275, 0.55/4 = 0.1375, .825 + .1375 = .9625, .825 - .55/4 = .6875
iSeq.name = "Real FACE (Centered / Decentered)"

iSeq.data_base_dir = frgc_normalized_base_dir
iSeq.ids = numpy.arange(8000,10000) # 8000
iSeq.faces = numpy.arange(0,2) # 0=centered normalized face, 1=not centered normalized face

#iSeq.scales = numpy.linspace(pipeline_fd['smin0'], pipeline_fd['smax0'], 50) # (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.faces) != 0:
    ex="Here the number of scales must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is whether there is a centered or descentered face
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=4, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * 2
#To avoid grouping similar images next to one other
numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.faces)
print "BLOCK SIZE =", iSeq.block_size 

iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.faces*2-1, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Real Face  ****************"
sSeq = sNewidRFace = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 135
sSeq.subimage_height = 135

sSeq.trans_x_max = pipeline_fd['dx1']
sSeq.trans_x_min = -1 * pipeline_fd['dx1']
sSeq.trans_y_max = pipeline_fd['dy1']
sSeq.trans_y_min = -1 * pipeline_fd['dy1']
sSeq.min_sampling = pipeline_fd['smin1']
sSeq.max_sampling = pipeline_fd['smax1']

sSeq.noface_trans_x_max = 45
sSeq.noface_trans_x_min = -45
sSeq.noface_trans_y_max = 19
sSeq.noface_trans_y_min = -19
sSeq.noface_min_sampling = 0.55
sSeq.noface_max_sampling = 1.1
 

sSeq.pixelsampling_x = numpy.zeros(sSeq.num_images)
sSeq.pixelsampling_y = numpy.zeros(sSeq.num_images) 

#Centered Face
sSeq.pixelsampling_x[0:iSeq.block_size] = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, size=iSeq.block_size)
sSeq.pixelsampling_y[0:iSeq.block_size] = sSeq.pixelsampling_x[0:iSeq.block_size] + 0.0 #MUST BE A DIFFERENT OBJECT
#sSeq.pixelsampling_x[iSeq.block_size:] = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, size=iSeq.block_size)
#sSeq.pixelsampling_y[iSeq.block_size:] = sSeq.pixelsampling_x[iSeq.block_size:] + 0.0
#Decentered Face, using different x and y samplings
sSeq.pixelsampling_x[iSeq.block_size:] = double_uniform(sSeq.noface_min_sampling, sSeq.min_sampling, sSeq.max_sampling, sSeq.noface_max_sampling , size=iSeq.block_size,   p2=0.5)
sSeq.pixelsampling_y[iSeq.block_size:] = double_uniform(sSeq.noface_min_sampling, sSeq.min_sampling, sSeq.max_sampling, sSeq.noface_max_sampling , size=iSeq.block_size,   p2=0.5)

sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None

#random translation for th w coordinate
#sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.zeros(sSeq.num_images)
sSeq.translations_y = numpy.zeros(sSeq.num_images)
#Centered Face
sSeq.translations_x[0:iSeq.block_size] = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, iSeq.block_size)
sSeq.translations_y[0:iSeq.block_size] = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, iSeq.block_size)
#Decentered Face
sSeq.translations_x[iSeq.block_size:] = double_uniform(sSeq.noface_trans_x_min, sSeq.trans_x_min, sSeq.trans_x_max, sSeq.noface_trans_x_max, size=iSeq.block_size, p2=0.5)
sSeq.translations_y[iSeq.block_size:] = double_uniform(sSeq.noface_trans_y_min, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.noface_trans_y_max, size=iSeq.block_size, p2=0.5)

sSeq.trans_sampled = True
sSeq.name = "Face. Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f, 50)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, int(sSeq.min_sampling*1000), int(sSeq.max_sampling*1000))

iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)


####################################################################
###########    SYSTEM FOR REAL_FACE CLASSIFICATION      ############
####################################################################  
ParamsRFace = SystemParameters.ParamsSystem()
ParamsRFace.name = sTrainRFace.name
ParamsRFace.network = "linearNetwork4L"
ParamsRFace.iTrain = iTrainRFace
ParamsRFace.sTrain = sTrainRFace
ParamsRFace.iSeenid = iSeenidRFace
ParamsRFace.sSeenid = sSeenidRFace
ParamsRFace.iNewid = iNewidRFace 
ParamsRFace.sNewid = sNewidRFace 
##MEGAWARNING!!!!
#ParamsRFace.iNewid = iNewidScale
#ParamsRFace.sNewid = sNewidScale
#ParamsRFace.sNewid.translations_y = ParamsRFace.sNewid.translations_y * 0.0 + 8.0

ParamsRFace.block_size = iTrainRFace.block_size
ParamsRFace.train_mode = 'clustered' # 'mixed'
ParamsRFace.analysis = None

import object_cache as cache

robject_center_base_dir = "/local/escalafl/Alberto/FaubelSet_01/Center"
robject_down_base_dir = "/local/escalafl/Alberto/FaubelSet_01/Down"
robject_up_base_dir = "/local/escalafl/Alberto/FaubelSet_01/Up"

#Dirty function to deal with filename convention obj#-##__#-##_ ... and  to acces several directories at once
def find_filenames_beginning_with_numbers(base_dirs=[""], base_filename="obj", base_numbers=None, extension=".png"):
    if base_numbers is None:
        return cache.find_filenames_beginning_with(base_dirs, base_filename, recursion=False, extension=extension)
    else:
        filenames = []
        for n, i in enumerate(base_numbers):
            filenames.append([])
            for base_dir in base_dirs:
                filenames[n].extend(cache.find_filenames_beginning_with(base_dir, base_filename+"%d_"%i, recursion=False, extension=extension))
#            print "looking for %s //  %s"%(base_dir, base_filename+"%d_"%i)
#            print "found:", cache.find_filenames_beginning_with(base_dir, base_filename+"%d"%i, recursion=False, extension=extension)
        return filenames

#Cooperation with Christian Faubel. Object Recognition
#Images by Christian Faubel
#Attempt to distinguish some types of objects
robject_convert_format='L'
print "***** Setting Training Information Parameters for RObject ******"
iSeq = iTrainRObject = SystemParameters.ParamsInput()
# (0.55+1.1)/2 = 0.825, 0.55/2 = 0.275, 0.55/4 = 0.1375, .825 + .1375 = .9625, .825 - .55/4 = .6875
iSeq.name = "Real Object Recognition"

iSeq.data_base_dir = [robject_center_base_dir, robject_down_base_dir, robject_up_base_dir]
iSeq.ids = numpy.arange(1,21) # 1-31
#iSeq.faces = numpy.arange(0,2) # 0=centered normalized face, 1=not centered normalized face
#iSeq.scales = numpy.linspace(pipeline_fd['smin0'], pipeline_fd['smax0'], 50) # (-50, 50, 2)
#if len(iSeq.ids) % len(iSeq.faces) != 0:
#    ex="Here the number of scales must be a divisor of the number of identities"
#    raise Exception(ex)
iSeq.all_input_files = find_filenames_beginning_with_numbers(iSeq.data_base_dir, "obj", iSeq.ids, extension=".png")
#print "iSeq.all_input_files", iSeq.all_input_files

iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = map(len, iSeq.all_input_files)
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is whether there is a centered or descentered face
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = []
for single_file_list in iSeq.all_input_files:
    iSeq.input_files += single_file_list
iSeq.block_sizes = numpy.array(iSeq.poses)
print "totaling %d images"%len(iSeq.input_files)

#imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
#                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
#                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=4, image_postfix=".jpg")
#iSeq.input_files = iSeq.input_files * 8 #4 was overfitting non linear sfa slightly
#To avoid grouping similar images next to one other
#numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]

#iSeq.block_size = 10 # WAAARRNNNIIINNGGG!!!
iSeq.block_size = iSeq.block_sizes

#iSeq.num_images / len (iSeq.faces)
print "BLOCK SIZE =", iSeq.block_size 
print "BLOCK SIZES =", iSeq.block_sizes

iSeq.correct_classes = []
for i, block_size in enumerate(iSeq.block_sizes):
    iSeq.correct_classes += [iSeq.ids[i]]*block_size
iSeq.correct_classes = numpy.array(iSeq.correct_classes)
print iSeq.correct_classes
#quit()

#sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
iSeq.correct_labels = iSeq.correct_classes + 0.0
print iSeq.correct_labels



#sfa_libs.wider_1Darray(iSeq.faces*2-1, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Real Object  ****************"
sSeq = sTrainRObject = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 52
sSeq.image_height = 52
sSeq.subimage_width = 32
sSeq.subimage_height = 32

#sSeq.trans_x_max = pipeline_fd['dx1']
#sSeq.trans_x_min = -1 * pipeline_fd['dx1']
#sSeq.trans_y_max = pipeline_fd['dy1']
#sSeq.trans_y_min = -1 * pipeline_fd['dy1']
#sSeq.min_sampling = pipeline_fd['smin1']
#sSeq.max_sampling = pipeline_fd['smax1']
#sSeq.noface_trans_x_max = 45
#sSeq.noface_trans_x_min = -45
#sSeq.noface_trans_y_max = 19
#sSeq.noface_trans_y_min = -19
#sSeq.noface_min_sampling = 0.55
#sSeq.noface_max_sampling = 1.1

sSeq.pixelsampling_x = 1.5 #1.625
sSeq.pixelsampling_y = 1.5

##Centered Face
#sSeq.pixelsampling_x[0:iSeq.block_size] = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, size=iSeq.block_size)
#sSeq.pixelsampling_y[0:iSeq.block_size] = sSeq.pixelsampling_x[0:iSeq.block_size] + 0.0 #MUST BE A DIFFERENT OBJECT
##sSeq.pixelsampling_x[iSeq.block_size:] = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, size=iSeq.block_size)
##sSeq.pixelsampling_y[iSeq.block_size:] = sSeq.pixelsampling_x[iSeq.block_size:] + 0.0
##Decentered Face, using different x and y samplings
#sSeq.pixelsampling_x[iSeq.block_size:] = double_uniform(sSeq.noface_min_sampling, sSeq.min_sampling, sSeq.max_sampling, sSeq.noface_max_sampling , size=iSeq.block_size,   p2=0.5)
#sSeq.pixelsampling_y[iSeq.block_size:] = double_uniform(sSeq.noface_min_sampling, sSeq.min_sampling, sSeq.max_sampling, sSeq.noface_max_sampling , size=iSeq.block_size,   p2=0.5)

sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column =" sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = robject_convert_format
sSeq.background_type = None

#random translation for th w coordinate
#sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.zeros(sSeq.num_images)
sSeq.translations_y = numpy.zeros(sSeq.num_images)
#Centered Face
##sSeq.translations_x[0:iSeq.block_size] = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, iSeq.block_size)
##sSeq.translations_y[0:iSeq.block_size] = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, iSeq.block_size)
###sSeq.translations_x[iSeq.block_size:] = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, iSeq.block_size)
###sSeq.translations_y[iSeq.block_size:] = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, iSeq.block_size)
###Decentered Face
##sSeq.translations_x[iSeq.block_size:] = double_uniform(sSeq.noface_trans_x_min, sSeq.trans_x_min, sSeq.trans_x_max, sSeq.noface_trans_x_max, size=iSeq.block_size, p2=0.5)
##sSeq.translations_y[iSeq.block_size:] = double_uniform(sSeq.noface_trans_y_min, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.noface_trans_y_max, size=iSeq.block_size, p2=0.5)

sSeq.trans_sampled = True
sSeq.name = "Object"
#sSeq.name = "Object. Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f, 50)"%(sSeq.trans_x_min, 
#    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, int(sSeq.min_sampling*1000), int(sSeq.max_sampling*1000))

print " sSeq.subimage_first_row =", sSeq.subimage_first_row
print "sSeq.pixelsampling_x", sSeq.pixelsampling_x
print "sSeq.translations_x", sSeq.translations_x

iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)


#2
print "***** Setting Seenid Information Parameters for RObject ******"
iSeq = iSeenidRObject = SystemParameters.ParamsInput()
# (0.55+1.1)/2 = 0.825, 0.55/2 = 0.275, 0.55/4 = 0.1375, .825 + .1375 = .9625, .825 - .55/4 = .6875
iSeq.name = "Real Object Recognition"

iSeq.data_base_dir = [robject_down_base_dir, robject_up_base_dir]
iSeq.ids = numpy.arange(21,31) # 1-31
#iSeq.faces = numpy.arange(0,2) # 0=centered normalized face, 1=not centered normalized face
#iSeq.scales = numpy.linspace(pipeline_fd['smin0'], pipeline_fd['smax0'], 50) # (-50, 50, 2)
#if len(iSeq.ids) % len(iSeq.faces) != 0:
#    ex="Here the number of scales must be a divisor of the number of identities"
#    raise Exception(ex)
iSeq.all_input_files = find_filenames_beginning_with_numbers(iSeq.data_base_dir, "obj", iSeq.ids, extension=".png")
#print "iSeq.all_input_files", iSeq.all_input_files

iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = map(len, iSeq.all_input_files)
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is whether there is a centered or descentered face
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = []
for single_file_list in iSeq.all_input_files:
    iSeq.input_files += single_file_list
iSeq.block_sizes = numpy.array(iSeq.poses)
print "totaling %d images"%len(iSeq.input_files)

#imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
#                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
#                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=4, image_postfix=".jpg")
#iSeq.input_files = iSeq.input_files * 8 #4 was overfitting non linear sfa slightly
#To avoid grouping similar images next to one other
#numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]

#iSeq.block_size = 10 # WAAARRNNNIIINNGGG!!!
iSeq.block_size = iSeq.block_sizes

#iSeq.num_images / len (iSeq.faces)
print "BLOCK SIZE =", iSeq.block_size 
print "BLOCK SIZES =", iSeq.block_sizes

iSeq.correct_classes = []
for i, block_size in enumerate(iSeq.block_sizes):
    iSeq.correct_classes += [iSeq.ids[i]]*block_size
iSeq.correct_classes = numpy.array(iSeq.correct_classes)
print iSeq.correct_classes
#quit()

#sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
iSeq.correct_labels = iSeq.correct_classes + 0.0
print iSeq.correct_labels



#sfa_libs.wider_1Darray(iSeq.faces*2-1, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Real Object  ****************"
sSeq = sSeenidRObject = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 52
sSeq.image_height = 52
sSeq.subimage_width = 32
sSeq.subimage_height = 32

#sSeq.trans_x_max = pipeline_fd['dx1']
#sSeq.trans_x_min = -1 * pipeline_fd['dx1']
#sSeq.trans_y_max = pipeline_fd['dy1']
#sSeq.trans_y_min = -1 * pipeline_fd['dy1']
#sSeq.min_sampling = pipeline_fd['smin1']
#sSeq.max_sampling = pipeline_fd['smax1']
#sSeq.noface_trans_x_max = 45
#sSeq.noface_trans_x_min = -45
#sSeq.noface_trans_y_max = 19
#sSeq.noface_trans_y_min = -19
#sSeq.noface_min_sampling = 0.55
#sSeq.noface_max_sampling = 1.1

sSeq.pixelsampling_x = 1.5 #1.625
sSeq.pixelsampling_y = 1.5

##Centered Face
#sSeq.pixelsampling_x[0:iSeq.block_size] = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, size=iSeq.block_size)
#sSeq.pixelsampling_y[0:iSeq.block_size] = sSeq.pixelsampling_x[0:iSeq.block_size] + 0.0 #MUST BE A DIFFERENT OBJECT
##sSeq.pixelsampling_x[iSeq.block_size:] = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, size=iSeq.block_size)
##sSeq.pixelsampling_y[iSeq.block_size:] = sSeq.pixelsampling_x[iSeq.block_size:] + 0.0
##Decentered Face, using different x and y samplings
#sSeq.pixelsampling_x[iSeq.block_size:] = double_uniform(sSeq.noface_min_sampling, sSeq.min_sampling, sSeq.max_sampling, sSeq.noface_max_sampling , size=iSeq.block_size,   p2=0.5)
#sSeq.pixelsampling_y[iSeq.block_size:] = double_uniform(sSeq.noface_min_sampling, sSeq.min_sampling, sSeq.max_sampling, sSeq.noface_max_sampling , size=iSeq.block_size,   p2=0.5)

sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column =" sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = robject_convert_format
sSeq.background_type = None

#random translation for th w coordinate
#sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.zeros(sSeq.num_images)
sSeq.translations_y = numpy.zeros(sSeq.num_images)
#Centered Face
##sSeq.translations_x[0:iSeq.block_size] = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, iSeq.block_size)
##sSeq.translations_y[0:iSeq.block_size] = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, iSeq.block_size)
###sSeq.translations_x[iSeq.block_size:] = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, iSeq.block_size)
###sSeq.translations_y[iSeq.block_size:] = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, iSeq.block_size)
###Decentered Face
##sSeq.translations_x[iSeq.block_size:] = double_uniform(sSeq.noface_trans_x_min, sSeq.trans_x_min, sSeq.trans_x_max, sSeq.noface_trans_x_max, size=iSeq.block_size, p2=0.5)
##sSeq.translations_y[iSeq.block_size:] = double_uniform(sSeq.noface_trans_y_min, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.noface_trans_y_max, size=iSeq.block_size, p2=0.5)

sSeq.trans_sampled = True
sSeq.name = "Object"
#sSeq.name = "Object. Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f, 50)"%(sSeq.trans_x_min, 
#    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, int(sSeq.min_sampling*1000), int(sSeq.max_sampling*1000))

print " sSeq.subimage_first_row =", sSeq.subimage_first_row
print "sSeq.pixelsampling_x", sSeq.pixelsampling_x
print "sSeq.translations_x", sSeq.translations_x

iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)

#3
print "***** Setting Training Information Parameters for RObject ******"
iSeq = iNewidRObject = SystemParameters.ParamsInput()
# (0.55+1.1)/2 = 0.825, 0.55/2 = 0.275, 0.55/4 = 0.1375, .825 + .1375 = .9625, .825 - .55/4 = .6875
iSeq.name = "Real Object Recognition"

iSeq.data_base_dir =  [robject_center_base_dir]
iSeq.ids = numpy.arange(21,31) # 1-31
#iSeq.faces = numpy.arange(0,2) # 0=centered normalized face, 1=not centered normalized face
#iSeq.scales = numpy.linspace(pipeline_fd['smin0'], pipeline_fd['smax0'], 50) # (-50, 50, 2)
#if len(iSeq.ids) % len(iSeq.faces) != 0:
#    ex="Here the number of scales must be a divisor of the number of identities"
#    raise Exception(ex)
iSeq.all_input_files = find_filenames_beginning_with_numbers(iSeq.data_base_dir, "obj", iSeq.ids, extension=".png")
#print "iSeq.all_input_files", iSeq.all_input_files

iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = map(len, iSeq.all_input_files)
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is whether there is a centered or descentered face
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = []
for single_file_list in iSeq.all_input_files:
    iSeq.input_files += single_file_list
iSeq.block_sizes = numpy.array(iSeq.poses)
print "totaling %d images"%len(iSeq.input_files)

#imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
#                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
#                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=4, image_postfix=".jpg")
#iSeq.input_files = iSeq.input_files * 8 #4 was overfitting non linear sfa slightly
#To avoid grouping similar images next to one other
#numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]

#iSeq.block_size = 10 # WAAARRNNNIIINNGGG!!!
iSeq.block_size = iSeq.block_sizes

#iSeq.num_images / len (iSeq.faces)
print "BLOCK SIZE =", iSeq.block_size 
print "BLOCK SIZES =", iSeq.block_sizes

iSeq.correct_classes = []
for i, block_size in enumerate(iSeq.block_sizes):
    iSeq.correct_classes += [iSeq.ids[i]]*block_size
iSeq.correct_classes = numpy.array(iSeq.correct_classes)
print iSeq.correct_classes
#quit()

#sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
iSeq.correct_labels = iSeq.correct_classes + 0.0
print iSeq.correct_labels



#sfa_libs.wider_1Darray(iSeq.faces*2-1, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Real Object  ****************"
sSeq = sNewidRObject = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 52
sSeq.image_height = 52
sSeq.subimage_width = 32
sSeq.subimage_height = 32

#sSeq.trans_x_max = pipeline_fd['dx1']
#sSeq.trans_x_min = -1 * pipeline_fd['dx1']
#sSeq.trans_y_max = pipeline_fd['dy1']
#sSeq.trans_y_min = -1 * pipeline_fd['dy1']
#sSeq.min_sampling = pipeline_fd['smin1']
#sSeq.max_sampling = pipeline_fd['smax1']
#sSeq.noface_trans_x_max = 45
#sSeq.noface_trans_x_min = -45
#sSeq.noface_trans_y_max = 19
#sSeq.noface_trans_y_min = -19
#sSeq.noface_min_sampling = 0.55
#sSeq.noface_max_sampling = 1.1

sSeq.pixelsampling_x = 1.5 #1.625
sSeq.pixelsampling_y = 1.5

##Centered Face
#sSeq.pixelsampling_x[0:iSeq.block_size] = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, size=iSeq.block_size)
#sSeq.pixelsampling_y[0:iSeq.block_size] = sSeq.pixelsampling_x[0:iSeq.block_size] + 0.0 #MUST BE A DIFFERENT OBJECT
##sSeq.pixelsampling_x[iSeq.block_size:] = numpy.random.uniform(sSeq.min_sampling, sSeq.max_sampling, size=iSeq.block_size)
##sSeq.pixelsampling_y[iSeq.block_size:] = sSeq.pixelsampling_x[iSeq.block_size:] + 0.0
##Decentered Face, using different x and y samplings
#sSeq.pixelsampling_x[iSeq.block_size:] = double_uniform(sSeq.noface_min_sampling, sSeq.min_sampling, sSeq.max_sampling, sSeq.noface_max_sampling , size=iSeq.block_size,   p2=0.5)
#sSeq.pixelsampling_y[iSeq.block_size:] = double_uniform(sSeq.noface_min_sampling, sSeq.min_sampling, sSeq.max_sampling, sSeq.noface_max_sampling , size=iSeq.block_size,   p2=0.5)

sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
#sSeq.subimage_first_column =" sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
sSeq.add_noise_L0 = True
sSeq.convert_format = robject_convert_format
sSeq.background_type = None

#random translation for th w coordinate
#sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
sSeq.translations_x = numpy.zeros(sSeq.num_images)
sSeq.translations_y = numpy.zeros(sSeq.num_images)
#Centered Face
##sSeq.translations_x[0:iSeq.block_size] = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, iSeq.block_size)
##sSeq.translations_y[0:iSeq.block_size] = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, iSeq.block_size)
###sSeq.translations_x[iSeq.block_size:] = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, iSeq.block_size)
###sSeq.translations_y[iSeq.block_size:] = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, iSeq.block_size)
###Decentered Face
##sSeq.translations_x[iSeq.block_size:] = double_uniform(sSeq.noface_trans_x_min, sSeq.trans_x_min, sSeq.trans_x_max, sSeq.noface_trans_x_max, size=iSeq.block_size, p2=0.5)
##sSeq.translations_y[iSeq.block_size:] = double_uniform(sSeq.noface_trans_y_min, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.noface_trans_y_max, size=iSeq.block_size, p2=0.5)

sSeq.trans_sampled = True
sSeq.name = "Object"
#sSeq.name = "Object. Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f, 50)"%(sSeq.trans_x_min, 
#    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, int(sSeq.min_sampling*1000), int(sSeq.max_sampling*1000))

print " sSeq.subimage_first_row =", sSeq.subimage_first_row
print "sSeq.pixelsampling_x", sSeq.pixelsampling_x
print "sSeq.translations_x", sSeq.translations_x

iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)

####################################################################
###########    SYSTEM FOR REAL_OBJECT RECOGNITION       ############
####################################################################  
ParamsRObject = SystemParameters.ParamsSystem()
ParamsRObject.name = sTrainRObject.name
ParamsRObject.network = "linearNetwork4L"
ParamsRObject.iTrain = iTrainRObject
ParamsRObject.sTrain = sTrainRObject
ParamsRObject.iSeenid = iSeenidRObject
ParamsRObject.sSeenid = sSeenidRObject
ParamsRObject.iNewid = iNewidRObject
ParamsRObject.sNewid = sNewidRObject
##MEGAWARNING!!!!
#ParamsRFace.iNewid = iNewidScale
#ParamsRFace.sNewid = sNewidScale
#ParamsRFace.sNewid.translations_y = ParamsRFace.sNewid.translations_y * 0.0 + 8.0

ParamsRObject.block_size = iTrainRObject.block_size
ParamsRObject.train_mode = 'clustered' # 'mixed'
ParamsRObject.analysis = None
ParamsRObject.enable_reduced_image_sizes = False
ParamsRObject.reduction_factor = 1.0
ParamsRObject.hack_image_size = 32
ParamsRObject.enable_hack_image_size = True






print "***** Project: Processing natural images with SFA,  ******"
print "***** Image Patches courtesy of Niko Wilbert ******"
print "***** Setting Training Information Parameters for RawNatural ******"
iSeq = iTrainRawNatural = SystemParameters.ParamsInput()
iSeq.name = "Natural image patches"
iSeq.data_base_dir = "/home/escalafl/Databases/cooperations/igel/patches_8x8"
iSeq.base_filename = "bochum_natural_8_5000.bin"

iSeq.samples = numpy.arange(0, 4000, dtype="int")
iSeq.ids = iSeq.samples # 1 - 4000+1
iSeq.num_images = len(iSeq.samples)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #slow parameter is the image number
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = "LoadRawData"
iSeq.block_size = 1
print "totaling %d samples"% iSeq.num_images

iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]

print "BLOCK SIZE =", iSeq.block_size 

iSeq.correct_classes = iSeq.ids * 1
#print iSeq.correct_classes
#quit()
#sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
iSeq.correct_labels = iSeq.correct_classes * 1
#print iSeq.correct_labels

#sfa_libs.wider_1Darray(iSeq.faces*2-1, iSeq.block_size)
SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for RawNatural  ****************"
sSeq = sTrainRawNatural = SystemParameters.ParamsDataLoading()
sSeq.base_filename = iSeq.base_filename
sSeq.data_base_dir = iSeq.data_base_dir
sSeq.input_files = iSeq.input_files
sSeq.samples = iSeq.samples
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.subimage_width = 8
sSeq.subimage_height = 8
sSeq.input_dim = 64
sSeq.dtype = "uint8"
sSeq.convert_format = "binary"
sSeq.name = "Natural Patch. 8x8, input_dim = %d, num_images %d"%(sSeq.input_dim, iSeq.num_images)
iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)


print "***** Setting Training Information Parameters for RawNatural ******"
iSeq = iNewidRawNatural = SystemParameters.ParamsInput()
iSeq.name = "Natural image patches"
iSeq.data_base_dir = "/home/escalafl/Databases/cooperations/igel/patches_8x8"
iSeq.base_filename = "bochum_natural_8_5000.bin"

iSeq.samples = numpy.arange(4000, 5000, dtype="int")
iSeq.ids = iSeq.samples # 1 - 4000+1
iSeq.num_images = len(iSeq.samples)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #slow parameter is the image number
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = "LoadRawData"
iSeq.block_size = 1
print "totaling %d samples"% iSeq.num_images

iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]

print "BLOCK SIZE =", iSeq.block_size 

iSeq.correct_classes = iSeq.ids * 1
#print iSeq.correct_classes
#quit()
#sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
iSeq.correct_labels = iSeq.correct_classes * 1
#print iSeq.correct_labels

#sfa_libs.wider_1Darray(iSeq.faces*2-1, iSeq.block_size)
SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Natural  ****************"
sSeq = sNewidRawNatural = SystemParameters.ParamsDataLoading()
sSeq.base_filename = iSeq.base_filename
sSeq.data_base_dir = iSeq.data_base_dir
sSeq.input_files = iSeq.input_files
sSeq.samples = iSeq.samples
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.subimage_width = 8
sSeq.subimage_height = 8
sSeq.input_dim = 64
sSeq.dtype = "uint8"
sSeq.convert_format = "binary"
sSeq.name = "Natural Patch. 8x8, input_dim = %d, num_images %d"%(sSeq.input_dim, iSeq.num_images)
iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)

####################################################################
###########    SYSTEM FOR RAW NATURAL IMAGE PATCHES      ###########
####################################################################  
ParamsRawNatural = SystemParameters.ParamsSystem()
ParamsRawNatural.name = sTrainRawNatural.name
ParamsRawNatural.network = None
ParamsRawNatural.iTrain = iTrainRawNatural
ParamsRawNatural.sTrain = sTrainRawNatural
ParamsRawNatural.iSeenid = iTrainRawNatural
ParamsRawNatural.sSeenid = sTrainRawNatural
ParamsRawNatural.iNewid = iNewidRawNatural
ParamsRawNatural.sNewid = sNewidRawNatural
ParamsRawNatural.block_size = iTrainRawNatural.block_size
ParamsRawNatural.train_mode = 'serial' # 'mixed'
ParamsRawNatural.analysis = False
ParamsRawNatural.enable_reduced_image_sizes = False
ParamsRawNatural.reduction_factor = -1
ParamsRawNatural.hack_image_size = -1
ParamsRawNatural.enable_hack_image_size = False





print "***** Project: Integration of RBM and SFA,  ******"
rbm_sfa_iteration = 19999 # 99 or 4999, now also 9999. 14999, 19999
rbm_sfa_numHid = 64 #64 or 128
rbm_sfa_data_base_dir = "/home/escalafl/Databases/cooperations/igel/rbm_%d"%rbm_sfa_numHid # 64 or 128

print "***** Setting Training Information Parameters for Natural ******"
iSeq = iTrainNatural = SystemParameters.ParamsInput()
# (0.55+1.1)/2 = 0.825, 0.55/2 = 0.275, 0.55/4 = 0.1375, .825 + .1375 = .9625, .825 - .55/4 = .6875
iSeq.name = "Natural images RBM"

iSeq.data_base_dir = rbm_sfa_data_base_dir
iSeq.iteration = rbm_sfa_iteration
iSeq.base_filename = "data_bin_%d.bin"%(iSeq.iteration+1)

(iSeq.magic_num, iteration, iSeq.numSamples, iSeq.numHid, iSeq.sampleSpan) = imageLoader.read_binary_header(iSeq.data_base_dir, iSeq.base_filename)
if iteration != iSeq.iteration:
    er = "wrong iteration number in file, was %d, should be %d"%(iteration, iSeq.iteration)
    raise Exception(er)

if iSeq.numHid != rbm_sfa_numHid:
    er = "wrong number of output Neurons %d, 64 were assumed"%iSeq.numHid
    raise Exception(er)

if iSeq.numSamples != 5000:
    er = "wrong number of Samples %d, 5000 were assumed"%iSeq.numSamples
    raise Exception(er)

iSeq.numSamples = 4000
iSeq.samples = numpy.arange(0, iSeq.numSamples, dtype="int")
iSeq.ids = numpy.arange(1,iSeq.numSamples+1) # 1 - 4000+1
iSeq.num_images = len(iSeq.samples)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #slow parameter is the image number
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = "LoadBinaryData00"
iSeq.block_size = 1
print "totaling %d samples"% iSeq.num_images

iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]

#iSeq.num_images / len (iSeq.faces)
print "BLOCK SIZE =", iSeq.block_size 

iSeq.correct_classes = iSeq.ids * 1
#print iSeq.correct_classes
#quit()
#sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
iSeq.correct_labels = iSeq.correct_classes * 1
#print iSeq.correct_labels

#sfa_libs.wider_1Darray(iSeq.faces*2-1, iSeq.block_size)
SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Natural  ****************"
sSeq = sTrainNatural = SystemParameters.ParamsDataLoading()
sSeq.base_filename = iSeq.base_filename
sSeq.data_base_dir = iSeq.data_base_dir
sSeq.input_files = iSeq.input_files
sSeq.samples = iSeq.samples
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.subimage_width = rbm_sfa_numHid / 8
sSeq.subimage_height = rbm_sfa_numHid / sSeq.subimage_width
sSeq.convert_format = "binary"
sSeq.name = "RBM Natural. 8x8 (exp 64=%d), iter %d, num_images %d"%(iSeq.numHid, iSeq.iteration, iSeq.num_images)
iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)

#NOTE: There is no Seenid training data because we do not have labels for the classifier

print "***** Setting Newid Information Parameters for Natural ******"
iSeq = iNewidNatural = SystemParameters.ParamsInput()
iSeq.name = "Natural images"

iSeq.data_base_dir = rbm_sfa_data_base_dir
#iSeq.magic_num = 666
iSeq.iteration = rbm_sfa_iteration #0
iSeq.base_filename = "data_bin_%d.bin"%(iSeq.iteration+1)

(iSeq.magic_num, iteration, iSeq.numSamples, iSeq.numHid, iSeq.sampleSpan) = imageLoader.read_binary_header(iSeq.data_base_dir, iSeq.base_filename)
if iteration != iSeq.iteration:
    er = "wrong iteration number in file, was %d, should be %d"%(iteration, iSeq.iteration)
    raise Exception(er)

if iSeq.numHid != rbm_sfa_numHid:
    er = "wrong number of output Neurons %d, %d were assumed"%(iSeq.numHid,rbm_sfa_numHid)
    raise Exception(er)

if iSeq.numSamples != 5000:
    er = "wrong number of Samples %d, 5000 were assumed"%iSeq.numSamples
    raise Exception(er)

iSeq.samples = numpy.arange(4000, 5000, dtype="int")
iSeq.ids = iSeq.samples+1 # 1 - 4000+1
iSeq.num_images = len(iSeq.samples)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #slow parameter is the image number
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = "LoadBinaryData00"
iSeq.block_size = 1
print "totaling %d images"% iSeq.num_images

iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]

#iSeq.num_images / len (iSeq.faces)
print "BLOCK SIZE =", iSeq.block_size 

iSeq.correct_classes = iSeq.ids * 1
#print iSeq.correct_classes
#quit()
#sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
iSeq.correct_labels = iSeq.correct_classes * 1
#print iSeq.correct_labels

#sfa_libs.wider_1Darray(iSeq.faces*2-1, iSeq.block_size)
SystemParameters.test_object_contents(iSeq)

print "******** Setting Newid Data Parameters for Natural ****************"
sSeq = sNewidNatural = SystemParameters.ParamsDataLoading()
sSeq.base_filename = iSeq.base_filename
sSeq.data_base_dir = iSeq.data_base_dir
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.samples = iSeq.samples
sSeq.subimage_width = rbm_sfa_numHid / 8
sSeq.subimage_height = rbm_sfa_numHid / sSeq.subimage_width
sSeq.convert_format = "binary"
sSeq.name = "RBM Natural. 8x8 (exp 100=%d), iter %d, num_images %d"%(iSeq.numHid, iSeq.iteration, iSeq.num_images)
iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)
#quit()



####################################################################
###########     SYSTEM FOR RBM NATURAL ANALYSIS         ############
####################################################################  
ParamsNatural = SystemParameters.ParamsSystem()
ParamsNatural.name = sTrainNatural.name
ParamsNatural.network = None
ParamsNatural.iTrain = iTrainNatural
ParamsNatural.sTrain = sTrainNatural
ParamsNatural.iSeenid = copy.deepcopy(iTrainNatural)
ParamsNatural.sSeenid = copy.deepcopy(sTrainNatural)
ParamsNatural.iNewid = iNewidNatural
ParamsNatural.sNewid = sNewidNatural
#ParamsNatural.iSeenid = iSeenidNatural
#ParamsNatural.sSeenid = sSeenidNatural
#ParamsNatural.iNewid = iNewidNatural
#ParamsNatural.sNewid = sNewidNatural
ParamsNatural.block_size = iTrainNatural.block_size
ParamsNatural.train_mode = 'serial' # 'mixed'
ParamsNatural.analysis = False
ParamsNatural.enable_reduced_image_sizes = False
ParamsNatural.reduction_factor = -1
ParamsNatural.hack_image_size = -1
ParamsNatural.enable_hack_image_size = False









#FaceDiscrimination
#TODO: Explain this, enlarge largest face, 
print "***** Setting Training Information Parameters for RFaceCentering******"
iSeq = iTrainRFaceCentering= SystemParameters.ParamsInput()
# (0.55+1.1)/2 = 0.825, 0.55/2 = 0.275, 0.55/4 = 0.1375, .825 + .1375 = .9625, .825 - .55/4 = .6875
iSeq.name = "Real FACE DISCRIMINATION (Centered / Decentered)"

iSeq.data_base_dir = alldbnormalized_base_dir
alldbnormalized_available_images = numpy.arange(0,55000)
numpy.random.shuffle(alldbnormalized_available_images)
alldb_noface_available_images = numpy.arange(0,12000)
numpy.random.shuffle(alldb_noface_available_images)

iSeq.ids = alldbnormalized_available_images[0:6000] #30000, numpy.arange(0,6000) # 6000
iSeq.faces = numpy.arange(0,10) # 0=centered normalized face, 1=not centered normalized face
block_sizeT = len(iSeq.ids) / len(iSeq.faces)

#iSeq.scales = numpy.linspace(pipeline_fd['smin0'], pipeline_fd['smax0'], 50) # (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.faces) != 0:
    ex="Here the number of scales must be a divisor of the number of identities"
    raise Exception(ex)

iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is whether there is the amount of face centering
iSeq.step = 1
iSeq.offset = 0
repetition_factorT = 2 # WARNING 2, 8
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * repetition_factorT  #  4 was overfitting non linear sfa slightly
#To avoid grouping similar images next to one other or in the same block
numpy.random.shuffle(iSeq.input_files)  

iSeq.data2_base_dir = alldb_noface_base_dir
iSeq.ids2 = alldb_noface_available_images[0: block_sizeT * repetition_factorT]
iSeq.input_files2 = imageLoader.create_image_filenames3(iSeq.data2_base_dir, "image", iSeq.slow_signal, iSeq.ids2, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
iSeq.input_files2 = iSeq.input_files2 
numpy.random.shuffle(iSeq.input_files2)

iSeq.input_files = iSeq.input_files[0:-block_sizeT* repetition_factorT] + iSeq.input_files2

iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.faces)
print "BLOCK SIZE =", iSeq.block_size 

iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
iSeq.correct_labels = iSeq.correct_classes / (len(iSeq.faces)-1)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Real Face Centering****************"
sSeq = sTrainRFaceCentering= SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 135
sSeq.subimage_height = 135

sSeq.trans_x_max = pipeline_fd['dx0'] * 1.0
sSeq.trans_y_max = pipeline_fd['dy0'] * 1.0 * 0.998
sSeq.min_sampling = pipeline_fd['smin0'] - 0.1 #WARNING!!!
sSeq.max_sampling = pipeline_fd['smax0']
sSeq.avg_sampling = (sSeq.min_sampling + sSeq.max_sampling)/2


sSeq.pixelsampling_x = numpy.zeros(sSeq.num_images)
sSeq.pixelsampling_y = numpy.zeros(sSeq.num_images) 
sSeq.translations_x = numpy.zeros(sSeq.num_images)
sSeq.translations_y = numpy.zeros(sSeq.num_images)


num_blocks = sSeq.num_images/sSeq.block_size
for block_nr in range(num_blocks):
    #For exterior box
    fraction = ((block_nr+1.0) / (num_blocks-1)) ** 0.333
    if fraction > 1:
        fraction = 1
    x_max = sSeq.trans_x_max * fraction
    y_max = sSeq.trans_y_max * fraction
    samp_max = sSeq.avg_sampling + (sSeq.max_sampling-sSeq.avg_sampling) * fraction
    samp_min = sSeq.avg_sampling + (sSeq.min_sampling-sSeq.avg_sampling) * fraction

    box_ext = [(-x_max, x_max), (-y_max, y_max), (samp_min, samp_max), (samp_min, samp_max)] 

    if block_nr >= 0:
        #For interior boxiSeq.ids = alldbnormalized_available_images[30000:45000]       
        if block_nr < num_blocks-1:
            eff_block_nr = block_nr
        else:
            eff_block_nr = block_nr-1
        fraction2 = (eff_block_nr / (num_blocks-1)) ** 0.333
        if fraction2 > 1:
            fraction2 = 1
        x_max = sSeq.trans_x_max * fraction2
        y_max = sSeq.trans_y_max * fraction2
        samp_max = sSeq.avg_sampling + (sSeq.max_sampling-sSeq.avg_sampling) * fraction2
        samp_min = sSeq.avg_sampling + (sSeq.min_sampling-sSeq.avg_sampling) * fraction2
        box_in = [(-x_max, x_max), (-y_max, y_max), (samp_min, samp_max), (samp_min, samp_max)] 
    
    samples = sub_box_sampling(box_in, box_ext, sSeq.block_size)
    sSeq.translations_x[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,0]
    sSeq.translations_y[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,1]
    sSeq.pixelsampling_x[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,2]
    sSeq.pixelsampling_y[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,3]
            
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0

sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
sSeq.trans_sampled = True

sSeq.name = "Face Centering. Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f, 50)"%(-sSeq.trans_x_max, 
    sSeq.trans_x_max, -sSeq.trans_y_max, sSeq.trans_y_max, int(sSeq.min_sampling*1000), int(sSeq.max_sampling*1000))
print sSeq.name
iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)



print "***** Setting SeenId Information Parameters for RFaceCentering******"
iSeq = iSeenidRFaceCentering= SystemParameters.ParamsInput()
# (0.55+1.1)/2 = 0.825, 0.55/2 = 0.275, 0.55/4 = 0.1375, .825 + .1375 = .9625, .825 - .55/4 = .6875
iSeq.name = "Real FACE DISCRIMINATION (Centered / Decentered)"

iSeq.data_base_dir = alldbnormalized_base_dir
iSeq.ids = alldbnormalized_available_images[30000:45000] # 30000-45000 numpy.arange(6000,8000) # 6000-8000
iSeq.faces = numpy.arange(0,10) # 0=centered normalized face, 1=not centered normalized face
block_sizeS = len(iSeq.ids) / len(iSeq.faces)

#iSeq.scales = numpy.linspace(pipeline_fd['smin0'], pipeline_fd['smax0'], 50) # (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.faces) != 0:
    ex="Here the number of scales must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is whether there is the amount of face centering
iSeq.step = 1
iSeq.offset = 0
repetition_factorS = 1 # 2 was 4
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * repetition_factorS #  4 was overfitting non linear sfa slightly
#To avoid grouping similar images next to one other or in the same block
numpy.random.shuffle(iSeq.input_files)  


iSeq.data2_base_dir = alldb_noface_base_dir
iSeq.ids2 = alldb_noface_available_images[block_sizeT* repetition_factorT: block_sizeT*repetition_factorT+block_sizeS*repetition_factorS]

iSeq.input_files2 = imageLoader.create_image_filenames3(iSeq.data2_base_dir, "image", iSeq.slow_signal, iSeq.ids2, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
iSeq.input_files2 = iSeq.input_files2 
numpy.random.shuffle(iSeq.input_files2)

iSeq.input_files = iSeq.input_files[0:-block_sizeS * repetition_factorS] + iSeq.input_files2


iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.faces)
print "BLOCK SIZE =", iSeq.block_size 

iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
iSeq.correct_labels = iSeq.correct_classes / (len(iSeq.faces)-1)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Seenid Data Parameters for Real Face Centering****************"
sSeq = sSeenidRFaceCentering= SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 135
sSeq.subimage_height = 135

sSeq.trans_x_max = pipeline_fd['dx0'] * 1.0
sSeq.trans_y_max = pipeline_fd['dy0'] * 1.0 * 0.998
sSeq.min_sampling = pipeline_fd['smin0']- 0.1 #WARNING!!!
sSeq.max_sampling = pipeline_fd['smax0']
sSeq.avg_sampling = (sSeq.min_sampling + sSeq.max_sampling)/2


sSeq.pixelsampling_x = numpy.zeros(sSeq.num_images)
sSeq.pixelsampling_y = numpy.zeros(sSeq.num_images) 
sSeq.translations_x = numpy.zeros(sSeq.num_images)
sSeq.translations_y = numpy.zeros(sSeq.num_images)

num_blocks = sSeq.num_images/sSeq.block_size
for block_nr in range(num_blocks):
    #For exterior box
    fraction = ((block_nr+1.0) / (num_blocks-1)) ** 0.333
    if fraction > 1:
        fraction = 1
    x_max = sSeq.trans_x_max * fraction
    y_max = sSeq.trans_y_max * fraction
    samp_max = sSeq.avg_sampling + (sSeq.max_sampling-sSeq.avg_sampling) * fraction
    samp_min = sSeq.avg_sampling + (sSeq.min_sampling-sSeq.avg_sampling) * fraction

    box_ext = [(-x_max, x_max), (-y_max, y_max), (samp_min, samp_max), (samp_min, samp_max)] 

    if block_nr >= 0:
        #For interior boxiSeq.ids = alldbnormalized_available_images[30000:45000]       
        if block_nr < num_blocks-1:
            eff_block_nr = block_nr
        else:
            eff_block_nr = block_nr-1
        fraction2 = (eff_block_nr / (num_blocks-1)) ** 0.333
        if fraction2 > 1:
            fraction2 = 1
        x_max = sSeq.trans_x_max * fraction2
        y_max = sSeq.trans_y_max * fraction2
        samp_max = sSeq.avg_sampling + (sSeq.max_sampling-sSeq.avg_sampling) * fraction2
        samp_min = sSeq.avg_sampling + (sSeq.min_sampling-sSeq.avg_sampling) * fraction2
        box_in = [(-x_max, x_max), (-y_max, y_max), (samp_min, samp_max), (samp_min, samp_max)] 
           
    samples = sub_box_sampling(box_in, box_ext, sSeq.block_size)
    sSeq.translations_x[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,0]
    sSeq.translations_y[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,1]
    sSeq.pixelsampling_x[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,2]
    sSeq.pixelsampling_y[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,3]
            
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0

sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
sSeq.trans_sampled = True

sSeq.name = "Face Centering. Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f, 50)"%(-sSeq.trans_x_max, 
    sSeq.trans_x_max, -sSeq.trans_y_max, sSeq.trans_y_max, int(sSeq.min_sampling*1000), int(sSeq.max_sampling*1000))
print sSeq.name
iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)


print "***** Setting NewId Information Parameters for RFaceCentering******"
iSeq = iNewidRFaceCentering= SystemParameters.ParamsInput()
# (0.55+1.1)/2 = 0.825, 0.55/2 = 0.275, 0.55/4 = 0.1375, .825 + .1375 = .9625, .825 - .55/4 = .6875
iSeq.name = "Real FACE DISCRIMINATION (Centered / Decentered)"

iSeq.data_base_dir = alldbnormalized_base_dir
iSeq.ids = alldbnormalized_available_images[45000:46000] #45000:55000 numpy.arange(8000,10000) # 6000-8000
iSeq.faces = numpy.arange(0,10) # 0=centered normalized face, 1=not centered normalized face
block_sizeN = len(iSeq.ids) / len(iSeq.faces)

#iSeq.scales = numpy.linspace(pipeline_fd['smin0'], pipeline_fd['smax0'], 50) # (-50, 50, 2)
if len(iSeq.ids) % len(iSeq.faces) != 0:
    ex="Here the number of scales must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is whether there is the amount of face centering
iSeq.step = 1
iSeq.offset = 0
repetition_factorN = 2 # was 4
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * repetition_factorN#  4 was overfitting non linear sfa slightly
#To avoid grouping similar images next to one other or in the same block
numpy.random.shuffle(iSeq.input_files)  

iSeq.data2_base_dir = alldb_noface_base_dir
iSeq.ids2 = alldb_noface_available_images[block_sizeT*repetition_factorT+block_sizeS*repetition_factorS: block_sizeT*repetition_factorT+block_sizeS*repetition_factorS+block_sizeN*repetition_factorN]

iSeq.input_files2 = imageLoader.create_image_filenames3(iSeq.data2_base_dir, "image", iSeq.slow_signal, iSeq.ids2, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
iSeq.input_files2 = iSeq.input_files2
numpy.random.shuffle(iSeq.input_files2)

iSeq.input_files = iSeq.input_files[0:-block_sizeN * repetition_factorN] + iSeq.input_files2


iSeq.num_images = len(iSeq.input_files)
#iSeq.params = [ids, expressions, morphs, poses, lightings]
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                  iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.faces)
print "BLOCK SIZE =", iSeq.block_size 

iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
iSeq.correct_labels = iSeq.correct_classes / (len(iSeq.faces)-1)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Seenid Data Parameters for Real Face Centering****************"
sSeq = sNewidRFaceCentering= SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 135
sSeq.subimage_height = 135

sSeq.trans_x_max = pipeline_fd['dx0'] * 1.0
sSeq.trans_y_max = pipeline_fd['dy0'] * 1.0 * 0.998
sSeq.min_sampling = pipeline_fd['smin0']- 0.1 #WARNING!!!
sSeq.max_sampling = pipeline_fd['smax0']
sSeq.avg_sampling = (sSeq.min_sampling + sSeq.max_sampling)/2


sSeq.pixelsampling_x = numpy.zeros(sSeq.num_images)
sSeq.pixelsampling_y = numpy.zeros(sSeq.num_images) 
sSeq.translations_x = numpy.zeros(sSeq.num_images)
sSeq.translations_y = numpy.zeros(sSeq.num_images)

num_blocks = sSeq.num_images/sSeq.block_size
for block_nr in range(num_blocks):
    #For exterior box
    fraction = ((block_nr+1.0) / (num_blocks-1)) ** 0.333
    if fraction > 1:
        fraction = 1
    x_max = sSeq.trans_x_max * fraction
    y_max = sSeq.trans_y_max * fraction
    samp_max = sSeq.avg_sampling + (sSeq.max_sampling-sSeq.avg_sampling) * fraction
    samp_min = sSeq.avg_sampling + (sSeq.min_sampling-sSeq.avg_sampling) * fraction

    box_ext = [(-x_max, x_max), (-y_max, y_max), (samp_min, samp_max), (samp_min, samp_max)] 

    if block_nr >= 0:
        #For interior boxiSeq.ids = alldbnormalized_available_images[30000:45000]       
        if block_nr < num_blocks-1:
            eff_block_nr = block_nr
        else:
            eff_block_nr = block_nr-1
        fraction2 = (eff_block_nr / (num_blocks-1)) ** 0.333
        if fraction2 > 1:
            fraction2 = 1
        x_max = sSeq.trans_x_max * fraction2
        y_max = sSeq.trans_y_max * fraction2
        samp_max = sSeq.avg_sampling + (sSeq.max_sampling-sSeq.avg_sampling) * fraction2
        samp_min = sSeq.avg_sampling + (sSeq.min_sampling-sSeq.avg_sampling) * fraction2
        box_in = [(-x_max, x_max), (-y_max, y_max), (samp_min, samp_max), (samp_min, samp_max)] 
        
    samples = sub_box_sampling(box_in, box_ext, sSeq.block_size)
    sSeq.translations_x[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,0]
    sSeq.translations_y[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,1]
    sSeq.pixelsampling_x[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,2]
    sSeq.pixelsampling_y[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,3]
            
sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0

sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
sSeq.trans_sampled = True

sSeq.name = "Face Centering. Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f, 50)"%(-sSeq.trans_x_max, 
    sSeq.trans_x_max, -sSeq.trans_y_max, sSeq.trans_y_max, int(sSeq.min_sampling*1000), int(sSeq.max_sampling*1000))
print sSeq.name
iSeq.name = sSeq.name
SystemParameters.test_object_contents(sSeq)


####################################################################
###########    SYSTEM FOR REAL_FACE CLASSIFICATION      ############
####################################################################  
ParamsRFaceCentering = SystemParameters.ParamsSystem()
ParamsRFaceCentering.name = sTrainRFaceCentering.name
ParamsRFaceCentering.network = "linearNetwork4L"
ParamsRFaceCentering.iTrain = iTrainRFaceCentering
ParamsRFaceCentering.sTrain = sTrainRFaceCentering
ParamsRFaceCentering.iSeenid = iSeenidRFaceCentering
ParamsRFaceCentering.sSeenid = sSeenidRFaceCentering
ParamsRFaceCentering.iNewid = iNewidRFaceCentering
ParamsRFaceCentering.sNewid = sNewidRFaceCentering
##MEGAWARNING!!!!
#ParamsRFace.iNewid = iNewidScale
#ParamsRFace.sNewid = sNewidScale
#ParamsRFace.sNewid.translations_y = ParamsRFace.sNewid.translations_y * 0.0 + 8.0

ParamsRFaceCentering.block_size = iTrainRFaceCentering.block_size
ParamsRFaceCentering.train_mode = 'clustered' #clustered improves final performance! mixed
# 'mixed'!!! mse 0.31 clustered @ 6000 samples LSFA 11L, mse 0.30 mixed
# uexp08 => 0.019, 0.0147 @ 30 Signals (clustered)
# uexp08 => 0.063  @ 30 Signals (mixed, 5 levels)
# uexp08 => 0.034 @ 30 Signals (mixed, 10 levels)
# uexp08 => 0.027 @ 30 signals(mixed, 10 levels, pca_sfa_expo) pca_expo

ParamsRFaceCentering.analysis = None
ParamsRFaceCentering.enable_reduced_image_sizes = True
ParamsRFaceCentering.reduction_factor = 8.0 # WARNING 2.0, 4.0, 8.0
ParamsRFaceCentering.hack_image_size = 16 # WARNING 64, 32, 16
ParamsRFaceCentering.enable_hack_image_size = True

#sys.path.append("/home/escalafl/workspace/hiphi/src/hiphi/utils")







# EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X, EYE_L_X
#This network actually supports images in the closed intervals: [-eye_dx, eye_dx], [-eye_dy, eye_dy], [eye_smin0, eye_smax0]
eye_dx = 10
eye_dy = 10
eye_smax0 = 0.825 + 0.15
eye_smin0 = 0.825 - 0.15

print "***** Setting Training Information Parameters for Real Eye Translation X ******"
iSeq = iTrainREyeTransX = SystemParameters.ParamsInput()
iSeq.data_base_dir = frgc_eyeL_normalized_base_dir
iSeq.ids = numpy.arange(0,6000) # 8000, 7965

iSeq.trans = numpy.arange(-1 * eye_dx, eye_dx, 1)
if len(iSeq.ids) % len(iSeq.trans) != 0:
    ex="Here the number of translations must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * 8 # warning!!! 8
#To avoid grouping similar images next to one other
numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.trans)
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.trans)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Training Data Parameters for Real Eye TransX  ****************"
sSeq = sTrainREyeTransX = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 64
sSeq.subimage_height = 64 

sSeq.trans_x_max = eye_dx
sSeq.trans_x_min = -eye_dx
sSeq.trans_y_max = eye_dy
sSeq.trans_y_min = -eye_dy
sSeq.min_sampling = eye_smin0
sSeq.max_sampling = eye_smax0

sSeq.pixelsampling_x = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
sSeq.pixelsampling_y = sSeq.pixelsampling_x * 1.0
sSeq.subimage_first_row =  sSeq.image_height/2.0-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2.0-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.translations_y = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images)

sSeq.trans_sampled = True
sSeq.name = "REyeTans X Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
iSeq.name = sSeq.name
print sSeq.name
SystemParameters.test_object_contents(sSeq)


print "***** Setting Seenid Information Parameters for Real Eye Translation X ******"
iSeq = iSeenidREyeTransX = SystemParameters.ParamsInput()
iSeq.data_base_dir = frgc_eyeL_normalized_base_dir
iSeq.ids = numpy.arange(6000,8000) # 8000, 7965

iSeq.trans = numpy.arange(-1 * eye_dx, eye_dx, 1)
if len(iSeq.ids) % len(iSeq.trans) != 0:
    ex="Here the number of translations must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * 4 # warning!!! 4
#To avoid grouping similar images next to one other
numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.trans)
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.trans)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Seenid Data Parameters for Real Eye TransX  ****************"
sSeq = sSeenidREyeTransX = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 64
sSeq.subimage_height = 64 

sSeq.trans_x_max = eye_dx
sSeq.trans_x_min = -eye_dx
sSeq.trans_y_max = eye_dy
sSeq.trans_y_min = -eye_dy
sSeq.min_sampling = eye_smin0
sSeq.max_sampling = eye_smax0

sSeq.pixelsampling_x = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
sSeq.pixelsampling_y = sSeq.pixelsampling_x * 1.0
sSeq.subimage_first_row =  sSeq.image_height/2.0-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2.0-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.translations_y = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images)

sSeq.trans_sampled = True
sSeq.name = "REyeTans X Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
iSeq.name = sSeq.name
print sSeq.name
SystemParameters.test_object_contents(sSeq)


print "***** Setting Newid Information Parameters for Real Eye Translation X ******"
iSeq = iNewidREyeTransX = SystemParameters.ParamsInput()
iSeq.data_base_dir = frgc_eyeL_normalized_base_dir
iSeq.ids = numpy.arange(8000,10000) # 8000, 7965

iSeq.trans = numpy.arange(-1 * eye_dx, eye_dx, 1)
if len(iSeq.ids) % len(iSeq.trans) != 0:
    ex="Here the number of translations must be a divisor of the number of identities"
    raise Exception(ex)
iSeq.ages = [None]
iSeq.genders = [None]
iSeq.racetweens = [None]
iSeq.expressions = [None]
iSeq.morphs = [None]
iSeq.poses = [None]
iSeq.lightings = [None]
iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
iSeq.step = 1
iSeq.offset = 0
iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
iSeq.input_files = iSeq.input_files * 4 # warning!!! 4
#To avoid grouping similar images next to one other
numpy.random.shuffle(iSeq.input_files)  

iSeq.num_images = len(iSeq.input_files)
iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, iSeq.poses, iSeq.lightings]
iSeq.block_size = iSeq.num_images / len (iSeq.trans)
iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.trans)), iSeq.block_size)
iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)

SystemParameters.test_object_contents(iSeq)

print "******** Setting Newid Data Parameters for Real Eye TransX  ****************"
sSeq = sNewidREyeTransX = SystemParameters.ParamsDataLoading()
sSeq.input_files = iSeq.input_files
sSeq.num_images = iSeq.num_images
sSeq.block_size = iSeq.block_size
sSeq.image_width = 256
sSeq.image_height = 192
sSeq.subimage_width = 64
sSeq.subimage_height = 64 

sSeq.trans_x_max = eye_dx
sSeq.trans_x_min = -eye_dx
sSeq.trans_y_max = eye_dy
sSeq.trans_y_min = -eye_dy
sSeq.min_sampling = eye_smin0
sSeq.max_sampling = eye_smax0

sSeq.pixelsampling_x = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
sSeq.pixelsampling_y = sSeq.pixelsampling_x * 1.0
sSeq.subimage_first_row =  sSeq.image_height/2.0-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
sSeq.subimage_first_column = sSeq.image_width/2.0-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
sSeq.add_noise_L0 = True
sSeq.convert_format = "L"
sSeq.background_type = None
sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
sSeq.translations_y = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images)

sSeq.trans_sampled = True
sSeq.name = "REyeTans X Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f)"%(sSeq.trans_x_min, 
    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
iSeq.name = sSeq.name
print sSeq.name
SystemParameters.test_object_contents(sSeq)

#iSeenidREyeTransX = copy.deepcopy(iTrainREyeTransX)
#sSeenidREyeTransX = copy.deepcopy(sTrainREyeTransX)
#iNewidREyeTransX = copy.deepcopy(iTrainREyeTransX)
#sNewidREyeTransX = copy.deepcopy(sTrainREyeTransX)

####################################################################
#######    SYSTEM FOR REAL_EYE_TRANSLATION_X EXTRACTION     ########
####################################################################  
ParamsREyeTransX = SystemParameters.ParamsSystem()
ParamsREyeTransX.name = sTrainREyeTransX.name
ParamsREyeTransX.network = "linearNetwork4L"
ParamsREyeTransX.iTrain = iTrainREyeTransX
ParamsREyeTransX.sTrain = sTrainREyeTransX
ParamsREyeTransX.iSeenid = iSeenidREyeTransX
ParamsREyeTransX.sSeenid = sSeenidREyeTransX
ParamsREyeTransX.iNewid = iNewidREyeTransX
ParamsREyeTransX.sNewid = sNewidREyeTransX
ParamsREyeTransX.block_size = iTrainREyeTransX.block_size
ParamsREyeTransX.train_mode = 'mixed'
ParamsREyeTransX.analysis = None
ParamsREyeTransX.enable_reduced_image_sizes = True
ParamsREyeTransX.reduction_factor = 2.0
ParamsREyeTransX.hack_image_size = 32
ParamsREyeTransX.enable_hack_image_size = True


#REAL_EYE_TRANSLATION_Y REAL_EYE_TRANSLATION_Y REAL_EYE_TRANSLATION_Y REAL_EYE_TRANSLATION_Y REAL_EYE_TRANSLATION_Y REAL_EYE_TRANSLATION_Y
#Just exchange translations_x and translations_y to create iTrainREyeTransY
iTrainREyeTransY = copy.deepcopy(iTrainREyeTransX)
sTrainREyeTransY = copy.deepcopy(sTrainREyeTransX)
sTrainREyeTransY.name = sTrainREyeTransY.name[0:10]+"Y"+sTrainREyeTransY.name[11:]
tmp = sTrainREyeTransY.translations_x
sTrainREyeTransY.translations_x = sTrainREyeTransY.translations_y
sTrainREyeTransY.translations_y = tmp

iSeenidREyeTransY = copy.deepcopy(iSeenidREyeTransX)
sSeenidREyeTransY = copy.deepcopy(sSeenidREyeTransX)
sSeenidREyeTransY.name = sSeenidREyeTransY.name[0:10]+"Y"+sSeenidREyeTransY.name[11:]
tmp = sSeenidREyeTransY.translations_x
sSeenidREyeTransY.translations_x = sSeenidREyeTransY.translations_y
sSeenidREyeTransY.translations_y = tmp

iNewidREyeTransY = copy.deepcopy(iNewidREyeTransX)
sNewidREyeTransY = copy.deepcopy(sNewidREyeTransX)
sNewidREyeTransY.name= sSeenidREyeTransY.name[0:10]+"Y"+sSeenidREyeTransY.name[11:]
tmp = sNewidREyeTransY.translations_x
sNewidREyeTransY.translations_x = sNewidREyeTransY.translations_y
sNewidREyeTransY.translations_y = tmp

####################################################################
######    SYSTEM FOR REAL_EYE_TRANSLATION_Y EXTRACTION     #########
####################################################################  
ParamsREyeTransY = SystemParameters.ParamsSystem()
ParamsREyeTransY.name = sTrainREyeTransY.name
ParamsREyeTransY.network = "linearNetwork4L"
ParamsREyeTransY.iTrain = iTrainREyeTransY
ParamsREyeTransY.sTrain = sTrainREyeTransY
ParamsREyeTransY.iSeenid = iSeenidREyeTransY
ParamsREyeTransY.sSeenid = sSeenidREyeTransY
ParamsREyeTransY.iNewid = iNewidREyeTransY
ParamsREyeTransY.sNewid = sNewidREyeTransY
ParamsREyeTransY.block_size = iTrainREyeTransY.block_size
ParamsREyeTransY.train_mode = 'mixed' #mixed
ParamsREyeTransY.analysis = None
ParamsREyeTransY.enable_reduced_image_sizes = True
ParamsREyeTransY.reduction_factor = 2.0
ParamsREyeTransY.hack_image_size = 32
ParamsREyeTransY.enable_hack_image_size = True



############################################################
########## Function Defined Data Sources ###################
############################################################
def iSeqCreateRFaceCentering(num_images, alldbnormalized_available_images, alldb_noface_available_images, first_image=0, repetition_factor=1, seed=-1):
    if seed >= 0 or seed is None: #also works for 
        numpy.random.seed(seed)
    #else seed <0 then, do not change seed
    
    print "***** Setting information Parameters for RFaceCentering******"
    iSeq = SystemParameters.ParamsInput()
    # (0.55+1.1)/2 = 0.825, 0.55/2 = 0.275, 0.55/4 = 0.1375, .825 + .1375 = .9625, .825 - .55/4 = .6875
    iSeq.name = "Real FACE DISCRIMINATION (Centered / Decentered)"

    
    if num_images > len(alldbnormalized_available_images):
        err = "Number of images to be used exceeds the number of available images"
        raise Exception(err) 

    if num_images/10 * repetition_factor> len(alldb_noface_available_images):
        err = "Number of no_face images to be used exceeds the number of available images"
        raise Exception(err) 

    iSeq.data_base_dir = alldbnormalized_base_dir
   
    iSeq.ids = alldbnormalized_available_images[first_image:first_image + num_images] #30000, numpy.arange(0,6000) # 6000
    iSeq.faces = numpy.arange(0,10) # 0=centered normalized face, 1=not centered normalized face
    block_size = len(iSeq.ids) / len(iSeq.faces)
    
    #iSeq.scales = numpy.linspace(pipeline_fd['smin0'], pipeline_fd['smax0'], 50) # (-50, 50, 2)
    if len(iSeq.ids) % len(iSeq.faces) != 0:
        ex="Here the number of scales must be a divisor of the number of identities"
        raise Exception(ex)
    
    iSeq.ages = [None]
    iSeq.genders = [None]
    iSeq.racetweens = [None]
    iSeq.expressions = [None]
    iSeq.morphs = [None]
    iSeq.poses = [None]
    iSeq.lightings = [None]
    iSeq.slow_signal = 0 #real slow signal is whether there is the amount of face centering
    iSeq.step = 1
    iSeq.offset = 0
    iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                                iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                                iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
    iSeq.input_files = iSeq.input_files * repetition_factor  #  4 was overfitting non linear sfa slightly
    #To avoid grouping similar images next to one other or in the same block
    numpy.random.shuffle(iSeq.input_files)  
    
    #Background images are not duplicated, instead more are taken
    iSeq.data2_base_dir = alldb_noface_base_dir
    iSeq.ids2 = alldb_noface_available_images[0: block_size * repetition_factor]
    iSeq.input_files2 = imageLoader.create_image_filenames3(iSeq.data2_base_dir, "image", iSeq.slow_signal, iSeq.ids2, iSeq.ages, \
                                                iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                                iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
    iSeq.input_files2 = iSeq.input_files2 
    numpy.random.shuffle(iSeq.input_files2)
    
    iSeq.input_files = iSeq.input_files[0:-block_size* repetition_factor] + iSeq.input_files2
    
    iSeq.num_images = len(iSeq.input_files)
    #iSeq.params = [ids, expressions, morphs, poses, lightings]
    iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                      iSeq.morphs, iSeq.poses, iSeq.lightings]
    iSeq.block_size = iSeq.num_images / len (iSeq.faces)
    iSeq.train_mode = "clustered"
    print "BLOCK SIZE =", iSeq.block_size 
    
    iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.faces)), iSeq.block_size)
    iSeq.correct_labels = iSeq.correct_classes / (len(iSeq.faces)-1)
    
    SystemParameters.test_object_contents(iSeq)
    return iSeq


def sSeqCreateRFaceCentering(iSeq, seed=-1):
    if seed >= 0 or seed is None: #also works for 
        numpy.random.seed(seed)
    #else seed <0 then, do not change seed
    
    print "******** Setting Training Data Parameters for Real Face Centering****************"
    sSeq = SystemParameters.ParamsDataLoading()
    sSeq.input_files = iSeq.input_files
    sSeq.num_images = iSeq.num_images
    sSeq.block_size = iSeq.block_size
    sSeq.train_mode = iSeq.train_mode
    sSeq.image_width = 256
    sSeq.image_height = 192
    sSeq.subimage_width = 135
    sSeq.subimage_height = 135
    
    sSeq.trans_x_max = pipeline_fd['dx0'] * 1.0
    sSeq.trans_y_max = pipeline_fd['dy0'] * 1.0 * 0.998
    sSeq.min_sampling = pipeline_fd['smin0'] - 0.1 #WARNING!!!
    sSeq.max_sampling = pipeline_fd['smax0']
    sSeq.avg_sampling = (sSeq.min_sampling + sSeq.max_sampling)/2
    
    
    sSeq.pixelsampling_x = numpy.zeros(sSeq.num_images)
    sSeq.pixelsampling_y = numpy.zeros(sSeq.num_images) 
    sSeq.translations_x = numpy.zeros(sSeq.num_images)
    sSeq.translations_y = numpy.zeros(sSeq.num_images)
    
    
    num_blocks = sSeq.num_images/sSeq.block_size
    for block_nr in range(num_blocks):
        #For exterior box
        fraction = ((block_nr+1.0) / (num_blocks-1)) ** 0.333
        if fraction > 1:
            fraction = 1
        x_max = sSeq.trans_x_max * fraction
        y_max = sSeq.trans_y_max * fraction
        samp_max = sSeq.avg_sampling + (sSeq.max_sampling-sSeq.avg_sampling) * fraction
        samp_min = sSeq.avg_sampling + (sSeq.min_sampling-sSeq.avg_sampling) * fraction
    
        box_ext = [(-x_max, x_max), (-y_max, y_max), (samp_min, samp_max), (samp_min, samp_max)] 
    
        if block_nr >= 0:
            #For interior boxiSeq.ids = alldbnormalized_available_images[30000:45000]       
            if block_nr < num_blocks-1:
                eff_block_nr = block_nr
            else:
                eff_block_nr = block_nr-1
            fraction2 = (eff_block_nr / (num_blocks-1)) ** 0.333
            if fraction2 > 1:
                fraction2 = 1
            x_max = sSeq.trans_x_max * fraction2
            y_max = sSeq.trans_y_max * fraction2
            samp_max = sSeq.avg_sampling + (sSeq.max_sampling-sSeq.avg_sampling) * fraction2
            samp_min = sSeq.avg_sampling + (sSeq.min_sampling-sSeq.avg_sampling) * fraction2
            box_in = [(-x_max, x_max), (-y_max, y_max), (samp_min, samp_max), (samp_min, samp_max)] 
        
        samples = sub_box_sampling(box_in, box_ext, sSeq.block_size)
        sSeq.translations_x[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,0]
        sSeq.translations_y[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,1]
        sSeq.pixelsampling_x[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,2]
        sSeq.pixelsampling_y[block_nr*sSeq.block_size: (block_nr+1)*sSeq.block_size] = samples[:,3]
                
    sSeq.subimage_first_row =  sSeq.image_height/2-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
    sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
    
    sSeq.add_noise_L0 = True
    sSeq.convert_format = "L"
    sSeq.background_type = None
    sSeq.trans_sampled = True
    
    sSeq.name = "Face Centering. Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f, 50)"%(-sSeq.trans_x_max, 
        sSeq.trans_x_max, -sSeq.trans_y_max, sSeq.trans_y_max, int(sSeq.min_sampling*1000), int(sSeq.max_sampling*1000))
    print sSeq.name
    iSeq.name = sSeq.name

    
    sSeq.load_data = lambda : load_data_from_sSeq(sSeq)

    SystemParameters.test_object_contents(sSeq)


alldbnormalized_available_images = numpy.arange(0,55000)
numpy.random.shuffle(alldbnormalized_available_images)  
av_fim = alldbnormalized_available_images
alldb_noface_available_images = numpy.arange(0,12000)
numpy.random.shuffle(alldb_noface_available_images)
av_nfim =alldb_noface_available_images

iSeq = iSeqCreateRFaceCentering(3000, av_fim, av_nfim, first_image=0, repetition_factor=2, seed=-1)
sSeq = sSeqCreateRFaceCentering(iSeq, seed=-1)
print ";)"


iSeq = iTrainRFaceCentering2 = \
[[iSeqCreateRFaceCentering(3000, av_fim, av_nfim, first_image=0, repetition_factor=2, seed=-1)], \
[iSeqCreateRFaceCentering(3000, av_fim, av_nfim, first_image=3000, repetition_factor=2, seed=-1),iSeqCreateRFaceCentering(3000, av_fim, av_nfim, first_image=6000, repetition_factor=2, seed=-1)]]

sTrainRFaceCentering2 = [[sSeqCreateRFaceCentering(iSeq[0][0], seed=-1)], \
                        [sSeqCreateRFaceCentering(iSeq[1][0], seed=-1), sSeqCreateRFaceCentering(iSeq[1][1], seed=-1)]]
iSeq = iSeenidRFaceCentering2 = [[iSeqCreateRFaceCentering(1000, av_fim, av_nfim, first_image=30000, repetition_factor=2, seed=-1)]]
sSeenidRFaceCentering2 =  [[sSeqCreateRFaceCentering(iSeq[0][0], seed=-1)]]
iSeq = iNewidRFaceCentering2 = [[iSeqCreateRFaceCentering(1000, av_fim, av_nfim, first_image=45000, repetition_factor=2, seed=-1)]]
sNewidRFaceCentering2 = [[sSeqCreateRFaceCentering(iSeq[0][0], seed=-1)]]
      
ParamsRFaceCenteringFunc = SystemParameters.ParamsSystem()
ParamsRFaceCenteringFunc.name = "Function Based Data Creation for RFaceCentering"
ParamsRFaceCenteringFunc.network = "linearNetwork4L"  #Default Network, but ignored
ParamsRFaceCenteringFunc.iTrain =iTrainRFaceCentering2
ParamsRFaceCenteringFunc.sTrain = sTrainRFaceCentering2
ParamsRFaceCenteringFunc.iSeenid = iSeenidRFaceCentering2
ParamsRFaceCenteringFunc.sSeenid = sSeenidRFaceCentering2
ParamsRFaceCenteringFunc.iNewid = iNewidRFaceCentering2
ParamsRFaceCenteringFunc.sNewid = sNewidRFaceCentering2
ParamsRFaceCenteringFunc.block_size = iTrainRFaceCentering2[0][0].block_size
ParamsRFaceCenteringFunc.train_mode = 'clustered' #clustered improves final performance! mixed
ParamsRFaceCenteringFunc.analysis = None
ParamsRFaceCenteringFunc.enable_reduced_image_sizes = True
ParamsRFaceCenteringFunc.reduction_factor = 8.0 # WARNING 2.0, 4.0, 8.0
ParamsRFaceCenteringFunc.hack_image_size = 16 # WARNING 64, 32, 16
ParamsRFaceCenteringFunc.enable_hack_image_size = True






#PIPELINE FOR FACE DETECTION:
#Orig=TX: DX0=+/- 45, DY0=+/- 20, DS0= 0.55-1.1
#TY: DX1=+/- 20, DY0=+/- 20, DS0= 0.55-1.1
#S: DX1=+/- 20, DY1=+/- 10, DS0= 0.55-1.1
#TMX: DX1=+/- 20, DY1=+/- 10, DS1= 0.775-1.05
#TMY: DX2=+/- 10, DY1=+/- 10, DS1= 0.775-1.05
#MS: DX2=+/- 10, DY2=+/- 5, DS1= 0.775-1.05
#Out About: DX2=+/- 10, DY2=+/- 5, DS2= 0.8875-1.025
#notice: for dx* and dy* intervals are open, while for smin and smax intervals are closed
#Pipeline actually supports inputs in: [-dx0, dx0-2] [-dy0, dy0-2] [smin0, smax0] 
#Remember these values are before image resizing
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#This network actually supports images in the closed intervals: [smin0, smax0] [-dy0, dy0]
#but halb-open [-dx0, dx0) 
pipeline_fd = dict(dx0 = 45, dy0 = 20, smin0 = 0.55, smax0 = 1.1,
                dx1 = 20, dy1 = 10, smin1 = 0.775, smax1 = 1.05)
#7965, 8
def iSeqCreateRTransX(num_images, alldbnormalized_available_images, first_image=0, repetition_factor=1, seed=-1):
    if seed >= 0 or seed is None: #also works for 
        numpy.random.seed(seed)

    if num_images > len(alldbnormalized_available_images):
        err = "Number of images to be used exceeds the number of available images"
        raise Exception(err) 


    print "***** Setting Information Parameters for Real Translation X ******"
    iSeq = SystemParameters.ParamsInput()
    iSeq.name = "Real Translation X: (-45, 45, 2) translation and y 40"
    iSeq.data_base_dir = alldbnormalized_base_dir
    iSeq.ids = alldbnormalized_available_images[first_image:first_image + num_images] 

    iSeq.trans = numpy.arange(-1 * pipeline_fd['dx0'], pipeline_fd['dx0'], 2) # (-50, 50, 2)
    if len(iSeq.ids) % len(iSeq.trans) != 0:
        ex="Here the number of translations must be a divisor of the number of identities"
        raise Exception(ex)
    iSeq.ages = [None]
    iSeq.genders = [None]
    iSeq.racetweens = [None]
    iSeq.expressions = [None]
    iSeq.morphs = [None]
    iSeq.poses = [None]
    iSeq.lightings = [None]
    iSeq.slow_signal = 0 #real slow signal is the translation in the x axis (correlated to identity), added during image loading
    iSeq.step = 1
    iSeq.offset = 0
    iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                                iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                                iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
    iSeq.input_files = iSeq.input_files * repetition_factor # warning!!! 4, 8
    #To avoid grouping similar images next to one other, even though available images already shuffled
    numpy.random.shuffle(iSeq.input_files)  
    
    iSeq.num_images = len(iSeq.input_files)
    #iSeq.params = [ids, expressions, morphs, poses, lightings]
    iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                      iSeq.morphs, iSeq.poses, iSeq.lightings]
    iSeq.block_size = iSeq.num_images / len (iSeq.trans)
    iSeq.train_mode = "mixed"
    print "BLOCK SIZE =", iSeq.block_size 
    iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.trans)), iSeq.block_size)
    iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
    
    SystemParameters.test_object_contents(iSeq)
    return iSeq

def sSeqCreateRTransX(iSeq, seed=-1):
    if seed >= 0 or seed is None: #also works for 
        numpy.random.seed(seed)
    #else seed <0 then, do not change seed
    
    print "******** Setting Training Data Parameters for Real TransX  ****************"
    sSeq = SystemParameters.ParamsDataLoading()
    sSeq.input_files = iSeq.input_files
    sSeq.num_images = iSeq.num_images
    sSeq.block_size = iSeq.block_size
    sSeq.train_mode = iSeq.train_mode
    sSeq.include_latest = iSeq.include_latest
    sSeq.image_width = 256
    sSeq.image_height = 192
    sSeq.subimage_width = 128
    sSeq.subimage_height = 128 
    
    sSeq.trans_x_max = pipeline_fd['dx0']
    sSeq.trans_x_min = -1 * pipeline_fd['dx0']
    
    #WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    sSeq.trans_y_max = pipeline_fd['dy0']
    sSeq.trans_y_min = -1 * sSeq.trans_y_max
    
    #iSeq.scales = numpy.linspace(0.5, 1.30, 16) # (-50, 50, 2)
    sSeq.min_sampling = pipeline_fd['smin0']
    sSeq.max_sampling = pipeline_fd['smax0']
    
    sSeq.pixelsampling_x = sSeq.pixelsampling_y = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
    #sSeq.subimage_pixelsampling = 2
    sSeq.subimage_first_row =  sSeq.image_height/2.0-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
    sSeq.subimage_first_column = sSeq.image_width/2.0-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
    #sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
    sSeq.add_noise_L0 = True
    sSeq.convert_format = "L"
    sSeq.background_type = None
    #random translation for th w coordinate
    #sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
    #sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)                                                           
    sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
    sSeq.translations_y = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, sSeq.num_images)
    sSeq.trans_sampled = True
    sSeq.name = "RTans X Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f)"%(sSeq.trans_x_min, 
        sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)

    sSeq.load_data = load_data_from_sSeq
    SystemParameters.test_object_contents(sSeq)
    return sSeq
    


####################################################################
###########    SYSTEM FOR REAL_TRANSLATION_X EXTRACTION      ############
####################################################################  
av_fim = alldbnormalized_available_images = numpy.arange(0,55000)
numpy.random.shuffle(alldbnormalized_available_images)  

#iSeq = iSeqCreateRTransX(4500, av_fim, first_image=0, repetition_factor=2, seed=-1)
#sSeq = sSeqCreateRTransX(iSeq, seed=-1)
#print ";) 2"
#iSeq=None 
#sSeq =None

## CASE [[F]]
iSeq_set = iTrainRTransX2 = [[iSeqCreateRTransX(9000, av_fim, first_image=0, repetition_factor=1, seed=-1)]]
sSeq_set = sTrainRTransX2 = [[sSeqCreateRTransX(iSeq_set[0][0], seed=-1)]]
#print sSeq_set[0][0].block_size

## CASE [[F1, F2]]
#iSeq_set = iTrainRTransX2 = [[iSeqCreateRTransX(4500, av_fim, first_image=0, repetition_factor=1, seed=-1), 
#                              iSeqCreateRTransX(2250, av_fim, first_image=4500, repetition_factor=1, seed=-1)]]
#sSeq_set = sTrainRTransX2 = [[sSeqCreateRTransX(iSeq_set[0][0], seed=-1), sSeqCreateRTransX(iSeq_set[0][1], seed=-1)]]

## CASE [[F1],[F2], ...] 
#iSeq_set = iTrainRTransX2 = [[iSeqCreateRTransX(1800, av_fim, first_image=0, repetition_factor=1, seed=-1)], 
#                             [iSeqCreateRTransX(1800, av_fim, first_image=1800, repetition_factor=1, seed=-1)], 
#                             [iSeqCreateRTransX(1800, av_fim, first_image=3600, repetition_factor=1, seed=-1)], 
#                             [iSeqCreateRTransX(1800, av_fim, first_image=5400, repetition_factor=1, seed=-1)], 
#                             [iSeqCreateRTransX(1800, av_fim, first_image=7200, repetition_factor=1, seed=-1)]]
#sSeq_set = sTrainRTransX2 = [[sSeqCreateRTransX(iSeq_set[0][0], seed=-1)], 
#                             [sSeqCreateRTransX(iSeq_set[1][0], seed=-1)], 
#                             [sSeqCreateRTransX(iSeq_set[2][0], seed=-1)], 
#                             [sSeqCreateRTransX(iSeq_set[3][0], seed=-1)], 
#                             [sSeqCreateRTransX(iSeq_set[4][0], seed=-1)]]


## CASE [[F1, F2],[F1, F3], ...] 
#iSeq0 = iSeqCreateRTransX(4500, av_fim, first_image=0, repetition_factor=1, seed=-1)
#sSeq0 = sSeqCreateRTransX(iSeq0, seed=-1)
#
#iSeq_set = iTrainRTransX2 = [[copy.deepcopy(iSeq0), iSeqCreateRTransX(900, av_fim, first_image=4500, repetition_factor=1, seed=-1)], 
#                             [copy.deepcopy(iSeq0), iSeqCreateRTransX(900, av_fim, first_image=5400, repetition_factor=1, seed=-1)], 
#                             [copy.deepcopy(iSeq0), iSeqCreateRTransX(900, av_fim, first_image=6300, repetition_factor=1, seed=-1)], 
#                             [copy.deepcopy(iSeq0), iSeqCreateRTransX(900, av_fim, first_image=7200, repetition_factor=1, seed=-1)],
#                             [copy.deepcopy(iSeq0), iSeqCreateRTransX(900, av_fim, first_image=8100, repetition_factor=1, seed=-1)],                             
#                             ]
#sSeq_set = sTrainRTransX2 = [[copy.deepcopy(sSeq0), sSeqCreateRTransX(iSeq_set[0][1], seed=-1)], 
#                             [copy.deepcopy(sSeq0), sSeqCreateRTransX(iSeq_set[1][1], seed=-1)], 
#                             [copy.deepcopy(sSeq0), sSeqCreateRTransX(iSeq_set[2][1], seed=-1)],
#                             [copy.deepcopy(sSeq0), sSeqCreateRTransX(iSeq_set[3][1], seed=-1)],                              
#                             [copy.deepcopy(sSeq0), sSeqCreateRTransX(iSeq_set[4][1], seed=-1)],
#                             ]


print sSeq_set[0][0].subimage_width 


iSeq = iSeenidRTransX2 = iSeqCreateRTransX(9000, av_fim, first_image=9000, repetition_factor=1, seed=-1)
sSeenidRTransX2 = sSeqCreateRTransX(iSeq, seed=-1)
print sSeenidRTransX2.subimage_width

iSeq_set = iNewidRTransX2 = [[iSeqCreateRTransX(4500, av_fim, first_image=18000, repetition_factor=1, seed=-1)]]
sNewidRTransX2 = [[sSeqCreateRTransX(iSeq_set[0][0], seed=-1)]]
print sSeq_set[0][0].subimage_width


ParamsRTransXFunc = SystemParameters.ParamsSystem()
ParamsRTransXFunc.name = "Function Based Data Creation for RTransX"
ParamsRTransXFunc.network = "linearNetwork4L" #Default Network, but ignored
ParamsRTransXFunc.iTrain =iTrainRTransX2
ParamsRTransXFunc.sTrain = sTrainRTransX2

ParamsRTransXFunc.iSeenid = iSeenidRTransX2
ParamsRTransXFunc.sSeenid = sSeenidRTransX2

ParamsRTransXFunc.iNewid = iNewidRTransX2
ParamsRTransXFunc.sNewid = sNewidRTransX2

ParamsRTransXFunc.block_size = iTrainRTransX2[0][0].block_size
ParamsRTransXFunc.train_mode = 'clustered' #clustered improves final performance! mixed
ParamsRTransXFunc.analysis = None
ParamsRTransXFunc.enable_reduced_image_sizes = True
ParamsRTransXFunc.reduction_factor = 8.0 # WARNING 1.0, 2.0, 4.0, 8.0
ParamsRTransXFunc.hack_image_size = 16 # WARNING 128, 64, 32, 16
ParamsRTransXFunc.enable_hack_image_size = True






# YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYyYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
#This network actually supports images in the closed intervals: [-dx1, dx1], [smin0, smax0]
#but halb-open [-dy0, dy0)
def iSeqCreateRTransY(num_images, alldbnormalized_available_images, first_image=0, repetition_factor=1, seed=-1): 
    if seed >= 0 or seed is None: #also works for 
        numpy.random.seed(seed)

    if num_images > len(alldbnormalized_available_images):
        err = "Number of images to be used exceeds the number of available images"
        raise Exception(err) 

    print "***** Setting Training Information Parameters for Real Translation Y ******"
    iSeq = SystemParameters.ParamsInput()
    iSeq.name = "Real Translation Y: Y(-20, 20, 1) translation and dx 20"

    iSeq.data_base_dir = alldbnormalized_base_dir
    iSeq.ids = alldbnormalized_available_images[first_image:first_image + num_images] 
    
    iSeq.trans = numpy.arange(-1 * pipeline_fd['dy0'], pipeline_fd['dy0'], 1) # (-50, 50, 2)
    if len(iSeq.ids) % len(iSeq.trans) != 0:
        ex="Here the number of translations (%d) must be a divisor of the number of identities (%d)"%(len(iSeq.ids), len(iSeq.trans))
        raise Exception(ex)
        
    iSeq.ages = [None]
    iSeq.genders = [None]
    iSeq.racetweens = [None]
    iSeq.expressions = [None]
    iSeq.morphs = [None]
    iSeq.poses = [None]
    iSeq.lightings = [None]
    iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
    iSeq.step = 1
    iSeq.offset = 0
    iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                                iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                                iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
    iSeq.input_files = iSeq.input_files * repetition_factor # warning!!! 4, 8
    #To avoid grouping similar images next to one other
    numpy.random.shuffle(iSeq.input_files)  
    
    iSeq.num_images = len(iSeq.input_files)
    #iSeq.params = [ids, expressions, morphs, poses, lightings]
    iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                      iSeq.morphs, iSeq.poses, iSeq.lightings]
    iSeq.block_size = iSeq.num_images / len (iSeq.trans)
    iSeq.train_mode = "mixed"    
    print "BLOCK SIZE =", iSeq.block_size 
    iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.trans)), iSeq.block_size)
    iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)   
    SystemParameters.test_object_contents(iSeq)
    return iSeq

def sSeqCreateRTransY(iSeq, seed=-1):
    if seed >= 0 or seed is None: #also works for 
        numpy.random.seed(seed)
    #else seed <0 then, do not change seed

    print "******** Setting Training Data Parameters for Real TransY  ****************"
    sSeq = SystemParameters.ParamsDataLoading()
    sSeq.input_files = iSeq.input_files
    sSeq.num_images = iSeq.num_images
    sSeq.block_size = iSeq.block_size
    sSeq.train_mode = iSeq.train_mode
    sSeq.image_width = 256
    sSeq.image_height = 192
    sSeq.subimage_width = 128
    sSeq.subimage_height = 128 
    
    sSeq.trans_x_max = pipeline_fd['dx1']
    sSeq.trans_x_min = -1 * pipeline_fd['dx1']
    
    sSeq.trans_y_max = pipeline_fd['dy0']
    sSeq.trans_y_min = -1 * sSeq.trans_y_max
    
    #iSeq.scales = numpy.linspace(0.5, 1.30, 16) # (-50, 50, 2)
    sSeq.min_sampling = pipeline_fd['smin0']
    sSeq.max_sampling = pipeline_fd['smax0']
    
    sSeq.pixelsampling_x = sSeq.pixelsampling_y = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
    #sSeq.subimage_pixelsampling = 2
    sSeq.subimage_first_row =  sSeq.image_height/2.0-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
    sSeq.subimage_first_column = sSeq.image_width/2.0-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
    #sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
    sSeq.add_noise_L0 = True
    sSeq.convert_format = "L"
    sSeq.background_type = None
    #random translation for th w coordinate
    #sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
    #sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)                                                           
    sSeq.translations_x = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images)
    sSeq.translations_y = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
    
    sSeq.trans_sampled = True
    sSeq.name = "RTans Y Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f)"%(sSeq.trans_x_min, 
        sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
    iSeq.name = sSeq.name
    SystemParameters.test_object_contents(sSeq)
    return sSeq


av_fim = alldbnormalized_available_images = numpy.arange(0,55000)
numpy.random.shuffle(alldbnormalized_available_images)  

#iSeq = iSeqCreateRTransY(4800, av_fim, first_image=0, repetition_factor=2, seed=-1)
#sSeq = sSeqCreateRTransY(iSeq, seed=-1)
#print ";) 3"
#quit()

iSeq=None 
sSeq =None

## CASE [[F]]
iSeq_set = iTrainRTransY2 = [[iSeqCreateRTransY(10000, av_fim, first_image=0, repetition_factor=1, seed=-1)]]
sSeq_set = sTrainRTransY2 = [[sSeqCreateRTransY(iSeq_set[0][0], seed=-1)]]

## CASE [[F1, F2]]
#iSeq_set = iTrainRTransY2 = [[iSeqCreateRTransY(4500, av_fim, first_image=0, repetition_factor=1, seed=-1), 
#                              iSeqCreateRTransY(2250, av_fim, first_image=4500, repetition_factor=1, seed=-1)]]
#sSeq_set = sTrainRTransY2 = [[sSeqCreateRTransY(iSeq_set[0][0], seed=-1), sSeqCreateRTransY(iSeq_set[0][1], seed=-1)]]

## CASE [[F1],[F2], ...] 
#iSeq_set = iTrainRTransY2 = [[iSeqCreateRTransY(1800, av_fim, first_image=0, repetition_factor=1, seed=-1)], 
#                             [iSeqCreateRTransY(1800, av_fim, first_image=1800, repetition_factor=1, seed=-1)], 
#                             [iSeqCreateRTransY(1800, av_fim, first_image=3600, repetition_factor=1, seed=-1)], 
#                             [iSeqCreateRTransY(1800, av_fim, first_image=5400, repetition_factor=1, seed=-1)], 
#                             [iSeqCreateRTransY(1800, av_fim, first_image=7200, repetition_factor=1, seed=-1)]]
#sSeq_set = sTrainRTransY2 = [[sSeqCreateRTransY(iSeq_set[0][0], seed=-1)], 
#                             [sSeqCreateRTransY(iSeq_set[1][0], seed=-1)], 
#                             [sSeqCreateRTransY(iSeq_set[2][0], seed=-1)], 
#                             [sSeqCreateRTransY(iSeq_set[3][0], seed=-1)], 
#                             [sSeqCreateRTransY(iSeq_set[4][0], seed=-1)]]


## CASE [[F1, F2],[F1, F3], ...] 
#iSeq0 = iSeqCreateRTransY(4500, av_fim, first_image=0, repetition_factor=1, seed=-1)
#sSeq0 = sSeqCreateRTransY(iSeq0, seed=-1)
#
#iSeq_set = iTrainRTransY2 = [[copy.deepcopy(iSeq0), iSeqCreateRTransY(900, av_fim, first_image=4500, repetition_factor=1, seed=-1)], 
#                             [copy.deepcopy(iSeq0), iSeqCreateRTransY(900, av_fim, first_image=5400, repetition_factor=1, seed=-1)], 
#                             [copy.deepcopy(iSeq0), iSeqCreateRTransY(900, av_fim, first_image=6300, repetition_factor=1, seed=-1)], 
#                             [copy.deepcopy(iSeq0), iSeqCreateRTransY(900, av_fim, first_image=7200, repetition_factor=1, seed=-1)],
#                             [copy.deepcopy(iSeq0), iSeqCreateRTransY(900, av_fim, first_image=8100, repetition_factor=1, seed=-1)],                             
#                             ]
#sSeq_set = sTrainRTransY2 = [[copy.deepcopy(sSeq0), sSeqCreateRTransY(iSeq_set[0][1], seed=-1)], 
#                             [copy.deepcopy(sSeq0), sSeqCreateRTransY(iSeq_set[1][1], seed=-1)], 
#                             [copy.deepcopy(sSeq0), sSeqCreateRTransY(iSeq_set[2][1], seed=-1)],
#                             [copy.deepcopy(sSeq0), sSeqCreateRTransY(iSeq_set[3][1], seed=-1)],                              
#                             [copy.deepcopy(sSeq0), sSeqCreateRTransY(iSeq_set[4][1], seed=-1)],
#                             ]


print sSeq_set[0][0].subimage_width 


iSeq = iSeenidRTransY2 = iSeqCreateRTransY(10000, av_fim, first_image=10000, repetition_factor=1, seed=-1)
sSeenidRTransY2 = sSeqCreateRTransY(iSeq, seed=-1)
print sSeenidRTransY2.subimage_width

iSeq_set = iNewidRTransY2 = [[iSeqCreateRTransY(5000, av_fim, first_image=20000, repetition_factor=1, seed=-1)]]
sNewidRTransY2 = [[sSeqCreateRTransY(iSeq_set[0][0], seed=-1)]]
print sSeq_set[0][0].subimage_width


ParamsRTransYFunc = SystemParameters.ParamsSystem()
ParamsRTransYFunc.name = "Function Based Data Creation for RTransY"
ParamsRTransYFunc.network = "linearNetwork4L" #Default Network, but ignored
ParamsRTransYFunc.iTrain =iTrainRTransY2
ParamsRTransYFunc.sTrain = sTrainRTransY2

ParamsRTransYFunc.iSeenid = iSeenidRTransY2
ParamsRTransYFunc.sSeenid = sSeenidRTransY2

ParamsRTransYFunc.iNewid = iNewidRTransY2
ParamsRTransYFunc.sNewid = sNewidRTransY2

ParamsRTransYFunc.block_size = iTrainRTransY2[0][0].block_size
ParamsRTransYFunc.train_mode = 'clustered' #clustered improves final performance! mixed
ParamsRTransYFunc.analysis = None
ParamsRTransYFunc.enable_reduced_image_sizes = True
ParamsRTransYFunc.reduction_factor = 8.0 # WARNING 1.0, 2.0, 4.0, 8.0
ParamsRTransYFunc.hack_image_size = 16 # WARNING 128, 64, 32, 16
ParamsRTransYFunc.enable_hack_image_size = True



#Mixed training PosX & PosY
#NOTE: This is a hack to avoid repetition, the logic needs to be improved
iTrainRTransXY2 = [[copy.deepcopy(iTrainRTransX2[0][0]), copy.deepcopy(iTrainRTransY2[0][0])],
                   None,
                   None,
                   None,
                   [copy.deepcopy(iTrainRTransX2[0][0])],
                   ] 
                   
sTrainRTransXY2 = [[copy.deepcopy(sTrainRTransX2[0][0]), copy.deepcopy(sTrainRTransY2[0][0])],
                   None,
                   None,
                   None,
                   [copy.deepcopy(sTrainRTransX2[0][0])],
                   ]

ParamsRTransXYFunc = SystemParameters.ParamsSystem()
ParamsRTransXYFunc.name = "Function Based Data Creation for RTransY with generic data RTransX & RTransY"
ParamsRTransXYFunc.network = "linearNetwork4L" #Default Network, but ignored
ParamsRTransXYFunc.iTrain =iTrainRTransXY2
ParamsRTransXYFunc.sTrain = sTrainRTransXY2

ParamsRTransXYFunc.iSeenid = iSeenidRTransX2
ParamsRTransXYFunc.sSeenid = sSeenidRTransX2

ParamsRTransXYFunc.iNewid = iNewidRTransX2
ParamsRTransXYFunc.sNewid = sNewidRTransX2

ParamsRTransXYFunc.block_size = iTrainRTransXY2[0][0].block_size
ParamsRTransXYFunc.train_mode = 'clustered' #clustered improves final performance! mixed
ParamsRTransXYFunc.analysis = None
ParamsRTransXYFunc.enable_reduced_image_sizes = True
ParamsRTransXYFunc.reduction_factor = 8.0 # WARNING 1.0, 2.0, 4.0, 8.0
ParamsRTransXYFunc.hack_image_size = 16 # WARNING 128, 64, 32, 16
ParamsRTransXYFunc.enable_hack_image_size = True


##############################################
#The German Traffic Sign Recognition Benchmark
##############################################
#Base code originally taken from the competition website
import csv

# function for reading the image annotations and labels
# arguments: path to the traffic sign data, for example './GTSRB/Training'
# returns: list of image filenames, list of all tracks, list of all image annotations, list of all labels, 
def readTrafficSignsAnnotations(rootpath, shrink_signs=True, shrink_factor = 0.8, correct_sizes=True, include_labels=False, sign_selection=None):
    '''Reads traffic sign data for German Traffic Sign Recognition Benchmark.

    Arguments: path to the traffic sign data, for example './GTSRB/Training'
    Returns:   list of images, list of corresponding labels'''
#    images = [] # image filenames
    annotations =  [] #annotations for each image
#    labels = [] # corresponding labels
#    tracks = []
    # loop over all 42 classes
    delta_rand_scale=0.0
    repetition_factors=None
    
    if sign_selection==None:
        sign_selection = numpy.arange(43)
    
    if repetition_factors is None:
        repetition_factors = [1]*43
    for c in sign_selection:
        prefix = rootpath + '/' + "%05d"%c + '/' # subdirectory for class. format(c, '05d')
        gtFile = open(prefix + 'GT-'+ "%05d"%c + '.csv') # annotations file. format(c, '05d')
        gtReader = csv.reader(gtFile, delimiter=';') # csv parser for annotations file
        gtReader.next() # skip header
        # loop over all images in current annotations file
        for ii, row in enumerate(gtReader):           
#            if ii%1000==0:
#                print row
            image_filename = prefix + row[0]
            extended_row = [image_filename] # extended_row: filename, track number, im_width, im_height, x0, y0, x1, y1
            if correct_sizes:   
                im = Image.open(image_filename)
#                row[1:3] = map(int, row[1:3])
#                if row[1] != im.size[0] or row[2] != im.size[1]:
#                    print "Image %s has incorrect size label"%image_filename, row[1:3], im.size[0:2]
                row[1] = im.size[0]
                row[2] = im.size[1]
                del im
            extended_row.append(int(row[0][0:5])) #Extract track number
            if shrink_signs:
                sign_coordinates = map(float, row[3:7])
                center_x = (sign_coordinates[0] + sign_coordinates[2])/2.0
                center_y = (sign_coordinates[1] + sign_coordinates[3])/2.0
                rand_scale_factor1 = 1.0 + numpy.random.uniform(-delta_rand_scale,delta_rand_scale)
                rand_scale_factor2 = 1.0 + numpy.random.uniform(-delta_rand_scale,delta_rand_scale)
                width = (sign_coordinates[2] - sign_coordinates[0]+1)*shrink_factor* rand_scale_factor1
                height = (sign_coordinates[3] - sign_coordinates[1]+1)*shrink_factor * rand_scale_factor2         
                row[3] = center_x - width/2
                row[5] = center_x + width/2
                row[4] = center_y - height/2
                row[6] = center_y + height/2
            extended_row = extended_row + map(float, row[1:7])
            if include_labels:
                extended_row.append(int(row[7])) # the 8th column is the label
            for i in range(repetition_factors[c]):
                annotations.append(extended_row)
        gtFile.close()
    
#     #Correct class indices, so that only consecutive classes appear
#     if correct_classes:
#         all_classes=[]
#         for row in annotations:
#             all_classes.append(row[8])
#         unique, corrected_classes = numpy.unique(all_classes, return_inverse=True) 
#         print "unique classes:", unique
#         for ii, row in enumerate(annotations):
#             row[8] = corrected_classes[ii]
    
    return annotations


def readTrafficSignsAnnotationsOnline(prefix, csv_file, shrink_signs=True, correct_sizes=True, include_labels=False, sign_selection=None):
    '''Reads traffic sign data for German Traffic Sign Recognition Benchmark.

    Arguments: path to the traffic sign data, for example './GTSRB/Training'
    Returns:   list of images, list of corresponding labels'''
    
    if sign_selection==None:
        sign_selection = numpy.arange(43)
        
    images = [] # image filenames
    annotations =  [] #annotations for each image
    labels = [] # corresponding labels
    tracks = []
    # loop over all 42 classes
    gtFile = open(prefix + '/' + csv_file) # annotations file
    gtReader = csv.reader(gtFile, delimiter=';') # csv parser for annotations file
    gtReader.next() # skip header
    # loop over all images in current annotations file
    for ii, row in enumerate(gtReader):           
#            if ii%1000==0:
#                print row
        image_filename = prefix + "/" + row[0]
        extended_row = [image_filename] # extended_row: filename, track number, im_width, im_height, x0, y0, x1, y1
        if correct_sizes:   
            im = Image.open(image_filename)
#                row[1:3] = map(int, row[1:3])
#                if row[1] != im.size[0] or row[2] != im.size[1]:
#                    print "Image %s has incorrect size label"%image_filename, row[1:3], im.size[0:2]
            row[1] = im.size[0]
            row[2] = im.size[1]
            del im
        extended_row.append(0) #Fictuous track number
        if shrink_signs:
            shrink_factor = 0.8
            sign_coordinates = map(float, row[3:7])
            center_x = (sign_coordinates[0] + sign_coordinates[2])/2.0
            center_y = (sign_coordinates[1] + sign_coordinates[3])/2.0
            width = (sign_coordinates[2] - sign_coordinates[0]+1)*shrink_factor
            height = (sign_coordinates[3] - sign_coordinates[1]+1)*shrink_factor                
            row[3] = center_x - width/2
            row[5] = center_x + width/2
            row[4] = center_y - height/2
            row[6] = center_y + height/2
        extended_row = extended_row + map(float, row[1:7])
        if include_labels:
            label = int(row[7])
            if label in sign_selection:
                extended_row.append(label) # the 8th column is the label, not available in online test
                annotations.append(extended_row)
        else:
            extended_row.append(0)
            annotations.append(extended_row)
    gtFile.close()
   
    return annotations


def count_annotation_classes(annotations):
    classes = []
    count = []
    for row in annotations:
        classes.append(row[8])
    classes = numpy.array(classes)
    for c in range(0,43):
        #print "  class %d appears:"%c, (classes[:]==c).sum(),
        count.append((classes[:]==c).sum())
    return numpy.array(count)

def enforce_max_samples_per_class(annotations, max_samples=150, repetition=1):
    annot_list = [None]*43 
    for i in range(len(annot_list)):
        annot_list[i] = []

    if isinstance(repetition, int):
        repetition = [repetition]*43

    for row in annotations:
        c = int(row[8])
        for i in range(repetition[c]):
            annot_list[c] += [copy.deepcopy(row)]
    
    print "fixing max number of samples per class"
    for c in range(43):
        if len(annot_list[c])>max_samples:
#            print "len(class[%d])=%d"%(c, len(annot_list[c])),
            numpy.random.shuffle(annot_list[c])
            annot_list[c] = annot_list[c][0:max_samples]
    new_annotations = []
    for c in range(43):
#        print " len(class[%d])="%c, len(annot_list[c]), 
        new_annotations += annot_list[c]
    return new_annotations
        
def sample_annotations(annotations, first_sample=0, num_samples=None):
    if len(annotations[0]) < 8 or (first_sample==None and num_samples==None):
        return annotations

    c_annotations = []
    for c in range(43):        
        c_annotations.append([])
    for row in annotations:
        c_annotations[row[8]].append(row)

    out_annotations = []
    for c in range(43):        
        if num_samples is None:
            num_samples = len(c_annotations[c]) - first_sample
        #print "Add", first_sample, first_sample+num_samples, len(c_annotations[c]),          
        out_annotations += c_annotations[c][first_sample:first_sample+num_samples]
#    print "out_annotations=", out_annotations
    return out_annotations

GTSRB_Images_dir_training = "/local/escalafl/Alberto/GTSRB/Final_Training/Images"
GTSRB_HOG_dir_training = "/local/escalafl/Alberto/GTSRB/Final_Training/HOG"
GTSRB_SFA_dir_training = "/local/escalafl/Alberto/GTSRB/Final_Training/HOG"

GTSRB_Images_dir_test = "/local/escalafl/Alberto/GTSRB/Final_Test/Images"
GTSRB_HOG_dir_test = "/local/escalafl/Alberto/GTSRB/Final_Test/HOG"
GTSRB_SFA_dir_test = "/local/escalafl/Alberto/GTSRB/Final_Test/SFA"

GTSRB_Images_dir_Online = "/local/escalafl/Alberto/GTSRB/Final_Test/Images"
GTSRB_HOG_dir_Online = "/local/escalafl/Alberto/GTSRB/Final_Test/HOG"
GTSRB_SFA_dir_Online = "/local/escalafl/Alberto/GTSRB/Final_Test/SFA"

GTSRB_Images_dir_UnlabeledOnline = "/local/escalafl/Alberto/GTSRB/Online-Test/Images"
GTSRB_HOG_dir_UnlabeledOnline = "/local/escalafl/Alberto/GTSRB/Online-Test/HOG"
GTSRB_SFA_dir_UnlabeledOnline = "/local/escalafl/Alberto/GTSRB/Online-Test/SFA"

      
#Switch either HOG or SFA here
def load_HOG_data(base_GTSRB_dir="/home/eban/GTSRB", filenames=None, switch_SFA_over_HOG="HOG02", feature_noise = 0.0, padding=False):
    all_data = []
    print "HOG DATA LOADING %d images..."%len(filenames)
    #online_base_dir = GTSRB_HOG_dir_testing #GTSRB_Images_dir_UnlabeledOnline #Unlabeled data dir

    #warning, assumes all filenames belong to same directory!!!
    #make this a good function and apply it to every file
    if filenames[0][0:len(GTSRB_Images_dir_UnlabeledOnline)] == GTSRB_Images_dir_UnlabeledOnline: #or final data base dir
        if switch_SFA_over_HOG in ["HOG01", "HOG02", "HOG03"]:     
            base_hog_dir = GTSRB_HOG_dir_UnlabeledOnline
        elif switch_SFA_over_HOG in ["SFA"]:
            base_hog_dir = GTSRB_SFA_dir_UnlabeledOnline            
        else:
            er = "Incorrect 1 switch_SFA_over_HOG value:", switch_SFA_over_HOG
            raise Exception(er)
        unlabeled_data = True
    elif filenames[0][0:len(GTSRB_Images_dir_training)] == GTSRB_Images_dir_training:
        if switch_SFA_over_HOG in ["HOG01", "HOG02", "HOG03"]:     
            base_hog_dir = GTSRB_HOG_dir_training
        elif switch_SFA_over_HOG in ["SFA02"]:
            base_hog_dir = GTSRB_SFA_dir_training
        else:
            er = "Incorrect 2 switch_SFA_over_HOG value:", switch_SFA_over_HOG
            raise Exception(er)
        unlabeled_data = False
    elif filenames[0][0:len(GTSRB_Images_dir_test)] == GTSRB_Images_dir_test:
        if switch_SFA_over_HOG in ["HOG01", "HOG02", "HOG03"]:     
            base_hog_dir = GTSRB_HOG_dir_test
        elif switch_SFA_over_HOG in ["SFA02"]:
            base_hog_dir = GTSRB_SFA_dir_training ##undefined, 
        else:
            er = "Incorrect 2 switch_SFA_over_HOG value:", switch_SFA_over_HOG
            raise Exception(er)
        unlabeled_data = True
    elif filenames[0][0:len(GTSRB_Images_dir_Online)] == GTSRB_Images_dir_Online:
        if switch_SFA_over_HOG in ["HOG01", "HOG02", "HOG03"]:     
            base_hog_dir = GTSRB_HOG_dir_Online
        elif switch_SFA_over_HOG in ["SFA02"]:
            base_hog_dir = GTSRB_SFA_dir_Online
        else:
            er = "Incorrect 2.3 switch_SFA_over_HOG value:", switch_SFA_over_HOG
            raise Exception(er)
        unlabeled_data = False
    else:
        er = "Filename does not belong to known data sets: ", filenames[0]
        raise Exception(er)

    feat_set = switch_SFA_over_HOG[-2:]
    sample_hog_filename = "00000/00001_00000.txt" #"00000/00001_00000.txt" (Older)
    print "HOG loading...", feat_set, filenames[0], filenames[-1]
    for ii, image_filename in enumerate(filenames):
        if ii==0:
            print "image_filename=", image_filename
        if unlabeled_data:
            if switch_SFA_over_HOG in ["HOG01", "HOG02", "HOG03"]:   
                hog_filename = base_hog_dir + "/HOG_" + feat_set + "/" + image_filename[-9:-3]+"txt"
            elif switch_SFA_over_HOG in ["SFA02"]:
                hog_filename = base_hog_dir + "/SFA_" + feat_set + "/" + image_filename[-9:-3]+"txt"
            else:
                er = "Incorrect 3 switch_SFA_over_HOG value:", switch_SFA_over_HOG
                raise Exception(er)
        else:
            if switch_SFA_over_HOG in ["HOG01", "HOG02", "HOG03"]:
                hog_filename = base_hog_dir + "/HOG_" + feat_set + "/" + image_filename[-len(sample_hog_filename):-3]+"txt"
            elif switch_SFA_over_HOG in ["SFA02"]:
                hog_filename = base_hog_dir + "/SFA_" + feat_set + "/" + image_filename[-len(sample_hog_filename):-3]+"txt"
            else:
                er = "Incorrect 4 switch_SFA_over_HOG value:", switch_SFA_over_HOG
                raise Exception(er)               
        if ii==0:
            print "first hogh_filename:", hog_filename
        data_file = open(hog_filename, "rb") 
        data = [float(line) for line in data_file.readlines()]
        data_file.close( )
        data = numpy.array(data)
        #print data    
        all_data.append(data)
    all_data = numpy.array(all_data)
    
    #0.035 => New Id: 0.938 CR_CCC, CR_Gauss 0.943,
    #0.025 => New Id: 0.938 CR_CCC, CR_Gauss 0.940,
    #Adding repetitions for balancing: 0.025 => New Id: 0.939 CR_CCC, CR_Gauss 0.949
    #Adding repetitions for balancing: 0.04 => New Id: 0.936 CR_CCC, CR_Gauss 0.956
    if feature_noise > 0.0:
        noise = numpy.random.normal(loc=0.0, scale=feature_noise, size=all_data.shape)
        print "feature (SFA/HOG) Noise added in amount:", feature_noise
        all_data += noise
    else:
        print "NO feature (SFA/HOG) Noise added"    

    if padding:
        if switch_SFA_over_HOG in ["HOG01", "HOG02"]:
            num_samples = all_data.shape[0]
            true_feature_data_shape = (num_samples, 14, 14, 8) 
            desired_feature_data_shape = (num_samples, 16, 16, 8)
            all_data = numpy.reshape(all_data, true_feature_data_shape)
            noise_data = numpy.random.normal(loc=1.0, scale=0.05, size=desired_feature_data_shape) 
            noise_data[:, 0:14, 0:14, 0:8] = all_data[:,:,:,:]
            all_data = numpy.reshape(noise_data, (num_samples, 16*16*8))
        else:
            er = "Padding not supported for data type: ", switch_SFA_over_HOG
            raise Exception(er)
    return all_data


#Real last_track is num_tracks - skip_end_tracks -1
def iSeqCreateRGTSRB_Labels(annotations, labels_available=True, repetition_factors=1, seed=-1): 
    if seed >= 0 or seed is None:
        numpy.random.seed(seed)

    print "***** Setting Training Information Parameters for German Traffic Sign Recognition Benchmark ******"
    iSeq = SystemParameters.ParamsInput()
    iSeq.name = "German Traffic Sign Recognition Benchmark"

    iSeq.data_base_dir = ""
#
    all_classes = []
    for row in annotations:
        all_classes.append(row[8])
        #print "adding ", row[8], 
    print "all_classes=", all_classes
    all_classes = numpy.unique(all_classes) 
    print "all_classes=", all_classes

    c_filenames = {}
    c_info = {}
    c_labels = {}
    for c in all_classes:
        c_filenames[c] = []
        c_info[c] = []
        c_labels[c] = []

    counter = 0
    for row in annotations:
        c = row[8] #extract class number
        c_filenames[c].append(row[0])
        c_info[c].append(row[2:8])
        c_labels[c].append(c)
        counter += 1
    print "Sample counter before repetition=", counter

    if repetition_factors is None:
        repetition_factors = 1
    if isinstance(repetition_factors, int):
        num_classes = len(all_classes)
        repetition_factors = [repetition_factors]*num_classes
    if isinstance(repetition_factors, list):
        dic = {}
        for i, c in enumerate(all_classes):
            dic[c] = repetition_factors[i]
    print repetition_factors
    for c in all_classes:  
        #print "c=", c, len(c_info[c]), len(c_info), len(c_info[0]), len(c_info[1])
        c_filenames[c] = (c_filenames[c]) * (repetition_factors[c])
        c_info[c] = (c_info[c]) * (repetition_factors[c])
        c_labels[c] = (c_labels[c]) * (repetition_factors[c])  
    
##    counter = 0
##    for row in annotations:
###        print "T=%d"%row[1],
##        if row[1] >= first_track and row[1] < last_track:
##            c = row[8] #extract class number
###            print c, len(c_filenames)
##            c_filenames[c].append(row[0])
##            c_info[c].append(row[2:8])
##            c_labels[c].append(c)
##            counter += 1
##    print "Sample counter after repetition=", counter
##    quit()
#    quit()
#    print c_filenames[0][0], c_filenames[1][0]
#    print c_filenames[0][1], c_filenames[1][1]
    
    conc_c_info = []
    for c in all_classes:
        conc_c_info += c_info[c]
    
    #print "conc_c_info is", conc_c_info
#Avoids void entries
    iSeq.c_info = numpy.array(conc_c_info)

    print "len(iSeq.c_info)", len(iSeq.c_info)
    #zeros((counter, 6))

    iSeq.ids = []
    iSeq.input_files = []
    iSeq.block_size = []

    for c in all_classes:
        if len(c_filenames[c]) > 0:
            iSeq.block_size.append(len(c_filenames[c]))
            print "iSeq.block_size[%d]="%c, iSeq.block_size[-1],
            for filename in c_filenames[c]:
                iSeq.ids.append(c)
                iSeq.input_files.append(filename)

    iSeq.block_size = numpy.array(iSeq.block_size)
#    print iSeq.block_size
#    quit()
#    ii = 130
#    print ii, iSeq.input_files[ii], iSeq.c_info[ii]
#    print len(iSeq.input_files), len(iSeq.c_info)
#    quit()
      
    iSeq.ids = numpy.array(iSeq.ids)
    #print "iSeq.ids", iSeq.ids
#    quit()
    iSeq.ages = [None]
    iSeq.genders = [None]
    iSeq.racetweens = [None]
    iSeq.expressions = [None]
    iSeq.morphs = [None]
    iSeq.poses = [None]
    iSeq.lightings = [None]
    iSeq.slow_signal = 0 #real slow signal is the class number (type of sign)
    iSeq.step = 1
    iSeq.offset = 0
    
    iSeq.num_images = len(iSeq.input_files)
    #iSeq.params = [ids, expressions, morphs, poses, lightings]
    iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                      iSeq.morphs, iSeq.poses, iSeq.lightings]
    if labels_available:
        iSeq.train_mode = "clustered" #"compact_classes+5" #"clustered" #"compact_classes+31"
    else:
        iSeq.train_mode = "unlabeled"
    print "BLOCK SIZE =", iSeq.block_size 
    iSeq.correct_classes = copy.deepcopy(iSeq.ids)
    iSeq.correct_labels = copy.deepcopy(iSeq.ids) 
    SystemParameters.test_object_contents(iSeq)
    return iSeq



def sSeqCreateRGTSRB(iSeq, delta_translation = 2.0, delta_scaling = 0.1, delta_rotation = 4.0, contrast_enhance=True, activate_HOG=False, switch_SFA_over_HOG="HOG02", feature_noise = 0.0, seed=-1):
    if seed >= 0 or seed is None: #also works for 
        numpy.random.seed(seed)
    #else seed <0 then, do not change seed

    print "******** Setting Training Data Parameters for German Traffic Sign Recognition Benchmark  ****************"
    sSeq = SystemParameters.ParamsDataLoading()
    sSeq.input_files = iSeq.input_files
    sSeq.num_images = iSeq.num_images
    sSeq.block_size = iSeq.block_size
    sSeq.train_mode = iSeq.train_mode
    print "iSec.c_info is", iSeq.c_info
    sSeq.image_width = iSeq.c_info[:, 0]
    sSeq.image_height = iSeq.c_info[:,1]
    sSeq.subimage_width = 32
    sSeq.subimage_height = 32 
    
#    sign_size = ((iSeq.c_info[:,4] - iSeq.c_info[:,2]) + (iSeq.c_info[:,5] - iSeq.c_info[:,3]))/2.0
    #Keep aspect ratio as in the original
#    sSeq.pixelsampling_x = sign_size * 1.0 /  sSeq.subimage_width
#    sSeq.pixelsampling_y = sign_size * 1.0 /  sSeq.subimage_height
#    sSeq.subimage_first_row =  (iSeq.c_info[:,5] + iSeq.c_info[:,3])/2.0 - sign_size / 2.0
#    sSeq.subimage_first_column = (iSeq.c_info[:,4] + iSeq.c_info[:,2])/2.0 - sign_size / 2.0

    sSeq.scales = 1+numpy.random.uniform(-delta_scaling, delta_scaling, sSeq.num_images)
        
    sign_widths = (iSeq.c_info[:,4] - iSeq.c_info[:,2]+1) * sSeq.scales
    sign_heights = iSeq.c_info[:,5] - iSeq.c_info[:,3]+1 * sSeq.scales
    sign_centers_x = (iSeq.c_info[:,4] + iSeq.c_info[:,2])*0.5
    sign_centers_y = (iSeq.c_info[:,5] + iSeq.c_info[:,3])*0.5

    sSeq.pixelsampling_x = sign_widths /  sSeq.subimage_width
    sSeq.pixelsampling_y = sign_heights /  sSeq.subimage_height   
    sSeq.subimage_first_row = sign_centers_y - sign_heights/2 
    sSeq.subimage_first_column = sign_centers_x - sign_widths/2  

    #sSeq.image_width/2.0-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
    sSeq.add_noise_L0 = True
    if activate_HOG==False:
        sSeq.convert_format = "RGB"       
    else:
        sSeq.convert_format = switch_SFA_over_HOG

    sSeq.background_type = None


    sSeq.translations_x = numpy.random.uniform(-delta_translation, delta_translation, sSeq.num_images)                                                           
    sSeq.translations_y = numpy.random.uniform(-delta_translation, delta_translation, sSeq.num_images)                                                           
    
    sSeq.rotation = numpy.random.uniform(-delta_rotation, delta_rotation, sSeq.num_images)
        
#    if contrast_enhance == False:
#        print "WTF 2???"
#        quit()
        
    sSeq.contrast_enhance = contrast_enhance
    sSeq.trans_sampled = True #Translations are given in subimage coordinates
    sSeq.name = "GTSRB"
    iSeq.name = sSeq.name

    if activate_HOG == False:
        sSeq.load_data = load_data_from_sSeq
    else:
        if switch_SFA_over_HOG in ["HOG01", "HOG02", "HOG03", "SFA02"]:
            sSeq.load_data = lambda sSeq: load_HOG_data(base_GTSRB_dir="/local/scalafl/Alberto/GTSRB", filenames=sSeq.input_files, switch_SFA_over_HOG=switch_SFA_over_HOG,feature_noise=feature_noise,padding=True)
        elif switch_SFA_over_HOG == "SFA02_HOG02":
            sSeq.load_data = lambda sSeq: numpy.concatenate((
                load_HOG_data(base_GTSRB_dir="/local/scalafl/Alberto/GTSRB", filenames=sSeq.input_files, switch_SFA_over_HOG="SFA02",feature_noise=feature_noise)[:,0:49*2],
                load_HOG_data(base_GTSRB_dir="/local/scalafl/Alberto/GTSRB", filenames=sSeq.input_files, switch_SFA_over_HOG="HOG02",feature_noise=feature_noise)),axis=1)
        else:
            er = "Unknown switch_SFA_over_HOG:", switch_SFA_over_HOG
            raise Exception(er)

        if switch_SFA_over_HOG in ["HOG01", "HOG02"]:
            sSeq.subimage_width = 16 #14 #49
            sSeq.subimage_height = 16 #14 #32 #channel dim = 8
            sSeq.convert_format = switch_SFA_over_HOG
        elif switch_SFA_over_HOG in ["HOG03"]:
            sSeq.subimage_width = 54
            sSeq.subimage_height = 54
            sSeq.convert_format = switch_SFA_over_HOG    
        elif switch_SFA_over_HOG == "SFA02":
            sSeq.subimage_width = 7
            sSeq.subimage_height = 7
            sSeq.convert_format = switch_SFA_over_HOG
        elif switch_SFA_over_HOG == "SFA02_HOG02":
            sSeq.subimage_width = 49
            sSeq.subimage_height = 34
            sSeq.convert_format = switch_SFA_over_HOG
        else:
            quit()
    sSeq.train_mode = iSeq.train_mode
    SystemParameters.test_object_contents(sSeq)
    return sSeq



#Annotations: filename, track, Width, Height, ROI.x1, ROI.y1, ROI.x2, ROI.y2, [label]

#class 0 : 150   class 1 : 1500   class 2 : 1500   class 3 : 960   class 4 : 1320   class 5 : 1260   class 6 : 300   class 7 : 960   class 8 : 960   
#class 9 : 990   class 10 : 1350   class 11 : 900   class 12 : 1410   class 13 : 1440   class 14 : 540   class 15 : 420   class 16 : 300   
#class 17 : 750   class 18 : 810   class 19 : 150   class 20 : 240   class 21 : 240   class 22 : 270   class 23 : 360   class 24 : 180   
#class 25 : 1020   class 26 : 420   class 27 : 180   class 28 : 360   class 29 : 180   class 30 : 300   class 31 : 540   class 32 : 180   
#class 33 : 480   class 34 : 300   class 35 : 810   class 36 : 270   class 37 : 150   class 38 : 1380   class 39 : 210   class 40 : 240   
#class 41 : 180   class 42 : 180

#repetition_factors = [10  1  1  1  1  1  5  1  1  1  1  1  1  1  2  3  5  2  1 10  6  6  5  4  8
#  1  3  8  4  8  5  2  8  3  5  1  5 10  1  7  6  8  8]

#repetition_factors = [5  1  1  1  1
#                      1  3  1  1  1
#                      1  1  1  1  2
#                      2  3  2  1  5  4  
#                      4  3  4  8
#  1  3  8  4  8  5  2  8  3  5  1  5 10  1  7  6  8  8]

#For all tracks:
#repetition_factorsTrain = [10,  1,  1,  1,  1,  1,  5,  1,  1,  1,  1,  1,  1,  1,  2,  3,  5,  2, 1, 10,  6,  6,  5,  4,  8,
#                       1,  3,  8,  4,  8,  5,  2,  8,  3,  5,  1,  5, 10,  1,  7,  6,  8,  8]


#To support even/odd distribution
#W
#repetition_factors = numpy.array(repetition_factors)*2
#repetition_factorsTrain = numpy.array(repetition_factorsTrain)*2

#At most 15 tracks:
#repetition_factors = [ 4, 1, 1, 1, 1, 1,
#  2, 1, 1, 1, 1, 1,
#  1, 1, 1, 2, 2, 1,
#  1, 4, 3, 3, 2, 2,
#  3, 1, 2, 3, 2, 3,
#  2, 1, 3, 2, 2, 1,
#  2, 4, 1, 3, 3, 3,
#  3]

GTSRB_present = os.path.lexists("/local/escalafl/Alberto/GTSRB/") and False #and os.path.lexists("/local/escalafl/on_lux10")
if GTSRB_present:
    GTSRBTrain_base_dir = "/local/escalafl/Alberto/GTSRB/Final_Training/Images" #"/local/escalafl/Alberto/GTSRB/Final_Training/Images"
    GTSRBTrain_base_dir = "/local/escalafl/Alberto/GTSRB/Final_Training/Images" #"/local/escalafl/Alberto/GTSRB/Final_Training/Images"
    GTSRBOnline_base_dir = "/local/escalafl/Alberto/GTSRB/Online-Test-sort/Images" #"/local/escalafl/Alberto/GTSRB/Online-Test-sort/Images"
    repetition_factorsTrain = None
    
#TODO:Repetition factors should not be at this level, also randomization of scales does not belong here.
#TODO:Update the databases used to the final system
    sign_selection = numpy.arange(43)
    
    sign_selection = list(set(sign_selection)-set([ 0, 19, 21, 24, 27, 29, 32, 37, 39, 41, 42]))
    
    GTSRB_annotationsTrain_Train = readTrafficSignsAnnotations(GTSRBTrain_base_dir, include_labels=True, sign_selection=sign_selection) #delta_rand_scale=0.07
    print "Len GTSRB_annotationsTrain_Train=,", len(GTSRB_annotationsTrain_Train)
    GTSRB_annotationsTrain_Seenid = readTrafficSignsAnnotations(GTSRBTrain_base_dir, include_labels=True, sign_selection=sign_selection) #delta_rand_scale=0.07
    GTSRB_annotationsTrain_Newid = readTrafficSignsAnnotations(GTSRBTrain_base_dir, include_labels=True, sign_selection=sign_selection)
    
   
#    GTSRB_annotationsOnline_Train = readTrafficSignsAnnotations(GTSRBOnline_base_dir, include_labels=True)
#    GTSRB_annotationsOnline_Seenid = readTrafficSignsAnnotations(GTSRBOnline_base_dir, include_labels=True)
#    GTSRB_annotationsOnline_Newid = readTrafficSignsAnnotations(GTSRBOnline_base_dir, include_labels=True)
#    print "Len GTSRB_annotationsOnline_Newid=", len(GTSRB_annotationsOnline_Newid)
#    quit()

    activate_HOG = True and False #for direct image processing, true for SFA/HOG features
    #TODO: HOG set selection HOG02, SFA, 
    switch_SFA_over_HOG = "HOG02" #"SFA" # "HOG02", "SFA"

    print "fixing max_samples_per_class"
    GTSRB_rep=1#6
    GTSRB_constant_block_size = 360*GTSRB_rep
    GTSRB_annotationsTrain_Train = enforce_max_samples_per_class(GTSRB_annotationsTrain_Train, GTSRB_constant_block_size, repetition=GTSRB_rep)
    GTSRB_annotationsTrain_Seenid = enforce_max_samples_per_class(GTSRB_annotationsTrain_Seenid, GTSRB_constant_block_size, repetition=GTSRB_rep)
    GTSRB_annotationsTrain_Newid = enforce_max_samples_per_class(GTSRB_annotationsTrain_Newid, GTSRB_constant_block_size)


    count = count_annotation_classes(GTSRB_annotationsTrain_Train)
    print "number of samples per each class A (GTSRB_annotationsTrain_Train): ", count
    
    #Correct class indices, so that only consecutive classes appear
    consequtive_classes = True
    if consequtive_classes:
        all_classes=[]
        for row in GTSRB_annotationsTrain_Train:
            all_classes.append(row[8])
        unique, corrected_classes = numpy.unique(all_classes, return_inverse=True) 
        correction_c = {}
        for i, c in enumerate(unique):
            correction_c[c] = i

        print "unique classes in GTSRB_annotationsTrain_Train:", unique

        for ii, row in enumerate(GTSRB_annotationsTrain_Train):
            row[8] = correction_c[row[8]]
        for row in GTSRB_annotationsTrain_Seenid:
            row[8] = correction_c[row[8]]
        for row in GTSRB_annotationsTrain_Newid:
            row[8] = correction_c[row[8]]
        print "class consequtive correction mapping", correction_c
        
        
    count = count_annotation_classes(GTSRB_annotationsTrain_Train)
    print "number of samples per each class B (GTSRB_annotationsTrain_Train): ", count
        
    shuffle_classes = True
    if shuffle_classes:
        all_classes=[]
        for row in GTSRB_annotationsTrain_Train:
            all_classes.append(row[8])
        unique_c = numpy.unique(all_classes)
        print "unique_c=", unique_c

        shuffled_c = unique_c.copy()
        numpy.random.shuffle(shuffled_c)
        print "shuffled_c=", shuffled_c
        
        shuffling_c={}
        for i, c in enumerate(unique_c):
            shuffling_c[c] = shuffled_c[i]
        print "shuffling_c=", shuffling_c

        for row in GTSRB_annotationsTrain_Train:
            row[8] = shuffling_c[row[8]]

        for row in GTSRB_annotationsTrain_Seenid:
            row[8] = shuffling_c[row[8]]
        
        for row in GTSRB_annotationsTrain_Newid:
            row[8] = shuffling_c[row[8]]
        
        print "class shuffling mapping", shuffling_c
        
    count = count_annotation_classes(GTSRB_annotationsTrain_Train)
    print "number of samples per each class C (GTSRB_annotationsTrain_Train): ", count

#    count = count_annotation_classes(GTSRB_annotationsTrain_Seenid)
#    print "number of samples per each class (GTSRB_annotationsTrain_Seenid): ", count


#    count = count_annotation_classes(GTSRB_annotationsTrain_Newid)
#    print "number of samples per each class (GTSRB_annotationsTrain_Newid): ", count

    #print 500.0/count+0.99
    #print 700/count
    #print GTSRB_annotationsTrain[0]
    #
    #TODO:Add a first_sample parameter
    
    GTSRB_annotationsTrain_TrainOrig = GTSRB_annotationsTrain_Train
    GTSRB_annotationsTrain_Train = sample_annotations(GTSRB_annotationsTrain_TrainOrig, first_sample = 0, num_samples=360*GTSRB_rep) #W 0.6, 0.5, Odd, AllP, Univ, 2/3
    GTSRB_annotationsTrain_Seenid = sample_annotations(GTSRB_annotationsTrain_TrainOrig, first_sample = 0*GTSRB_rep, num_samples=360*GTSRB_rep ) #W 1.0, 0.3, Even, 1/3
    GTSRB_annotationsTrain_Newid = sample_annotations(GTSRB_annotationsTrain_TrainOrig, first_sample = 240*GTSRB_rep, num_samples=120*GTSRB_rep ) #make testing faster for now, 0.3 , 1.0

#    GTSRB_annotationsTrain_Train = sample_annotations(GTSRB_annotationsTrain_TrainOrig, first_sample = 0, num_samples=360*GTSRB_rep) #W 0.6, 0.5, Odd, AllP, Univ, 2/3
#    GTSRB_annotationsTrain_Seenid = sample_annotations(GTSRB_annotationsTrain_TrainOrig, first_sample = 0*GTSRB_rep, num_samples=360*GTSRB_rep ) #W 1.0, 0.3, Even, 1/3
#    GTSRB_annotationsTrain_Newid = sample_annotations(GTSRB_annotationsTrain_TrainOrig, first_sample = 240*GTSRB_rep, num_samples=10*GTSRB_rep ) #make testing faster for now, 0.3 , 1.0
   

    #GTSRB_annotationsOnline_Train = sample_annotations(GTSRB_annotationsOnline_Train, flag="Univ", passing=0.25) #W 0.6, 0.5, Odd, AllP, Univ
    #GTSRB_annotationsOnline_Seenid = sample_annotations(GTSRB_annotationsOnline_Seenid, flag="Univ", passing=0.25) #W 1.0, 0.3, Even
    #GTSRB_annotationsOnline_Newid = sample_annotations(GTSRB_annotationsOnline_Newid, flag="Univ", passing=1.0) #make testing faster for now, 0.3 , 1.0
    
    #count = count_annotation_classes(GTSRB_annotationsTest)      
    #print count    
    #quit()
#    
    GTSRB_Unlabeled_base_dir = "/local/escalafl/Alberto/GTSRB/Final_Test/Images" # "/local/escalafl/Alberto/GTSRB/Online-Test/Images"
    GTSRB_Unlabeled_csvfile =  "GT-final_test.csv" #  "GT-final_test.csv" / "GT-final_test.test.csv" / "GT-online_test.test.csv"
    GTSRB_UnlabeledAnnotations = readTrafficSignsAnnotationsOnline(GTSRB_Unlabeled_base_dir, GTSRB_Unlabeled_csvfile, shrink_signs=True, correct_sizes=True, include_labels=True, sign_selection=sign_selection) #include_labels=False
  
  
    if consequtive_classes:
        for ii, row in enumerate(GTSRB_UnlabeledAnnotations):
            if row[8] in correction_c.keys():
                row[8] = correction_c[row[8]]
            
    if shuffle_classes:
        for row in GTSRB_UnlabeledAnnotations:
            if row[8] in shuffling_c.keys():
                row[8] = shuffling_c[row[8]]
            
    
    GTSRB_UnlabeledAnnotations = sample_annotations(GTSRB_UnlabeledAnnotations) #make testing faster for now, 0.3 , 1.0
    #print GTSRB_UnlabeledAnnotations[0], len(GTSRB_UnlabeledAnnotations)
    #quit() 
    
    GTSRB_annotationsTrain = GTSRB_annotationsTrain_Train
    GTSRB_annotationsSeenid = GTSRB_annotationsTrain_Seenid
    GTSRB_annotationsTest = GTSRB_UnlabeledAnnotations # GTSRB_UnlabeledAnnotations, GTSRB_annotationsOnline_Newid
    
    ## CASE [[F]]
    #WARNING!
    ##############################'''WAAAAAARNNNNIIINNNNNNGGGG TRTRAAAACKKKKSSSSSS 1111
    #W first track=1
    ##iSeq_set = iTrainRGTSRB_Labels = [[iSeqCreateRGTSRB_Labels(GTSRB_annotationsTrain, first_track = 0, last_track=100, seed=-1),
    ##                                   iSeqCreateRGTSRB_Labels(GTSRB_annotationsTestData, first_track = 0, last_track=4, labels_available=False, seed=-1)]]
    ##sSeq_set = sTrainRGTSRB = [[sSeqCreateRGTSRB(iSeq_set[0][0], enable_translation=True, enable_rotation=True, contrast_enhance=True, activate_HOG=activate_HOG, switch_SFA_over_HOG= switch_SFA_over_HOG, add_HOG_noise=True, seed=-1),
    ##                            sSeqCreateRGTSRB(iSeq_set[0][1], enable_translation=False, enable_rotation=False, contrast_enhance=True, activate_HOG=activate_HOG, switch_SFA_over_HOG= switch_SFA_over_HOG, add_HOG_noise=True,  seed=-1)]]
    ##
    ##iSeq_set = iSeenidRGTSRB_Labels = iSeqCreateRGTSRB_Labels(GTSRB_annotationsSeenid, first_track = 0, last_track=100, seed=-1)
    ##sSeq_set = sSeenidRGTSRB = sSeqCreateRGTSRB(iSeq_set, enable_translation=True, enable_rotation=True, contrast_enhance=True, activate_HOG=activate_HOG, switch_SFA_over_HOG= switch_SFA_over_HOG, add_HOG_noise=True, seed=-1)
    
##    iSeq_set = iTrainRGTSRB_Labels = [[iSeqCreateRGTSRB_Labels(GTSRB_annotationsTrain, first_track = 0, last_track=100, seed=-1),
##                                       iSeqCreateRGTSRB_Labels(GTSRB_annotationsTest, first_track = 0, last_track=100, labels_available=False, seed=-1)]]
##    sSeq_set = sTrainRGTSRB = [[sSeqCreateRGTSRB(iSeq_set[0][0], enable_translation=True, enable_rotation=True, contrast_enhance=True, activate_HOG=activate_HOG, switch_SFA_over_HOG= switch_SFA_over_HOG, feature_noise=0.03, seed=-1),
##                                sSeqCreateRGTSRB(iSeq_set[0][1], enable_translation=True, enable_rotation=True, contrast_enhance=True, activate_HOG=activate_HOG, switch_SFA_over_HOG= switch_SFA_over_HOG, feature_noise=0.0,  seed=-1)]]

    #delta_translation=0.0, delta_scaling=0.1, delta_rotation=4.0
    contrast_enhance = "GTSRBContrastEnhancement"
#    delta_translation_t= 1.25 #1.5 #1.25
#    delta_scaling_t= 0.070 #0.075 #0.065
#    delta_rotation_t = 3.5 #2.5 pointer
#
#    delta_translation_s= 2.0 #RETUNE! # 1.0 #1.5 #1.25
#    delta_scaling_s= 0.110 # Retune! 0.056 #0.075 #0.065
#    delta_rotation_s = 2.75 #2.8 #2.5 pointer
#NOTE: TUNED PARAMS: 2.0, 0.11 and 2.75, however strange results, so reverting to same parameters used for training

    delta_translation_t= 1.5 
    delta_scaling_t= 0.090 
    delta_rotation_t = 3.15 

# #WARNING, ONLY FOR PLOT!
#     delta_translation_t= 0.0001 
#     delta_scaling_t= 0.0001 
#     delta_rotation_t = 0.0001

    delta_translation_s= 1.5 
    delta_scaling_s= 0.090 
    delta_rotation_s = 3.15 

#NOTE: TUNED PARAMS: 2.0, 0.11 and 2.75, however strange results, so reverting to same parameters used for training

#    factor_seenid = 0.80 #2.5/3.5

    iSeq_set = iTrainRGTSRB_Labels = [[iSeqCreateRGTSRB_Labels(GTSRB_annotationsTrain, repetition_factors=6, seed=-1)]] #repetition_factors=4 ##last_track=100
#    sSeq_set = sTrainRGTSRB = [[sSeqCreateRGTSRB(iSeq_set[0][0], delta_translation=0.0, delta_scaling=0.0, delta_rotation=0.0, contrast_enhance=contrast_enhance, activate_HOG=activate_HOG, switch_SFA_over_HOG= switch_SFA_over_HOG, feature_noise=0.00, seed=-1) ]] #feature_noise=0.04
    sSeq_set = sTrainRGTSRB = [[sSeqCreateRGTSRB(iSeq_set[0][0], delta_translation=delta_translation_t, delta_scaling=delta_scaling_t, delta_rotation=delta_rotation_t, contrast_enhance=contrast_enhance, activate_HOG=activate_HOG, switch_SFA_over_HOG= switch_SFA_over_HOG, feature_noise=0.00, seed=-1) ]] #feature_noise=0.04

    iSeq_set = iSeenidRGTSRB_Labels = iSeqCreateRGTSRB_Labels(GTSRB_annotationsSeenid, repetition_factors=6,  seed=-1) #repetition_factors=2
#    sSeq_set = sSeenidRGTSRB = sSeqCreateRGTSRB(iSeq_set, delta_translation=0.0, delta_scaling=0.00, delta_rotation=0.0, contrast_enhance=contrast_enhance, activate_HOG=activate_HOG, switch_SFA_over_HOG= switch_SFA_over_HOG, feature_noise=0.00, seed=-1) #feature_noise=0.07
    sSeq_set = sSeenidRGTSRB = sSeqCreateRGTSRB(iSeq_set, delta_translation=delta_translation_s, delta_scaling=delta_scaling_s, delta_rotation=delta_rotation_s, contrast_enhance=contrast_enhance, activate_HOG=activate_HOG, switch_SFA_over_HOG= switch_SFA_over_HOG, feature_noise=0.00, seed=-1) #feature_noise=0.07

    #GTSRB_onlineAnnotations, GTSRB_annotationsTest
    iSeq_set = iNewidRGTSRB_Labels = iSeqCreateRGTSRB_Labels(GTSRB_annotationsTest, repetition_factors=1, seed=-1)
    sSeq_set = sNewidRGTSRB = sSeqCreateRGTSRB(iSeq_set, delta_translation=0.0, delta_scaling=0.0, delta_rotation=0.0, contrast_enhance=contrast_enhance, activate_HOG=activate_HOG, switch_SFA_over_HOG= switch_SFA_over_HOG, feature_noise=0.0, seed=-1)
    #sSeq_set.add_noise_L0 = False
    #sSeq_set.rotation = 0.0              
    
#    print iTrainRGTSRB_Labels[0][0].input_files[0:5]
#    print iSeenidRGTSRB_Labels.input_files[0:5]
#    quit()
    print iTrainRGTSRB_Labels[0][0].correct_labels
    print iSeenidRGTSRB_Labels.correct_labels
    print iNewidRGTSRB_Labels.correct_labels
    #quit()
    
    ParamsRGTSRBFunc = SystemParameters.ParamsSystem()
    ParamsRGTSRBFunc.name = "Function Based Data Creation for GTSRB"
    ParamsRGTSRBFunc.network = "linearNetwork4L" #Default Network, but ignored
    ParamsRGTSRBFunc.iTrain =iTrainRGTSRB_Labels
    ParamsRGTSRBFunc.sTrain = sTrainRGTSRB
    
    ParamsRGTSRBFunc.iSeenid = iSeenidRGTSRB_Labels
    ParamsRGTSRBFunc.sSeenid = sSeenidRGTSRB
    
    ParamsRGTSRBFunc.iNewid = iNewidRGTSRB_Labels
    ParamsRGTSRBFunc.sNewid = sNewidRGTSRB
    
    ParamsRGTSRBFunc.block_size = iTrainRGTSRB_Labels[0][0].block_size
    ParamsRGTSRBFunc.train_mode = "ignored" #clustered, #Identity recognition task
    ParamsRGTSRBFunc.analysis = None
    ParamsRGTSRBFunc.activate_HOG = activate_HOG
    
    if activate_HOG==False:
        ParamsRGTSRBFunc.enable_reduced_image_sizes = True #and False #Set to false if network is a cascade
        ParamsRGTSRBFunc.reduction_factor = 32.0/48 #1.0 # WARNING   0.5, 1.0, 2.0, 4.0, 8.0
        ParamsRGTSRBFunc.hack_image_size = 48            # WARNING    64,  32,  16,   8
        ParamsRGTSRBFunc.enable_hack_image_size = True #and False #Set to false if network is a cascade
    else:
        if switch_SFA_over_HOG == "HOG02":
            ParamsRGTSRBFunc.enable_reduced_image_sizes = False
            ParamsRGTSRBFunc.enable_hack_image_size = True
            ParamsRGTSRBFunc.hack_image_size = 16 # WARNING    32,  16,   8
        else:
            ParamsRGTSRBFunc.enable_reduced_image_sizes = False
            ParamsRGTSRBFunc.enable_hack_image_size = False
else:
    print "GTSRBFunc not present or disabled"
    ParamsRGTSRBFunc = None


### Function based definitions for face detections
###PIPELINE FOR FACE DETECTION:
###Orig=TX: DX0=+/- 45, DY0=+/- 20, DS0= 0.55-1.1
###TY: DX1=+/- 20, DY0=+/- 20, DS0= 0.55-1.1
###S: DX1=+/- 20, DY1=+/- 10, DS0= 0.55-1.1
###TMX: DX1=+/- 20, DY1=+/- 10, DS1= 0.775-1.05
###TMY: DX2=+/- 10, DY1=+/- 10, DS1= 0.775-1.05
###MS: DX2=+/- 10, DY2=+/- 5, DS1= 0.775-1.05
###Out About: DX2=+/- 10, DY2=+/- 5, DS2= 0.8875-1.025
##notice: for dx* and dy* intervals are open, while for smin and smax intervals are closed
#pipeline_fd = dict(dx0 = 45, dy0 = 20, smin0 = 0.55, smax0 = 1.1,
#                dx1 = 20, dy1 = 10, smin1 = 0.775, smax1 = 1.05)
##Pipeline actually supports inputs in: [-dx0, dx0-2] [-dy0, dy0-2] [smin0, smax0] 
##Remember these values are before image resizing
#
##XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
##This network actually supports images in the closed intervals: [smin0, smax0] [-dy0, dy0]
##but halb-open [-dx0, dx0) 
#print "***** Setting Training Information Parameters for Real Translation X ******"
#iSeq = iTrainRTransX = SystemParameters.ParamsInput()
#iSeq.name = "Real Translation X: (-45, 45, 2) translation and y 40"
#iSeq.data_base_dir = frgc_normalized_base_dir
#iSeq.ids = numpy.arange(0,7965) # 8000, 7965
#
#iSeq.trans = numpy.arange(-1 * pipeline_fd['dx0'], pipeline_fd['dx0'], 2) # (-50, 50, 2)
#if len(iSeq.ids) % len(iSeq.trans) != 0:
#    ex="Here the number of translations must be a divisor of the number of identities"
#    raise Exception(ex)
#iSeq.ages = [None]
#iSeq.genders = [None]
#iSeq.racetweens = [None]
#iSeq.expressions = [None]
#iSeq.morphs = [None]
#iSeq.poses = [None]
#iSeq.lightings = [None]
#iSeq.slow_signal = 0 #real slow signal is the translation in the x axis, added during image loading
#iSeq.step = 1
#iSeq.offset = 0
#iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
#                                            iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
#                                            iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=4, image_postfix=".jpg")
#iSeq.input_files = iSeq.input_files * 4 # warning!!! 4, 8
##To avoid grouping similar images next to one other
#numpy.random.shuffle(iSeq.input_files)  
#
#iSeq.num_images = len(iSeq.input_files)
##iSeq.params = [ids, expressions, morphs, poses, lightings]
#iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
#                  iSeq.morphs, iSeq.poses, iSeq.lightings]
#iSeq.block_size = iSeq.num_images / len (iSeq.trans)
#print "BLOCK SIZE =", iSeq.block_size 
#iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(iSeq.trans)), iSeq.block_size)
#iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
#
#SystemParameters.test_object_contents(iSeq)
#
#print "******** Setting Training Data Parameters for Real TransX  ****************"
#sSeq = sTrainRTransX = SystemParameters.ParamsDataLoading()
#sSeq.input_files = iSeq.input_files
#sSeq.num_images = iSeq.num_images
#sSeq.block_size = iSeq.block_size
#sSeq.image_width = 256
#sSeq.image_height = 192
#sSeq.subimage_width = 128
#sSeq.subimage_height = 128 
#
#
#sSeq.trans_x_max = pipeline_fd['dx0']
#sSeq.trans_x_min = -1 * pipeline_fd['dx0']
#
##WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#sSeq.trans_y_max = pipeline_fd['dy0']
#sSeq.trans_y_min = -1 * sSeq.trans_y_max
#
##iSeq.scales = numpy.linspace(0.5, 1.30, 16) # (-50, 50, 2)
#sSeq.min_sampling = pipeline_fd['smin0']
#sSeq.max_sampling = pipeline_fd['smax0']
#
#sSeq.pixelsampling_x = sSeq.pixelsampling_y = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
##sSeq.subimage_pixelsampling = 2
#sSeq.subimage_first_row =  sSeq.image_height/2.0-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
#sSeq.subimage_first_column = sSeq.image_width/2.0-sSeq.subimage_width*sSeq.pixelsampling_x/2.0
##sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
#sSeq.add_noise_L0 = True
#sSeq.convert_format = "L"
#sSeq.background_type = None
##random translation for th w coordinate
##sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
##sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)                                                           
#sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
#sSeq.translations_y = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, sSeq.num_images)
#sSeq.trans_sampled = True
#sSeq.name = "RTans X Dx in (%d, %d) Dy in (%d, %d), sampling in (%f, %f)"%(sSeq.trans_x_min, 
#    sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, sSeq.min_sampling*100, sSeq.max_sampling*100)
#SystemParameters.test_object_contents(sSeq)

                           

#This subsumes RTransX, RTransY, RTrainsScale
#pipeline_fd:
#dx0 = 45, 45 Steps,
#dy0 = 20, 20 Steps,
#smin0 = 0.55, smax0 = 1.1, 40 Steps
def iSeqCreateRTransXYScale(dx=45, dy=20, smin=0.55, smax=1.1, num_steps=20, slow_var = "X", continuous=False, pre_mirroring="none", num_images_used=10000, images_base_dir= alldbnormalized_base_dir, normalized_images = alldbnormalized_available_images, first_image_index=0, repetition_factor=1, seed=-1):
    if seed >= 0 or seed is None: #also works for 
        numpy.random.seed(seed)

    if first_image_index + num_images_used > len(alldbnormalized_available_images):
        err = "Images to be used exceeds the number of available images"
        raise Exception(err) 

    print "***** Setting Information Parameters for Real Translation XYScale ******"
    iSeq = SystemParameters.ParamsInput()
    iSeq.name = "Real Translation " + slow_var + ": (%d, %d, %d, %d) numsteps %d"%(dx, dy, smin, smax, num_steps)
    iSeq.data_base_dir = images_base_dir
    iSeq.ids = normalized_images[first_image_index:first_image_index + num_images_used] 
    iSeq.slow_var = slow_var
    iSeq.dx = dx
    iSeq.dy = dy
    iSeq.smin = smin
    iSeq.smax = smax
    iSeq.pre_mirroring = pre_mirroring
    
    if continuous == True:
        real_num_steps = num_images_used * repetition_factor
    else:
        real_num_steps = num_steps

    if iSeq.pre_mirroring == "duplicate":
        real_num_steps *= 2     

    #Here only the unique discrete values for each class are coumputed, these might need to be repeated multiple times
    if slow_var == "X":
        #iSeq.trans = numpy.arange(-1 * pipeline_fd['dx0'], pipeline_fd['dx0'], 2) # (-50, 50, 2)
        iSeq.trans = numpy.linspace(-1 * dx, dx, real_num_steps) # (-50, 50, 2)
    elif slow_var == "Y":
        iSeq.trans = numpy.linspace(-1 * dy, dy, real_num_steps)        
    elif slow_var == "Scale":
        iSeq.scales = numpy.linspace(smin, smax, real_num_steps)      
    else:
        er = "Wrong slow_variable: ", slow_var
        raise Exception(er)  

    if len(iSeq.ids) % len(iSeq.trans) != 0 and continuous == False:
        ex="Here the number of translations/scalings must be a divisor of the number of identities"
        raise Exception(ex)

    iSeq.ages = [None]
    iSeq.genders = [None]
    iSeq.racetweens = [None]
    iSeq.expressions = [None]
    iSeq.morphs = [None]
    iSeq.poses = [None]
    iSeq.lightings = [None]
    iSeq.slow_signal = 0 #real slow signal is the translation in the x axis (correlated to identity), added during image loading
    iSeq.step = 1
    iSeq.offset = 0
    iSeq.input_files = imageLoader.create_image_filenames3(iSeq.data_base_dir, "image", iSeq.slow_signal, iSeq.ids, iSeq.ages, \
                                                iSeq.genders, iSeq.racetweens, iSeq.expressions, iSeq.morphs, \
                                                iSeq.poses, iSeq.lightings, iSeq.step, iSeq.offset, len_ids=5, image_postfix=".jpg")
    ##WARNING! (comment this!)
#    dir_list = os.listdir(iSeq.data_base_dir)
#    iSeq.input_files = []
#    for filename in dir_list:
#        iSeq.input_files.append( os.path.join(iSeq.data_base_dir,filename) )

    print "number of input files=", len(iSeq.input_files)
    print "number of iSeq.ids=", len(iSeq.ids)

    iSeq.input_files = iSeq.input_files * repetition_factor # warning!!! 4, 8
    iSeq.num_images = len(iSeq.input_files)

    #To avoid grouping similar images next to one other, even though available images already shuffled
    numpy.random.shuffle(iSeq.input_files)  

    if iSeq.pre_mirroring == "none":
        iSeq.pre_mirror_flags = [False] * iSeq.num_images
    elif iSeq.pre_mirroring == "all":
        iSeq.pre_mirror_flags = [True] * iSeq.num_images
    elif iSeq.pre_mirroring == "random":
        iSeq.pre_mirror_flags = more_nodes.random_boolean_array(iSeq.num_images)
    elif iSeq.pre_mirroring == "duplicate":
        input_files_duplicated = list(iSeq.input_files)
        iSeq.pre_mirror_flags = more_nodes.random_boolean_array(iSeq.num_images)

        shuffling = numpy.arange(0, iSeq.num_images)
        numpy.random.shuffle(shuffling)
        
        input_files_duplicated = [input_files_duplicated[i] for i in shuffling]
        pre_mirror_flags_duplicated = iSeq.pre_mirror_flags[shuffling]^True

        iSeq.input_files.extend(input_files_duplicated)
        iSeq.pre_mirror_flags = numpy.concatenate((iSeq.pre_mirror_flags, pre_mirror_flags_duplicated))  
        iSeq.num_images *= 2
    else:
        er = "Erroneous parameter iSeq.pre_mirroring=",iSeq.pre_mirroring
        raise Exception(er)
    
    #iSeq.params = [ids, expressions, morphs, poses, lightings]
    iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                      iSeq.morphs, iSeq.poses, iSeq.lightings]

    iSeq.block_size = iSeq.num_images / num_steps

    if continuous == False:
        print "before len(iSeq.trans=", len(iSeq.trans)
        if slow_var == "X" or slow_var == "Y": 
            iSeq.trans = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
        elif slow_var == "Scale":
            iSeq.scales = sfa_libs.wider_1Darray(iSeq.scales, iSeq.block_size)
        else:
            er = "Wrong slow_variable: ", slow_var
            raise Exception(er)  
        print "after len(iSeq.trans=", len(iSeq.trans)
        
#    if continuous == False:
#        iSeq.train_mode = "serial" # = "serial" "mixed", None
#    else:
#        iSeq.train_mode = "mirror_window64" # "mirror_window32" "smirror_window32" # None, "regular", "window32", "fwindow16", "fwindow32", "fwindow64", "fwindow128", 

#        quit()
    iSeq.train_mode = "mirror_window256" #"mirror_window32" # "mirror_window32", "regular", "fwindow16" "serial" "mixed", None
#        iSeq.train_mode = None 

    print "BLOCK SIZE =", iSeq.block_size
    iSeq.correct_classes = numpy.arange(num_steps*iSeq.block_size)/iSeq.block_size
#    sfa_libs.wider_1Darray(numpy.arange(len(iSeq.trans)), iSeq.block_size)
#    if continuous == False:
#        iSeq.correct_labels = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
#    else:
    iSeq.correct_labels = iSeq.trans + 0.0
    SystemParameters.test_object_contents(iSeq)
    return iSeq

def sSeqCreateRTransXYScale(iSeq, seed=-1):
    if seed >= 0 or seed is None: #also works for 
        numpy.random.seed(seed)
    #else seed <0 then, do not change seed
    
    print "******** Setting Training Data Parameters for Real TransX  ****************"
    sSeq = SystemParameters.ParamsDataLoading()
    sSeq.input_files = iSeq.input_files
    sSeq.num_images = iSeq.num_images
    sSeq.block_size = iSeq.block_size
    sSeq.train_mode = iSeq.train_mode
    sSeq.include_latest = iSeq.include_latest
    sSeq.pre_mirror_flags = iSeq.pre_mirror_flags

    sSeq.image_width = 256
    sSeq.image_height = 192
    sSeq.subimage_width = 128
    sSeq.subimage_height = 128 
    
    sSeq.trans_x_max = iSeq.dx
    sSeq.trans_x_min = -1 * iSeq.dx
    
    #WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    sSeq.trans_y_max = iSeq.dy
    sSeq.trans_y_min = -1 * iSeq.dy
    
    #iSeq.scales = numpy.linspace(0.5, 1.30, 16) # (-50, 50, 2)
    sSeq.min_sampling = iSeq.smin
    sSeq.max_sampling = iSeq.smax
    
    #sSeq.subimage_pixelsampling = 2
    #sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
    sSeq.add_noise_L0 = True
    sSeq.convert_format = "L"
    sSeq.background_type = None
    #random translation for th w coordinate
    #sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
    #sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)                                                           
    if iSeq.slow_var == "X":
        sSeq.translations_x = iSeq.trans
        #sSeq.translations_x = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
        #print "sSeq.translations_x=", sSeq.translations_x
        #print "len( sSeq.translations_x)=",  len(sSeq.translations_x)
    else:
        sSeq.translations_x = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images)
        
    if iSeq.slow_var == "Y":
        sSeq.translations_y = sfa_libs.wider_1Darray(iSeq.trans, iSeq.block_size)
    else:
        sSeq.translations_y = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, sSeq.num_images)

    if iSeq.slow_var == "Scale":
        sSeq.pixelsampling_x = sfa_libs.wider_1Darray(iSeq.scales,  iSeq.block_size)
        sSeq.pixelsampling_y =  sfa_libs.wider_1Darray(iSeq.scales,  iSeq.block_size)
    else:
        sSeq.pixelsampling_x = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
        sSeq.pixelsampling_y = sSeq.pixelsampling_x + 0.0

    #Warning, code below seems to have been deleted at some point!!!
    sSeq.subimage_first_row =  sSeq.image_height/2.0-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
    sSeq.subimage_first_column = sSeq.image_width/2.0-sSeq.subimage_width*sSeq.pixelsampling_x/2.0

    sSeq.trans_sampled = True #TODO: Why are translations specified according to the sampled images?
    
    sSeq.name = "RTans XYScale %s Dx in (%d, %d) Dy in (%d, %d), sampling in (%d, %d)"%(iSeq.slow_var, sSeq.trans_x_min, 
        sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, int(sSeq.min_sampling*100), int(sSeq.max_sampling*100))

    print "Var in trans X is:", sSeq.translations_x.var()
    sSeq.load_data = load_data_from_sSeq
    SystemParameters.test_object_contents(sSeq)
    return sSeq

print ":)***********************"

alldbnormalized_available_images = numpy.arange(0,64470)
numpy.random.shuffle(alldbnormalized_available_images)  

#iSeq = iSeqCreateRTransY(4800, av_fim, first_image=0, repetition_factor=2, seed=-1)
#sSeq = sSeqCreateRTransY(iSeq, seed=-1)
#print ";) 3"
#quit()
normalized_base_dir_INIBilder = "/local/escalafl/Alberto/INIBilder/INIBilderNormalized"

## CASE [[F]]iSeqCreateRTransXYScale(dx=45, dy=20, smin=0.55, smax=1.1, num_steps=20, slow_var = "X", continuous=False, num_images_used=10000, images_base_dir= alldbnormalized_base_dir, normalized_images = alldbnormalized_available_images, first_image_index=0, repetition_factor=1, seed=-1):
continuous = True #and False

iSeq_set = iTrainRTransXYScale = [[iSeqCreateRTransXYScale(dx=45, dy=20, smin=0.55, smax=1.1, num_steps=50, slow_var = "X", continuous=continuous, num_images_used=30000, #30000 
                                                      images_base_dir=alldbnormalized_base_dir, normalized_images = alldbnormalized_available_images, 
                                                      first_image_index=0, pre_mirroring="none", repetition_factor=2, seed=-1)]]
#Experiment below is just for display purposes!!! comment it out!
#iSeq_set = iTrainRTransXYScale = [[iSeqCreateRTransXYScale(dx=45, dy=2, smin=0.85, smax=0.95, num_steps=50, slow_var = "X", continuous=continuous, num_images_used=15000, #30000 
#                                                      images_base_dir=alldbnormalized_base_dir, normalized_images = alldbnormalized_available_images, 
#                                                      first_image_index=0, repetition_factor=1, seed=-1)]]

#For generating INI images
#iSeq_set = iTrainRTransXYScale = [[iSeqCreateRTransXYScale(dx=45, dy=20, smin=0.55, smax=1.1, num_steps=71, slow_var = "X", continuous=continuous, num_images_used=71, #30000 
#                                                      images_base_dir=normalized_base_dir_INIBilder, normalized_images = numpy.arange(0, 71), 
#                                                      first_image_index=0, repetition_factor=1, seed=143)]]
sSeq_set = sTrainRTransXYScale = [[sSeqCreateRTransXYScale(iSeq_set[0][0], seed=-1)]]

#iSeq_set = iTrainRTransY2 = [[copy.deepcopy(iSeq0), iSeqCreateRTransY(900, av_fim, first_image=4500, repetition_factor=1, seed=-1)], 
#                             [copy.deepcopy(iSeq0), iSeqCreateRTransY(900, av_fim, first_image=8100, repetition_factor=1, seed=-1)],                             
#                             ]
#sSeq_set = sTrainRTransY2 = [[copy.deepcopy(sSeq0), sSeqCreateRTransY(iSeq_set[0][1], seed=-1)], 
#                             [copy.deepcopy(sSeq0), sSeqCreateRTransY(iSeq_set[4][1], seed=-1)],
#                             ]

iSeq_set = iSeenidRTransXYScale = iSeqCreateRTransXYScale(dx=45, dy=20, smin=0.55, smax=1.1, num_steps=50, slow_var = "X", continuous=True, num_images_used=25000, #20000
                                                      images_base_dir=alldbnormalized_base_dir, normalized_images = alldbnormalized_available_images, 
                                                      first_image_index=30000, pre_mirroring="none", repetition_factor=2, seed=-1)
sSeq_set = sSeenidRTransXYScale = sSeqCreateRTransXYScale(iSeq_set, seed=-1)

#WARNING, here continuous=continuous was wrong!!! we should always use the same test data!!!
iSeq_set = iNewidRTransXYScale = [[iSeqCreateRTransXYScale(dx=45, dy=20, smin=0.55, smax=1.1, num_steps=50, slow_var = "X", continuous=True, num_images_used=9000, #9000 
                                                      images_base_dir=alldbnormalized_base_dir, normalized_images = alldbnormalized_available_images, 
                                                      first_image_index=55000, pre_mirroring="none", repetition_factor=2, seed=-1)]]      #repetition_factor=4
#WARNING, code below is for display purposes only, it should be commented out!
#iSeq_set = iNewidRTransXYScale = [[iSeqCreateRTransXYScale(dx=45, dy=2, smin=0.85, smax=0.95, num_steps=50, slow_var = "X", continuous=True, num_images_used=2000, #9000 
#                                                      images_base_dir=alldbnormalized_base_dir, normalized_images = alldbnormalized_available_images, 
#                                                      first_image_index=55000, repetition_factor=1, seed=-1)]]


sSeq_set = sNewidRTransXYScale = [[sSeqCreateRTransXYScale(iSeq_set[0][0], seed=-1)]]

#This fixes classes of Newid data

print "Orig iSeenidRTransXYScale.correct_labels=", iSeenidRTransXYScale.correct_labels
print "Orig len(iSeenidRTransXYScale.correct_labels)=", len(iSeenidRTransXYScale.correct_labels)
print "Orig len(iSeenidRTransXYScale.correct_classes)=", len(iSeenidRTransXYScale.correct_classes)
all_classes = numpy.unique(iSeenidRTransXYScale.correct_classes)
print "all_classes=", all_classes
avg_labels = more_nodes.compute_average_labels_for_each_class(iSeenidRTransXYScale.correct_classes, iSeenidRTransXYScale.correct_labels)
print "avg_labels=", avg_labels 
iNewidRTransXYScale[0][0].correct_classes = more_nodes.map_labels_to_class_number(all_classes, avg_labels, iNewidRTransXYScale[0][0].correct_labels)


#quit()

ParamsRTransXYScaleFunc = SystemParameters.ParamsSystem()
ParamsRTransXYScaleFunc.name = "Function Based Data Creation for RTransXYScale"
ParamsRTransXYScaleFunc.network = "linearNetwork4L" #Default Network, but ignored
ParamsRTransXYScaleFunc.iTrain =iTrainRTransXYScale
ParamsRTransXYScaleFunc.sTrain = sTrainRTransXYScale

ParamsRTransXYScaleFunc.iSeenid = iSeenidRTransXYScale

ParamsRTransXYScaleFunc.sSeenid = sSeenidRTransXYScale

ParamsRTransXYScaleFunc.iNewid = iNewidRTransXYScale
ParamsRTransXYScaleFunc.sNewid = sNewidRTransXYScale

ParamsRTransXYScaleFunc.block_size = iTrainRTransXYScale[0][0].block_size
#if continuous == False:
#    ParamsRTransXYScaleFunc.train_mode = 'serial' #clustered improves final performance! mixed
#else:
#    ParamsRTransXYScaleFunc.train_mode = "window32" #clustered improves final performance! mixed
    
ParamsRTransXYScaleFunc.analysis = None
ParamsRTransXYScaleFunc.enable_reduced_image_sizes = True
ParamsRTransXYScaleFunc.reduction_factor = 1.0 # WARNING 1.0, 2.0, 4.0, 8.0  / 1.0 2.0 ... 
ParamsRTransXYScaleFunc.hack_image_size = 128 # WARNING   128,  64,  32 , 16 / 160  80 ...
ParamsRTransXYScaleFunc.enable_hack_image_size = True

#quit()






#######################################################################################################################
#################                  AGE Extraction Experiments                             #############################
#######################################################################################################################
def find_available_images(base_dir, from_subdirs=None, verbose=False):
    """Counts how many files are in each subdirectory.
    Returns a dictionary d, with entries: d[subdir] = (num_files_in_subfolder, label, [file names])
    where the file names have a relative path w.r.t. the base directory """    

    files_dict={}
    if os.path.lexists(base_dir):
        dirList=os.listdir(base_dir)
    else:
        dirList = []
    for subdir in dirList:
        if from_subdirs is None or subdir in from_subdirs:
            subdir_full = os.path.join(base_dir, subdir)
            subdirList = os.listdir(subdir_full)
            subdirList.sort()
            if subdir in ["Male","Female", "Unknown"]:
                if  subdir == "Male":
                    label=1
                elif subdir == "Female":
                    label=-1
                else:
                    label = 0 
            else:
                if verbose:
                    print "Subdir: ", subdir,
                label = float(subdir)
            files_dict[subdir] = (len(subdirList), label, subdirList)
    return files_dict      

def list_available_images(base_dir, from_subdirs=None, verbose=False):
    """Finds the files in all subdirectory.
    Returns a list l, with entries: l[k] = (file_name, subfolder)
    where the file names have a relative path w.r.t. the base directory """    

    if os.path.lexists(base_dir):
        dirList=os.listdir(base_dir)
#        dirList.append("")
    else:
        dirList = []
        print "WARNING! base_dir", base_dir, " does not exist!"

    files_list=[]   
    for filename in dirList:
        file_full = os.path.join(base_dir, filename)
        if os.path.isdir(file_full):
            subdir = filename
            if from_subdirs is None or subdir in from_subdirs:
                subdir_full = os.path.join(base_dir, subdir)
                subdirList = os.listdir(subdir_full)
                subdirList.sort()
        
                for filename in subdirList:
                    files_list.append((os.path.join(subdir, filename), subdir))            
        else:
            if verbose:
                print "filename", filename
            files_list.append((filename, "100"))

#    for subdir in dirList:
#%        if from_subdirs is None or subdir in from_subdirs:
#            subdir_full = os.path.join(base_dir, subdir)
#            if os.path.isdir(subdir_full):
#                subdirList = os.listdir(subdir_full)
#                subdirList.sort()
#    
#                for filename in subdirList:
#                    files_list.append((os.path.join(subdir, filename), subdir))             
    
    return files_list

age_all_labels_map_MORPH = load_GT_labels("/local/escalafl/Alberto/MORPH_setsS1S2S3_seed12345/GT_MORPH_AgeRAgeGenderRace.txt", age_included=True, rAge_included=True, gender_included=True, race_included=True, avgColor_included=False)
age_all_labels_map_INI = load_GT_labels("/home/escalafl/Databases/faces/INIBilder/GT_INI_AgeRAgeGenderRace.txt", age_included=True, rAge_included=True, gender_included=True, race_included=True, avgColor_included=False)
age_all_labels_map_FGNet = load_GT_labels("/home/escalafl/workspace4/FaceDetectSFA/FGNet_FD/GT_FGNet_AgeRAgeGenderRace.txt", age_included=True, rAge_included=True, gender_included=True, race_included=True, avgColor_included=False)

#print age_all_labels_map_FGNet
#quit()

def append_GT_labels_to_files(files_list, age_all_labels_map, min_age=0.0, max_age=365000.0, select_races=[-2,-1,0,1,2], verbose=False):
#min_age and max_age in days
    print "age_all_labels_map has %d entries"%(len(age_all_labels_map.keys()))
#    rAge_labels_TrainRAge = []
#    gender_labels_TrainRAge = []
#    race_labels_TrainRAge = []   
    labeled_files_list = []
    for (input_file, subdir) in files_list:
        input_file_short = string.split(input_file,"/")[-1]
#        rAge_labels_TrainRAge.append(age_all_labels_map[input_file_short][1]) 
#        gender_labels_TrainRAge.append(age_all_labels_map[input_file_short][2]) 
#        race_labels_TrainRAge.append(age_all_labels_map[input_file_short][3]) 
#               (input_file, age, rAge, race, gender)
        iage = int(subdir)
        if iage == 100:
            iage = age_all_labels_map[input_file_short][0]

        entry = (input_file, int(subdir), age_all_labels_map[input_file_short][1], age_all_labels_map[input_file_short][3], age_all_labels_map[input_file_short][2])
        if entry[2] < min_age or entry[2] > max_age:
            if verbose:
                print "entry ", entry, " discarded due to age out of range: ", entry[2]
        elif entry[3] not in select_races:
            if verbose:
                print "entry ", entry, " discarded due to race not in select_races: ", entry[3]        
        else:
            labeled_files_list.append(entry)
    print "after appending label and filtering samples, the number of original filenames is:", len(labeled_files_list)
#    rAge_labels_TrainRAge = numpy.array(rAge_labels_TrainRAge).reshape((-1,1))
#    race_labels_TrainRAge = numpy.array(race_labels_TrainRAge).reshape((-1,1))
#    gender_labels_TrainRAge = numpy.array(gender_labels_TrainRAge).reshape((-1,1))

    return labeled_files_list

def age_cluster_labeled_files(labeled_files_list, repetition=1, num_clusters=1, trim_number=None, shuffle_each_cluster=False):
    """ clusters/joins the entries of files_dict, so that
        each cluster has the same size  
        The set of clusters is represented as a list of clusters [cluster1, cluster2, ...],
        and each cluster is a list of one tuples [(num_files, label, files_with_subdir_dict, ages, rAges, races, genders)]  
        """
    labeled_files_list = sorted(labeled_files_list, key = lambda labeled_file: labeled_file[2])
    num_files = len(labeled_files_list)
    print "num_files =", num_files
    
    cluster_size = num_files/num_clusters
    if cluster_size * num_clusters != num_files:
        print "Number of files %d is not a multiple of num_clusters %d. Fixing this discarding first few samples"%(num_files, num_clusters) 
        labeled_files_list = labeled_files_list[-cluster_size * num_clusters:]
        num_files = len(labeled_files_list)
        print "new num_files=", num_files

    if num_files == 0:
        num_clusters = 0

    clusters = []
    for c in range(num_clusters):
        cluster_labeled_files_list = labeled_files_list[c*cluster_size:(c+1)*cluster_size]

        cluster_files_list = [labeled_file[0] for rep in range(repetition) for labeled_file in cluster_labeled_files_list]
        
        cluster_ages_rAges_races_genders_list = [(labeled_file[1], labeled_file[2], labeled_file[3], labeled_file[4]) for rep in range(repetition) for labeled_file in cluster_labeled_files_list]
        cluster_ages_rAges_races_genders_list = numpy.array(cluster_ages_rAges_races_genders_list)
                
#        cluster_ages_list = [labeled_file[1] for labeled_file in cluster_labeled_files_list]
#        cluster_rAges_list = [labeled_file[2] for labeled_file in cluster_labeled_files_list]
#        cluster_races_list = [labeled_file[3] for labeled_file in cluster_labeled_files_list]
#        cluster_genders_list = [labeled_file[4] for labeled_file in cluster_labeled_files_list]
        
#        cluster_files_list = sfa_libs.repeat_list_elements(cluster_files_list, rep=repetition)
#        cluster_ages_list = sfa_libs.repeat_list_elements(cluster_ages_list, rep=repetition)
#        cluster_rAges_list = sfa_libs.repeat_list_elements(cluster_rAges_list, rep=repetition)
#        cluster_races_list = sfa_libs.repeat_list_elements(cluster_races_list, rep=repetition)
#        cluster_genders_list = sfa_libs.repeat_list_elements(cluster_genders_list, rep=repetition)

        if trim_number > 0:
            cluster_num_files = trim_number
        else:
            cluster_num_files = cluster_size*repetition

        if shuffle_each_cluster:
            ordering = numpy.arange(cluster_size*repetition)
            numpy.random.shuffle(ordering)
            cluster_files_list = cluster_files_list[ordering][0:cluster_num_files]
            cluster_ages_rAges_races_genders_list = cluster_ages_rAges_races_genders_list[ordering,:]
#            cluster_rAges_list = cluster_rAges_list[ordering][0:cluster_num_files]
#            cluster_races_list = cluster_races_list[ordering][0:cluster_num_files]
#            cluster_genders_list = cluster_genders_list[ordering][0:cluster_num_files]

        #print "cluster_ages_rAges_races_genders_list=",cluster_ages_rAges_races_genders_list
        cluster_label = cluster_ages_rAges_races_genders_list[:,0].mean()

        cluster = [cluster_num_files, cluster_label, cluster_files_list, cluster_ages_rAges_races_genders_list]
        clusters.append(cluster)
    return clusters

def age_cluster_list(files_dict, repetition=1, smallest_number_images=None, largest_number_images=None):
    """ clusters/joins the entries of files_dict, so that
        each cluster has at least smallest_number_images images. 
        The set of clusters is represented as a list of clusters [cluster1, cluster2, ...],
        and each cluster is a list of tuples [(num_files, label, files_with_subdir_dict), ...]  
        """
    subdirs = files_dict.keys()
    subdirs = sorted(subdirs, key = lambda subdir: float(subdir))
    subdirs.reverse()

    clusters = []
    cluster = []
    cluster_size = 0
    for subdir in subdirs:
        num_files_subdir, label, files_subdir = files_dict[subdir]
        if num_files_subdir > 0:
            if largest_number_images != None:
                max_repetition = int(numpy.min((numpy.ceil(largest_number_images*1.0/num_files_subdir), repetition)))
            else:
                max_repetition = repetition
            print "max_repetition=", max_repetition, "from ", num_files_subdir, " to ", num_files_subdir*max_repetition
            num_files_subdir *= max_repetition
            files_subdir *= max_repetition   
                 
            files_subdir_with_subdir = []
            for file_name in files_subdir:
                files_subdir_with_subdir.append(os.path.join(subdir,file_name))
            cluster.append( (num_files_subdir, label, files_subdir_with_subdir) )
            cluster_size += num_files_subdir
            if smallest_number_images==None or cluster_size >=  smallest_number_images:
                #Save cluster
                clusters.append(cluster)
                #Start a new cluster
                cluster = []
                cluster_size=0
    if cluster_size != 0: #Something has not reached proper size, add it to lastly created cluster
        if len(clusters)>0:
            clusters[-1].extend(cluster)      
        else:
            clusters.append(cluster)
    return clusters

def cluster_to_labeled_samples(clusters, trim_number=None, shuffle_each_cluster=True, verbose=False):
    """ Reads a cluster structure in a nested list, generates representative labels, 
    joins filenames and trims them.
    If trim_number is None, no trimming is done. 
    Otherwise clusters are of size at most trim_number
    new_clusters[0]= a cluster
    cluster = (total_files_cluster, avg_label, files_subdirs, orig_labels))
    """
    new_clusters=[]
    #print "clusters[0] is", clusters[0]
    #print "len(clusters[0]) is", len(clusters[0])

    for cluster in clusters:
        total_files_cluster = 0
        files_subdirs = []
        orig_labels = []
        sum_labels = 0
        #print "Processing cluster:", cluster
        if verbose:
            print "ClustersAdded:"
        for (num_files_subdir, label, files_subdir) in cluster:
            if verbose:
                print " With label:", label, "(%d imgs)"%num_files_subdir
            total_files_cluster += num_files_subdir
            files_subdirs.extend(files_subdir)
            orig_labels += [label]*num_files_subdir
            #TODO: handle non-float labels
            sum_labels += label*num_files_subdir
        avg_label = sum_labels / total_files_cluster
        if verbose:
            print ""

        if shuffle_each_cluster:
            selected = list(range(total_files_cluster))
            numpy.random.shuffle(selected)
            files_subdirs = [files_subdirs[i] for i in selected]
            orig_labels = [orig_labels[i] for i in selected]

        if len(files_subdirs) != len(orig_labels):
            print "Wrong cluster files and orig labels lenghts"
            print len(files_subdirs)
            print len(orig_labels)

        if trim_number != None:
            files_subdirs = files_subdirs[0:trim_number]
            orig_labels = orig_labels[0:trim_number]
            total_files_cluster = min(total_files_cluster, trim_number)
        new_clusters.append((total_files_cluster, avg_label, files_subdirs, orig_labels))

    new_clusters.reverse()
    return new_clusters


def MORPH_leave_k_identities_out_list(available_images_list, k=0):
    if k==0:
        return available_images_list, []
    
    #subdirs = available_images_dict.keys()
    #all_filenames = []
    #for subdir in subdirs:
    #    all_filenames.extend(available_images_dict[subdir][2])
    all_identities_list = []
    for (filename, subdir) in available_images_list:
        identity = string.split(filename, "_")[0]
        identity = string.split(identity, "/")[-1]
        all_identities_list.append(identity)
    
    all_identities = set(all_identities_list)
    all_identities_unique = list(all_identities)
    print "%d unique identities detected"%len(all_identities_unique)

    num_identities = numpy.arange(len(all_identities_unique))
    numpy.random.shuffle(num_identities)
    separated_identities = all_identities_unique[0:k]

    #print "separated_identities=", separated_identities
    
    #now create two dictionaries
    available_images_list_orig = []
    available_images_list_separated = []
    num_separated = 0
    num_orig = 0
    for current_index, (filename, subdir) in enumerate(available_images_list):
        if all_identities_list[current_index] in separated_identities:
            available_images_list_separated.append((filename, subdir))
            num_separated +=1
        else:
            available_images_list_orig.append((filename, subdir))
            num_orig +=1
        
    print "Separating %d/%d (LKO)"%(num_orig, num_separated)
    print "available_images_list_orig[0]=", available_images_list_orig[0]
    print "available_images_list_separated[0]=", available_images_list_separated[0]
    return available_images_list_orig, available_images_list_separated

# # def MORPH_leave_k_identities_out(available_images_dict, k=0):
# #     # available_images_dict[subdir] = (num_files_in_subfolder, label, [file names])
# #     if k==0:
# #         return available_images_dict, {}
# #     
# #     subdirs = available_images_dict.keys()
# #     all_filenames = []
# #     for subdir in subdirs:
# #         all_filenames.extend(available_images_dict[subdir][2])
# #     all_identities_list = []
# #     for filename in all_filenames:
# #         all_identities_list.append(string.split(filename, "_")[0])
# #     
# #     all_identities = set(all_identities_list)
# #     all_identities_unique = list(all_identities)
# # 
# #     num_identities = numpy.arange(len(all_identities_unique))
# #     numpy.random.shuffle(num_identities)
# #     separated_identities = all_identities_unique[0:k]
# #     #print "separated_identities=", separated_identities
# #     
# #     #now create two dictionaries
# #     available_images_dict_orig = {}
# #     available_images_dict_separated = {}
# #     current_index = 0
# #     for subdir in subdirs:
# #         num_files_in_subfolder, label, filenames = available_images_dict[subdir]
# #         filenames_orig = []
# #         filenames_separated = []
# #         num_orig = 0
# #         num_separated = 0
# #         for file_name in filenames:
# #             sid = all_identities_list[current_index]
# #             #sid = string.split(file_name, "_")[0]
# #             if sid in separated_identities:
# #                 filenames_separated.append(file_name)
# #                 num_separated +=1
# #             else:
# #                 filenames_orig.append(file_name)
# #                 num_orig +=1
# #             current_index +=1
# #         if num_separated+num_orig != num_files_in_subfolder:
# #             er = "Unexpected error in the sizes of the filename arrays"
# #             raise Exception(er)
# #         available_images_dict_orig[subdir]=(num_orig, label, filenames_orig)
# #         available_images_dict_separated[subdir]=(num_separated, label, filenames_separated)
# #         print "Separating %d/%d (LKO)"%(num_orig, num_separated),
# #     return available_images_dict_orig, available_images_dict_separated

# # def MORPH_leave_k_identities_out_old(available_images_dict, k=0):
# #     # available_images_dict[subdir] = (num_files_in_subfolder, label, [file names])
# #     if k==0:
# #         return available_images_dict, {}
# #     
# #     subdirs = available_images_dict.keys()
# #     all_filenames = []
# #     for subdir in subdirs:
# #         all_filenames.extend(available_images_dict[subdir][2])
# #     all_identities = set()
# #     for filename in all_filenames:
# #         all_identities.add(string.split(filename, "_")[0])
# #     all_identities_list = list(all_identities)
# #     numpy.random.shuffle(all_identities_list)
# # 
# #     separated_identities = all_identities_list[0:k]
# #     #print "separated_identities=", separated_identities
# #     
# #     #now create two dictionaries
# #     available_images_dict_orig = {}
# #     available_images_dict_separated = {}
# #     for subdir in subdirs:
# #         num_files_in_subfolder, label, filenames = available_images_dict[subdir]
# #         filenames_orig = []
# #         filenames_separated = []
# #         num_orig = 0
# #         num_separated = 0
# #         for file_name in filenames:
# #             sid = string.split(file_name, "_")[0]
# #             if sid in separated_identities:
# #                 filenames_separated.append(file_name)
# #                 num_separated +=1
# #             else:
# #                 filenames_orig.append(file_name)
# #                 num_orig +=1
# #         if len(filenames_separated)+len(filenames_orig) != num_files_in_subfolder:
# #             er = "Unexpected error in the sizes of the filename arrays"
# #             raise Exception(er)
# #         available_images_dict_orig[subdir]=(num_orig, label, filenames_orig)
# #         available_images_dict_separated[subdir]=(num_separated, label, filenames_separated)
# #         print "Separating %d/%d (LKO)"%(num_orig, num_separated),
# #     return available_images_dict_orig, available_images_dict_separated


def MORPH_select_k_images_list(available_images_list, k=0, replacement=False):
    # available_images_dict[subdir] = (num_files_in_subfolder, label, [file names])
    if k==0:
        return available_images_list, []
    
    num_filenames = len(available_images_list)
    if k > num_filenames:
        er = "selecting too many images k=%d, but available=%d"%(k,num_filenames)
        raise Exception(er)
    
    selection = numpy.arange(num_filenames)
    numpy.random.shuffle(selection)
    selection = selection[0:k]
    separated = numpy.zeros(num_filenames)
    separated[selection] = 1
    available_images_list_orig = []
    available_images_list_separated = []
    num_orig = 0
    num_separated = 0
    for current_index, filename_subdir in enumerate(available_images_list):
        if separated[current_index]:
            available_images_list_separated.append(filename_subdir)
            num_separated +=1
        else:
            available_images_list_orig.append(filename_subdir)
            num_orig +=1
    if num_separated+num_orig != num_filenames:
        er = "Unexpected error in the sizes of the filename lists"
        raise Exception(er)
    print "Separating %d/%d (selecting k=%d) ..."%(num_orig, num_separated, k)
    #print "available_images_list_separated=", available_images_list_separated
    if replacement:
        available_images_list_orig = available_images_list

    print "available_images_list_orig[0]=", available_images_list_orig[0]
    print "available_images_list_separated[0]=", available_images_list_separated[0]
    
    return available_images_list_orig, available_images_list_separated

# # #TODO: Test function. Do the same for LkPO out??
# # def MORPH_select_k_images(available_images_dict, k=0, replacement=False):
# #     # available_images_dict[subdir] = (num_files_in_subfolder, label, [file names])
# #     if k==0:
# #         return available_images_dict, {}
# #     
# #     subdirs = available_images_dict.keys() #any order should be fine
# #     num_filenames = 0
# #     for subdir in subdirs:
# #         num_filenames += available_images_dict[subdir][0]
# # 
# #     selection = numpy.arange(num_filenames)
# #     numpy.random.shuffle(selection)
# #     selection = selection[0:k]
# #     separated = numpy.zeros(num_filenames)
# #     separated[selection] = 1
# #     
# #     available_images_dict_orig = {}
# #     available_images_dict_separated = {}
# #     current_index = 0
# #     for subdir in subdirs:
# #         num_files_in_subfolder, label, filenames = available_images_dict[subdir]
# #         filenames_orig = []
# #         filenames_separated = []
# #         num_orig = 0
# #         num_separated = 0
# #         for filename in filenames:
# #             if separated[current_index]:
# #                 filenames_separated.append(filename)
# #                 num_separated +=1
# #             else:
# #                 filenames_orig.append(filename)
# #                 num_orig +=1
# #             current_index +=1
# #         if num_separated+num_orig != num_files_in_subfolder:
# #             er = "Unexpected error in the sizes of the filename arrays"
# #             raise Exception(er)
# #         if num_orig > 0:
# #             available_images_dict_orig[subdir]=(num_orig, label, filenames_orig)
# #         if num_separated > 0:
# #             available_images_dict_separated[subdir]=(num_separated, label, filenames_separated)
# #         print "Separating %d/%d (select k)"%(num_orig, num_separated),
# # 
# #     if replacement:
# #         available_images_dict_orig = available_images_dict
# #     return available_images_dict_orig, available_images_dict_separated

# # def MORPH_select_k_images_old(available_images_dict, k=0, replacement=False):
# #     # available_images_dict[subdir] = (num_files_in_subfolder, label, [file names])
# #     if k==0:
# #         return available_images_dict, {}
# #     
# #     subdirs = available_images_dict.keys()
# #     all_filenames = []
# #     for subdir in subdirs:
# #         all_filenames.extend(available_images_dict[subdir][2])
# # 
# #     num_filenames = len(all_filenames)
# #     selection = numpy.arange(num_filenames)
# #     numpy.random.shuffle(selection)
# #     separated_filenames = [all_filenames[d] for d in selection[0:k]] #WARNING; PATH IS RELATIVE, NOT ABSOLUTE; THERE MIGHT BE COLISIONS!!!
# # 
# #     available_images_dict_orig = {}
# #     available_images_dict_separated = {}
# #     for subdir in subdirs:
# #         num_files_in_subfolder, label, filenames = available_images_dict[subdir]
# #         filenames_orig = []
# #         filenames_separated = []
# #         num_orig = 0
# #         num_separated = 0
# #         for file_name in filenames:
# #             if file_name in separated_filenames: #THIS IS TOO SLOW!!! OPTIMIZE THIS USING SELECTION?
# #                 filenames_separated.append(file_name)
# #                 num_separated +=1
# #             else:
# #                 filenames_orig.append(file_name)
# #                 num_orig +=1
# #         if num_separated+num_orig != num_files_in_subfolder:
# #             er = "Unexpected error in the sizes of the filename arrays"
# #             raise Exception(er)
# #         available_images_dict_orig[subdir]=(num_orig, label, filenames_orig)
# #         available_images_dict_separated[subdir]=(num_separated, label, filenames_separated)
# #         print "Separating %d/%d (select k)"%(num_orig, num_separated),
# # 
# #     if replacement:
# #         available_images_dict_orig = available_images_dict
# #     return available_images_dict_orig, available_images_dict_separated

#numpy.random.seed(111222333)
#r_age_clusters = [[21,22,23],[24,25,26],[27,28,29],[30,31],[32,33],[34,35],[36,37],[38,39],
#                [40],[41],[42],[43],[44],[45],[46],[47],[48],[49],
#                [50],[51],[52],[53],[54],[55],[56],[57],[58],[59],
#                [60],[61],[62],[63],[64],[65],[66],[67],[68],[69],
#                [70]]

#####
####r_age_all_clustered_available_images = TODO: write this part. 

def iSeqCreateRAge(dx=2, dy=2, smin=0.95, smax=1.05, delta_rotation=0.0, pre_mirroring="none", 
                   contrast_enhance=False, obj_avg_std=0.0, obj_std_min=0.20, obj_std_max=0.20, new_clusters=None, num_images_per_cluster_used=10, 
                   images_base_dir="wrong dir", first_image_index=0, repetition_factor=1, seed=-1, use_orig_label_as_class=False, use_orig_label=True, increasing_orig_label=True):
    if seed >= 0 or seed is None: #also works for 
        numpy.random.seed(seed)

    if len(new_clusters)>0:
        min_cluster_size = new_clusters[0][0]
    else:
        return None
        
    for cluster in new_clusters:
        min_cluster_size = min(min_cluster_size, cluster[0])

    if first_image_index + num_images_per_cluster_used > min_cluster_size and num_images_per_cluster_used>0:
        err = "Images to be used %d + %d exceeds the number of available images %d of at least one cluster"%(first_image_index, num_images_per_cluster_used, min_cluster_size)
        raise Exception(err) 

    print "***** Setting Information Parameters for Real Translation XYScale ******"
    iSeq = SystemParameters.ParamsInput()
    #iSeq.name = "Real Translation " + slow_var + ": (%d, %d, %d, %d) numsteps %d"%(dx, dy, smin, smax, num_steps)
    iSeq.data_base_dir = images_base_dir
    #TODO: create clusters here. 
    iSeq.ids = []
    iSeq.input_files = []
    iSeq.orig_labels = []
    for cluster in new_clusters:
        cluster_id = [cluster[1]] * repetition_factor * num_images_per_cluster_used #avg_label. The average label of the current cluster being considered
        iSeq.ids.extend(cluster_id)

        increasing_indices = numpy.arange(num_images_per_cluster_used*repetition_factor)/repetition_factor
        cluster_labels = (cluster[3][first_image_index:first_image_index+num_images_per_cluster_used,:])[increasing_indices, :] #orig_label
        if len(cluster_id) != len(cluster_labels):
            print "ERROR: Wrong number of cluster labels and original labels"
            print "len(cluster_id)=", len(cluster_id)
            print "len(cluster_labels)=", len(cluster_labels)
            quit()
        iSeq.orig_labels.extend(cluster_labels)
        selected_image_filenames = repeat_list_elements(cluster[2][first_image_index:first_image_index + num_images_per_cluster_used], repetition_factor) #filenames
        iSeq.input_files.extend(selected_image_filenames)
    if len(iSeq.orig_labels) > 1:
        iSeq.orig_labels = numpy.vstack(iSeq.orig_labels)
        print "iSeq.orig_labels.shape=",iSeq.orig_labels.shape

    if use_orig_label and increasing_orig_label:
        if iSeq.orig_labels.shape[1] > 1:
            original_label_index = 1 #rAge
        else:
            original_label_index = 0 #age     
        print "Reordering image filenames of data set according to the original labels"
        ordering = numpy.argsort(iSeq.orig_labels[:,original_label_index])
        ordered_input_files = [iSeq.input_files[i] for i in ordering]
        ordered_orig_labels = iSeq.orig_labels[ordering,:]
        ordered_ids = [iSeq.ids[i] for i in ordering]
        iSeq.input_files = ordered_input_files
        iSeq.orig_labels = ordered_orig_labels
        iSeq.ids = ordered_ids
    else:
        print "Image filenames of data set not reordered according to the original labels"

    iSeq.num_images = len(iSeq.input_files)
    iSeq.pre_mirroring = pre_mirroring
    
    if iSeq.pre_mirroring == "none":
        iSeq.pre_mirror_flags = [False] * iSeq.num_images
    elif iSeq.pre_mirroring == "all":
        iSeq.pre_mirror_flags = [True] * iSeq.num_images
    elif iSeq.pre_mirroring == "random":
        iSeq.pre_mirror_flags = more_nodes.random_boolean_array(iSeq.num_images)
    elif iSeq.pre_mirroring == "duplicate":
        iSeq.input_files = sfa_libs.repeat_list_elements(iSeq.input_files, rep=2)
        iSeq.ids = sfa_libs.repeat_list_elements(iSeq.ids)
        increasing_indices = numpy.arange(iSeq.num_images*repetition_factor)/repetition_factor
        iSeq.orig_labels = iSeq.orig_labels[increasing_indices,:]
        tmp_pre_mirror_flags = more_nodes.random_boolean_array(iSeq.num_images) #e.g., [T, T, F, F, T, F]
        iSeq.pre_mirror_flags = numpy.array([item^val for item in tmp_pre_mirror_flags for val in (False,True)]) #e.g., [T,F, T,F, F,T, F,T, T,F, F,T])
        iSeq.num_images *= 2
        repetition_factor *= 2
    else:
        er = "Erroneous parameter iSeq.pre_mirroring=",iSeq.pre_mirroring
        raise Exception(er)
        


    #iSeq.slow_var = slow_var
    iSeq.dx = dx
    iSeq.dy = dy
    iSeq.smin = smin
    iSeq.smax = smax
    iSeq.delta_rotation = delta_rotation
    if contrast_enhance == True:
        contrast_enhance = "AgeContrastEnhancement_Avg_Std" # "PostEqualizeHistogram" # "AgeContrastEnhancement"
    if contrast_enhance in ["AgeContrastEnhancement_Avg_Std", "AgeContrastEnhancement25", "AgeContrastEnhancement20", "AgeContrastEnhancement15", "AgeContrastEnhancement", "PostEqualizeHistogram", "SmartEqualizeHistogram", False, ]:
        iSeq.contrast_enhance = contrast_enhance
    else:
        ex = "Contrast method unknown"
        raise Exception(ex)

    iSeq.obj_avg_std=obj_avg_std
    iSeq.obj_std_min=obj_std_min
    iSeq.obj_std_max=obj_std_max
        
#    if len(iSeq.ids) % len(iSeq.trans) != 0 and continuous == False:
#        ex="Here the number of translations/scalings must be a divisor of the number of identities"
#        raise Exception(ex)
    iSeq.ages = [None]
    iSeq.genders = [None]
    iSeq.racetweens = [None]
    iSeq.expressions = [None]
    iSeq.morphs = [None]
    iSeq.poses = [None]
    iSeq.lightings = [None]
    iSeq.slow_signal = 0 #real slow signal is the translation in the x axis (correlated to identity), added during image loading
    iSeq.step = 1
    iSeq.offset = 0

    #iSeq.params = [ids, expressions, morphs, poses, lightings]
    iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                      iSeq.morphs, iSeq.poses, iSeq.lightings]

    iSeq.block_size = num_images_per_cluster_used * repetition_factor

    iSeq.train_mode = "serial" #"regular" #"serial" # = "serial" "mixed", None
# None, "regular", "fwindow16", "fwindow32", "fwindow64", "fwindow128"
#        quit()
#        iSeq.train_mode = None 

    print "BLOCK SIZE =", iSeq.block_size 
#     if use_orig_label_as_class == False: #Use cluster (average) labels as classes, or the true original labels
#         unique_ids, iSeq.correct_classes = numpy.unique(iSeq.ids, return_inverse=True)
# #        iSeq.correct_classes_from_zero = iSeq.correct_classes
# #        iSeq.correct_classes = sfa_libs.wider_1Darray(numpy.arange(len(clusters)),  iSeq.block_size)
#     else:
#         unique_labels, iSeq.correct_classes = numpy.unique(iSeq.orig_labels, return_inverse=True)
# #        iSeq.correct_classes_from_zero = iSeq.correct_classes

           
    if use_orig_label == False: #Use cluster (average) labels as labels, or the true original labels
        iSeq.correct_labels = numpy.array(iSeq.ids)
    else:
        iSeq.correct_labels = numpy.array(iSeq.orig_labels[:,1])
    unique_labels, iSeq.correct_classes = numpy.unique(iSeq.correct_labels, return_inverse=True)
    #iSeq.correct_classes_from_zero = iSeq.correct_labels[:,1]


    if len(iSeq.ids) != len(iSeq.orig_labels) or len(iSeq.orig_labels) != len(iSeq.input_files):
        er = "Computation of orig_labels failed:"+str(iSeq.ids)+str(iSeq.orig_labels)
        er += "len(iSeq.ids)=%d"%len(iSeq.ids) + "len(iSeq.orig_labels)=%d"%len(iSeq.orig_labels)+"len(iSeq.input_files)=%d"%len(iSeq.input_files)
        raise Exception(er)

    SystemParameters.test_object_contents(iSeq)
    return iSeq

def sSeqCreateRAge(iSeq, seed=-1, use_RGB_images=False):
    if seed >= 0 or seed is None: #also works for 
        numpy.random.seed(seed)
    #else seed <0 then, do not change seed
    
    if iSeq==None:
        print "iSeq was None, this might be an indication that the data is not available"
        sSeq = SystemParameters.ParamsDataLoading()
        return sSeq
    
    print "******** Setting Training Data Parameters for Real Age  ****************"
    sSeq = SystemParameters.ParamsDataLoading()
    #print "iSeq.input_files=", iSeq.input_files
    #print "iSeq.input_files[0]=", iSeq.input_files[0]
    #print "iSeq.data_base_dir", iSeq.data_base_dir
    sSeq.input_files = [ os.path.join(iSeq.data_base_dir, file_name) for file_name in iSeq.input_files]
    sSeq.num_images = iSeq.num_images
    sSeq.block_size = iSeq.block_size
    sSeq.train_mode = iSeq.train_mode
    sSeq.include_latest = iSeq.include_latest
    sSeq.image_width = 256
    sSeq.image_height = 260 #192
    sSeq.subimage_width = 160 #(article 160) #192 # 160 #128 
    sSeq.subimage_height = 160 #(article 160) #192 # 160 #128 
    sSeq.pre_mirror_flags = iSeq.pre_mirror_flags
    
    sSeq.trans_x_max = iSeq.dx
    sSeq.trans_x_min = -1 * iSeq.dx
    sSeq.trans_y_max = iSeq.dy
    sSeq.trans_y_min = -1 * iSeq.dy
    sSeq.min_sampling = iSeq.smin
    sSeq.max_sampling = iSeq.smax
    sSeq.delta_rotation = iSeq.delta_rotation
    sSeq.contrast_enhance = iSeq.contrast_enhance
    sSeq.obj_avg_std = iSeq.obj_avg_std
    sSeq.obj_std_min = iSeq.obj_std_min
    sSeq.obj_std_max = iSeq.obj_std_max
            
    #sSeq.subimage_pixelsampling = 2
    #sSeq.subimage_first_column = sSeq.image_width/2-sSeq.subimage_width*sSeq.pixelsampling_x/2+ 5*sSeq.pixelsampling_x
    sSeq.add_noise_L0 = True
    if use_RGB_images:
        sSeq.convert_format = "RGB" # "RGB", "L"
    else:
        sSeq.convert_format = "L"
    sSeq.background_type = None
    #random translation for th w coordinate
    #sSeq.translation = 20 # 25, Should be 20!!! Warning: 25
    #sSeq.translations_x = numpy.random.random_integers(-sSeq.translation, sSeq.translation, sSeq.num_images)                                                           
#    print "=>", sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images, sSeq.translations_x
#    quit()

#    Do integer displacements make more sense? depends if respect to original image or not. Translation logic needs urgent review!!!
#    sSeq.translations_x = numpy.random.uniform(low=sSeq.trans_x_min, high=sSeq.trans_x_max, size=sSeq.num_images)
#    sSeq.translations_y = numpy.random.uniform(low=sSeq.trans_y_min, high=sSeq.trans_y_max, size=sSeq.num_images)
    #BUG0: why is this an integer offset? also frationary offsets should be supported and give acceptable results.
    
    #Continuous translations: 
#    sSeq.translations_x = numpy.random.uniform(low=sSeq.trans_x_min, high=sSeq.trans_x_max, size=sSeq.num_images)
#    sSeq.translations_y = numpy.random.uniform(low=sSeq.trans_y_min, high=sSeq.trans_y_max, size=sSeq.num_images) 
    #Or alternatively, discrete ofsets:  
    sSeq.offset_translation_x = 0.0 #WARNING, experimental recentering!!!
    sSeq.offset_translation_y = -6.0 #-6.0
#    sSeq.offset_translation_x = -15.0 
#    sSeq.offset_translation_y = -10.0
    integer_translations = True and False
    if integer_translations:
        sSeq.translations_x = numpy.random.randint(sSeq.trans_x_min, sSeq.trans_x_max+1, sSeq.num_images) + sSeq.offset_translation_x
        sSeq.translations_y = numpy.random.randint(sSeq.trans_y_min, sSeq.trans_y_max+1, sSeq.num_images) + sSeq.offset_translation_y
    else:
        sSeq.translations_x = numpy.random.uniform(sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images) + sSeq.offset_translation_x
        sSeq.translations_y = numpy.random.uniform(sSeq.trans_y_min, sSeq.trans_y_max, sSeq.num_images) + sSeq.offset_translation_y

    print "GSP: sSeq.translations_x=", sSeq.translations_x

    sSeq.pixelsampling_x = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
    sSeq.pixelsampling_y = sSeq.pixelsampling_x + 0.0

    sSeq.rotation = numpy.random.uniform(-sSeq.delta_rotation, sSeq.delta_rotation, sSeq.num_images)
    if iSeq.obj_avg_std is None:
        sSeq.obj_avgs = [None,]*sSeq.num_images
        print "Good 1/3"
    elif iSeq.obj_avg_std > 0:
        sSeq.obj_avgs = numpy.random.normal(0.0, iSeq.obj_avg_std, size=sSeq.num_images) #mean intensity, centered at zero here
    else:
        sSeq.obj_avgs = numpy.zeros(sSeq.num_images)
    sSeq.obj_stds = numpy.random.uniform(sSeq.obj_std_min, sSeq.obj_std_max, sSeq.num_images) #contrast

    #BUG1 fix
    sSeq.subimage_first_row =  (sSeq.image_height-sSeq.subimage_height*sSeq.pixelsampling_y)/2.0
    sSeq.subimage_first_column = (sSeq.image_width-sSeq.subimage_width*sSeq.pixelsampling_x)/2.0

    ##BUG1: image center is not computed that way!!! also half(width-1) computation is wrong!!!
    #sSeq.subimage_first_row =  sSeq.image_height/2.0-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
    #sSeq.subimage_first_column = sSeq.image_width/2.0-sSeq.subimage_width*sSeq.pixelsampling_x/2.0

    sSeq.trans_sampled = True #TODO:check semantics, when is sampling/translation done? why does this value matter?
    sSeq.name = "RAge Dx in (%d, %d) Dy in (%d, %d), sampling in (%d perc, %d perc)"%(sSeq.trans_x_min, 
        sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, int(sSeq.min_sampling*100), int(sSeq.max_sampling*100))

    print "Mean in correct_labels is:", iSeq.correct_labels.mean()
    print "Var in correct_labels is:", iSeq.correct_labels.var()
    sSeq.load_data = load_data_from_sSeq
    SystemParameters.test_object_contents(sSeq)
    return sSeq


experiment_seed = os.getenv("CUICUILCO_EXPERIMENT_SEED") #1112223339 #1112223339
if experiment_seed:
    experiment_seed = int(experiment_seed)
else:
    experiment_seed = 1112223334 #111222333
    ex = "CUICUILCO_EXPERIMENT_SEED unset"
    raise Exception(ex)
print "Age estimation. experiment_seed=", experiment_seed
numpy.random.seed(experiment_seed) #seed|-5789
print "experiment_seed=", experiment_seed

age_use_RGB_images = False #LRec_use_RGB_images
#TODO: Repeat computation of blind levels for MORPH, FG_Net and MORPH+FGNet. (orig labels, no rep, all images)
#min_cluster_size_MORPH = 60000 # 1400 # 60000
#max_cluster_size_MORPH = None  # 1400 # None
#age_trim_number_MORPH = 1400 # 1400
leave_k_out_MORPH = 2000 #2000 #1000 #0 #Number of subjects left out for testing
if leave_k_out_MORPH == 0:
    select_k_images_newid = 8000
#select_k_images_seenid = 1500 #16000 #4000 #3000 #3750

option_setup_CNN = 1 # 1=CNN setup, 0=my setup
if option_setup_CNN: 
    leave_k_out_MORPH = 0 #to speed on unnecessary computation 
    select_k_images_newid = 1000
    select_k_images_seenid = 1000 #4000 #3000 #3750 

if age_use_RGB_images:
    age_eyes_normalized_base_dir_MORPH = "/local/escalafl/Alberto/MORPH_normalizedEyesZ4_horiz_RGB_ByAge" #RGB: "/local/escalafl/Alberto/MORPH_normalizedEyesZ3_horiz_RGB_ByAge"
else:
    age_eyes_normalized_base_dir_MORPH = "/local/escalafl/Alberto/MORPH_normalizedEyesZ4_horiz_ByAge"
age_files_list_MORPH = list_available_images(age_eyes_normalized_base_dir_MORPH, from_subdirs=None) #change from_subdirs to select a subset of all ages!

if leave_k_out_MORPH:
    print "LKO enabled, k=%d"%leave_k_out_MORPH
    age_files_list_MORPH, age_files_list_MORPH_out = MORPH_leave_k_identities_out_list(age_files_list_MORPH, k=leave_k_out_MORPH)
# #     if leave_k_out_MORPH == 1000:
# #         age_trim_number_MORPH = 1270 #age_trim_number_MORPH = 1270. This might be important to preserve the number of clusters
# #     else:
# #         age_trim_number_MORPH = 1160
# #     #print "age_files_dict_MORPH_out=", age_files_dict_MORPH_out
else:
    age_files_list_MORPH, age_files_list_MORPH_out = MORPH_select_k_images_list(age_files_list_MORPH, k=select_k_images_newid)

select_k_images_seenid = len(age_files_list_MORPH)
age_files_list_MORPH, age_files_list_MORPH_seenid = MORPH_select_k_images_list(age_files_list_MORPH, k=select_k_images_seenid, replacement=True)

#counter = 0
#for subdir in age_files_dict_MORPH.keys():
#    counter += age_files_dict_MORPH[subdir][0]
#print "age_files_dict_MORPH contains %d images"%counter
#counter = 0
#for subdir in age_files_dict_MORPH_seenid.keys():
#    counter += age_files_dict_MORPH_seenid[subdir][0]
#print "age_files_dict_MORPH_seenid contains %d images"%counter
#counter = 0
#for subdir in age_files_dict_MORPH_out.keys():
#    counter += age_files_dict_MORPH_out[subdir][0]
#print "age_files_dict_MORPH_out (LKO) contains %d images"%counter

age_labeled_files_list_MORPH = append_GT_labels_to_files(age_files_list_MORPH, age_all_labels_map_MORPH, select_races=[-2,-1,0,1,2], verbose=True)
age_labeled_files_list_MORPH_seenid = append_GT_labels_to_files(age_files_list_MORPH_seenid, age_all_labels_map_MORPH, select_races=[-2,-1,0,1,2], verbose=True)
#age_labeled_files_list_MORPH_seenid = age_labeled_files_list_MORPH #WARNING!!!!!
age_labeled_files_list_MORPH_out = append_GT_labels_to_files(age_files_list_MORPH_out, age_all_labels_map_MORPH, select_races=[-2,-1,0,1,2], verbose=True)

print "age_labeled_files_list_MORPH contains %d images"%len(age_labeled_files_list_MORPH)
print "age_labeled_files_list_MORPH_seenid contains %d images"%len(age_labeled_files_list_MORPH_seenid)
print "age_labeled_files_list_MORPH_out contains %d images"%len(age_labeled_files_list_MORPH_out)

print "age_labeled_files_list_MORPH_seenid[0,1,2]=", age_labeled_files_list_MORPH_seenid[0], age_labeled_files_list_MORPH_seenid[1], age_labeled_files_list_MORPH_seenid[2]

# # if option_setup_CNN: #just to speed this up
# #     pre_repetitions=1
# #     age_trim_number_MORPH = (pre_repetitions*1075)
# # else:
# #     pre_repetitions = 4 #4
# #     age_trim_number_MORPH = (pre_repetitions*1075)
# #     age_trim_number_MORPH = (pre_repetitions*1250) #When replacement=True in seenid selection from training and L1K0
# #     #age_trim_number_MORPH = (pre_repetitions*1180) #When replacement=True in seenid selection from training and L2K0
# #     
#pre_repetitions = 1
#age_trim_number_MORPH = (pre_repetitions*1250) #When replacement=True in seenid selection from training
 
num_clusters_MORPH_serial = 32
age_trim_number_MORPH = None

#print "age_labeled_files_list_INIBilder", age_labeled_files_list_INIBilder
#age_trim_number_MORPH = 200
age_clusters_MORPH = age_cluster_labeled_files(age_labeled_files_list_MORPH, repetition=2, num_clusters=num_clusters_MORPH_serial, trim_number=None, shuffle_each_cluster=False) #r=5, r=6, trim_number=None
#age_clusters_MORPH = age_cluster_list(age_files_dict_MORPH, repetition=pre_repetitions, smallest_number_images=age_trim_number_MORPH, largest_number_images=age_trim_number_MORPH) #Cluster so that all clusters have size at least 1400 or 1270 for L1KPO
print "len(age_clusters_MORPH)=", len(age_clusters_MORPH)
num_images_per_cluster_used_MORPH = age_clusters_MORPH[0][0]
#len(age_labeled_files_list_MORPH) / num_clusters_MORPH_serial

print "num_images_per_cluster_used_MORPH=", num_images_per_cluster_used_MORPH
#age_clusters_MORPH = cluster_to_labeled_samples(age_clusters_MORPH, trim_number=age_trim_number_MORPH)

age_clusters_MORPH_seenid = age_cluster_labeled_files(age_labeled_files_list_MORPH_seenid, repetition=1, num_clusters=1, trim_number=None, shuffle_each_cluster=False) #trim_number=None
#age_clusters_MORPH_seenid = age_cluster_list(age_files_dict_MORPH_seenid, repetition=1, smallest_number_images=800000, largest_number_images=None) #A single cluster for all images, WARNING, was 800000!!!!
#age_clusters_MORPH_seenid = cluster_to_labeled_samples(age_clusters_MORPH_seenid, trim_number=None, shuffle_each_cluster=False)

age_clusters_MORPH_out = age_cluster_labeled_files(age_labeled_files_list_MORPH_out, repetition=1, num_clusters=1, trim_number=None, shuffle_each_cluster=False) #trim_number=None
#age_clusters_MORPH_out = age_cluster_list(age_files_dict_MORPH_out, smallest_number_images=800000) #A single cluster for all images
#age_clusters_MORPH_out = cluster_to_labeled_samples(age_clusters_MORPH_out, trim_number=None, shuffle_each_cluster=False)

if len(age_clusters_MORPH_seenid) > 0:
    num_images_per_cluster_used_MORPH_seenid =  age_clusters_MORPH_seenid[0][0]
else:
    print "???"
    quit()
    num_images_per_cluster_used_MORPH_seenid = 0
print "num_images_per_cluster_used_MORPH_seenid=", num_images_per_cluster_used_MORPH_seenid


if len(age_clusters_MORPH_out) > 0:
    num_images_per_cluster_used_MORPH_out =  age_clusters_MORPH_out[0][0]
else:
    num_images_per_cluster_used_MORPH_out = 0
print "num_images_per_cluster_used_MORPH_out=", num_images_per_cluster_used_MORPH_out


numpy.random.seed(experiment_seed+123123)
#min_cluster_size_FGNet = 5000 # 32 #5000
#max_cluster_size_FGNet = None # 32 #None
if age_use_RGB_images:
    age_eyes_normalized_base_dir_FGNet = "/local/escalafl/Alberto/FGNet/FGNet_normalizedEyesZ4_horiz_RGB_2015_08_25"
else:
    age_eyes_normalized_base_dir_FGNet = "/local/escalafl/Alberto/FGNet/FGNet_normalizedEyesZ4_horiz_2015_08_25"
subdirs_FGNet=None
subdirs_FGNet=["%d"%i for i in range(16, 77)] #70 77 #OBSOLETE: all images are in a single directory

age_files_list_FGNet = list_available_images(age_eyes_normalized_base_dir_FGNet, from_subdirs=None, verbose=False)
#age_files_dict_FGNet = find_available_images(age_eyes_normalized_base_dir_FGNet, from_subdirs=subdirs_FGNet) #change from_subdirs to select a subset of all ages!

age_labeled_files_list_FGNet = append_GT_labels_to_files(age_files_list_FGNet, age_all_labels_map_FGNet, min_age=15.99*DAYS_IN_A_YEAR, max_age = 77.01*DAYS_IN_A_YEAR, verbose=True)
#age_clusters_FGNet = age_cluster_list(age_files_dict_FGNet, smallest_number_images=min_cluster_size_FGNet) #Cluster so that all clusters have size at least 1400 
#print "******************"
#print len(age_clusters_FGNet), age_clusters_FGNet[0], ":)"
#print "******************"

age_clusters_FGNet = age_cluster_labeled_files(age_labeled_files_list_FGNet, repetition=1, num_clusters=1, trim_number=None, shuffle_each_cluster=False)
#age_clusters_FGNet = cluster_to_labeled_samples(age_clusters_FGNet, trim_number=max_cluster_size_FGNet)

if len(age_clusters_FGNet) > 0:
    num_images_per_cluster_used_FGNet =  age_clusters_FGNet[0][0]
else:
    num_images_per_cluster_used_FGNet = 0
#print "******************"
#print len(age_clusters_FGNet), age_clusters_FGNet[0], ":)"
#print "******************"
print "num_images_per_cluster_used_FGNet=", num_images_per_cluster_used_FGNet
#quit()



numpy.random.seed(experiment_seed+432432432)
#age_trim_number_INIBilder = None
if age_use_RGB_images:
    age_eyes_normalized_base_dir_INIBilder = "/local/escalafl/Alberto/INIBilder/INIBilder_normalizedEyesZ4_horiz_RGB"
else:
    age_eyes_normalized_base_dir_INIBilder = "/local/escalafl/Alberto/INIBilder/INIBilder_normalizedEyesZ4_horiz_byAge"
#age_files_dict_INIBilder = find_available_images(age_eyes_normalized_base_dir_INIBilder, from_subdirs=None) #change from_subdirs to select a subset of all ages!
#age_clusters_INIBilder = age_cluster_list(age_files_dict_INIBilder, smallest_number_images=age_trim_number_INIBilder) #Cluster so that all clusters have size at least 1400 
#age_clusters_INIBilder = cluster_to_labeled_samples(age_clusters_INIBilder, trim_number=age_trim_number_INIBilder, shuffle_each_cluster=False) 
age_files_list_INIBilder = list_available_images(age_eyes_normalized_base_dir_INIBilder, from_subdirs=None, verbose=False)
#print "age_files_list_INIBilder=",age_files_list_INIBilder
age_labeled_files_list_INIBilder = append_GT_labels_to_files(age_files_list_INIBilder, age_all_labels_map_INI)
#print "age_labeled_files_list_INIBilder", age_labeled_files_list_INIBilder
age_clusters_INIBilder = age_cluster_labeled_files(age_labeled_files_list_INIBilder, repetition=1, num_clusters=1, trim_number=None, shuffle_each_cluster=False)


if len(age_clusters_INIBilder) > 0:
    num_images_per_cluster_used_INIBilder =  age_clusters_INIBilder[0][0]
else:
    num_images_per_cluster_used_INIBilder = 0
print "num_images_per_cluster_used_INIBilder=", num_images_per_cluster_used_INIBilder
#quit()

numpy.random.seed(experiment_seed+654654654)
age_trim_number_MORPH_FGNet = 1400
if age_use_RGB_images:
    age_eyes_normalized_base_dir_MORPH_FGNet = "/local/escalafl/Alberto/MORPH_FGNet_normalizedEyesZ3_horiz_ByAge"
else:
    age_eyes_normalized_base_dir_MORPH_FGNet = "/local/escalafl/Alberto/MORPH_FGNet_normalizedEyesZ3_horiz"
age_files_dict_MORPH_FGNet = find_available_images(age_eyes_normalized_base_dir_MORPH_FGNet, from_subdirs=None) #change from_subdirs to select a subset of all ages!
age_clusters_MORPH_FGNet = age_cluster_list(age_files_dict_MORPH_FGNet, smallest_number_images=age_trim_number_MORPH_FGNet) #Cluster so that all clusters have size at least 1400 
age_clusters_MORPH_FGNet = cluster_to_labeled_samples(age_clusters_MORPH_FGNet, trim_number=age_trim_number_MORPH_FGNet)
if len(age_clusters_MORPH_FGNet) > 0:
    num_images_per_cluster_used_MORPH_FGNet =  age_clusters_MORPH_FGNet[0][0]
else:
    num_images_per_cluster_used_MORPH_FGNet = 0
print "num_images_per_cluster_used_MORPH_FGNet=", num_images_per_cluster_used_MORPH_FGNet

################################################ CRUCIAL FOR MCNN TESTING ################
#age_all_labels_map = load_GT_labels("/local/escalafl/Alberto/MORPH_setsS1S2S3_seed12345/GT_MORPH_AgeRAgeGenderRace.txt", age_included=True, rAge_included=True, gender_included=True, race_included=True, avgColor_included=False)

numpy.random.seed(experiment_seed+432432432)
##pre_repetitions = 2 #16 # 24 #18 # ** 16 #2, 4, 4*4
##age_trim_number_set1 = (pre_repetitions*250)

MORPH_base_dir = "/local/escalafl/Alberto/MORPH_splitted_GUO_2015_09_02/"
#MORPH_base_dir = "/local/escalafl/Alberto/MORPH_setsS1S2S3_seed12345/"   #WARNING!!!
if age_use_RGB_images:
    age_eyes_normalized_base_dir_set1 = "/local/escalafl/Alberto/MORPH_splitted_GUO_2015_09_02/nonexistent"
else:
    age_eyes_normalized_base_dir_set1 = MORPH_base_dir + "Fs1" #F s 1 ot F s 2 #WARNING!
#age_files_dict_set1 = find_available_images(age_eyes_normalized_base_dir_set1, from_subdirs=None) #change from_subdirs to select a subset of all ages!
age_files_list_set1 = list_available_images(age_eyes_normalized_base_dir_set1, from_subdirs=None, verbose=False)
age_labeled_files_list_set1 = append_GT_labels_to_files(age_files_list_set1, age_all_labels_map_MORPH)
age_clusters_set1 = age_cluster_labeled_files(age_labeled_files_list_set1, repetition=22, num_clusters=32, trim_number=None, shuffle_each_cluster=False) #r=22
#age_clusters_set1 = age_cluster_labeled_files(age_labeled_files_list_set1, repetition=16, num_clusters=33, trim_number=None, shuffle_each_cluster=False)
  
#age_clusters_set1 = age_cluster_list(age_files_dict_set1, repetition=pre_repetitions, smallest_number_images=age_trim_number_set1, largest_number_images=age_trim_number_set1) #Cluster so that all clusters have size at least 1400 
#age_clusters_set1 = cluster_to_labeled_samples(age_clusters_set1, trim_number=age_trim_number_set1, shuffle_each_cluster=True) 
if len(age_clusters_set1) > 0:
    num_images_per_cluster_used_set1 =  age_clusters_set1[0][0]
else:
    num_images_per_cluster_used_set1 =  0   
print "num_images_per_cluster_used_set1=", num_images_per_cluster_used_set1
print "num clusters: ", len(age_clusters_set1)
#print "len(age_files_dict_set1)=", len(age_files_dict_set1)

if age_use_RGB_images:
    age_eyes_normalized_base_dir_set1b = "/local/escalafl/Alberto/MORPH_setsS1S2S3_seed12345/nonexistent/s1_byAge_mcnn"
else:
    age_eyes_normalized_base_dir_set1b = MORPH_base_dir + "Fs1"
#age_files_dict_set1b = find_available_images(age_eyes_normalized_base_dir_set1b, from_subdirs=None) #change from_subdirs to select a subset of all ages!
age_files_list_set1b = list_available_images(age_eyes_normalized_base_dir_set1b, from_subdirs=None, verbose=False)
age_labeled_files_list_set1b = append_GT_labels_to_files(age_files_list_set1b, age_all_labels_map_MORPH, select_races=[-2,-1,0,1,2], verbose=True)
age_clusters_set1b = age_cluster_labeled_files(age_labeled_files_list_set1b, repetition=3, num_clusters=1, trim_number=None, shuffle_each_cluster=False) #r=3
#age_clusters_set1b = age_cluster_labeled_files(age_labeled_files_list_set1b, repetition=2, num_clusters=1, trim_number=None, shuffle_each_cluster=False)


#print "len(age_files_dict_set1b)=", len(age_files_dict_set1b)
#pre_repetitions = 2 # 2
#age_clusters_set1b = age_cluster_list(age_files_dict_set1b, repetition=pre_repetitions, smallest_number_images=800000, largest_number_images=None) #Cluster so that all clusters have size at least 1400 
#age_clusters_set1b = cluster_to_labeled_samples(age_clusters_set1b, trim_number=None, shuffle_each_cluster=True) 
if len(age_clusters_set1b) > 0:
    num_images_per_cluster_used_set1b =  age_clusters_set1b[0][0]
else:
    num_images_per_cluster_used_set1b =  0   
print "num_images_per_cluster_used_set1b=", num_images_per_cluster_used_set1b


#pre_repetitions = 1 
if age_use_RGB_images:
    age_eyes_normalized_base_dir_set1test = "/local/escalafl/Alberto/MORPH_setsS1S2S3_seed12345/s1-test_byAge_mcnn/nonexistent"
else:
    age_eyes_normalized_base_dir_set1test = MORPH_base_dir + "Fs1-test" # s2-test_byAge_mcnn2
    #age_files_dict_set1test = find_available_images(age_eyes_normalized_base_dir_set1test, from_subdirs=None) #change from_subdirs to select a subset of all ages!
age_files_list_set1test = list_available_images(age_eyes_normalized_base_dir_set1test, from_subdirs=None, verbose=False)
age_labeled_files_list_set1test = append_GT_labels_to_files(age_files_list_set1test, age_all_labels_map_MORPH, select_races=[-2,-1,0,1,2], verbose=True)
age_clusters_set1test = age_cluster_labeled_files(age_labeled_files_list_set1test, repetition=1, num_clusters=1, trim_number=None, shuffle_each_cluster=False)

#age_clusters_set1test = age_cluster_list(age_files_dict_set1test, repetition=1, smallest_number_images=800000, largest_number_images=None) #Cluster so that all clusters have size at least 1400 
#age_clusters_set1test = cluster_to_labeled_samples(age_clusters_set1test, trim_number=None, shuffle_each_cluster=False) 
if len(age_clusters_set1test) > 0:
    num_images_per_cluster_used_set1test =  age_clusters_set1test[0][0]
else:
    num_images_per_cluster_used_set1test =  0   
print "num_images_per_cluster_used_set1test=", num_images_per_cluster_used_set1test

numpy.random.seed(experiment_seed+987987987)
if option_setup_CNN==0: #MY MORPH SETUP
    age_clusters = age_clusters_MORPH  #_MORPH #_FGNet
    age_clusters_seenid = age_clusters_MORPH_seenid
    age_clusters_newid = age_clusters_MORPH_out
    
    age_eyes_normalized_base_dir_train = age_eyes_normalized_base_dir_MORPH
    age_eyes_normalized_base_dir_seenid = age_eyes_normalized_base_dir_MORPH
    age_eyes_normalized_base_dir_newid = age_eyes_normalized_base_dir_MORPH
elif option_setup_CNN==1: #CNN SETUP
    age_clusters = age_clusters_set1  #_MORPH #_FGNet
    age_clusters_seenid = age_clusters_set1b
    age_clusters_newid = age_clusters_set1test
    
#    age_trim_number_MORPH = num_images_per_cluster_used_set1 #age_trim_number_set1
    num_images_per_cluster_used_MORPH = num_images_per_cluster_used_set1
    num_images_per_cluster_used_MORPH_seenid = num_images_per_cluster_used_set1b
    num_images_per_cluster_used_MORPH_out = num_images_per_cluster_used_set1test
    #age_clusters_newid = age_clusters_set1b #WARNING!!!
    #num_images_per_cluster_used_MORPH_out = 15000 #num_images_per_cluster_used_set1b #WARNING!!!

    age_eyes_normalized_base_dir_train = MORPH_base_dir + "Fs1"
    age_eyes_normalized_base_dir_seenid = MORPH_base_dir + "Fs1"
    age_eyes_normalized_base_dir_newid = MORPH_base_dir + "Fs1-test" #s2-test_byAge_mcnn
       
    if num_images_per_cluster_used_set1 == 0:
        ex = "error: num_images_per_cluster_used_set1 = 0"
        raise Exception(ex)
    if num_images_per_cluster_used_set1b == 0:
        ex = "error: num_images_per_cluster_used_set1b = 0"
        raise Exception(ex)
    if num_images_per_cluster_used_set1test == 0:
        ex = "error: num_images_per_cluster_used_set1test = 0"
        raise Exception(ex)
    #quit()
age_all_labels_map_newid = age_all_labels_map_MORPH

print "age_eyes_normalized_base_dir_newid=", age_eyes_normalized_base_dir_newid

verbose=False or True
if verbose:
    print "num clusters =", len(age_clusters)
    for age_cluster in age_clusters:
        print "avg_label=%f, num_images=%d"%(age_cluster[1], age_cluster[0]), 
        print "filenames[0]=", age_cluster[2][0], 
        print "orig_labels[0]=", age_cluster[3][0],
        print "filenames[-1]=", age_cluster[2][-1],
        print "orig_labels[0]=", age_cluster[3][-1]
#quit()
if leave_k_out_MORPH > 0 and len(age_clusters) != 30 and len(age_clusters)!=0 and False: #WARNING! 33 clusters now!
    er = "leave_k_out_MORPH is changing the number of clusters (%d clusters instead of 30)"%len(age_clusters)
    raise Exception(er)

use_seenid_classes_to_generate_knownid_and_newid_classes = True #and False #WARNING

if option_setup_CNN==0: #WARNING!!!!!  ERROR!!! #MY MORPH SETUP, eventually use only one setup? why, nooo! # warning!!!
    base_scale = 1.14 #1.155 # 1.125 # 1.14 * (37.5/37.0) #1.14  #* 1.1 #*0.955 #*1.05 # 1.14 WARNING!!!
    factor_training = 1.03573 #1.04 #1.03573 (article) # 1.032157 #1.0393 # 1.03573
    factor_seenid = 1.01989 #1.021879 #1.018943  #1.020885         # 1.01989  
    scale_offset = 0.00 #0.08 0.04  
    delta_rotation = 2.0 #** 2.0 #2.0
    factor_rotation = 1.65 / 3.0
    delta_pos = 1.0 # ** 1.0 #1.2 #0.75 #eedit
    factor_pos = 0.5
    obj_avg_std = 0.0 # ** 0.0
    obj_std_base = 0.16 # ** 0.16
    obj_std_dif = 0.01 #WARNING! # ** 0.00
    
    obj_std_min=obj_std_base-obj_std_dif # ** 0.16
    obj_std_max=obj_std_base+obj_std_dif # ** 0.16    
else: #GUO MORPH SETUP
    #0.825 #0.55 # 1.1
    #smin=0.575, smax=0.625 (orig images) 
    # (zoomed images)     
    # smin=1.25, smax=1.40, 1.325
    base_scale = 1.14 #1.155 # 1.125 # 1.14 * (37.5/37.0) #1.14  #* 1.1 #*0.955 #*1.05 # 1.14 WARNING!!!
    factor_training = 1.04 # 1.04! #*** 1.03573 #1.04 #1.03573 (article) # 1.032157 #1.0393 # 1.03573
    factor_seenid = 1.01989 #1.021879 #1.018943  #1.020885         # 1.01989  
    scale_offset = 0.00 #0.08 0.04  
    delta_rotation = 2.0 #** 2.0 #2.0
    factor_rotation = 1.65 / 3.0
    delta_pos = 2.3 #2.5! # ** 1.0 #1.2 #0.75 #eedit
    factor_pos = 0.5
    obj_avg_std = 0.165 #0.17! # ** 0.0
    obj_std_base = 0.16 # ** 0.16
    obj_std_dif = 0.081 #0.096! # ** 0.00 #WARNING!!! WHY min can be smaller than zero???!!!
    
    obj_std_min=obj_std_base - obj_std_dif # ** 0.16
    obj_std_max=obj_std_base + obj_std_dif # ** 0.16

obj_avg_std_seenid = obj_avg_std * 0.0
obj_std_dif_seenid = obj_std_dif * 0.0
obj_std_min_seenid = obj_std_base - obj_std_dif_seenid # ** 0.16
obj_std_max_seenid = obj_std_base + obj_std_dif_seenid # ** 0.16

#0.825 #0.55 # 1.1
#smin=0.575, smax=0.625 (orig images) 
# (zoomed images)   
# smin=1.25, smax=1.40, 1.325
###base_scale = 1.14 #1.155 # 1.125 # 1.14 * (37.5/37.0) #1.14  #* 1.1 #*0.955 #*1.05 # 1.14 WARNING!!!
###factor_training = 1.03573 #1.04 #1.03573 (article) # 1.032157 #1.0393 # 1.03573
###factor_seenid = 1.01989 #1.021879 #1.018943  #1.020885         # 1.01989  
###scale_offset = 0.00 #0.08 0.04  
###delta_rotation = 2.0 #2.0
###factor_rotation = 1.65 / 3.0
###delta_pos = 1.0 #1.0 #1.2 #0.75 #eedit
###factor_pos = 0.5

print "Randomization parameters base_scale=%f, factor_training=%f, factor_seenid=%f, scale_offset=%f"%(base_scale, factor_training, factor_seenid, scale_offset)
print "Randomization parameters delta_rotation=%f, factor_rotation=%f, delta_pos=%f, factor_pos=%f"%(delta_rotation, factor_rotation, delta_pos, factor_pos)  

# if leave_k_out_MORPH == 1000:
#     extra_images_LKO_train = (age_trim_number_MORPH - 1200)*2/3 # (1270-1200)=70, 70/3 = 23
#     extra_images_LKO_seenid = (age_trim_number_MORPH - 1200)/3
#     images_after_LKO_train = 1075 + extra_images_LKO_train # (1270-1200)=70, 70/3 = 23
#     images_after_LKO_seenid = 125 + extra_images_LKO_seenid
#     print "Effective number of images for Train appears to be:", images_after_LKO_train
#     print "Effective number of images for SeenId appears to be:", images_after_LKO_seenid
# elif leave_k_out_MORPH == 2000:
#     extra_images_LKO_train = (age_trim_number_MORPH - 1100)*2/3 # (1270-1200)=70, 70/3 = 23
#     extra_images_LKO_seenid = (age_trim_number_MORPH - 1100)/3
#     images_after_LKO_train = 975 + extra_images_LKO_train # (1270-1200)=70, 70/3 = 23
#     images_after_LKO_seenid = 125 + extra_images_LKO_seenid
#     print "Effective number of images for Train appears to be:", images_after_LKO_train
#     print "Effective number of images for SeenId appears to be:", images_after_LKO_seenid
# 
# else:
#     images_after_LKO_train = 1075 # (1270-1200)=70, 70/3 = 23
#     images_after_LKO_seenid = 125

#DEFINITIVE:
#128x128: iSeq_set = iTrainRAge = [[iSeqCreateRAge(dx=0.0, dy=0.0, smin=1.275, smax=1.375, delta_rotation=3.0, pre_mirroring="none" "duplicate", contrast_enhance=True, 
#160x160:
iSeq_set = iTrainRAge = [[iSeqCreateRAge(dx=delta_pos, dy=delta_pos, smin=(base_scale+scale_offset) / factor_training, smax=(base_scale+scale_offset) * factor_training, delta_rotation=delta_rotation, pre_mirroring="none", contrast_enhance=True, #WARNING!!! pre_mirroring="none"
#-0.05
#192x192: iSeq_set = iTrainRAge = [[iSeqCreateRAge(dx=0.0, dy=0.0, smin=0.85+scale_offset, smax=0.91666+scale_offset, delta_rotation=3.0, pre_mirroring="none", contrast_enhance=True, 
                                         obj_avg_std=obj_avg_std, obj_std_min=obj_std_min, obj_std_max=obj_std_max, new_clusters=age_clusters, num_images_per_cluster_used=num_images_per_cluster_used_MORPH,  #=>=>=>1075 #1000 #1000, 900=>27000
                                         images_base_dir=age_eyes_normalized_base_dir_train, first_image_index=0, repetition_factor=1, seed=-1, use_orig_label_as_class=False, use_orig_label=True)]] #repetition_factor=8 (article 8), 6 or at least 4 #T: dx=2, dy=2, smin=1.25, smax=1.40, repetition_factor=5
#Experimental: 
#iSeq_set = iTrainRAge = [[iSeqCreateRAge(dx=0, dy=0, smin=1.0, smax=1.0, delta_rotation=0.0, pre_mirroring="none", contrast_enhance=True, 
#                                         obj_avg_std=0.00, obj_std_min=0.20, obj_std_max=0.20, clusters=age_clusters, num_images_per_cluster_used=1000,  #1000 #1000, 900=>27000
#                                         images_base_dir=age_eyes_normalized_base_dir, first_image_index=0, repetition_factor=1, seed=-1, use_orig_label=True)]] #repetition_factor=6 or at least 4 #T: dx=2, dy=2, smin=1.25, smax=1.40, repetition_factor=5
sSeq_set = sTrainRAge = [[sSeqCreateRAge(iSeq_set[0][0], seed=-1, use_RGB_images=age_use_RGB_images)]]



#MORPH+FGNet
#iSeq_set = iTrainRAge = [[iSeqCreateRAge(dx=2, dy=2, smin=1.25, smax=1.40, clusters=age_clusters, num_images_per_cluster_used=num_images_per_cluster_used_MORPH_FGNet,  #1000 =>30000, 900=>27000
#                                         images_base_dir=age_eyes_normalized_base_dir, first_image_index=0, repetition_factor=5, seed=-1, use_orig_label=False)]] #rep=5
#sSeq_set = sTrainRAge = [[sSeqCreateRAge(iSeq_set[0][0], seed=-1)]] 
#smin=0.595, smax=0.605 (orig images)
#128x128: iSeq_set = iSeenidRAge = iSeqCreateRAge(dx=0.0, dy=0.0, smin=1.3, smax=1.35, delta_rotation=1.5, pre_mirroring="none", contrast_enhance=True, 160x160: WARNING!!! WHY OBJ_STD_MIN/MAX is fixed???
#WARNING! USED age_clusters instead of age_clusters_seenid
iSeq_set = iSeenidRAge = iSeqCreateRAge(dx=delta_pos * factor_pos, dy=delta_pos * factor_pos, smin=(base_scale+scale_offset) / factor_seenid, smax=(base_scale+scale_offset) * factor_seenid, delta_rotation=delta_rotation*factor_rotation, pre_mirroring="none", contrast_enhance=True, 
#192x192:iSeq_set = iSeenidRAge = iSeqCreateRAge(dx=0.0, dy=0.0, smin=0.86667+scale_offset, smax=0.9+scale_offset, delta_rotation=1.5, pre_mirroring="none", contrast_enhance=True, 
                                        obj_avg_std=obj_avg_std_seenid, obj_std_min=obj_std_min_seenid, obj_std_max=obj_std_max_seenid,new_clusters=age_clusters_seenid, num_images_per_cluster_used=num_images_per_cluster_used_MORPH_seenid, #125+extra_images_LKO_third  #200 #300=>9000
                                        images_base_dir=age_eyes_normalized_base_dir_seenid, first_image_index=0, repetition_factor=1, seed=-1,  #repetition_factor= 6 (article 6), 12,8,4
                                        use_orig_label_as_class=use_seenid_classes_to_generate_knownid_and_newid_classes and False, use_orig_label=True) #repetition_factor=8, 4 #T=repetition_factor=3
sSeq_set = sSeenidRAge = sSeqCreateRAge(iSeq_set, seed=-1, use_RGB_images=age_use_RGB_images)
###Testing Original MORPH:
#128x128: iSeq_set = iNewidRAge = [[iSeqCreateRAge(dx=0, dy=0, smin=1.325, smax=1.326, delta_rotation=0.0, pre_mirroring="none", contrast_enhance=True, 
#192x192: 
#iSeq_set = iNewidRAge = [[iSeqCreateRAge(dx=0, dy=0, smin=0.8833+scale_offset, smax=0.8833+scale_offset, delta_rotation=0.0, pre_mirroring="none", contrast_enhance=True, 
#160x160: use_orig_label_as_class 
#TODO:get rid of this conditional. Add Leave-k-out for MORPH+FGNet
testing_INIBilder = (num_images_per_cluster_used_INIBilder > 0) and False
testing_FGNet = True and False
if (not testing_INIBilder) and (not testing_FGNet): 
    if leave_k_out_MORPH==0 and option_setup_CNN==0:
        print "Selecting NewId without using leave_k_out_strategy" ###WARNING!!!! HERE 0.16 instead of 0.2 should be used???
        iSeq_set = iNewidRAge = [[iSeqCreateRAge(dx=0, dy=0, smin=(base_scale+scale_offset), smax=(base_scale+scale_offset), delta_rotation=0.0, pre_mirroring="none", contrast_enhance=True, 
                                                 obj_avg_std=0.0, obj_std_min=obj_std_base, obj_std_max=obj_std_base, new_clusters=age_clusters, num_images_per_cluster_used=200,   #200=>6000 pre_mirroring="none"
                                                 images_base_dir=age_eyes_normalized_base_dir_newid, first_image_index=1200, repetition_factor=1, seed=-1, use_orig_label_as_class=False, use_orig_label=True,increasing_orig_label=True)]]
    else:
        print "Selecting NewId data using leave_k_out_strategy, with k=", leave_k_out_MORPH
        iSeq_set = iNewidRAge = [[iSeqCreateRAge(dx=0, dy=0, smin=(base_scale+scale_offset), smax=(base_scale+scale_offset), delta_rotation=0.0, pre_mirroring="none", contrast_enhance=True, 
                                                 obj_avg_std=0.0, obj_std_min=obj_std_base, obj_std_max=obj_std_base, new_clusters=age_clusters_newid, num_images_per_cluster_used=num_images_per_cluster_used_MORPH_out,   #200=>6000
                                                 images_base_dir=age_eyes_normalized_base_dir_newid, first_image_index=0, repetition_factor=1, seed=-1, use_orig_label_as_class=False, use_orig_label=True, increasing_orig_label=True)]]
    sSeq_set = sNewidRAge = [[sSeqCreateRAge(iSeq_set[0][0], seed=-1, use_RGB_images=age_use_RGB_images)]]


#iSeenidRAge = iTrainRAge[0][0]
#sSeenidRAge = sTrainRAge[0][0]
#iNewidRAge = iTrainRAge
#sNewidRAge = sTrainRAge
#Testing with INI Bilder:
if testing_INIBilder:
    print "Using INI Bilder for testing"
    iSeq_set = iNewidRAge = [[iSeqCreateRAge(dx=0, dy=0, smin=(base_scale+scale_offset), smax=(base_scale+scale_offset), delta_rotation=0.0, pre_mirroring="none", contrast_enhance=True, #pre_mirroring="none",
                                             obj_avg_std=0.0, obj_std_min=obj_std_base, obj_std_max=obj_std_base, new_clusters=age_clusters_INIBilder, num_images_per_cluster_used=num_images_per_cluster_used_INIBilder,   
                                             images_base_dir=age_eyes_normalized_base_dir_INIBilder, first_image_index=0, repetition_factor=1, seed=-1, use_orig_label_as_class=False, use_orig_label=True)]]
    sSeq_set = sNewidRAge = [[sSeqCreateRAge(iSeq_set[0][0], seed=-1, use_RGB_images=age_use_RGB_images)]]
    age_all_labels_map_newid = age_all_labels_map_INI
#Testing with FGNet:
if testing_FGNet:
    print "Using FGNet for testing"
    iSeq_set = iNewidRAge = [[iSeqCreateRAge(dx=0, dy=0, smin=(base_scale+scale_offset), smax=(base_scale+scale_offset), delta_rotation=0.0, pre_mirroring="none", contrast_enhance=True,
                                             obj_avg_std=0.0, obj_std_min=obj_std_base, obj_std_max=obj_std_base, new_clusters=age_clusters_FGNet, num_images_per_cluster_used=num_images_per_cluster_used_FGNet,  
                                             images_base_dir=age_eyes_normalized_base_dir_FGNet, first_image_index=0, repetition_factor=1, seed=-1, use_orig_label_as_class=False, use_orig_label=True, increasing_orig_label=True)]]
    sSeq_set = sNewidRAge = [[sSeqCreateRAge(iSeq_set[0][0], seed=-1, use_RGB_images=age_use_RGB_images)]]
    age_all_labels_map_newid = age_all_labels_map_FGNet

ParamsRAgeFunc = SystemParameters.ParamsSystem()
ParamsRAgeFunc.name = "Function Based Data Creation for RAge"
ParamsRAgeFunc.network = "linearNetwork4L" #Default Network, but ignored
ParamsRAgeFunc.iTrain = iTrainRAge
ParamsRAgeFunc.sTrain = sTrainRAge

ParamsRAgeFunc.iSeenid = iSeenidRAge
ParamsRAgeFunc.sSeenid = sSeenidRAge

ParamsRAgeFunc.iNewid = iNewidRAge
ParamsRAgeFunc.sNewid = sNewidRAge

if iTrainRAge != None and iTrainRAge[0][0]!=None:
    ParamsRAgeFunc.block_size = iTrainRAge[0][0].block_size
ParamsRAgeFunc.train_mode = "Weird Mode" #Ignored for the moment 
ParamsRAgeFunc.analysis = None
ParamsRAgeFunc.enable_reduced_image_sizes = True
ParamsRAgeFunc.reduction_factor = 160.0/96 #160.0/72 ## 160.0/96 # (article 2.0) T=2.0 WARNING 1.0, 2.0, 4.0, 8.0
ParamsRAgeFunc.hack_image_size = 96 #72 ## 96 # (article 80) # T=80 T=64 WARNING  96, 80, 128,  64,  32 , 16
ParamsRAgeFunc.enable_hack_image_size = True
ParamsRAgeFunc.patch_network_for_RGB = False #

#print sTrainRAge[0][0].translations_x
#print sSeenidRAge.translations_x
#print sNewidRAge[0][0].translations_x
#quit()

#TODO:This code seems broken, fix it!
if iSeenidRAge != None:
    all_classes = numpy.unique(iSeenidRAge.correct_classes)
    min_num_classes = 7 #40
    max_num_classes = 42 #42

    num_classes = len(all_classes)
    print "Updating num_classes in Seenid. Originally %d classes. Afterwards at least %d and at most %d."%(num_classes, min_num_classes, max_num_classes)

    if min_num_classes > num_classes:
        ex = "insufficient number of classes in seenid data: %d >= %d "%(min_num_classes, num_classes)
        raise Exception(ex)

    smallest_number_of_samples_per_class = 30
    class_list = list(all_classes) #This is the actual mapping from orig. classes to final classes
    #print "Original class list: ", class_list
    num_classes = len(class_list)
    factor_increment_samples = 1.1
    
    if num_classes > 1000:
        print "using optimized parameters for faster class partitioning for Seenid"
        min_num_classes = max_num_classes = 39 
        smallest_number_of_samples_per_class = len(iSeenidRAge.correct_classes) / (max_num_classes+0.3) #780
        factor_increment_samples = 1.02
    while num_classes > max_num_classes:
        current_count = 0
        current_class = 0
        class_list = []
        for classnr in all_classes: #[::-1]:
            class_list.append(current_class)
            current_count += (iSeenidRAge.correct_classes==classnr).sum()    
            if current_count >= smallest_number_of_samples_per_class:
                current_count = 0
                current_class += 1
        if current_count >= smallest_number_of_samples_per_class:
            print "last class cluster is fine"
        elif current_count > 0:
            print "fixing last class cluster by adding it to its predecesor"
            class_list = numpy.array(class_list)
            class_list[class_list == current_class] = current_class-1
        num_classes = len(numpy.unique(class_list))
        print "In iteration with smallest_number_of_samples_per_class=%d, we have %d clases"%(smallest_number_of_samples_per_class,num_classes)
        smallest_number_of_samples_per_class = factor_increment_samples * smallest_number_of_samples_per_class + 1
#class_list.reverse()
#class_list = numpy.array(class_list)
#class_list = class_list.max()-class_list
    if min_num_classes > num_classes:
        ex = "Resulting number of classes %d is smaller than min_num_classes %d"%(num_classes, min_num_classes)
        raise Exception(ex)

    print "class_list=", class_list
    for i, classnr in enumerate(all_classes):
        iSeenidRAge.correct_classes[iSeenidRAge.correct_classes==classnr] = class_list[i]
#quit()        

    if use_seenid_classes_to_generate_knownid_and_newid_classes:
        print "Orig iSeenidRAge.correct_labels=", iSeenidRAge.correct_labels
        print "Orig len(iSeenidRAge.correct_labels)=", len(iSeenidRAge.correct_labels)
        print "Orig len(iSeenidRAge.correct_classes)=", len(iSeenidRAge.correct_classes)
        all_classes = numpy.unique(iSeenidRAge.correct_classes)
        print "all_classes=", all_classes
        avg_labels = more_nodes.compute_average_labels_for_each_class(iSeenidRAge.correct_classes, iSeenidRAge.correct_labels)
        print "avg_labels=", avg_labels 
        iTrainRAge[0][0].correct_classes = more_nodes.map_labels_to_class_number(all_classes, avg_labels, iTrainRAge[0][0].correct_labels)
        iNewidRAge[0][0].correct_classes = more_nodes.map_labels_to_class_number(all_classes, avg_labels, iNewidRAge[0][0].correct_labels)

        for classnr in all_classes:
            print "|class %d| = %d,"%(classnr, (iSeenidRAge.correct_classes==classnr).sum()),
    #quit()

    print "Verifying that train and test image filenames are disjoint (not verifying leave-k-out here)"
    input_files_network = set(iTrainRAge[0][0].input_files)
    input_files_supervised = set(iSeenidRAge.input_files)
    input_files_testing = set(iNewidRAge[0][0].input_files)
    intersection_network = input_files_testing.intersection(input_files_network)
    intersection_supervised = input_files_testing.intersection(input_files_supervised)
    if len(intersection_network) > 0:
        ex = "Test data and training data have %d non disjoint input images!: "%len(intersection_network)+str(intersection_network)
        raise Exception(ex)
    elif len(intersection_supervised) > 0: #WARNING!!!!
        ex = "Test data and supervised data have %d non disjoint input images!: "%len(intersection_supervised)+str(intersection_supervised)
        raise Exception(ex)
    else:
        print "Test data is disjoint to training data and supervised data"


age_add_other_label_classes = True #and False
age_multiple_labels = age_add_other_label_classes #and False 
#age_first_age_label = True and False
age_label_ordering ="AgeRaceGenderIAge"
age_ordered_by_increasing_label = 0 #0=Age,1=Race, 2=Gender
age_subordered_by_increasing_color = True and False 
append_gender_classification = True #and False
append_race_classification = True #and False

#False, *, *, * => learn only age
#True, True, True, False, True  => learn both age and skin color, age is first label and determines ordering, color determines subordering inside the clusters
#True, True, True, False, False => learn both age and skin color, age is first label and determines ordering
#True, True, True, True, False => learn both age and skin color, color is first label and determines ordering
#True, False, *, *  => learn only color

#WARNING!!!! THERE SEEMS TO BE A BUG WITH THE FUNCTION load_skin_color_labels or with python get_lines()!!!!!! Fixed by repeating first line twice!!!
if age_add_other_label_classes:
    #age_all_labels_map = load_GT_labels("/local/escalafl/Alberto/MORPH_setsS1S2S3_seed12345/GT_MORPH_AgeRAgeGenderRace.txt", age_included=True, rAge_included=True, gender_included=True, race_included=True, avgColor_included=False)
    
#     if "EyeNZ4292740_05M30.JPG" not in age_skin_color_labels_map.keys():
#         print "key EyeNZ4292740_05M30.JPG still missing 1"
#         quit()
#     else:
#         print "OK 1"
#         print 'age_skin_color_labels_map["EyeNZ4292740_05M30.JPG"] =', age_skin_color_labels_map["EyeNZ4292740_05M30.JPG"]
         
    #print "age_skin_color_labels_map= ", age_skin_color_labels_map
    print "has %d entries"%(len(age_all_labels_map_MORPH.keys()))
#    for keys in age_skin_color_labels_map.keys():
#        if keys.startswith("EyeNZ4292740"):
#            print "Key <%s><%f>"%(keys, age_skin_color_labels_map[keys])
    iAge_labels_TrainRAge = []
    rAge_labels_TrainRAge = []
    gender_labels_TrainRAge = []
    race_labels_TrainRAge = []   
    for input_file in iTrainRAge[0][0].input_files:
        input_file_short = string.split(input_file,"/")[-1]
        all_labels = age_all_labels_map_MORPH[input_file_short]
        iAge_labels_TrainRAge.append(all_labels[0]) 
        rAge_labels_TrainRAge.append(all_labels[1]) 
        gender_labels_TrainRAge.append(all_labels[2]) 
        race_labels_TrainRAge.append(all_labels[3]) 
    iAge_labels_TrainRAge = numpy.array(iAge_labels_TrainRAge).reshape((-1,1))
    rAge_labels_TrainRAge = numpy.array(rAge_labels_TrainRAge).reshape((-1,1))
    race_labels_TrainRAge = numpy.array(race_labels_TrainRAge).reshape((-1,1))
    gender_labels_TrainRAge = numpy.array(gender_labels_TrainRAge).reshape((-1,1))

#    if "EyeNZ4292740_05M30.JPG" not in age_skin_color_labels_map.keys():
#        print "key EyeNZ4292740_05M30.JPG still missing 2"
#        #quit()
#    else:
#        print "OK 2"

    iAge_labels_SeenidRAge =[]
    rAge_labels_SeenidRAge =[]
    gender_labels_SeenidRAge =[]
    race_labels_SeenidRAge =[]   
    for input_file in iSeenidRAge.input_files:
        input_file_short =  string.split(input_file,"/")[-1]
        all_labels = age_all_labels_map_MORPH[input_file_short]
        iAge_labels_SeenidRAge.append(all_labels[0])   
        rAge_labels_SeenidRAge.append(all_labels[1])   
        gender_labels_SeenidRAge.append(all_labels[2])   
        race_labels_SeenidRAge.append(all_labels[3])
    iAge_labels_SeenidRAge = numpy.array(iAge_labels_SeenidRAge).reshape((-1,1))
    rAge_labels_SeenidRAge = numpy.array(rAge_labels_SeenidRAge).reshape((-1,1))
    gender_labels_SeenidRAge = numpy.array(gender_labels_SeenidRAge).reshape((-1,1))
    race_labels_SeenidRAge = numpy.array(race_labels_SeenidRAge).reshape((-1,1))
#    if "EyeNZ4292740_05M30.JPG" not in age_skin_color_labels_map.keys():
#        print "key EyeNZ4292740_05M30.JPG still missing 3"
#        #quit()
#    else:
#        print "OK 3"
    iAge_labels_NewidRAge=[]
    rAge_labels_NewidRAge =[]
    gender_labels_NewidRAge =[]
    race_labels_NewidRAge =[]
    for input_file in iNewidRAge[0][0].input_files:
        input_file_short = string.split(input_file,"/")[-1]
#       if "EyeNZ4292740_05M30.JPG" == input_file_short:
#           print "FOUND but not found?"
#        if input_file_short in age_skin_color_labels_map.keys():
#        xx = age_skin_color_labels_map[input_file_short]
        all_labels = age_all_labels_map_newid[input_file_short]
        iAge_labels_NewidRAge.append(all_labels[0])
        rAge_labels_NewidRAge.append(all_labels[1])
        gender_labels_NewidRAge.append(all_labels[2])
        race_labels_NewidRAge.append(all_labels[3])  
#        else:
#            print "entry-", input_file_short, "not found!!!", ":("
    iAge_labels_NewidRAge = numpy.array(iAge_labels_NewidRAge).reshape((-1,1))
    rAge_labels_NewidRAge = numpy.array(rAge_labels_NewidRAge).reshape((-1,1))
    gender_labels_NewidRAge = numpy.array(gender_labels_NewidRAge).reshape((-1,1))
    race_labels_NewidRAge = numpy.array(race_labels_NewidRAge).reshape((-1,1))

    print "comparing integer age vs. int(rAge/365.242+0.0006)"
    riAge_labels_NewidRAge = (rAge_labels_NewidRAge/DAYS_IN_A_YEAR+0.0006).astype(int)
    print "riAge_labels_NewidRAge=", riAge_labels_NewidRAge.flatten()
    print "iAge_labels_NewidRAge=", iAge_labels_NewidRAge.flatten()
    print "rAge_labels_NewidRAge=", rAge_labels_NewidRAge.flatten()
    print "Same: %d"%((riAge_labels_NewidRAge == iAge_labels_NewidRAge).sum())
    print "Diff: %d"%((riAge_labels_NewidRAge != iAge_labels_NewidRAge).sum())
    indices = numpy.arange(len(iAge_labels_NewidRAge))[riAge_labels_NewidRAge.flatten() != iAge_labels_NewidRAge.flatten()]
    print "Different indices:", indices
    print "iAge[indices]=", iAge_labels_NewidRAge.flatten()[indices]
    print "riAge[indices]=", riAge_labels_NewidRAge.flatten()[indices]
    print "rAge[indices]=", rAge_labels_NewidRAge.flatten()[indices]
   
#    race_labels = race_labels_SeenidRAge.flatten()
#    sorting = numpy.argsort(race_labels)
#    num_classes = 10
#    skin_color_classes_SeenidRAge = numpy.zeros(iSeenidRAge.num_images)
#    skin_color_classes_SeenidRAge[sorting] = numpy.arange(iSeenidRAge.num_images)*num_classes/iSeenidRAge.num_images
#    avg_labels = more_nodes.compute_average_labels_for_each_class(skin_color_classes_SeenidRAge, skin_color_labels)
#    all_classes = numpy.unique(skin_color_classes_SeenidRAge)
#    print "skin color avg_labels=", avg_labels 
#    skin_color_classes_TrainRAge = more_nodes.map_labels_to_class_number(all_classes, avg_labels, skin_color_labels_TrainRAge.flatten())
#    skin_color_classes_NewidRAge = more_nodes.map_labels_to_class_number(all_classes, avg_labels, skin_color_labels_NewidRAge.flatten())

#    skin_color_classes_TrainRAge = skin_color_classes_TrainRAge.reshape((-1,1))
#    skin_color_classes_SeenidRAge = skin_color_classes_SeenidRAge.reshape((-1,1))
#    skin_color_classes_NewidRAge = skin_color_classes_NewidRAge.reshape((-1,1))

    age_classes_TrainRAge = iTrainRAge[0][0].correct_classes.reshape((-1,1))
    age_classes_SeenidRAge = iSeenidRAge.correct_classes.reshape((-1,1))
    age_classes_NewidRAge = iNewidRAge[0][0].correct_classes.reshape((-1,1))

    #TODO: FIX class assignment for rAge
    min_rAge = int(rAge_labels_SeenidRAge.min()/DAYS_IN_A_YEAR)
    max_rAge = int(rAge_labels_SeenidRAge.max()/DAYS_IN_A_YEAR)

    rAge_classes_TrainRAge = (rAge_labels_TrainRAge/DAYS_IN_A_YEAR+0.0006).astype(int)
    rAge_classes_SeenidRAge = (rAge_labels_SeenidRAge/DAYS_IN_A_YEAR+0.0006).astype(int)
    rAge_classes_NewidRAge = (rAge_labels_NewidRAge/DAYS_IN_A_YEAR+0.0006).astype(int)
   

    #race_classes_tmp = numpy.ones_like(race_labels_TrainRAge) #B=-2, O=-1, A=0, H=1, W=2
    #race_classes_tmp[race_labels_TrainRAge == -2] = 0 #B
    #race_classes_tmp[race_labels_TrainRAge == 1] = 0  #H
    #race_classes_TrainRAge = race_classes_tmp

    #race_classes_tmp = numpy.ones_like(race_labels_SeenidRAge) #B=-2, O=-1, A=0, H=1, W=2
    #race_classes_tmp[race_labels_SeenidRAge == -2] = 0 #B
    #race_classes_tmp[race_labels_SeenidRAge == 1] = 0  #H
    #race_classes_SeenidRAge = race_classes_tmp 

    #race_classes_tmp = numpy.ones_like(race_labels_NewidRAge) #B=-2, O=-1, A=0, H=1, W=2
    #race_classes_tmp[race_labels_NewidRAge == -2] = 0 #B
    #race_classes_tmp[race_labels_NewidRAge == 1] = 0  #H
    #race_classes_NewidRAge = race_classes_tmp

    race_classes_TrainRAge = (race_labels_TrainRAge + 2+3).astype(int)/4 # B=0 O=1 A=1 H=1 W=1 
    race_classes_SeenidRAge = (race_labels_SeenidRAge + 2+3).astype(int)/4
    race_classes_NewidRAge = (race_labels_NewidRAge + 2+3).astype(int)/4
    
    gender_classes_TrainRAge = gender_labels_TrainRAge.reshape((-1,1))
    gender_classes_SeenidRAge = gender_labels_SeenidRAge.reshape((-1,1))
    gender_classes_NewidRAge = gender_labels_NewidRAge.reshape((-1,1))
    
    print "average gender_labels for training data:", gender_labels_TrainRAge.mean()
    num_males_TrainRAge = (gender_classes_TrainRAge == 0).sum()
    num_females_TrainRAge = iTrainRAge[0][0].num_images - num_males_TrainRAge

    print "average race_labels for training data:", race_labels_TrainRAge.mean()
    num_BO_TrainRAge = (race_classes_TrainRAge == 0).sum()
    num_AHW_TrainRAge = (race_classes_TrainRAge == 1).sum()


age_labels_TrainRAge = rAge_labels_TrainRAge
age_labels_SeenidRAge = rAge_labels_SeenidRAge
age_classes_NewidRAge_test = iAge_labels_NewidRAge

pure_integer_years = True #and False #DEFAULT: TRUE
if pure_integer_years:
#    age_labels_TrainRAge = iAge_labels_TrainRAge
#    age_labels_SeenidRAge = iAge_labels_SeenidRAge
    print "newid/test age labels are integers (integer years coded in days)"
    age_labels_NewidRAge_test = iAge_labels_NewidRAge * DAYS_IN_A_YEAR
else:
    print "newid/test age labels are real valued (in exact number of days)"
    age_labels_NewidRAge_test = rAge_labels_NewidRAge

print "age_labels_SeenidRAge =", age_labels_SeenidRAge
print "age_labels_NewidRAge_test =", age_labels_NewidRAge_test

if age_multiple_labels==True:
    list_all_labels = [[age_labels_TrainRAge,  race_labels_TrainRAge,  gender_labels_TrainRAge, iAge_labels_TrainRAge],
                       [age_labels_SeenidRAge, race_labels_SeenidRAge, gender_labels_SeenidRAge, iAge_labels_SeenidRAge],
                       [age_labels_NewidRAge_test,  race_labels_NewidRAge,  gender_labels_NewidRAge, iAge_labels_NewidRAge]]

    list_all_classes = [[age_classes_TrainRAge,  race_classes_TrainRAge,  gender_classes_TrainRAge, iAge_labels_TrainRAge],
                        [age_classes_SeenidRAge, race_classes_SeenidRAge, gender_classes_SeenidRAge, iAge_labels_SeenidRAge],
                        [age_classes_NewidRAge_test,  race_classes_NewidRAge,  gender_classes_NewidRAge, iAge_labels_NewidRAge]]

    if age_label_ordering == "AgeRaceGenderIAge":
        label_ordering = [0, 1, 2, 3]
    elif age_label_ordering == "RaceAgeGenderIAge":
        label_ordering = [1, 0, 2, 3]
    elif age_label_ordering == "GenderAgeRaceIAge":
        label_ordering = [2, 0, 1, 3]
    elif age_label_ordering == "AgeGenderRaceIAge":
        label_ordering = [0, 2, 1, 3]
    elif age_label_ordering == "RaceGenderAgerIAge":
        label_ordering = [1, 2, 0, 3]
    elif age_label_ordering == "GenderRaceAgeIAge":
        label_ordering = [2, 1, 0, 3]
    else:
        print "age_label_ordering unknown: ", age_label_ordering
        quit()

    print "iAge_labels_TrainRAge=",iAge_labels_TrainRAge
    print "iAge_labels_TrainRAge.shape=",iAge_labels_TrainRAge.shape
    iTrainRAge[0][0].correct_labels = numpy.concatenate((list_all_labels[0][label_ordering[0]], list_all_labels[0][label_ordering[1]], list_all_labels[0][label_ordering[2]], list_all_labels[0][label_ordering[3]]), axis=1)
    iSeenidRAge.correct_labels      = numpy.concatenate((list_all_labels[1][label_ordering[0]], list_all_labels[1][label_ordering[1]], list_all_labels[1][label_ordering[2]], list_all_labels[1][label_ordering[3]]), axis=1)
    iNewidRAge[0][0].correct_labels = numpy.concatenate((list_all_labels[2][label_ordering[0]], list_all_labels[2][label_ordering[1]], list_all_labels[2][label_ordering[2]], list_all_labels[2][label_ordering[3]]), axis=1)

    iTrainRAge[0][0].correct_classes = numpy.concatenate((list_all_classes[0][label_ordering[0]], list_all_classes[0][label_ordering[1]], list_all_classes[0][label_ordering[2]], list_all_classes[0][label_ordering[3]]), axis=1)
    iSeenidRAge.correct_classes      = numpy.concatenate((list_all_classes[1][label_ordering[0]], list_all_classes[1][label_ordering[1]], list_all_classes[1][label_ordering[2]], list_all_classes[1][label_ordering[3]]), axis=1)
    iNewidRAge[0][0].correct_classes = numpy.concatenate((list_all_classes[2][label_ordering[0]], list_all_classes[2][label_ordering[1]], list_all_classes[2][label_ordering[2]], list_all_classes[2][label_ordering[3]]), axis=1)

else:
    print "Learning only a single label"
    single_label = "Gender"
    if single_label == "Age":
        print "Learning age only"
    elif single_label == "Race":
        print "Learning race instead of age"
        iTrainRAge[0][0].correct_labels = race_labels_TrainRAge.flatten()
        iSeenidRAge.correct_labels = race_labels_SeenidRAge.flatten()
        iNewidRAge[0][0].correct_labels = race_labels_NewidRAge.flatten()
        iTrainRAge[0][0].correct_classes = race_classes_TrainRAge.flatten()
        iSeenidRAge.correct_classes = race_classes_SeenidRAge.flatten()
        iNewidRAge[0][0].correct_classes = race_classes_NewidRAge.flatten()
    elif single_label == "Gender":
        print "Learning gender instead of age"
        iTrainRAge[0][0].correct_labels = gender_labels_TrainRAge.flatten()
        iSeenidRAge.correct_labels = gender_labels_SeenidRAge.flatten()
        iNewidRAge[0][0].correct_labels = gender_labels_NewidRAge.flatten()
        iTrainRAge[0][0].correct_classes = gender_classes_TrainRAge.flatten()
        iSeenidRAge.correct_classes = gender_classes_SeenidRAge.flatten()
        iNewidRAge[0][0].correct_classes = gender_classes_NewidRAge.flatten()
    else:
        print "single_label has unknown value:", single_label
        quit()
    
if age_ordered_by_increasing_label > 0 and age_add_other_label_classes:
    if age_ordered_by_increasing_label == 1: 
        print "reordering by increasing race label"
        iSeqs_labels = [[iTrainRAge[0][0], race_labels_TrainRAge],
                         [iSeenidRAge, race_labels_SeenidRAge],
                         [iNewidRAge[0][0], race_labels_NewidRAge]]
    elif age_ordered_by_increasing_label == 2:
        print "reordering by increasing gender (male then female)"        
        iSeqs_labels = [[iTrainRAge[0][0], gender_labels_TrainRAge],
                         [iSeenidRAge, gender_labels_SeenidRAge],
                         [iNewidRAge[0][0], gender_labels_NewidRAge]]
    else:
        print "age_ordered_by_increasing_label has unknown value: ", age_ordered_by_increasing_label
        quit()
    for iSeq, labels in iSeqs_labels:
        all_labels = labels.flatten()
        reordering = numpy.argsort(all_labels)
        if age_multiple_labels:
            iSeq.correct_labels = iSeq.correct_labels[reordering,:]
            iSeq.correct_classes = iSeq.correct_classes[reordering,:]
        else:
            iSeq.correct_labels = iSeq.correct_labels[reordering]
            iSeq.correct_classes = iSeq.correct_classes[reordering]            
        reordered_files = []
        for i in range(len(iSeq.input_files)):
            reordered_files.append(iSeq.input_files[reordering[i]])
        iSeq.input_files = reordered_files
        #print "reordered_files=", reordered_files
        print "iSeq.input_files[0] =", iSeq.input_files[0]
        print "iSeq.input_files[-1] =", iSeq.input_files[-1]
    #quit()

# if age_subordered_by_increasing_color == True and age_add_other_label_classes and age_label_ordering=="AgeRaceGender":
#     print "subordering training data by increasing skin color label"
#     iSeq = iTrainRAge[0][0]
#     race_labels = race_labels_TrainRAge
#     age_labels = iSeq.correct_labels[:,0]
#     block_size = iTrainRAge[0][0].block_size
#     
#     color_labels = color_labels.flatten()
#     age_labels = age_labels.flatten()
#     reordered_files = []
#     for block in range(iTrainRAge[0][0].num_images/block_size):
#         block_color_labels = color_labels[block*block_size:(block+1)*block_size]
# #        block_age_labels = color_labels[block*block_size:(block+1)*block_size]
#         block_reordering = numpy.argsort(block_color_labels)
#         if age_multiple_labels:
#             iSeq.correct_labels[block*block_size:(block+1)*block_size] = iSeq.correct_labels[block*block_size:(block+1)*block_size,:][block_reordering,:]
#             iSeq.correct_classes[block*block_size:(block+1)*block_size] = iSeq.correct_classes[block*block_size:(block+1)*block_size,:][block_reordering,:]
#         else:
#             iSeq.correct_labels[block*block_size:(block+1)*block_size] = iSeq.correct_labels[block*block_size:(block+1)*block_size,:][block_reordering]
#             iSeq.correct_classes[block*block_size:(block+1)*block_size] = iSeq.correct_classes[block*block_size:(block+1)*block_size,:][block_reordering]
#         block_files = iSeq.input_files[block*block_size:(block+1)*block_size]
#         for i in range(block_size):
#             reordered_files.append(block_files[block_reordering[i]])
#     iSeq.input_files = reordered_files
#         #print "reordered_files=", reordered_files
#     print "labels/classes subreordered, age is primary label, and skin color is the secondary"
# 
#     sTrainRAge[0][0].train_mode = "DualSerial4" #"DualSerial10"
    
print "iTrainRAge[0][0].input_files[0]=", iTrainRAge[0][0].input_files[0]
print "iTrainRAge[0][0].input_files[1]=", iTrainRAge[0][0].input_files[1]
print "iTrainRAge[0][0].input_files[-2]=", iTrainRAge[0][0].input_files[-2]
print "iTrainRAge[0][0].input_files[-1]=", iTrainRAge[0][0].input_files[-1]

#quit()

#Update input_files in sSeqs
for (iSeq, sSeq) in ((iTrainRAge[0][0], sTrainRAge[0][0]), 
                     (iSeenidRAge, sSeenidRAge), 
                     (iNewidRAge[0][0], sNewidRAge[0][0])):
    sSeq.input_files = [ os.path.join(iSeq.data_base_dir, file_name) for file_name in iSeq.input_files]


if age_ordered_by_increasing_label == 2: #Gender
    sTrainRAge[0][0].train_mode = "clustered"
    iTrainRAge[0][0].block_size = [num_males_TrainRAge, num_females_TrainRAge]
    sTrainRAge[0][0].block_size = [num_males_TrainRAge, num_females_TrainRAge]

if age_ordered_by_increasing_label == 1: #Race
    sTrainRAge[0][0].train_mode = "clustered"
    iTrainRAge[0][0].block_size = [num_BO_TrainRAge, num_AHW_TrainRAge]
    sTrainRAge[0][0].block_size = [num_BO_TrainRAge, num_AHW_TrainRAge]
  

#WARNING, EXPERIMENTING WITH WEIGHT=2.0, it should be 1.0 
if append_gender_classification and append_race_classification and age_label_ordering == "AgeRaceGenderIAge" and age_add_other_label_classes:
    sTrainRAge[0][0].train_mode = [sTrainRAge[0][0].train_mode, ("classification", iTrainRAge[0][0].correct_classes[:,1], 1.0), ("classification", iTrainRAge[0][0].correct_classes[:,2], 1.0)]
elif append_gender_classification and age_label_ordering == "AgeRaceGenderIAge" and age_add_other_label_classes:
    sTrainRAge[0][0].train_mode = [sTrainRAge[0][0].train_mode, ("classification", iTrainRAge[0][0].correct_classes[:,2], 1.0)]
elif append_race_classification and age_label_ordering == "AgeRaceGenderIAge" and age_add_other_label_classes:
    sTrainRAge[0][0].train_mode = [sTrainRAge[0][0].train_mode, ("classification", iTrainRAge[0][0].correct_classes[:,1], 1.0)]
else:
    print "Not adding any graph to the current train_mode"


#######################################################################################################################
#################                   MNIST Number Database Experiments                     #############################
#######################################################################################################################
import mnist

def load_MNIST_clusters(digits_used=[2,8], image_set='training', images_base_dir='/home/escalafl/Databases/MNIST'):
    images, labels = mnist.read(digits_used, image_set, images_base_dir)
    #print images
    #print images.shape
    
    num_images = len(labels)
    all_indices = numpy.arange(num_images)
    
    clusters = {}
    for i, digit in enumerate(digits_used):
        #print "cluster ", i, " for digit ", digits_used
        cluster_indices = all_indices[(labels==digit)]
        clusters[digit] = cluster_indices
        numpy.random.shuffle(clusters[digit])
        print "cluster %d for digit %d has %d images"%(i, digit, len(cluster_indices))
    return clusters, images

def iSeqCreateMNIST(dx=0, dy=0, smin=1.0, smax=1.00, delta_rotation=0.0, pre_mirroring="none", contrast_enhance=False, obj_avg_std=0.0, obj_std_min=0.20, obj_std_max=0.20,
                    clusters={}, first_image_index=0, num_images_per_cluster_used=0, repetition_factor=1, seed=-1, use_orig_label=False, increasing_orig_label=False):
    if seed >= 0 or seed is None:
        numpy.random.seed(seed)
        print "MNIST. Using seed", seed

    if num_images_per_cluster_used > 0:
        for digit in clusters.keys():
            if first_image_index + num_images_per_cluster_used > len(clusters[digit]):
                err = "first_image_index + num_images_per_digit_used > len(cluster_indices)." + "%d + %d > %d"%(first_image_index, num_images_per_cluster_used, len(clusters[digit]))
                raise Exception(err)
        
    print "***** Setting Information Parameters for MNIST ******"
    iSeq = SystemParameters.ParamsInput()
    #iSeq.name = "MNISTReal Translation " + slow_var + ": (%d, %d, %d, %d) numsteps %d"%(dx, dy, smin, smax, num_steps)
    iSeq.data_base_dir = "wrong dir"
    #TODO: create clusters here. 
    iSeq.ids = []
    iSeq.orig_labels = []
    iSeq.block_sizes = []
    for digit in clusters.keys():
        cluster = clusters[digit]
        if num_images_per_cluster_used >= 0:
            cluster_id =  cluster[first_image_index:first_image_index+num_images_per_cluster_used]*repetition_factor #image numbers
        else:
            cluster_id = cluster[first_image_index:] * repetition_factor
        iSeq.ids.extend(cluster_id)

        if num_images_per_cluster_used >= 0:
            cluster_labels = [digit] * repetition_factor * num_images_per_cluster_used
        else:
            cluster_labels = [digit] * repetition_factor *  (len(cluster) - first_image_index)
        if len(cluster_id) != len(cluster_labels):
            print "ERROR: Wrong number of cluster labels and original labels"
            print "len(cluster_id)=", len(cluster_id)
            print "len(cluster_labels)=", len(cluster_labels)
            quit()
        iSeq.orig_labels.extend(cluster_labels)
        
    iSeq.input_files = iSeq.ids
    
    if use_orig_label and increasing_orig_label:
        print "Reordering image filenames of data set according to the original labels"
        ordering = numpy.argsort(iSeq.orig_labels)
        ordered_orig_labels = [iSeq.orig_labels[i] for i in ordering]
        ordered_ids = [iSeq.ids[i] for i in ordering]
        iSeq.orig_labels = ordered_orig_labels
        iSeq.ids = ordered_ids
    else:
        print "Image filenames of data set not reordered according to the original labels"

    iSeq.num_images = len(iSeq.ids)

    iSeq.dx = dx
    iSeq.dy = dy
    iSeq.smin = smin
    iSeq.smax = smax
    iSeq.delta_rotation = delta_rotation

    iSeq.contrast_enhance = contrast_enhance
        
    iSeq.pre_mirror_flags = False

#    if contrast_enhance == True:
#        contrast_enhance = "AgeContrastEnhancement_Avg_Std" # "PostEqualizeHistogram" # "AgeContrastEnhancement"
#    if contrast_enhance in ["AgeContrastEnhancement_Avg_Std", "AgeContrastEnhancement25", "AgeContrastEnhancement20", "AgeContrastEnhancement15", "AgeContrastEnhancement", "PostEqualizeHistogram", "SmartEqualizeHistogram", False]:
#        iSeq.contrast_enhance = contrast_enhance
#    else:
#        ex = "Contrast method unknown"
#        raise Exception(ex)

    iSeq.obj_avg_std=obj_avg_std
    iSeq.obj_std_min=obj_std_min
    iSeq.obj_std_max=obj_std_max
        
#    if len(iSeq.ids) % len(iSeq.trans) != 0 and continuous == False:
#        ex="Here the number of translations/scalings must be a divisor of the number of identities"
#        raise Exception(ex)
    iSeq.ages = [None]
    iSeq.genders = [None]
    iSeq.racetweens = [None]
    iSeq.expressions = [None]
    iSeq.morphs = [None]
    iSeq.poses = [None]
    iSeq.lightings = [None]
    iSeq.slow_signal = 0 #real slow signal is the translation in the x axis (correlated to identity), added during image loading
    iSeq.step = 1
    iSeq.offset = 0

    #iSeq.params = [ids, expressions, morphs, poses, lightings]
    iSeq.params = [iSeq.ids, iSeq.ages, iSeq.genders, iSeq.racetweens, iSeq.expressions, \
                      iSeq.morphs, iSeq.poses, iSeq.lightings]

    diff_labels = numpy.unique(iSeq.orig_labels)
    iSeq.block_size = [ (iSeq.orig_labels == label).sum() for label in diff_labels ]
    print "iSeq.block_size =", iSeq.block_size

#    if num_images_per_cluster_used >= 0:
#        iSeq.block_size = num_images_per_cluster_used * repetition_factor
#    else:
#        iSeq.block_size = 1
    iSeq.train_mode = "clustered" #compact_classes+7" #"compact_classes+7" #"compact_classes3" #"serial" #"clustered" #"serial" #"mixed", None, "regular", "fwindow16", "fwindow32", "fwindow64", "fwindow128"

    unique_labels, iSeq.correct_classes = numpy.unique(iSeq.orig_labels, return_inverse=True)
    print "unique labels = ", unique_labels
    #quit()
    iSeq.correct_labels = numpy.array(iSeq.orig_labels)
    
    if len(iSeq.ids) != len(iSeq.orig_labels):
        er = "Computation of orig_labels failed:"+str(iSeq.ids)+str(iSeq.orig_labels)
        er += "len(iSeq.ids)=%d"%len(iSeq.ids) + "len(iSeq.orig_labels)=%d"%len(iSeq.orig_labels)+"len(iSeq.input_files)=%d"%len(iSeq.input_files)
        raise Exception(er)

    SystemParameters.test_object_contents(iSeq)
    return iSeq

def sSeqCreateMNIST(iSeq, images_array, seed=-1, use_RGB_images=False):
    if seed >= 0 or seed is None: #also works for 
        numpy.random.seed(seed)
    #else seed <0 then, do not change seed
    
    if iSeq==None:
        print "iSeq was None, this might be an indication that the data is not available"
        sSeq = SystemParameters.ParamsDataLoading()
        return sSeq
    
    print "******** Setting Training Data Parameters for MNIST  ****************"
    sSeq = SystemParameters.ParamsDataLoading()
    sSeq.input_files = iSeq.input_files
    sSeq.images_array = images_array
    sSeq.num_images = iSeq.num_images
    sSeq.block_size = iSeq.block_size
    sSeq.train_mode = iSeq.train_mode
    sSeq.include_latest = iSeq.include_latest
    sSeq.image_width = 28
    sSeq.image_height = 28 #192
    sSeq.subimage_width = 28 #192 # 160 #128 
    sSeq.subimage_height = 28 #192 # 160 #128 
    sSeq.pre_mirror_flags = iSeq.pre_mirror_flags
    
    sSeq.trans_x_max = iSeq.dx
    sSeq.trans_x_min = -1 * iSeq.dx
    sSeq.trans_y_max = iSeq.dy
    sSeq.trans_y_min = -1 * iSeq.dy
    sSeq.min_sampling = iSeq.smin
    sSeq.max_sampling = iSeq.smax
    sSeq.delta_rotation = iSeq.delta_rotation
    sSeq.contrast_enhance = iSeq.contrast_enhance
    sSeq.obj_avg_std = iSeq.obj_avg_std
    sSeq.obj_std_min = iSeq.obj_std_min
    sSeq.obj_std_max = iSeq.obj_std_max
            
    sSeq.add_noise_L0 = True
    if use_RGB_images:
        sSeq.convert_format = "RGB" # "RGB", "L"
    else:
        sSeq.convert_format = "L"
    sSeq.background_type = None

    sSeq.offset_translation_x = 0.0 
    sSeq.offset_translation_y = 0.0
    sSeq.translations_x = numpy.random.random_integers(sSeq.trans_x_min, sSeq.trans_x_max, sSeq.num_images) + sSeq.offset_translation_x
    sSeq.translations_y = numpy.random.random_integers(sSeq.trans_y_min, sSeq.trans_y_max, sSeq.num_images) + sSeq.offset_translation_y
    #print "sSeq.translations_x=", sSeq.translations_x 

    sSeq.pixelsampling_x = numpy.random.uniform(low=sSeq.min_sampling, high=sSeq.max_sampling, size=sSeq.num_images)
    sSeq.pixelsampling_y = sSeq.pixelsampling_x + 0.0

    if sSeq.delta_rotation != None:
        sSeq.rotation = numpy.random.uniform(-sSeq.delta_rotation, sSeq.delta_rotation, sSeq.num_images)
    else:
        sSeq.rotation = None
    if iSeq.obj_avg_std > 0:
        sSeq.obj_avgs = numpy.random.normal(0.0, iSeq.obj_avg_std, size=sSeq.num_images)
    else:
        sSeq.obj_avgs = numpy.zeros(sSeq.num_images)
    sSeq.obj_stds = numpy.random.uniform(sSeq.obj_std_min, sSeq.obj_std_max, sSeq.num_images)

    #BUG1: image center is not computed that way!!! also half(width-1) computation is wrong!!!
    sSeq.subimage_first_row =  sSeq.image_height/2.0-sSeq.subimage_height*sSeq.pixelsampling_y/2.0
    sSeq.subimage_first_column = sSeq.image_width/2.0-sSeq.subimage_width*sSeq.pixelsampling_x/2.0

    sSeq.trans_sampled = True #TODO:check semantics, when is sampling/translation done? why does this value matter?
    sSeq.name = "MNIST Dx in (%d, %d) Dy in (%d, %d), sampling in (%d perc, %d perc)"%(sSeq.trans_x_min, 
        sSeq.trans_x_max, sSeq.trans_y_min, sSeq.trans_y_max, int(sSeq.min_sampling*100), int(sSeq.max_sampling*100))

    print "Mean in correct_labels is:", iSeq.correct_labels.mean()
    print "Var in correct_labels is:", iSeq.correct_labels.var()
    sSeq.load_data = load_data_from_sSeq
    SystemParameters.test_object_contents(sSeq)
    return sSeq

print "MNIST: starting with experiment_seed=", experiment_seed
numpy.random.seed(experiment_seed+123451313)
shuffle_digits = True #and False
num_digits_used = 8 # 10
digits_used = numpy.arange(10) #(8) numpy.arange(10) #[4,9] #(4,9) or (9,7) or numpy.arange(10)
if shuffle_digits:
    numpy.random.shuffle(digits_used)
digits_used = digits_used[0:num_digits_used]

mnist_enabled=False or True
if mnist_enabled:
    clusters_MNIST, images_array_MNIST = load_MNIST_clusters(digits_used=digits_used, image_set='training', images_base_dir='/home/escalafl/Databases/MNIST')
    clusters_MNIST_test, images_array_MNIST_test = load_MNIST_clusters(digits_used=digits_used, image_set='testing', images_base_dir='/home/escalafl/Databases/MNIST')
else:
    clusters_MNIST = clusters_MNIST_test = {}
    images_array_MNIST =  images_array_MNIST_test = []

numpy.random.seed(experiment_seed+987987987)

base_scale = 1.0
factor_training = 1.0 
factor_seenid = 1.0  
scale_offset = 0.00  

#5421 images for digit 5 WARNING, here use only 5000!!!!
iSeq_set1 = iSeqCreateMNIST(dx=0.0, dy=0.0, smin=1.0, smax=1.0, delta_rotation=None, pre_mirroring="none", contrast_enhance=None, obj_avg_std=0.0, obj_std_min=0.20, obj_std_max=0.20,
                    clusters=clusters_MNIST, first_image_index=421, num_images_per_cluster_used=5000, repetition_factor=1, seed=-1, use_orig_label=True, increasing_orig_label=True) #5000, num_images_per_cluster_used=-1
sSeq_set1 = sSeqCreateMNIST(iSeq_set1, images_array_MNIST, seed=-1, use_RGB_images=age_use_RGB_images)

semi_supervised_learning = True and False
if semi_supervised_learning == False:
    iSeq_set = iTrainMNIST = [[iSeq_set1]]
    sSeq_set = sTrainMNIST= [[sSeq_set1]]
else:
    iSeq_set2 = iSeqCreateMNIST(dx=0.0, dy=0.0, smin=1.0, smax=1.0, delta_rotation=None, pre_mirroring="none", contrast_enhance=None, obj_avg_std=0.0, obj_std_min=0.20, obj_std_max=0.20,
                    clusters=clusters_MNIST, first_image_index=921, num_images_per_cluster_used=4500, repetition_factor=1, seed=-1, use_orig_label=True, increasing_orig_label=True) #5000, num_images_per_cluster_used=-1
    iSeq_set2.train_mode = "smart_unlabeled2" #smart_unlabeled2" #"ignore_data" #"smart_unlabeled3"
    sSeq_set2 = sSeqCreateMNIST(iSeq_set2, images_array_MNIST, seed=-1, use_RGB_images=age_use_RGB_images)
    iSeq_set = iTrainMNIST = [[iSeq_set1,iSeq_set2]]
    sSeq_set = sTrainMNIST = [[sSeq_set1,sSeq_set2]]    
    
#print "iSeq_set.input_files=",iSeq_set[0][0].input_files
print "len(iSeq_set.input_files)=",len(iSeq_set[0][0].input_files)
#print "sSeq_set.input_files=",sSeq_set[0][0].input_files
print "len(sSeq_set.input_files)=",len(sSeq_set[0][0].input_files)

#WARNING HERE USE index 5000 and 421 images per cluster!!!
iSeq_set = iSeenidMNIST = iSeqCreateMNIST(dx=0.0, dy=0.0, smin=1.0, smax=1.0, delta_rotation=None, pre_mirroring="none", contrast_enhance=None, obj_avg_std=0.0, obj_std_min=0.20, obj_std_max=0.20,
                    clusters=clusters_MNIST, first_image_index=0, num_images_per_cluster_used=421, repetition_factor=1, seed=-1, use_orig_label=True, increasing_orig_label=True) #421
                           
sSeq_set = sSeenidMNIST = sSeqCreateMNIST(iSeq_set, images_array_MNIST, seed=-1, use_RGB_images=age_use_RGB_images)


iSeq_set = iNewidMNIST = [[iSeqCreateMNIST(dx=0.0, dy=0.0, smin=1.0, smax=1.0, delta_rotation=None, pre_mirroring="none", contrast_enhance=None, obj_avg_std=0.0, obj_std_min=0.20, obj_std_max=0.20,
                    clusters=clusters_MNIST_test, first_image_index=0, num_images_per_cluster_used=-1, repetition_factor=1, seed=-1, use_orig_label=True, increasing_orig_label=True) ]]
                           
sSeq_set = sNewidMNIST = [[sSeqCreateMNIST(iSeq_set[0][0], images_array_MNIST_test, seed=-1, use_RGB_images=age_use_RGB_images)]]

ParamsMNISTFunc = SystemParameters.ParamsSystem()
ParamsMNISTFunc.name = "Function Based Data Creation for MNIST"
ParamsMNISTFunc.network = "linearNetwork4L" #Default Network, but ignored
ParamsMNISTFunc.iTrain =iTrainMNIST
ParamsMNISTFunc.sTrain = sTrainMNIST

ParamsMNISTFunc.iSeenid = iSeenidMNIST
ParamsMNISTFunc.sSeenid = sSeenidMNIST
images_array_MNIST_test
ParamsMNISTFunc.iNewid = iNewidMNIST
ParamsMNISTFunc.sNewid = sNewidMNIST

if iTrainMNIST != None and iTrainMNIST[0][0]!=None:
    ParamsMNISTFunc.block_size = iTrainMNIST[0][0].block_size
ParamsMNISTFunc.train_mode = "Weird Mode" #Ignored for the moment 
ParamsMNISTFunc.analysis = None
ParamsMNISTFunc.enable_reduced_image_sizes = True
ParamsMNISTFunc.reduction_factor = 1.0 # T=1.0 WARNING 1.0, 2.0, 3, 4
ParamsMNISTFunc.hack_image_size = 28 # T=24 WARNING      24, 12, 8, 6 #IS IT 24 or 28!!!!! 28=2*2*7, 24=2*2*2*3
ParamsMNISTFunc.enable_hack_image_size = True
ParamsMNISTFunc.patch_network_for_RGB = False # 


#TODO: IS a mapping from classes to zero-starting classes needed????
# all_classes = numpy.unique(iSeenidRAge.correct_classes)
# 
# min_num_classes = 7 #40
# max_num_classes = 42 #42
# 
# num_classes = len(all_classes)
# if min_num_classes > num_classes:
#     ex = "insufficient number of classes in seenid data: %d >= %d "%(min_num_classes, num_classes)
#     raise Exception(ex)
# 
# smallest_number_of_samples_per_class = 30
# class_list = list(all_classes) #This is the actual mapping from orig. classes to final classes
# num_classes = len(class_list)    IEVMLRecNet_out_dims = [ 28, 52, 75, 85, 90, 90, 85, 100, 75,75,75 ] #Experiment with control2: Dt=1.9999

# while num_classes > max_num_classes:
#     current_count = 0
#     current_class = 0
#     class_list = []
#     for classnr in all_classes: #[::-1]:
#         class_list.append(current_class)
#         current_count += (iSeenidRAge.correct_classes==classnr).sum()    
#         if current_count >= smallest_number_of_samples_per_class:
#             current_count = 0
#             current_class += 1
#     if current_count >= smallest_number_of_samples_per_class:
#         print "last class cluster is fine"
#     elif current_count > 0:
#         print "fixing last class cluster by adding it to its predecesor"
#         class_list = numpy.array(class_list)
#         class_list[class_list == current_class] = current_class-1
#     num_classes = len(numpy.unique(class_list))
#     print "In iteration with smallest_number_of_samples_per_class=%diSeenidGender = iSeqCreateGender(first_id = 0, num_ids = 25, user_base_dir=user_base_dir, data_dir="Alberto/RenderingsGender60x200", gender_continuous=True, seed=None)
####, we have %d clases"%(smallest_number_of_samples_per_class,num_classes)
#     smallest_number_of_samples_per_class = 1.1 * smallest_number_of_samples_per_class + 1
# #class_list.reverse()
# #class_list = numpy.array(class_list)
# #class_list = class_list.max()-class_list
# if min_num_classes > num_classes:pirate
#     ex = "Resulting number of classes %d is smaller than min_num_classes %d"%(num_classes, min_num_classes)
#     raise Exception(ex)
# 
# print "class_list=", class_list
# for i, classnr in enumerate(all_classes):
#     iSeenidRAge.correct_classes[iSeenidRAge.correct_classes==classnr] = class_list[i]
