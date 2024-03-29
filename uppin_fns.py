import csv
import numpy as np
import numpy.matlib as npm
from sklearn.neighbors import KDTree
from matplotlib import pyplot as plt
from statistics import mean
from math import sqrt

def gen_data(file_name,bond_dist):
    file_info = []
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            s = line[0]
            l = " ".join(s.split()) ## deletes all unnessecary white spaces
            file_info.append(l.split(' '))

    ## 
    xyz_coord = []
    for i in range(2,len(file_info)):
        #print(file_info[i][0])
        if file_info[i][0] == 'O' or file_info[i][0] == '2':
            file_info[i][0] = 2
        else:
            file_info[i][0] = 1
        xyz_coord.append([float(file_info[i][1]),float(file_info[i][2]),float(file_info[i][3])])
        #d=sqrt(float(file_info[i][1])**2 + float(file_info[i][2])**2 + float(file_info[i][3])**2)/10
        #file_info[i].append(round(d,2)) # Make separate list containing only distances from center in andstroms
    #print(f'Maximum distance from the center is {max_dist} nm')

    points = np.array(xyz_coord) # put values of list to numpy array to use KDTree
    ## Using KDTree, we calculate the nearest neighbours for each atom
    tree = KDTree(points, leaf_size=3)
    all_nn_indices = tree.query_radius(points, r=bond_dist)  # NNs within distance of r_bond of point
    all_nns = [[points[idx] for idx in nn_indices] for nn_indices in all_nn_indices]
    # Find CenterOfMass coordinates
    test = [[1] for i in range(len(points))]
    c = np.append(points,test,axis=1)
    CM = np.average(c[:,:3], axis=0, weights= c[:,3])
    # Add coordination number to the end of xyz coordinates:
    max_dist = 0
    for i in range(2,len(file_info)):
        X_dist = float(file_info[i][1]) - float(CM[0])
        Y_dist = float(file_info[i][2]) - float(CM[1])
        Z_dist = float(file_info[i][3]) - float(CM[2])
        d = sqrt(X_dist**2 + Y_dist**2 + Z_dist**2)/10
        if d > max_dist:
            max_dist = d
        file_info[i].append(round(d,2))
        file_info[i].append(len(all_nns[i-2])-1)    
    
    return file_info,round(max_dist,2)

def gen_analysis_data(distances, input_data, atom_type='all'):
    max_dist = max([input_data[i][-2] for i in range(2,len(input_data))])
    if atom_type == 'Me':
        test_type = [1]
    elif atom_type == 'O':
        test_type = [2]
    else:
        test_type = [1,2]
    mean_vals = []
    for i in range(len(distances)):
        core_values = []
        shell_values = []
        for j in range(2,len(input_data)):
            if input_data[j][-2] > max_dist-distances[i]:
                if input_data[j][0] in test_type:
                    shell_values.append(input_data[j][-1])
            else:
                if input_data[j][0] in test_type:
                    core_values.append(input_data[j][-1])
        np_values = shell_values+core_values
        if len(shell_values) == 0 or len(core_values) == 0:
            #print('Core or shell region is empty!')
            break
        shell_val = round(mean(shell_values),2)
        core_val = round(mean(core_values),2)
        to_app = list([distances[i],core_val,shell_val,mean(np_values)])
        mean_vals.append(to_app)
    return mean_vals

def get_atom_counts(input_data, distance = 0.5):
    core_length = max([input_data[i][-2] for i in range(2,len(input_data))]) - distance
    counter = {'Me_core':0,
              'Me_shell':0,
              'O_core':0,
              'O_shell':0}
    for i in range(2,len(input_data)):
        if input_data[i][-2] < core_length:
            if input_data[i][0] == 2:
                counter['O_core'] += 1
            else:
                counter['Me_core'] += 1
        else:
            if input_data[i][0] == 2:
                counter['O_shell'] += 1
            else:
                counter['Me_shell'] += 1
    tot_surface = counter['Me_shell'] + counter['O_shell']
    tot_core = counter['Me_core'] + counter['O_core']
    percentage = round(tot_surface/(tot_surface+tot_core)*100,0)
    percentage_Me = round(counter['Me_shell']/(counter['Me_shell']+counter['Me_core'])*100,0)
    print(f'In shell region: Me count = {counter["Me_shell"]} and O count = {counter["O_shell"]}')
    print(f'In core region: Me count = {counter["Me_core"]} and O count = {counter["O_core"]}')
    print(f'Percentage of atoms in surface region: {percentage}%')
    print(f'Percentage of Me atoms in surface region: {percentage_Me}%')
    print()

