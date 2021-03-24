from math import sqrt
import numpy as np

def xyz2POSCAR(xyz_file_name, out_file_name='POSCAR',move_COM=True):
    xyz_file = xyz_file_name
    out_file = out_file_name
    def get_box(xyz_file):
        with open(xyz_file) as in_xyz:
            line1 = in_xyz.readlines()[1] 
            if 'Lattice="' in line1: # Lattice='"40.0 0.0 0.0 0.0 40.0 0.0 0.0 0.0 40.0"
                box =  line1.rstrip().split('"')[1].split()
                a = box[0:3]
                b = box[3:6]
                c = box[6:]
#        print(hello1)
            else:
                print ('Do you want to type by hand or use the default vaules ( 40 x 40 x 40) ?')
                check = input()
#            print('hello2')
                if  check == 'y' or check == 'Y':
                    a = [input('please enter a direction: '), '0.0', '0.0']
                    b = ['0.0', input('please enter b direction: '), '0.0']
                    c = ['0.0', '0.0',input('please enter c direction: ') ]
                else:
                    a = ['40.0', '0.0', '0.0'] 
                    b = ['0.0', '40.0', '0.0'] 
                    c = ['0.0', '0.0', '40.0'] 
        return a, b, c 

    # get the elements list 
    def get_total_ele(xyz_file):
        ele_list = []
        with open(xyz_file) as in_xyz:
            in_file = in_xyz.readlines()[2:]
            for line in in_file:
                ele_list.append(line.rstrip().split()[0])
        return list(set(ele_list))

# get the coordination for one specifix element 
    def get_coordinations(ele):
        line_list = []
        with open(xyz_file) as in_xyz:
            in_file = in_xyz.readlines()[2:]
            for line in in_file:
                line_s = line.rstrip().split()[0:8]
                if ele in line_s:
                    line_list.append(line_s)
        return line_list

# Get the number of each element 
    def get_num_ele(ele):
        return len(get_coordinations(ele))


    poscar = open(out_file, 'w')
    poscar.write('Converted_POSCAR\n1.0\n')
    i_x = 0 # Needed to move the NP if COM is 0,0,0
    i_y = 0
    i_z = 0
    for i in get_box(xyz_file):
        poscar.write('%s %s %s\n' %(i[0], i[1], i[2]))
        if float(i[0]) != 0:
            i_x = float(i[0])
        if float(i[1]) != 0:
            i_y = float(i[1])
        if float(i[2]) != 0:
            i_z = float(i[2])

# Write Elements line 
    for i in get_total_ele(xyz_file):
        poscar.write(i+' ')
    poscar.write('\n')

# Write elements numbers line 
    for i in get_total_ele(xyz_file):
        poscar.write(str(get_num_ele(i))+' ')

# Write Cartesian line 
    poscar.write('\nSelective Dynamics')
    poscar.write('\nCartesian\n')

# Finding the Center-Of-Mass
    XYZ = []
    for i in get_total_ele(xyz_file):
        for j in get_coordinations(i):
            XYZ.append([float(j[1]),float(j[2]),float(j[3])])
    points = np.array(XYZ)
    test = [[1] for i in range(len(points))]
    c = np.append(points,test,axis=1)
    COM = np.average(c[:,:3], axis=0, weights= c[:,3])
    mover = []
    
# Finding need for moving the Center-Of-Mass
    if sqrt(COM[0]**2+COM[1]**2+COM[2]**2) != sqrt((i_x/2)**2+(i_y/2)**2+(i_z/2)**2):
#        print(COM[0],COM[1],COM[2],'for box:',i_x/2,i_y/2,i_z/2)
        mover.append((i_x/2) - COM[0])
        mover.append((i_y/2) - COM[1])
        mover.append((i_z/2) - COM[2])
#        print(mover)
        
# Write Cooridination part 
    for i in get_total_ele(xyz_file):
        if len(mover) != 0 and move_COM:
#            print("ver1")
            for j in get_coordinations(i):
                poscar.write('%s %s %s %s %s %s\n' %(float(j[1])+mover[0], float(j[2])+mover[1], float(j[3])+mover[2], j[5], j[6], j[7]))
        else:
#            print("ver2")
            for j in get_coordinations(i):
                poscar.write('%s %s %s %s %s %s\n' %(j[1], j[2], j[3], j[5], j[6], j[7]))

    print(('Done! the POSCAR is named as %s') %(out_file))
