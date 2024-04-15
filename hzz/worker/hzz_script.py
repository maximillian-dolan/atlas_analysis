import uproot # for reading .root files
import awkward as ak # to represent nested data in columnar format
import vector # for 4-momentum calculations
import time # to measure time to analyse
import math # for mathematical functions such as square root
import argparse # for passing command line arguments
import pickle

import infofile # local file containing cross-sections, sums of weights, dataset IDs

#===================================================================================
# Command line arguments

parser = argparse.ArgumentParser(description='Runs the HZZ analysis on data')
parser.add_argument('--rank', default = 0, help = 'which division node is doing' )

args = parser.parse_args()
#===================================================================================
# Load in start and end points

with open('data/starts.pkl', 'rb') as sd:
    start_dicts = pickle.load(sd)

with open('data/ends.pkl', 'rb') as ed:
    end_dicts = pickle.load(ed)

rank = int(args.rank)

# Do validation checks
if len(start_dicts) != len(end_dicts):
    raise IndexError('Start and End dictionaries are not the same length')

if rank >= len(start_dicts):
    raise ImportError(f'Highest rank possible is {len(start_dicts)-1}')

start_dict = start_dicts[rank]
end_dict = end_dicts[rank]

#print('========================================')
#print('starts:')
#for i, output_dict in enumerate(start_dicts):
    #print(f"Dictionary {i+1}: {output_dict}\n")
#print('=====')
#print('ends:')
#for i, output_dict in enumerate(end_dicts):
    #print(f"Dictionary {i+1}: {output_dict}\n")
#print('========================================')
#===================================================================================
# Define variables

#General definitions of fraction of data used, where to access the input files

#lumi = 0.5 # fb-1 # data_A only
#lumi = 1.9 # fb-1 # data_B only
#lumi = 2.9 # fb-1 # data_C only
#lumi = 4.7 # fb-1 # data_D only
lumi = 10 # fb-1 # data_A,data_B,data_C,data_D
                                                                                                                                  
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

# Set units
MeV = 0.001
GeV = 1.0

#===================================================================================
# Weight functions 

# Define function to calculate weight of MC event
def calc_weight(xsec_weight, events):
    return (xsec_weight * events.mcWeight * events.scaleFactor_PILEUP * events.scaleFactor_ELE * events.scaleFactor_MUON * events.scaleFactor_LepTRIGGER)


# Define function to get cross-section weight
def get_xsec_weight(sample):
    info = infofile.infos[sample] # open infofile
    xsec_weight = (lumi*1000*info["xsec"])/(info["sumw"]*info["red_eff"]) #*1000 to go from fb-1 to pb-1
    return xsec_weight # return cross-section weight


def calc_mllll(lep_pt, lep_eta, lep_phi, lep_E):
    # construct awkward 4-vector array
    p4 = vector.zip({"pt": lep_pt, "eta": lep_eta, "phi": lep_phi, "E": lep_E})
    # calculate invariant mass of first 4 leptons
    # [:, i] selects the i-th lepton in each event
    # .M calculates the invariant mass
    return (p4[:, 0] + p4[:, 1] + p4[:, 2] + p4[:, 3]).M * MeV

#===================================================================================
# Cut functions

# cut on lepton charge
# paper: "selecting two pairs of isolated leptons, each of which is comprised of two leptons with the same flavour and opposite charge"
def cut_lep_charge(lep_charge):
# throw away when sum of lepton charges is not equal to 0
# first lepton in each event is [:, 0], 2nd lepton is [:, 1] etc
    return lep_charge[:, 0] + lep_charge[:, 1] + lep_charge[:, 2] + lep_charge[:, 3] != 0


# cut on lepton type
# paper: "selecting two pairs of isolated leptons, each of which is comprised of two leptons with the same flavour and opposite charge"
def cut_lep_type(lep_type):
# for an electron lep_type is 11
# for a muon lep_type is 13
# throw away when none of eeee, mumumumu, eemumu
    sum_lep_type = lep_type[:, 0] + lep_type[:, 1] + lep_type[:, 2] + lep_type[:, 3]
    return (sum_lep_type != 44) & (sum_lep_type != 48) & (sum_lep_type != 52)

