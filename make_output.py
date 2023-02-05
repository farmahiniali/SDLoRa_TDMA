# - 
import os 
import re
import csv 
import Node
import scheduling

# main_dir = r'D:\Course\PHD\UT\Papers\LoRa\Tool\Python\TimeCompTDMA_Aloha\TaskGenerator\TaskGenerator_same_exeTime'
main_dir = r'D:\Course\PHD\UT\Papers\LoRa\Tool\Python\TimeCompTDMA_Aloha\TaskGenerator\TaskGenerator_same_exeTime\sampleTasks_few'
os.chdir(main_dir)
all_folders = os.listdir()
# pat = r'sampleTasks-SG0.{2}'
pat = r'SG_0.5'
sample_folders = []
for i in all_folders:
    tmp = re.findall(pat,i)
    if len(tmp) > 0:
        sample_folders.append(tmp)
# now we have sample folders name 
file_pat = r'[\d].*'
for folder in sample_folders:
    path = main_dir + '\\' + str(folder[0])
    os.chdir(path)
    # os.getcwd()
    files = os.listdir()
    files = files[:len(files)-2] # with this we remove sub directories frome list of dir
    for i in files:
        file_path = path + '\\' + i
        nodes = []
        task_exist = True
        with open(file_path, 'r') as input_nodes:
            node_reader = csv.reader(input_nodes, delimiter=',')
            No_nodes = 0
            for row in node_reader:
                if len(row) == 0 :
                    break
                if row[0] == " operation was unsuccessful !!! ":
                    task_exist = False
                    break
                N_id = int(row[0])
                exe = int(float(row[1]))
                period = int(row[2])
                nodes.append(Node.NodeTDMA(N_id,period,exe))
                No_nodes += 1
        if task_exist == False:
            task_exist = True
            continue
        schedule_result = scheduling.offline_timeSynced(nodes,0.5)
        out_path = path + '\\TDMA\\' + i
        with open(out_path, 'w') as output_nodes:    
            # node_writer = csv.writer(output_nodes, delimiter=',')
            # header = ['node id', 'total No of sent msg', 'life time of node', 'needed sync of nodes']
            # print("header is : ", header)
            # node_writer.writerow(header)
            for i in range(len(nodes)):
                row = str(i) + ',' + str(schedule_result[i][0]) + ',' + str(schedule_result[i][1]) + ',' + str(schedule_result[i][2]) +'\n'
                output_nodes.writelines(row)




