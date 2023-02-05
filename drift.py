
import math
import Node
import LoRa_time_Power_TDMA


max_drift_per_crystal = 2  # the unit is PPM
crystal_freq_in_MHz = 865  # unit is MHz
err_in_each_sec = (max_drift_per_crystal * crystal_freq_in_MHz) / 1000000 
errInEachSecChangeToMS = err_in_each_sec / 1000

def modify_drift_by_temperature(temperature):
    if temperature < -20 or temperature > 60:
        return -1000
    else:
        normal_temperature = 25
        diff_temperature_to_normal = temperature - normal_temperature
        return diff_temperature_to_normal * 10 / 25


def timeToGetErrOf(deadlineOfSGinMs) : # deadlineOfSGinMs is our deadline before get error which is made by SG and this func retun in ms 
    return deadlineOfSGinMs / errInEachSecChangeToMS


def accepatableErrDriftSG(nodeExe, SG):
    return (nodeExe * SG) / 2 # this value present amount of error that is accptable,
    # safty guard is percent of exe time 
    # we divide it by 2 because we must consider plus/minus of this error and unit is ms


def timeToGetErrByDriftInSG(nodeExe, SG):
    acceptableErr = accepatableErrDriftSG(nodeExe, SG)
    timeToGetErr = timeToGetErrOf(acceptableErr)
    return(timeToGetErr)



def neededNumSync(nodePeriod, nodeExe, SG,nodeSyncExe):
    # if time of the period is small enough such that before SG/2 ,node get time and ack of gateway ,so there is no need to sync 
    timeToGetErr = timeToGetErrByDriftInSG(nodeExe, SG)
    if timeToGetErr >= nodePeriod:
        return 0  # , 0  # means to need to sync before next period, and there is not time to get error
    else:
        baseNeed = math.floor(nodePeriod / timeToGetErr) + 1 
        # this is only true when time of difference between first release and time to get error is greater than needed time to 
        # exe of sync 
        syncPeriod =  nodePeriod / (baseNeed + 1) # for example when we need 3 times to sync node, so we must devide period of exe divide by 3 + 1
        diffBasePeriod_timeToGetErr = timeToGetErr - syncPeriod
        if diffBasePeriod_timeToGetErr >= (2 * nodeSyncExe):
            return baseNeed
        else:
            # we have the smallest sync period when difference between release time and deadline which is 
            # time to get error is equal to (2 * sync exe time) so : 2*nodeSyncExe = timeToGetErr - syncPeriod => 
            # syncPeriod = timeToGetErr - (2*nodeSyncExe) => baseNeed + 1 = nodePeriod / (timeToGetErr - (2*nodeSyncExe))
            baseNeed = math.ceil((nodePeriod / (timeToGetErr - (2*nodeSyncExe))) - 1)  
            return baseNeed

def syncPeriodRelativeToPeriod(nodePeriod, nodeExe, SG,nodeSyncExe):
    # this period is start by start of period and counted between start and end of period
    numSync = neededNumSync(nodePeriod, nodeExe, SG, nodeSyncExe)
    syncPeriod =  nodePeriod / (numSync + 1) # for example when we need 3 times to sync node, so we must devide period of exe divide by 3 + 1 
    return syncPeriod


def diffRelativePeriod_timeToGetErr(nodePeriod, nodeExe, SG, nodeSyncExe):
    timeTogetErr = timeToGetErrByDriftInSG(nodeExe,SG)
    relativePeriod = syncPeriodRelativeToPeriod(nodePeriod, nodeExe, SG, nodeSyncExe)
    return (timeTogetErr - relativePeriod)

# def itItUsefulToUseRemainedUtilForExtSG(tasks, util):
#     if 

def calcPerfectSG_newExe_newUtil(node, util):
    if node.sync_num_per_period <= 0:
        return -1,-1,-1
    else :
        #timeToGetErr = [((exe * SG)/2) / errInEachSecConvertToMS] = period ,from this formula we can calculate
        # an SG whose exe no need to sync. so we have perfectSG =  note, err_in_each_sec unit is sec and we turn it into ms 
        perfectSG = (node.period * errInEachSecChangeToMS * 2) / node.exe + 1 # the unit is still ms 
        newExe = (node.exe * perfectSG) + node.exe
        print("new exe is : ", newExe)
        oldExe = node.effExe
        newUtil = calNewUtilByChangeJustOneExe(node.period, oldExe, newExe, util)
        return perfectSG, newExe, newUtil

def isThereEnoughUtilToExtendSG(node, util):
    (perfectSG, newExe, newUtil) = calcPerfectSG_newExe_newUtil(node, util)
    if newUtil > 1 :
        return False 
    else:     
        return True


def calNewUtilByChangeJustOneExe(nodePeriod, oldNodeExe,newNodeExe, util):
    # e1/p1 + e2/p2 + e3/p3 + ... = U, we call e2/p2 + ... = U1 so e1/p1 + U1 = U and new util can be calculated
    # newUtil = U1 + newExe/nodePeriod
    U1 = util - (oldNodeExe / nodePeriod)
    newUtil = U1 + (newNodeExe / nodePeriod)
    return newUtil


def howMuchExeOfOneTaskCanBeExtToUseAllRemainedUtil(nodePeriod, nodeExe, util):
    # e1/p1 + e2/p2 + e3/p3 + ... = U, we call e2/p2 + ... = U1 so e1/p1 + U1 = U = 1 so e1 can extend to (1 - U1)P1
    # in this func nodePeriod is p1 and nodeExe is e1 and Util is U
    U1 = util - (nodeExe / nodePeriod)
    amountOfExtendedExe = (1 - U1) * nodePeriod
    return  amountOfExtendedExe


# def schedulabilityTestAfterAddingNewSG()




# ----------------------------   runing this module   ---------------------
if __name__ == "__main__":
    n_pl = 125
    n_period = 700000
    eN = Node.NodeTDMA(0,n_period,n_pl,0.094,0.1) # example node of NodeTDMA(id,period, paylad,sg,syncSG)
    LoRa_time_Power_TDMA.setPayload(eN.payloadSize)
    print("utilization of exe of payload ",n_pl," and period of ", n_period, " is : ", eN.exe/eN.period)
    print("the time to get error is : {:,.2f} ms".format(timeToGetErrByDriftInSG(eN.exe,eN.SG)))
    print( "the number needed of sync: ", neededNumSync(eN.period,eN.exe,eN.SG,eN.syncEffExe))  
    # print("is it possible to extend exe of node: ", isThereEnoughUtilToExtendSG(30000,121,0.1,0.6))
    print("now exe time is :** {:,.2f} ** and period is : ## {:,} ## and effective exe is : ** {:,.2f} ** and \n\
          sync time is : ## {:,.2f} ## and effective sync exe time is : ** {:.2f} **".format(eN.exe, eN.period,eN.effExe,eN.syncExe,eN.syncEffExe))
    print("the relative period is {:,.2f} and time of different between relative period and time to get error is : {:,.2f}"\
        .format(syncPeriodRelativeToPeriod(eN.period,eN.exe,eN.SG,eN.syncEffExe),diffRelativePeriod_timeToGetErr(eN.period,eN.exe,eN.SG,eN.syncEffExe)))
    print("how much exe of node can be extended: {:,.2f}".format(howMuchExeOfOneTaskCanBeExtToUseAllRemainedUtil(eN.period, eN.exe,0.6)))

