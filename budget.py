#-
import LoRa_time_Power_TDMA

def calcUtilization(tasks): # parameter is a array of list [period,exe]
    # tasks are (exe,period)
    sum = 0
    for i in tasks:
        sum += i[1] / i[0]
    return sum

def calcUtilizationWithFixSG(tasks, fixSG):
    # tasks are (period,exe)
    newTasks = tasks
    for i in range(len(newTasks)):
        newTasks[i][1] += tasks[i][1] * fixSG
    return calcUtilization(newTasks)

def calcUtilWithNonUniformSG(tasksWithNonUniformSG): # tasksWithNonUniformSG : (period, exe, SG)
    # usual "tasks" are : (period, exe) but when we have non-uniform SG we have "tasksWithNonUniformSG" : (period, exe, SG)
    # in this state we assume we have tasks and each task is assigned with its certain SG
    newUtil = 0
    for i in range(len(tasksWithNonUniformSG)):
        newExe = tasksWithNonUniformSG[i][1] + (tasksWithNonUniformSG[i][1] * tasksWithNonUniformSG[i][2])
        newUtil += newExe / tasksWithNonUniformSG[i][0]
    return newUtil

def calcUtilWithSG_Sync(nodes):
    util = 0
    for node in nodes:
        syncTime = node.sync_num_per_period * (LoRa_time_Power_TDMA.sync_rec_time_on_air + LoRa_time_Power_TDMA.sync_ready_time_on_air)
        exeTimeInPeriod = node.effExe + (syncTime * node.sync_num_per_period)
        exeOnPeriod = exeTimeInPeriod / node.period
        util += exeOnPeriod
    return util 

def ifAddSgToNodeCanExtendLifeTimeOfNet(deadNode):
    if deadNode.sync_num_per_period == 0 : 
        return False
    else:
        return True
    


# ----------------------------   runing this module   ---------------------
if __name__ == "__main__": 
    # l1 = [[1,70],[1,87],[87,100],[1,97]]
    l1 = [[4,1],[5,1],[7,1],[3,1]]
    l2 = [[40,1,.5],[50,1,.2],[30,1,.7],[25,1,.1]]
    print("the old util is : ", calcUtilization(l2))
    print(" new util of L2 is : ", calcUtilWithNonUniformSG(l2))
    # print("utilization is : ", calcUtilization(l1))
    # res = checksufficientConditionNPEDF(l1,1)
    # print("result is : ", res)
    # print("old utilization is : ", calcUtilization(l1))
    # print("new util with fix SG is :",  calcUtilizationWithFixSG(l1,0.1))



