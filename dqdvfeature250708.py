import os
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import scipy.integrate as integrate

def dQdV(file, q_rate):
    d1 = pd.read_csv(file)[["Cycle_Number", "Voltage_V", "Current_mA","Time_s","Capacity_mAh"]]
    Vgrid = np.arange(4.2, 3.2, -0.01)
    Qgrid = np.arange(0, 1, 0.01)
    Qpdf = np.array([])
    Vpdf = np.array([])
    Cycle_count = np.array([])
    Q_limited_list = np.array([])
    maxV = np.array([])
    maxVpos = np.array([])

    for name, group in d1.groupby('Cycle_Number'):
        Vd = group.Voltage_V.values # + d1.Current.values 0.065/1000 
        Id = -group.Current_mA.values
        time = group.Time_s.values
        time = time - time[0]
        Qd = 1 - (integrate.cumulative_trapezoid(Id, x=time, initial=0)/(3600*q_rate))
        if np.size(Vd) > 0:
            Q = np.flip(np.interp(Vgrid, np.flip(Vd), np.flip(Qd)))
            Qpdf = np.append(Qpdf, Q)
            Q_limited_list = np.append(Q_limited_list, Qpdf[-1] - Q[0])
            maxV = np.append(maxV, np.max(dQdV))
														idx = np.argmin(np.abs(dQdV - np.max(dQdV))
            maxVpos = np.append(maxVpos, Vgrid[idx])

            cycle_number = int(name)
            Cycle_count = np.append(Cycle_count, cycle_number)
            Vpdf = np.append(Vpdf, Vgrid)
            debug_break = True

    Qplot = np.reshape(Qpdf,(-1,np.size(Vgrid))) #verify Q plot

    Qplot_odd = (Qplot-np.fliplr(Qplot))/2
    Qplot_even = (Qplot+np.fliplr(Qplot))/2

    dQdV_odd = integrate. cumulative_trapezoid(Qplot_odd[:,int(Qplot_odd.shape[1]/2):], initial=0)
    dQdV_even = np.mean(Qplot_even, axis=1) #confirm its same as cycle count

    return maxV, maxVpos, Cycle_count, Q_limited_list

#energy odd 
def Q_odd(file, q_rated):
    d1 = pd.read_csv(file)[["Cycle_Number", "Voltage_V", "Current_mA", "Time_s", "Capacity_mAh"]]

    Vgrid = np.arange(3.2, 4.2, 0.01)
    Qgrid = np.arange(0, 1, 0.01)
    Qpdf= np.array([])
    Vpdf = np.array([])
    Cycle_count = np.array([])
    Q_limited_list = np.array([])
    maxV= np.array([])
    maxVpos = np.array([])
    
    for name, group in d1.groupby("Cycle_Number"):
        Vd = group.Voltage_V.values # + dl.Current.values*0.065/1000 
        Id = -group.Current_mA.values 
        time = group.Time_s.values 
        time = time - time[0] 
        Qd = 1 - (integrate.cumulative_trapezoid(Id, x=time, initial=0)/(3600*q_rated)) 
        if np.size(Vd)> 0 :
            Q = np.flip(np.interp(Vgrid,np.flip(Vd),np.flip(Qd)))
            Qpdf = np.append(Qpdf,Q) 
            Q_limited_list = np.append(Q_limited_list, Q[0] - Q[-1])

            #calculate dQdV for maxVpos
            dQdV = np.diff(Q)
            maxV = np.append(maxV, np.max(dQdV))
            idx = np.argmin(np.abs(dQdV- np.max(dQdV)))
            maxVpos = np.append(maxVpos, Vgrid[idx])

            cycle_number = int(name)
            Cycle_count = np.append(Cycle_count, cycle_number)
            debug_break = True

    Qplot = np.reshape(Qpdf,(-1,np.size(Vgrid))) #verify Q plot

    Qplot_odd = (Qplot-np.fliplr(Qplot))/2
    Qplot_even = (Qplot+np.fliplr(Qplot))/2

    energy_odd = 3.6 * integrate.trapezoid(np.abs(Qplot_odd), x=Vgrid)
    energy_even = 3.6 * integrate.trapezoid(Qplot_even, x=Vgrid)

    return energy_odd, maxVpos, Cycle_count, Q_limited_list

#dataset = TRAIN_SET
def getGC(dataset, dataset_probe):
    capacity_list = np.array([])
    cycle_count = np.array([])
    voltage_list = np.array([])
    
    cycle_count_running = np.array([])
    
    for key, keyp in zip(list(dataset.keys()), list(dataset_probe.keys())):
        print(key, keyp, dataset_probe[keyp][1])
        file = os.path.join(dataset_probe[keyp][0], keyp)
        q_rated = dataset[key][1]
        file_running = os.path.join(dataset[key][0], key)
        # get the running cycle
        ds_running = pd.read_csv(file_running)[["Cycle_Number", "Voltage_V", "Current_mA", "Time_s", "Capacity_mAh"]]
        for name, group in ds_running.groupby('Cycle_Number'):
            cycle_count_running = np.append(cycle_count_running, int(name))
            # prob cycle
            ds = pd.read_csv(file)[["Cycle_number", "Voltage_V", "Current _mA", "Time_s", "Capacity_mAh"]]
            
            for name, group in ds.groupby("Cycle_Number"):
                voltage_list = np.append(voltoge_list, group.Voltage_V.values[0])
                cycle_count = np.append(cycle_count, int(name))
                capacity_list = np.append(capacity_list, group.Capacity_mAh.values[-1]/q_rated)
            
    # filter capacity, cycle
    filter_idx_list = np.where(voltage_list > 4.48715)
    capacity_list = capacity_list[filter_idx_list]
    cycle_count = cycle_count[filter_idx_list]
    plt.scatter(cycle_count[2:], capacity_list[2:])

    # linear fit
    coe = np.polyfit(cycle_count[2:], capacity_list[2:], 1)
    print(coe)

    #calculate capacity at each running cycle
    mod_cap_list = np.array([])
    for cycle in cycle_count_running:
        mod_cap_list = np.append(mod_cap_list, coe[0] * cycle + coe[1])
    plt.plot(cycle_count_running, mod_cap_list)
    plt.scatter(cycle_count, capacity_list)
#return cycle_count_running, mod_cap_list

# probe capacity
def getProbeCap(file, q_rated, file_running):
    # get the running cycle
    ds_running = pd.read_csv(file_running)[["Cycle_Number", "Voltage_V", "Current_mA", "Time_s", "Capacity_mAh"]]
    cycle_count_running = np.array([])

    for name, group in ds_running.groupby('Cycle_Number'):
        cycle_count_running = np.append(cycle_count_running, int(name))

    # prob cycle
    ds = pd.read_csv(file)[["Cycle_Number", "Voltage_V", "Current_mA", "Time_s", "Capacity_mAh"]]

    capacity_list = np.array([])
    cycle_count = np.array([])
    voltage_list = np.array([])

    for name, group in ds.groupby('Cycle_Number'):
        voltage_list = np.append(voltage_list, group.Voltage_V.values[0])
        cycle_count = np.append(cycle_count, int(name))
        capacity_list = np.append(capacity_list, group.Capacity_mAh.values[-1])
   
    percentile_80 = np.percentile(voltage_list, 80)
    percentile_50 = np.percentile(voltage_list, 50)
    print(percentile_80)
    print(percentile_50)

    # filter capacity, cycle
    filter_idx_list = np.where(voltage_list > 4.48715)
    capacity_list = capacity_list[filter_idx_list]
    cycle_count = cycle_count[filter_idx_list]
    plt.scatter(cycle_count[2:], capacity_list[2:])

    # linear fIt

    coe = np.polyfit(cycle_count[2:], capacity_list[2:], 1)
    print(coe)

    # calculate capacity at each running cycle
    mod_cap_list = np.array([])
    for cycle in cycle_count_running:
        mod_cap_list = np.append(mod_cap_list, coe[0] * cycle + coe[1])
    
    plt.plot(cycle_count_running, mod_cap_list)
    plt.scatter(cycle_count, capacity_list)

    return cycle_count_running, mod_cap_list

# probe capacity
def getProbeGCcap(file, q_rated, coeef, file_running):
    # get the running cycle
    ds_running = pd.read_csv(file_running)[["Cycle_Number", "Voltage_V", "Current_mA", "Time_s", "Capacity_mAh"]]
    
    cycle_count_running = np.array([])
    mod_cap_list = np.array([])
    for name, group in ds_running.groupby('Cycle_Number'):
        cycle_count_running = np.append(cycle_count_running, int(name))
        mod_cap_list = np.append(mod_cap_list, int(name) * coeef[0] + coeef[1])
    print("getProbeGCcap", mod_cap_list.shape)
    return cycle_count_running, mod_cap_list
    
    
if __name__ == "__main__":
    TRAIN_SET = {
        "ch09_SaveData_concatenated_p22_discharge_s3.csv":["../../data/processed/Dataset_A1_profile/A1_MP1_4500mAh_T23/", 4500],
      "ch10_SaveData_concatenated_p22_discharge_s3.csv":["../../data/processed/Dataset_A1_profile/A1_MP1_4500mAh_T23/", 4500]
    }

    TEST_SET = {
        "ch19_SaveData_concatenated_p22_discharge_s3.csv":["../../data/processed/Dataset_A1_profile/A1_MP2_4470mAh_T23/", 4470], 
        "ch06_SaveData_concatenated_p22_discharge_s3.csv":["../../data/processed/Dataset_A1_profile/A1_MP2_4470mAh_T23/", 4470] 
    }

    data = []

    for key in list(TRAIN_SET.keys()):
        dqdv, dqdv_pos, cyc, q_capacity = dQdV(os.path.join(TRAIN_SET[key][0], key), TRAIN_SET[key][1])
        q_odd, _, _, _ = Q_odd(os.path.join(TRAIN_SET[key][0], key), TRAIN_SET[key][1])
        data.append([dqdv, dqdv_pos, q_odd, cyc, q_capacity])

    df = np.asarray(data[0]).T
    #Create subplot of three plots in same row with shared y-axis 
    fig, ax = plt.subplots(1, 4, sharey=True, tight_layout = True) #"figsize=(15, 5) ", sharex-True
    ax[0].scatter(df[:,0], df[:,-1], s=1)
    ax[0].set_xlabel("dQdV")
    ax[0].set_ylabel("capacity")

    ax[1].scatter(df[:,1], df[:,-1], s=1)
    ax[1].set_xlabel("dQdV pos")

    ax[2].scatter(df[:,2], df[:,-1], s=1)
    ax[2].set_xlabel("Q_odd")

    ax[3].scatter(df[:,3], df[:,-1], s=1)
    ax[3].set_xlabel("cycle")

    plt.suptitle(list(TRAIN_SET.keys())[0].split("_", 1)[0]) #, fontsize=12)
    plt.savefig("dqdv.png")

    plt.show()