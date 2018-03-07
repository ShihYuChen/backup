# edit settings here
#data and results forder
ROOT_DIR ='/home/sychen/code/kaggle'
DATA_DIR    = ROOT_DIR + '/data'  #'/media/root/5453d6d1-e517-4659-a3a8-d0a878ba4b60/data/kaggle/science2018/data' #
RESULTS_DIR = ROOT_DIR + '/results'
EXCEL_PATH = DATA_DIR + '/split/stage1_train_sort_comment2.xlsx'
EXCEL_PATH_TEST = DATA_DIR + '/split/Annotate_stage_1_test_list.xlsx'
COMMENT_CSV_PATH = DATA_DIR +'/split/comment.csv'
TEST_CSV_PATH = DATA_DIR +'/split/test.csv'

PRETRAIN_FILE = ROOT_DIR + 'resnet-50.t7'
    # PRETRAIN_FILE = None
TASK_NAME = '/V10_test'  # task output folder, subfolder of RESULTS_DIR.

##Training
#checkpoint file for training
INITIAL_CP_FILE = '/home/sychen/code/kaggle/results/128_nms_test/checkpoint/00062000_model.pth'
# INITIAL_CP_FILE = None
LEARNING_RATE = 0.00003
LREARNING_BATCH = 4
LABEL_MAP =  {'Histology' : 1, 'Flouresence' : 2, 'Brightfield' : 3}
##Prediction
#checkpoint file for prediction
PREDICT_MODEL = '00062000_model.pth'
# PREDICT_CP_FILE = '/home/sychen/code/kaggle/results' + TASK_NAME + '/checkpoint/' + PREDICT_MODEL
PREDICT_CP_FILE = '/home/sychen/code/kaggle/results/128_nms_test/checkpoint/' + PREDICT_MODEL
SUBMIT_FOLDER = '/' + PREDICT_MODEL.split('_')[0] +'nms'
##---------------------------------------------------------------------
import os
from datetime import datetime
PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
IDENTIFIER   = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

#numerical libs
import math
import numpy as np
import random
import PIL
import cv2

import matplotlib
matplotlib.use('TkAgg')
#matplotlib.use('Qt4Agg')
#matplotlib.use('Qt5Agg')


# torch libs
import torch
import torchvision.transforms as transforms
from torch.utils.data.dataset import Dataset
from torch.utils.data import DataLoader
from torch.utils.data.sampler import *

import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import torch.optim as optim
from torch.nn.parallel.data_parallel import data_parallel


# std libs
import collections
import copy
import numbers
import inspect
import shutil
from timeit import default_timer as timer

import csv
import pandas as pd
import pickle
import glob
import sys
from distutils.dir_util import copy_tree
import time
import matplotlib.pyplot as plt

import skimage
import skimage.color
import skimage.morphology
from scipy import ndimage


#---------------------------------------------------------------------------------
# https://stackoverflow.com/questions/34968722/how-to-implement-the-softmax-function-in-python
def np_softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return e_x / e_x.sum(axis=1, keepdims=True)

def np_sigmoid(x):
  return 1 / (1 + np.exp(-x))


#---------------------------------------------------------------------------------
print('@%s:  ' % os.path.basename(__file__))

if 1:
    SEED = 35202 #1510302253  #int(time.time()) #
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    print ('\tset random seed')
    print ('\t\tSEED=%d'%SEED)

if 1:
    torch.backends.cudnn.benchmark = True  ##uses the inbuilt cudnn auto-tuner to find the fastest convolution algorithms. -
    torch.backends.cudnn.enabled   = True
    print ('\tset cuda environment')
    print ('\t\ttorch.__version__              =', torch.__version__)
    print ('\t\ttorch.version.cuda             =', torch.version.cuda)
    print ('\t\ttorch.backends.cudnn.version() =', torch.backends.cudnn.version())
    try:
        print ('\t\tos[\'CUDA_VISIBLE_DEVICES\']     =',os.environ['CUDA_VISIBLE_DEVICES'])
        NUM_CUDA_DEVICES = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
    except Exception:
        print ('\t\tos[\'CUDA_VISIBLE_DEVICES\']     =','None')
        NUM_CUDA_DEVICES = 1

    print ('\t\ttorch.cuda.device_count()      =', torch.cuda.device_count())
    print ('\t\ttorch.cuda.current_device()    =', torch.cuda.current_device())


print('')

#---------------------------------------------------------------------------------