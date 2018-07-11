import argparse
import logging
import pandas as pd
import numpy as np

from test_data_creation import create_data

def stat_test_binary_trees(data):
    raise NotImplementedError

def ___get_avr_btree_height(data):
    raise NotImplementedError

def stat_test_three_connected_graphs(data):
    raise NotImplementedError

def stat_test_two_connected_graphs(data):
    raise NotImplementedError

def stat_test_one_connected_graphs(data):
    raise NotImplementedError

def stat_test_planar_graphs(data):
    raise NotImplementedError

def test_distribution(data):
    raise NotImplementedError

def test_for_special_graphs(data):
    raise NotImplementedError

def avr_num_trials_hitting_the_size(data):
    raise NotImplementedError  

def find_the_right_const_for_evals(data):
    raise NotImplementedError

def ___data_list_to_data_frame(file_name):
    

def main():
    argparser = argparse.ArgumentParser(description='Test stuff')
    argparser.add_argument('-d', dest='loglevel', action='store_const', const=logging.DEBUG, help='Print Debug info')
    argparser.add_argument('-b', '--binary-tree', action='store_true', help='Make statistical tests for binary trees')
    argparser.add_argument('-three', '--three_connectd', action='store_true', help='Make statistical tests for three connected graphs')
    argparser.add_argument('-two', '--two_connected', action='store_true', help='Make statistical tests for two connected graphs')
    argparser.add_argument('-one', '--one_connected', action='store_true', help='Make statistical tests for one connected graphs')
    argparser.add_argument('samples', type=int, help="Sample x number of time.")
    argparser.add_argument('size', type=int, help="Sample object of a certain size.")
    
    args = argparser.parse_args()
    logging.basicConfig(level=args.loglevel)

    sample_num = args.samples
    samples_size = args.size

  
    if args.binary_tree:
        create_data("binary_tree", sample_num, samples_size)
        data = ___data_list_to_data_frame("binary_tree")
        passed = stat_test_binary_trees(data)
        if passed:
            print("binary-tree test.....................passed")
        else:
            print("binary-tree test.....................failed")

    elif args.three_connectd:
        raise NotImplementedError
    elif args.two_connected:
        raise NotImplementedError
    elif args.one_connected:
        raise NotImplementedError
    else:
        raise Exception("Wrong combinatorial class.")


if __name__ == '__main__':
    main()


