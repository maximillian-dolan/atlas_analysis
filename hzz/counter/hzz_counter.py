import uproot # for reading .root files
import time # to measure time to analyse
import argparse # for passing command line arguments
import pickle
import os

import infofile # local file containing cross-sections, sums of weights, dataset IDs

parser = argparse.ArgumentParser(description='Defines dictionaries with start and end points for each worker')
parser.add_argument('--number_workers', default=1, help='Number of workers being used')
args = parser.parse_args()

#===================================================================================
# Remove current .pkl files

# Directory path
directory = './data/'

# List all files in the directory
files = os.listdir(directory)

# Filter files ending with '.pkl'
pkl_files = [file for file in files if file.endswith('.pkl')]

# Remove each .pkl file
for pkl_file in pkl_files:
    file_path = os.path.join(directory, pkl_file)
    os.remove(file_path)

#===================================================================================
# Where to access the input files
                                                                                                                                  
#tuple_path = "Input/4lep/" # local 
tuple_path = "https://atlas-opendata.web.cern.ch/atlas-opendata/samples/2020/4lep/" # web address

# Samples to process
samples = {'data': {'list' : ['data_A','data_B','data_C','data_D'],
                    },
           r'Background $Z,t\bar{t}$' : { # Z + ttbar
                                         'list' : ['Zee','Zmumu','ttbar_lep'],
                                         'color' : "#6b59d3" # purple
                                         },
           r'Background $ZZ^*$' : { # ZZ
                                   'list' : ['llll'],
                                   'color' : "#ff0000" # red
                                   },
           r'Signal ($m_H$ = 125 GeV)' : { # H -> ZZ -> llll
                                          'list' : ['ggH125_ZZ4lep','VBFH125_ZZ4lep','WH125_ZZ4lep','ZH125_ZZ4lep'],
                                          'color' : "#00cdff" # light blue
                                          },

        }

#===================================================================================
# Data reading functions

# Define function to read and process individual files
def count_file(path,sample):

    start = time.time() # start the clock
    print("\tCounting: "+sample) # print which sample is being processed
    # open the tree called mini using a context manager (will automatically close files/resources)
    with uproot.open(path + ":mini") as tree:
        numevents = tree.num_entries # number of events
        count = numevents # number of events in this batch
 
        elapsed = time.time() - start # time taken to process
        print("\t\t Count: "+str(count)+",\t in "+str(round(elapsed,1))+"s") # number of counts
    
    return count # return array containing events passing all cuts

# Define function to get data from files
def get_data_from_files():

    counts = {} # define empty dictionary to hold awkward arrays
    for s in samples: # loop over samples
        dict = {}
        print('Counting '+s+' samples') # print which sample
        for val in samples[s]['list']: # loop over each file
            if s == 'data': prefix = "Data/" # Data prefix
            else: # MC prefix
                prefix = "MC/mc_"+str(infofile.infos[val]["DSID"])+"."
            fileString = tuple_path+prefix+val+".4lep.root" # file name to open
            count = count_file(fileString,val) # call the function read_file defined below
            dict[val] = count
        counts[s] = dict

    return counts # return dictionary of awkward arrays

#===================================================================================

# Define funciton to add nested dictionaries together
def add_dictionaries(dict1, dict2):
    result = {}
    for key in dict1.keys():
        if key in dict2:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                # Recursively call for nested dictionaries
                result[key] = add_dictionaries(dict1[key], dict2[key])
            else:
                # Add values if they are not nested dictionaries
                result[key] = dict1[key] + dict2[key]

    return result

def split_dictionary(original_dict, n):
    output_dicts = [{} for _ in range(n+1)]
    zeros, ones = {},{}

    for category, sub_dict in original_dict.items():
        for key, value in sub_dict.items():

            # Splitting the value into n parts
            split_values = [value // n] * n  
            remaining = value % n 

            # Distributing the remainder among the first 'remaining' dictionaries
            for i in range(remaining):
                split_values[i] += 1

            # Set initial dictionary of start points and create dictionary of 1s
            zeros.setdefault(category, {})[key] = 0
            ones.setdefault(category, {})[key] = 1

            output_dicts[0] = zeros

            # Assigning split values to output dictionaries
            for i in range(1,n+1):
                output_dicts[i].setdefault(category, {})[key] = split_values[i-1]
    
    # Make dictionaries to be cumulative
    for i in range(1,n+1):
        output_dicts[i] = add_dictionaries(output_dicts[i-1],output_dicts[i])

    # Create start and end value dictionaries
    start_dicts = output_dicts[:-1]
    end_dicts = output_dicts[1:]

    # Make start values 1 more than previous end values    
    for i in range(1,n):
        start_dicts[i] = add_dictionaries(start_dicts[i], ones)

    # Final validation check to ensure all dictionaries add up to original
    if output_dicts[n] == original_dict:
        return start_dicts, end_dicts

    else:
        raise ValueError('End verification failed')

def main():

    start = time.time() # time at start of whole processing
    counts = get_data_from_files() # process all files
    elapsed = time.time() - start # time after whole processing
    print("Time taken: "+str(round(elapsed,1))+"s") # print total time taken to process every file

    if float(args.number_workers).is_integer():
        n = int(args.number_workers)  # Number of output dictionaries
    else:
        raise ValueError('number of workers must be an integer')

    start_dicts, end_dicts = split_dictionary(counts, n)

    #Printing the results
    print('======')
    print('starts:')
    for i, output_dict in enumerate(start_dicts):
        print(f"Dictionary {i+1}: {output_dict}\n")
    print('========================================')
    print('ends')
    for i, output_dict in enumerate(end_dicts):
        print(f"Dictionary {i+1}: {output_dict}\n")

    # Save dictionaries
    with open('./data/starts.pkl', 'wb') as sd:
        pickle.dump(start_dicts, sd)
        print('start points saved')
    
    with open('./data/ends.pkl', 'wb') as ed:
        pickle.dump(end_dicts, ed)
        print('end points saved')

main()