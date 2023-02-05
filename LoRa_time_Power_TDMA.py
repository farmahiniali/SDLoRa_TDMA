# this module is about LoRa time on air calculation and power consumption in sleep or sending situation

from math import ceil

time_slot = 64
Node_PL = 125 # node_payload_size in byte
def setPayload (N_PL):
    global Node_PL 
    Node_PL = N_PL
Ack_PL = 13 # payload size of ack to message of node; from gateway to node 
sync_PL = 11 # payload size of sync message from gateway to node
sync_ready_PL = 5 # payload size of ready message from node to gateway to annouce ready to get time 

    
    # -------------- constants -----------------
safety_guard = 0.1 # when the config is fix, sf/bw=7/125, so exe time is fix
node_sleep_cur = 0.0001  # mA  --> node sleep current is 100nA
SF = 7
BW = 125000
TP = 17
CR = 1  # coding rate can be 5/4 to 8/4 CR=1 means 5/4 and CR=4 means 8/4
H = 1  # header is 0 when there is header and is 1 when there isn't header
DE = 0 # 1 when the low data rate optimization is enabled , DE = 0 for disabled.
# crc is enabled in my time calculation formulation 
No_preamble_symbol = 2

# ------ time on air calculation -----------------------
def symbolTime(sf,bw):
    return (2**sf)/bw

def preambleTime(noPreambleSymbole,sf,bw):# output is time in sec 
    timeSymbole = symbolTime(sf,bw)
    T_Preamble = (noPreambleSymbole + 4.25) * timeSymbole  # time unit is  second 
    return  T_Preamble  

def payloadTime(payload,sf,bw,H,CR):# output is time in sec
    N_payload_symbol = 8 + max(ceil(((8 * payload) - (4 * sf) + 16 + 28 - (20 * H))/(4 * (sf - 2 * DE))) * (CR + 4), 0)  # N stands for Node
    #N_payload_symbol = 8 + max(ceil(((8 * payload) - (4 * sf) + 16 + 28 - (20 * H))/(sf - 2 * DE)) * (8 / (CR + 4)), 0)  # N stands for Node
    T_PL = N_payload_symbol * symbolTime(sf,bw)  # time unit is  second
    return T_PL

def timeOnAir(payload,noPreambleSymbole=No_preamble_symbol, sf=SF,bw=BW,H=H,CR=CR) : # output is time in ms 
    T_PL = payloadTime(payload,sf,bw,H,CR)
    T_preamble = preambleTime(noPreambleSymbole,sf,bw)
    return (T_PL + T_preamble) * 1000  # time unit is milli second

# ----------- time on air of messages -----------------------

time_on_air = timeOnAir(Node_PL, No_preamble_symbol, SF, BW, H, CR) # time to send message from node to gateway
ack_time_on_air = timeOnAir(Ack_PL, No_preamble_symbol, SF, BW, H, CR) # time to get ack from gateway to node
sync_rec_time_on_air = timeOnAir(sync_PL,No_preamble_symbol, SF, BW, H, CR) # time to get sync message from gateway to node
sync_ready_time_on_air = timeOnAir(sync_ready_PL, No_preamble_symbol, SF, BW, H, CR) # time to send ready message from node to gateway 

# -------- Semtec SX1272 receiving energy consumption ----------------
# -------- this items are based on LoRa modem calculator tool -----


def lora_transmit_current(TP):  # unit is mA
    if 0 <= TP <= 20:
        transmit_cur = [22, 23, 24, 24, 24, 25, 25, 25, 25, 26, 31, 32, 34, 35, 44, 82, 85, 90, 105, 115, 125]
        return transmit_cur[int(TP)]
    else:
        return -1


def lora_receive_current(BW):  # unit is mA
    if int(BW) == 125000:
        return 10.8
    elif int(BW) == 250000:
        return 11.6
    elif int(BW) == 500000:
        return 13
    else:
        return -1


node_sleep_current_usage = 0.0000001  # unit is Amper
node_transmission_power_17dbm = 50  # transmission unit is mW and is equivalent to 17 dbm
node_transmission_power_20dbm = 100  # transmission unit is mW and is equivalent to 20 dbm


# ------- power consumption ---------------------------

