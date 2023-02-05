#-
import math
import csv
import sys
import LoRa_time_Power_TDMA 
import drift
import budget 
import Node
import os

# we have 4 type of scheduling
# 1- offline_timeSynced
# 2- offline_safetyGaurd
# 3- online_timeSynced_RM
# 4- online_safetyGaurd_RM
# 5- online_timeSynced_NPEDF
# 6- online_safetyGaurd_NPEDF
# in all types, timesynced means gateway send time sysnchronization to nodes periodicly based on crystal drift and


# # tasks = [[1028, 121], [1270, 121], [1452, 121]]


firstDeadNodeid = 0

def initialNodes():
    main_dir = r'D:\Course\PHD\UT\Papers\LoRa\Tool\Python\TimeCompTDMA_Aloha\TaskGenerator\TaskGenerator_same_exeTime\sampleTasks_1'
    os.chdir(main_dir) 
    fileName = "sample_task.csv"
    nodes = []
    with open(fileName,'r') as f :
        rows = f.readlines()            
        for row in rows:
            items = row.split(',')
            nodes.append(Node.NodeTDMA(int(items[0]),int(items[1]),int(items[2]),float(items[3]),float(items[4])))
    for i in range(len(nodes)):
        print("nodes id : {}, period : {}, payload : {}, sg : {}, syncsg : {} ".format(nodes[i].node_id,nodes[i].period,nodes[i].payloadSize,nodes[i].SG,nodes[i].syncSG))
    
     

def makeTaskListFromNodesofEffExe(nodes):
    """ 
        args:
            arg1: nodes
        returns:
            return1: task list with effective exe as a list [period,effExe]
    """
    taskList = []
    for node in nodes:
        period = node.period
        exe = node.effExe
        taskList.append([period, exe])
    return taskList

def makeTaskListFromOriginalExe(nodes):
    """ 
        args:
            arg1: nodes
        returns:
            return1: task list with original exe as a list [period,exe]
    """
    taskList = []
    for node in nodes:
        period = node.period
        exe = node.exe
        taskList.append([period, exe])
    return taskList

def minExe(tasks): # tasks are list of [period , effexe]
    """ 
        args:
            arg1: nodes
        returns:
            return1: minimum exe of all tasks 
    """
    exeTimes = []
    for task in tasks:
        exeTimes.append(int(task[1]))
    return min(exeTimes)

def checksufficientConditionNPEDF(tasks, ts):
    """
        this function check the ablity of NP-EDF

        "tasks" is tasks list and ts is timeslot and now we can assume that it is equal to exe
        tasks are (period,exe)
        sorting the tasks by period 

    """
    tasks.sort(key=lambda x: x[0])
    if budget.calcUtilization(tasks) <= 1:
        # print(" condition is met. ")
        for i in range(1, len(tasks)):
            L = tasks[0][0] + ts
            while(L < tasks[i][0]):
                sum = tasks[i][1]
                for j in range(i):
                    sum += math.floor((L - ts)/tasks[j][0]) * tasks[j][1] 
                if (L < sum):
                    print ("L is less than tasks demands")
                    return False
                L += ts 
        print(" L is greater than demands")
        return True
    else:
        print(" condition is missed; ")
        return False


def calcCurOfNode(node):
    """ 
        args:
            arg1: node
        returns:
            return1: total current usage of node 
            return2: number of needed synchronization per period 
    """
    # data_sending_cur = LoRa_time_Power_TDMA.sending_data_energy_consumption_curr(17) + LoRa_time_Power_TDMA.receiving_energy_consumption_curr(125)
    # sync_cur = LoRa_time_Power_TDMA.sending_ready_energy_consumption_curr()
    sync_num_per_period = drift.neededNumSync(node.period, node.exe, node.SG, node.syncEffExe)
    sync_energy_cur = (LoRa_time_Power_TDMA.sending_ready_energy_consumption_curr(node.TP) + \
        LoRa_time_Power_TDMA.receiving_ready_energy_consumption_curr(node.BW)) * sync_num_per_period
    sync_time = LoRa_time_Power_TDMA.sync_ready_time_on_air + LoRa_time_Power_TDMA.sync_rec_time_on_air
    # period = nodes[i].
    # exe = nodes[i][1]
    active_time_in_period = node.exe + (sync_num_per_period * sync_time)
    sleep_time_in_period = node.period - active_time_in_period
    sleep_cur = LoRa_time_Power_TDMA.sleep_energy_consumption_curr(0, sleep_time_in_period)
    exe_cur_per_period = LoRa_time_Power_TDMA.sending_data_energy_consumption_curr(node.TP) + \
        LoRa_time_Power_TDMA.receiving_energy_consumption_curr(node.BW)
    total_cur_usage_per_period = exe_cur_per_period + sync_energy_cur + sleep_cur
    return total_cur_usage_per_period, sync_num_per_period    