#===================================================================================
# Data reading functions

# Define function to read and process individual files
def read_file(path,sample,s):
    start = time.time() # start the clock
    start_point = start_dict[s][sample]
    end_point = end_dict[s][sample] + 1 # +1 as is the first point it ignores
    print("\tProcessing: "+sample,f' - start point: {start_point} , end point: {end_point-1}') # print which sample is being processed
    data_all = [] # define empty list to hold all data for this sample
    nIn = end_point-start_point 
    
    # open the tree called mini using a context manager (will automatically close files/resources)
    counter=0
    with uproot.open(path + ":mini") as tree:
        numevents = tree.num_entries # number of events
        nOut = [0]*numevents
        i = 0
        
        if 'data' not in sample:
            xsec_weight = get_xsec_weight(sample) # get cross-section weight
        for data in tree.iterate(['lep_pt','lep_eta','lep_phi',
                                  'lep_E','lep_charge','lep_type', 
                                  # add more variables here if you make cuts on them 
                                  'mcWeight','scaleFactor_PILEUP',
                                  'scaleFactor_ELE','scaleFactor_MUON',
                                  'scaleFactor_LepTRIGGER'], # variables to calculate Monte Carlo weight
                                 library="ak", # choose output type as awkward array
                                 entry_start = start_point, # start entry at
                                 entry_stop= end_point): # process up to numevents*fraction

            if 'data' not in sample: # only do this for Monte Carlo simulation files
                # multiply all Monte Carlo weights and scale factors together to give total weight
                data['totalWeight'] = calc_weight(xsec_weight, data)

            #if s == 'Signal ($m_H$ = 125 GeV)':
             #   if counter%100 ==0:
              #      print(counter) 
               # counter +=1


            # cut on lepton charge using the function cut_lep_charge defined above
            data = data[~cut_lep_charge(data.lep_charge)]

            # cut on lepton type using the function cut_lep_type defined above
            data = data[~cut_lep_type(data.lep_type)]

            # calculation of 4-lepton invariant mass using the function calc_mllll defined above
            data['mllll'] = calc_mllll(data.lep_pt, data.lep_eta, data.lep_phi, data.lep_E)
            
            # array contents can be printed at any stage like this
            #print(data)

            # array column can be printed at any stage like this
            #print(data['lep_pt'])

            # multiple array columns can be printed at any stage like this
            #print(data[['lep_pt','lep_eta']])

            #nOut = len(data) # number of events passing cuts in this batch       
            data_all.append(data) # append array from this batch

            nOut[i] = len(data)
            i+=1
            
        elapsed = time.time() - start # time taken to process
        print("\t\t nIn: "+str(nIn)+'/'+str(numevents)+",\t nOut: \t"+str(sum(nOut))+"\t in "+str(round(elapsed,1))+"s") # events before and after
    
    return ak.concatenate(data_all) # return array containing events passing all cuts


# Define function to get data from files
def get_data_from_files():

    data = {} # define empty dictionary to hold awkward arrays
    for s in samples: # loop over samples
        print('Processing '+s+' samples') # print which sample
        frames = [] # define empty list to hold data
        for val in samples[s]['list']: # loop over each file
            if s == 'data': prefix = "Data/" # Data prefix
            else: # MC prefix
                prefix = "MC/mc_"+str(infofile.infos[val]["DSID"])+"."
            fileString = tuple_path+prefix+val+".4lep.root" # file name to open
            temp = read_file(fileString,val,s) # call the function read_file defined below
            frames.append(temp) # append array returned from read_file to list of awkward arrays
        data[s] = ak.concatenate(frames) # dictionary entry is concatenated awkward arrays
    
    return data # return dictionary of awkward arrays

#===================================================================================

def main():
    print('=======================')
    print(f'Processing node {rank}')
    print('=======================')

    start = time.time() # time at start of whole processing
    data = get_data_from_files() # process all files
    elapsed = time.time() - start # time after whole processing
    print("Time taken: "+str(round(elapsed,1))+"s") # print total time taken to process every file

    with open(f'./data/data_{rank}.pkl', 'wb') as d:
        pickle.dump(data, d)
        print(f'data from {rank} saved')

main()