def find_coord(input_data, atom_type = 'all', shell_depth = 0.5):
    coords = gen_analysis_data([shell_depth], input_data, atom_type)
    print(f'\033[1mAvg. C.N. of {atom_type} atoms:')
    print(f'\033[0mIn nanoparticle: {float(coords[0][3]):.3}')
    print(f'In core region: {float(coords[0][1]):.3}')
    print(f'In shell region: {float(coords[0][2]):.3}')
    print()

def kneedle(distances, input_data, atom_type='all', show_graph = True):
    for_graph = gen_analysis_data(distances, input_data, atom_type)
    curve = [item[2] for item in for_graph]
    ypoints = [item[0] for item in for_graph]
    #print(ypoints)
    #print(curve)
    nPoints = len(curve)
    allCoord = np.vstack((ypoints, curve)).T
    np.array([ypoints, curve])
    firstPoint = allCoord[0]
    lineVec = allCoord[-1] - allCoord[0]
    lineVecNorm = lineVec / np.sqrt(np.sum(lineVec**2))
    vecFromFirst = allCoord - firstPoint
    scalarProduct = np.sum(vecFromFirst * npm.repmat(lineVecNorm, nPoints, 1), axis=1)
    vecFromFirstParallel = np.outer(scalarProduct, lineVecNorm)
    vecToLine = vecFromFirst - vecFromFirstParallel
    distToLine = np.sqrt(np.sum(vecToLine ** 2, axis=1))
    idxOfBestPoint = np.argmax(distToLine)
    if show_graph:
        plt.xlabel('Shell depth (nm)', fontsize=16)
        plt.ylabel(f'Avg. C.N. of {atom_type} atoms', fontsize=16)
        plt.plot(ypoints,curve)
        plt.show()
    return ypoints[idxOfBestPoint]

def xyz_freeze_core(input_data, shell_depth = 0.5, Me_atom = 'Me', o_file_name= 'Freeze.xyz'):  
    f = open(o_file_name, "w")
    f.write(input_data[0][0]+'\n')
    f.write("XYZ file generated by Calc_shell_depth.ipynb with command to freeze atoms in the core region\n")
    np_size = max([input_data[i][-2] for i in range(2,len(input_data))])
    core_length = np_size - shell_depth
    for i in range(2,len(input_data)):
        # As atomtype is removed beforehand assign the atomtypes to match with original data
        if  input_data[i][0] == 2:
            atom = 'O'
        else:
            atom = Me_atom
        # Below we will make numbers into nice format (always having 4 decimal places)
        X = '{:.4f}'.format(round(float(input_data[i][1]),4))
        Y = '{:.4f}'.format(round(float(input_data[i][2]),4))
        Z = '{:.4f}'.format(round(float(input_data[i][3]),4))
        # Check if atom is in core ore shell. If in core add text for freezing the atom in calcs.
        if input_data[i][-2] < core_length:
            line = atom + ' ' + X + ' ' + Y + ' ' + Z + ' ! F  F  F\n'
            '''if input_data[i][0] == 'O':
                counter['O_core'] += 1
            else:
                counter['Me_core'] += 1'''
        else:
            line = atom + ' ' + X + ' ' + Y + ' ' + Z + ' ! T  T  T\n'
            '''if input_data[i][0] == 'O':
                counter['O_shell'] += 1
            else:
                counter['Me_shell'] += 1'''
        f.write(line)
    f.close()