def updateNode_msg_life_sync(node):
    """
        args:
            arg1: node
        returns:
            it updates properties of node including : total_correct_sent_msg, total_life_ms, total_life_day, sync_num_per_period
    """
    bat = node.battery
    BP_in_mAms = bat.bat_charge # 3600 to convert hour to second and 1000 to convert second to milli sec
    (total_cur_usage_per_period, node.sync_num_per_period) = calcCurOfNode(node)
    # total_num_sent_msg_of_node = math.floor(BP_in_mAms / total_cur_usage_per_period)
    node.total_correct_sent_msg = math.floor(BP_in_mAms / total_cur_usage_per_period)
    node.total_life_ms = (node.total_correct_sent_msg * node.period)
    node.lifeTimeDayUpdate()

# def updateNode_msg_life_withZeroSync(node)

    
def whichNodeDeadFirst(nodes):
    minLife = sys.float_info.max 
    firstNodeID = -1
    for i in range(len(nodes)):
        if nodes[i].total_life_ms < minLife : 
            minLife = nodes[i].total_life_ms
            firstNodeID = i
    return minLife, firstNodeID


def updateNodesSG_calcNewNetLife(nodes):
    (netLife,candidNodeToExtSG) = whichNodeDeadFirst(nodes)
    print("candidate node to extend SG is : node[{}]".format(candidNodeToExtSG))
    tasks = makeTaskListFromNodesofEffExe(nodes)
    util = budget.calcUtilization(tasks)
    print("now util is : ",util)
    while(util <= 1 and checksufficientConditionNPEDF(tasks.copy(),minExe(tasks)) and\
             budget.ifAddSgToNodeCanExtendLifeTimeOfNet(nodes[candidNodeToExtSG]) ):
        (perfectSG, newExe, util) = drift.calcPerfectSG_newExe_newUtil(nodes[candidNodeToExtSG], util)
        nodes[candidNodeToExtSG].updateSG_effExe(perfectSG)
        updateNode_msg_life_sync(nodes[candidNodeToExtSG])
        print("candidate node to extend SG is : node[{}]".format(candidNodeToExtSG))
        print("now util is : ", util)
        tasks = makeTaskListFromNodesofEffExe(nodes)
        (netLife,candidNodeToExtSG) = whichNodeDeadFirst(nodes)

    if util > 1:
        print(" util is greater than 1 ")
    if not budget.ifAddSgToNodeCanExtendLifeTimeOfNet(nodes[candidNodeToExtSG]):
        print("number of sync per period of node[{}] is 0 ".format(candidNodeToExtSG))
    if not checksufficientConditionNPEDF(tasks.copy(),minExe(tasks)):
        print("sufficient condition of scheduling is failed ")
      

def offlineTimeSyncedFixSG(nodes):  
    # task_list is list of nodes, so has battery property and also has safty guard 
    # tasks is a 2d array [[period,exe]]
    nodeExe = nodes[0].effExe
    taskList = makeTaskListFromNodesofEffExe(nodes)
    if checksufficientConditionNPEDF(taskList.copy(), nodeExe) == False:
        return -1
    else: 
        node_res = []
        for i in range(len(nodes)):
            # bat = task_list[i].battery
            # BP_in_mAms = bat.bat_charge # 3600 to convert hour to second and 1000 to convert second to milli sec
            # (total_cur_usage_per_period, sync_num_per_period) = calcCurOfNode(task_list[i],safty_guard)
            # total_num_sent_msg_of_node = math.floor(BP_in_mAms / total_cur_usage_per_period)
            # (life_time_of_node_in_ms, total_num_sent_msg_of_node, sync_num_per_period ) = 
            updateNode_msg_life_sync(nodes[i])
            node_res.append([nodes[i].total_correct_sent_msg, nodes[i].total_life_day, nodes[i].sync_num_per_period])
        return node_res