Battery_volt = 3  # default battery voltage is 3 volt


class Battery:
    def __init__(self, bat_cap=1000, bat_volt=3):  # capacity unit is mAH and bat_volt unit is volt
        self.bat_cap = bat_cap
        self.bat_volt = bat_volt
        self.bat_charge = self.bat_cap * 3600 * 1000  # unit is turned into milli amper mili second
        # self.bat_energy = self.bat_charge * self.bat_volt  # energy unit is milli joule


def sleep_energy_consumption_curr(sleep_start_time, sleep_end_time):  # time unit is ms and sleep mode is bool
    duration = sleep_end_time - sleep_start_time
    energy_usage_curr = duration * node_sleep_cur  # the unit is milli amper milli second
    return energy_usage_curr


# def sending_energy_consumption_curr(TP):
#     energy_usage_curr = time_on_air * lora_transmit_current(TP)  # energy unit is milli amper per milli second
#     return energy_usage_curr  # energy unit is milli joule


# def synchronization_energy_consumption_curr(TP, BW):
#     return ((T_Preamble * 1000) * lora_transmit_current(TP)) + (sync_rec_time_on_air * lora_receive_current(BW))


# def sychronization_active_time():
#     return (T_Preamble * 1000) + sync_rec_time_on_air


def sleep_energy_consumption_curr(sleep_start_time, sleep_end_time):  # time unit is ms and sleep mode is bool
    duration = sleep_end_time - sleep_start_time
    energy_usage_curr = duration * node_sleep_cur  # the unit is milli amper milli second
    return energy_usage_curr


def sending_data_energy_consumption_curr(TP):
    energy_usage_curr = time_on_air * lora_transmit_current(TP)  # energy unit is milli amper
    return energy_usage_curr  # energy unit is milli joule


def sending_ready_energy_consumption_curr(TP):
    energy_usage_curr = sync_ready_time_on_air * lora_transmit_current(TP)  # energy unit is milli amper
    return energy_usage_curr  # energy unit is milli joule


def receiving_energy_consumption_curr(BW):
    return lora_receive_current(BW) * ack_time_on_air


def receiving_ready_energy_consumption_curr(BW):
    return lora_receive_current(BW) * sync_rec_time_on_air

# def new_exe_to_use_util(node_period, node_exe, util):
    # this function calculate new exe to use remaining utillization to convert util to 1. for example when util is 60%
    # and e1/p1 + e2/p2 + e3/p3 = util and we focus just on e1,p1 and we can use to remaining util to make util = 1
    # e1/p1 = 5 /100 + other e/p = 60% => e1' = (e1/p1 + (1 - U)) * p1 =>    ****  e1' = e1 + p1 - U*p1   ***** 





# ----------------------------   runing this module   ---------------------
if __name__ == "__main__":
    #setPayload(120)
    print("node payload size is : ", Node_PL)
    print ("time on air for ",Node_PL," byte payload is : ", time_on_air)
    print ("time on air for ",Ack_PL," byte ack is : ", ack_time_on_air)
    print("**** so the time of exe of a message with ",Node_PL," byte messsage and ack size ",Ack_PL,"size is **** : ", (time_on_air + ack_time_on_air),'\n')
    x = 4
    print("since exe time is",x , " times of time-slot so the result sg is : ", ((x * time_slot)/ (time_on_air + ack_time_on_air))-1, "\n")
    print ('energy usage of sending such message is : ', sending_data_energy_consumption_curr(TP) + receiving_energy_consumption_curr(BW),"mAms\n\n")
    print ("time on air for ",sync_ready_PL," byte ready is : ",sync_ready_time_on_air)
    print ("time on air for ",sync_PL ," byte receive by node to sync is : ", sync_rec_time_on_air)
    print ("**** so the time of such sync ready plus rec sync is **** : ", (sync_ready_time_on_air + sync_rec_time_on_air))
    print ("so the sg for sync is : ",(time_slot / (sync_ready_time_on_air + sync_rec_time_on_air)) -1, "\n\n")
    print ('energy usage of sync is : ', sending_ready_energy_consumption_curr(TP) + receiving_ready_energy_consumption_curr(BW),"mAms\n")
