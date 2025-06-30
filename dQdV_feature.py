import os
import numpy as np
import pandas as pd
import scipy.integrate as integrate

def dQdV(file, q_rate):
    d1 = pd.read_csv(file)[["Cycle_Number", "Voltage_V", "Current_mA","Time_s","Capacity_mAh"]]
    Vgrid = np.arange(4.2, 3.2, -0.01)
    Qgrid = np.arange(0, 1, 0.01)
    Qpdf = np.array([])
    Vpdf = np.array([])
    Gycle_count = np.array([])
    Qlimited_list = np.array([])
    maxV = np.array([])
    maxVpos = np.array([])

    for name, group in d1.groupby('Cycle_Number'):
        Vd = group.voltage_V.values # + d1.Current.values 0.065/1000 
        Id = -group. Current_mA.values
        time = group.Time_s.values
        time = time - time[0]
        Qd = (integrate.cumtrapz(Id, x=time, initial=0)/(3600*q_rate))
        if np.size(Vd) > 0:
            Q = np.flip(np.interp(Vgrid, np.flip(Vd), np.flip(Qd)))
            Opdf = np.append(Opdf, Q)
            Q_limited_list = np.append(Q_limited_list, Opdf[-1] - Q[0])
            maxV = np.append(maxV, np.max(Vd))
            maxVpos = np.append(maxVpos, np.argmax(Vd))

            cycle_number = int(name)
            Cycle_count = np.append(Cycle_count, cycle_number)
            Vpdf = np.append(Vpdf, Vgrid)
            debug_break = True

    Qplot = np.reshape(Qpdf,(-1,np.size(Vgrid))) #verify Q plot

    Qplot_odd = (Qplot-np.fliplr(Qplot))/2
    Qplot_even = (Qplot+np.fliplr(Qplot))/2

    dQdv_odd = integrate. cumtrapz(Qplot_odd[:,int(Qplot_odd.shape[1]/2):], initial=o)
    dQdV_even = np.mean(Qplot_even, axis=1) #confirm its same as cycle count

    return maxV, maxVpos, Cycle_count, Q_limited_list

#energy odd 
def Qodd(file, q_rated):
    d1 = pd.read_csv(file)[["Cycle_Number", "Voltage_V", "Current _mA", "Time_s", "Capacity_mAh"]]

    Vgrid = np.arange(3.2, 4.2, 0.01)
    Qgrid = np.arange(0, 1, 0.01)
    Qpdf= np.array([])
    Vpdf = np.array([])
    Cycle_count = np.array([])
    Q_1imited_list = np.array([])
    maxV= np.array([])
    maxVpos = np.array([])
    
    for name, group in d1.groupby("Cycle_Number"):
        Vd = group.Voltage_V.values # + dl.Current.values*0.065/1000 
        Id = -group.Current_mA.values 
        time = group.Time_s.values 
        time = time - time[0] 
        Qd = 1 - (integrate.cumtrapz(Id, x=time, initial=0)/(3600*q_rated)) 
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

RAIILSET ( "ch09_ SaveData_concatenated_p22_discharge_s3.csv":["../../data/pro d/Dataset Al_ orofile/A1 MP1 4500mAh_T23/". 4500], "ch10_SaveDsta_concatenated_ p22 discharge_ss.csv":["../../data/processed/Dataset_A1_profile/A1_MP1_4508mAh_T23/", 4500] A TEST_SET ( "ch19_SaveData concatenated p22 discharce_s3.csv":["../../data/processed/Dataset_A1_profile/A1_MP2_4470mAh_T23/". 4470]. 4470], data [ for kay in list(TRAII_SET. kays()): dqdv, dadv_pos, cyc, Q_empacity " doaV(os.prth.join(TRAI_SET[kay][0], kay), TRAIM_SET[key][1]] "Lodd, ",-- Q_odd(os. path.-]odn(TRAIM_sET[kay][0], kay), TRAIN_SET[kay][1]) data.append([dadv, dedv_pos, a_odd, cyc, "_capacity]) break df-np.asarray(data[0]).T #Create subplot of three plots in same row with shared y-axis fis, ax = plt. subplots(1, 4, sharwy-Truo, tieht_2ayout True) "figsize=(15, 5) ", sharex-True ax[o].scatter(af[:, 0]. af[:, -1], 1) mx[o].sat_rlabe1("dQdv") ax[o].set_ylabal("capacity") wx[1].scattar(af[:, 1], df[:, -1], s-1) ax[1].sat_dabel("dQdV pos") ax[2].scattar(af[:, 2], af[:, -1], s1) ax[2].set_xlebel("Q_od") ax[s].scatter(af[:, 3], df[:, -1], sm1) ax[s].set_xlabel("cycle") plt.suptitle(list(TRAIM_SET.kays())[0].spllt("_", 1)[0]) ", fontsize=12 plt.savefig(dqdv.png")    