# def offlineSyncedFixSGScheduleTasks_and_syncs(nodes):
#     tasks = makeTasks(nodes)
#     for task in tasks:
#         neededSync = drift.neededNumSync(node.period, node.exe, node.SG, node.)
#         sync_task()
    



# ----------------------------   runing this module   ---------------------
if __name__ == '__main__':
    initialNodes()
    # nodes = []
    # # get nodes from a csv file
    # dir = r'D:\Course\PHD\UT\Papers\LoRa\Tool\Python\TimeCompTDMA_Aloha\TaskGenerator\TaskGenerator_same_exeTime\sampleTasks'
    # file = '\\sampleTasks.csv'
    # in_path = dir + file 
    # with open(in_path, 'r') as input_nodes:
    #     node_reader = csv.reader(input_nodes, delimiter=',')
    #     No_nodes = 0
    #     for row in node_reader:
    #         if len(row) == 0:
    #             break
    #         N_id = int(row[0])
    #         period = int(row[1])
    #         payload = int(float(row[2]))
    #         sg = float(row[3])
    #         nodes.append(Node.NodeTDMA(N_id,period,payload,sg))
    #         No_nodes += 1







    # print("[result of scheduling ### before modification of first dead node ### \
    #      total number of msg, life time of node in day, needed No of sync per period]\n", offlineTimeSyncedFixSG(nodes))
    # (netLifeTime,firstDeadNodeId) = whichNodeDeadFirst(nodes)
    # taskListOfEffExe = makeTaskListFromNodesofEffExe(nodes) # tasklist is a list of [period, exeWithSG]
    # taskListOfOrigExe = makeTaskListFromOriginalExe(nodes) # tasklist is a list of [period, exe]
    # print("the life time of network in ms is : ", netLifeTime, " and first dead node is : ", firstDeadNodeId)
    # print("is it possible to extend the life time of network : ", budget.ifAddSgToNodeCanExtendLifeTimeOfNet(nodes[firstDeadNodeId]))
    # print("utilization of effective exe time of task list is : ", \
    #     budget.calcUtilization(taskListOfEffExe),\
    #         "\n and utilization of original tasks is : ", budget.calcUtilization(taskListOfOrigExe))
    # (perfectSG, newExe, newUtil) = drift.calcPerfectSG_newExe_newUtil(nodes[firstDeadNodeId],budget.calcUtilization(taskListOfEffExe))
    # print("perfectSG, newExe, newUtil of first dead node is : ", perfectSG, newExe, newUtil)
    
    # updateNodesSG_calcNewNetLife(nodes)
    # print("[result of scheduling $$$$ after modification all dead node $$$$\
    #     total number of msg, life time of node in day, needed No of sync per period]\n", offlineTimeSyncedFixSG(nodes))
    # (newNetLifeTime,newFirstDeadNodeId) = whichNodeDeadFirst(nodes)
    # print("new lifetime of network is : ", newNetLifeTime, " and dead node id is : ", newFirstDeadNodeId)
    








    # out_path = dir + "\\TDMA_out\\out1t.csv"
    # # with open("D:\\Course\\PHD\\UT\\Papers\\LoRa\\Tool\\Python\\TimeCompTDMA_Aloha\\System\\TDMA_output_nodes.csv", 'w') as output_nodes:
    # with open(out_path, 'w') as output_nodes:    
    #     node_writer = csv.writer(output_nodes, delimiter=',')
    #     header = ['node id', 'total No of sent msg', 'life time of node', 'needed sync of nodes']
    #     print("header is : ", header)
    #     node_writer.writerow(header)
    #     row = []
    #     for i in range(len(nodes)):
    #         row.append(i)
    #         row.append(schedule_result[i][0])
    #         row.append(schedule_result[i][1])
    #         row.append(schedule_result[i][2])
    #         node_writer.writerow(row)
    #         row.clear()






