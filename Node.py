import LoRa_time_Power_TDMA
import drift 
import random
from enum import Enum


# ************   constants and definitions  *******************
max_collision_allowed = 3


class NodeTDMA(object):
    def __init__(self, node_id, node_period, payloadSize,assigned_timeSlot):
        self.node_id = node_id
        self.period = node_period
        self.payloadSize = payloadSize
        self.exe = self.calcExeFromPayload(payloadSize)
        self.alive = True
        self.TP = 17
        self.BW = 125000
        self.SF = 7
        self.arrival_time = random.randrange(0, node_period)  #this is the first sending time
        # self.ack = ack_stat.ack
        # self.defaultSG = 0.1 # default SG is safty guard that is assigned to node at the start of network time 
        # self.SG = SG
        # self.syncSG = syncSG
        # self.effExe = (self.exe * self.SG) + self.exe
        self.effExe = assigned_timeSlot * LoRa_time_Power_TDMA.time_slot
        self.syncExe = self.calcSyncExe()
        self.syncEffExe = (self.syncExe * self.syncSG) + self.syncExe
        self.total_correct_sent_msg = 0
        self.total_life_ms = 0  # this variable is in mili second 
        self.total_life_day = "0.000" # this variable is in days
        self.sync_num_per_period = 0 # it shows the number of sync per period that a node needs 

        self.battery = LoRa_time_Power_TDMA.Battery(100, 3)
        self.drift = drift.max_drift_per_crystal
        self.sync_flag = False
        self.sync_time_add = 0
        self.time = 0
        # self.stat = TDMA_Node_states.sleep  # this property will only assign with time trigger
        self.next_event_time = self.arrival_time  # this property will assign with sens_msg method

    def calcExeFromPayload(self,payloadSize):
        sendTime = LoRa_time_Power_TDMA.timeOnAir(payloadSize)
        recTime = LoRa_time_Power_TDMA.ack_time_on_air
        exe = sendTime + recTime
        return exe 

    def calcSyncExe(self):
        syncSendTime = LoRa_time_Power_TDMA.sync_ready_time_on_air
        syncRecTime = LoRa_time_Power_TDMA.sync_rec_time_on_air
        return (syncSendTime + syncRecTime)



    def lifeTimeDayUpdate(self):
        self.total_life_day = "{:.3f}".format(self.total_life_ms / (86400 * 1000))

    def updateSG_effExe(self, SG):
        self.effExe = (self.exe * SG) + self.exe
        


    


# ************   end of definitions    ************************


# class Node_states(Enum):
#     sleep = 1
#     sending = 2
#     receiving = 3
#     receive_stop = 4
#     dead = 5

# class ack_stat(Enum):
#     ack = 0
#     nak = 1
#     time_out = 2
#     nothing = 3

# class output_stat(Enum):
#     nothing = 0
#     send_start = 1
#     receive_start = 2
#     receive_stop = 3


# --------------------------------   TDMA Nodes -------------------------------------------------------------------

# class TDMA_Node_states(Enum):
#     sleep = 1
#     sending = 2
#     receiving = 3
#     receive_stop = 4
#     time_sync = 5
#     dead = 6




    # def wakeup(self, global_time):
    #     # if global_time == self.next_event_time:
    #     if self.stat == TDMA_Node_states.dead or self.alive == False:
    #         return -1
    #     elif self.stat == TDMA_Node_states.sleep:
    #         self.total_life = int(global_time/(24 * 60 * 60 * 1000))
    #         if self.node_battery.bat_charge < LoRa_time_Power_TDMA.sending_data_energy_consumption_curr(self.TP) + \
    #                 LoRa_time_Power_TDMA.receiving_energy_consumption_curr(self.BW):
    #             self.alive = False
    #             nx_t_plus = self.next_event_time_plus(global_time, TDMA_Node_states.dead)
    #             self.node_modify(global_time, TDMA_Node_states.dead, nx_t_plus, output_stat.nothing)
    #         else:
    #             if self.sync_flag == False:
    #                 nx_t_plus = self.next_event_time_plus(global_time, TDMA_Node_states.sending)
    #                 self.node_modify(global_time, TDMA_Node_states.sending, nx_t_plus, output_stat.send_start)
    #             else:
    #                 nx_t_plus = self.next_event_time_plus(global_time, TDMA_Node_states.receiving)
    #                 self.node_modify(global_time, TDMA_Node_states.receiving, nx_t_plus, output_stat.receive_start)

    #     elif self.stat == TDMA_Node_states.sending:
    #         self.total_life = int(global_time / (24 * 60 * 60 * 1000))
    #         nx_t_plus = self.next_event_time_plus(global_time, TDMA_Node_states.receiving)
    #         self.node_modify(global_time, TDMA_Node_states.receiving, nx_t_plus, output_stat.receive_start)
    #     elif self.stat == TDMA_Node_states.receiving:
    #         self.total_life = int(global_time / (24 * 60 * 60 * 1000))
    #         nx_t_plus = self.next_event_time_plus(global_time, TDMA_Node_states.receive_stop)
    #         self.node_modify(global_time, TDMA_Node_states.receive_stop, nx_t_plus, output_stat.receive_stop)
    #     elif self.stat == TDMA_Node_states.receive_stop:
    #         self.total_life = int(global_time / (24 * 60 * 60 * 1000))
    #         nx_t_plus = self.next_event_time_plus(global_time, TDMA_Node_states.sleep)
    #         self.node_modify(global_time, TDMA_Node_states.sleep, nx_t_plus, output_stat.nothing)

    # def next_event_time_plus(self, global_time, current_state):
    #     if current_state == TDMA_Node_states.dead:
    #         return LoRa_time_Power_TDMA.time_on_air
    #     elif current_state == TDMA_Node_states.sending:
    #         return LoRa_time_Power_TDMA.time_on_air
    #     elif current_state == TDMA_Node_states.receiving:
    #         return LoRa_time_Power_TDMA.ack_time_on_air
    #     elif current_state == TDMA_Node_states.receive_stop:
    #         return 0
    #     elif current_state == Node_states.sleep:
    #         if self.sync_flag == True :
    #             return self.sync_time_add
    #         else:
    #             plus_time = self.node_period - ((global_time - self.arrival_time) % self.node_period)
    #             return plus_time

    # def battery_charge_update(self, global_time):
    #     if self.stat == TDMA_Node_states.sleep:
    #         self.node_battery.bat_charge -= LoRa_time_Power_TDMA.sleep_energy_consumption_curr(self.time, global_time)
    #     elif self.stat == TDMA_Node_states.sending:
    #         self.node_battery.bat_charge -= LoRa_time_Power_TDMA.sending_data_energy_consumption_curr(self.TP)
    #     elif self.stat == TDMA_Node_states.receiving:
    #         self.node_battery.bat_charge -= LoRa_time_Power_TDMA.receiving_energy_consumption_curr(self.BW)

    # def node_modify(self, glob_time, stat, next_event_time_plus, output):
    #     self.battery_charge_update(glob_time)
    #     self.time = glob_time
    #     self.stat = stat
    #     self.next_event_time = glob_time + next_event_time_plus
    #     self.output_signal = output

    # def sync_time(self, sync_flag, sync_addition_time):
    #     self.sync_flag = sync_flag
    #     self.sync_time_add = sync_addition_time


