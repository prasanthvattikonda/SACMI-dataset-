""" Read binary files

The file structure is as follows:
/ Header / Length of DataRecord1 / DataRecord1
         / Length of DataRecord2 / DataRecord2
         / ...
         / Length of DataRecordX / DataRecordX

"""

import struct
import datetime
import numpy as np

### read DataRecord X (where X must be a positve integer) from file named fileName
### Output is: ['Date_Time', [P1_x - P1_y - P1_z - P2_x - P2_y - P2_z]]
def read_record(fileName, DataRecord):
    ptr = ptr_record(fileName)
    if (DataRecord in ptr[:, 0]) == True:
        ptr_pos = ptr[DataRecord-1,1]
        with open(fileName, mode='rb') as file:
            file.seek(ptr_pos)
            signal = read_signal(file)
            file.seek(6*8*4*2, 1) # Skip some unwanted data
            date_time = read_time(file)
            file.close()
        
        return([date_time, signal])
    else:
        print('DataRecord not contained in file')
        return(None)


### get the ptr. position at the beginning of each DataRecord in the file named fileName
### Output is: [X (DataRecord number) - ptr. position - dim of DataRecord in bytes]
def ptr_record(fileName):
    with open(fileName, mode='rb') as file:
        header = read_header(file)
        nCount = header[0]
        ptr = np.zeros((nCount, 3), 'i')
        i = 0
        while (i < nCount):
               ptr[i,0] = i + 1
               length = read_lengthData(file)
               ptr[i,2] = length
               ptr[i,1] = file.tell()
               file.seek(length, 1)
               i = i + 1
    
    file.close()
    return(ptr)


### read the header -- file is the pointer to the file named fileName
def read_header(file):
    fileContent = file.read(48)
    x = struct.unpack('i'*12, fileContent)
    return(x[4], x[6], x[7])


### read the length of the DataRecord -- file is the pointer to the file named fileName
def read_lengthData(file):
    fileContent = file.read(4)
    length = struct.unpack('i', fileContent)
    return(length[0])


### read the rescaled signals -- file is the pointer to the file named fileName
def read_signal(file):
    nrow = 75000
    ncol = 6
    signal = np.zeros((nrow, ncol), 'f')
    i = 0
    while (i < 6):
        j = 0
        while (j < nrow):
            fileContent = file.read(2)
            x = struct.unpack('h', fileContent)
            signal[j,i] = x[0]
            j = j + 1

        fileContent = file.read(6*4)
        y = struct.unpack('f'*6, fileContent)
        scale = ( y[2] / (y[0] - y[1]) ) / y[4]
        signal[:,i] = signal[:,i] * scale

        i = i + 1

    return(signal) 


### read the time stamp -- file is the pointer to the file named fileName
def read_time(file):
    fileContent = file.read(36)
    info = struct.unpack('iiibbhiHHHHHHHH', fileContent)
    time = datetime.datetime(info[7], info[8], info[10], info[11], info[12], info[13], info[14]*1000)
    return(time.isoformat(' '))

