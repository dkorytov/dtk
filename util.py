
import numpy as np
from scipy.integrate import cumtrapz
from scipy.interpolate import interp1d
from scipy.interpolate import InterpolatedUnivariateSpline
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import h5py 
import pandas as pd
import os.path
import time 

def cat_strings(strings):
    string_result = "";
    for st in strings:
        string_result +=st;
    return string_result;


def replace_strings(strings,target,new_val):
    st_result = []
    for st in strings:
        if(st==target):
            st=str(new_val)
        st_result.append(st)
    return st_result
        
def cat_replace_strings(strings,target,new_val):
    return cat_strings(replace_strings(strings,target,new_val))

def file_exists(fname):
    return os.path.isfile(fname) 

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

dtk_figcount =1
dtk_figs_path = ""

def set_fig_path(path):
    global dtk_figs_path
    dtk_figs_path = path
    ensure_dir(path)

def save_figs(path=None,extension='.png'):
    global dtk_figcount
    if(path is None):
        path = dtk_figs_path
    ensure_dir(path)
    for i in plt.get_fignums():
        plt.figure(i)
        plt.savefig(""+path+'fig%d' % (dtk_figcount)+extension)
        dtk_figcount+=1

def get_colors(data,cmap,log=False,vmax=None, vmin=None):
    if(vmax == None):
        vmax = np.max(data)
    if(vmin == None):
        vmin = np.min(data)
    if(log):
        cnorm = colors.LogNorm(vmin=vmin,vmax=vmax)
    else:
        cnorm = colors.Normalize(vmin=vmin,vmax=vmax)
    smp = cm.ScalarMappable(norm=cnorm,cmap=cmap)
    clrs = smp.to_rgba(data)
    return clrs

def pandas_to_hdf5(df,output):
    hfile = h5py.File(output,'w')
    columns = list(df.columns.values)
    for col in columns:
        hfile[col] = df[col]
    hfile.flush()
    hfile.close()

def pandas_from_hdf5(output):
    hfile = h5py.File(output,'r')
    keys = hfile.keys()
    dic = {}
    for key in keys:
        dic[key]=hfile[key][:]
        hfile.flush()
    return pd.DataFrame(dic)

def hdf5_replace(hfile,name, data):
    del hfile[name]
    hfile[name]=data

def log_avg(xs):
    xs = np.array(xs)
    lg_xs = np.log(xs)
    lg_avg = np.mean(lg_xs)
    return np.exp(lg_avg)

def bins_avg(data):
    return (data[1:]+data[:-1])/2.0

def log_bins_avg(data):
    return 10**((np.log10(data[1:])+np.log10(data[:-1]))/2.0)

def bins_width_dex(bins):
    bins = np.log10(bins)
    return bins[1:]-bins[:-1]

def step_line_bins(bins):
    new_bins = np.zeros((bins.size-1)*2)
    new_bins[::2] = bins[:-1]
    new_bins[1::2] = bins[1:]
    return new_bins

def step_line_data(data):
    new_data = np.zeros(data.size*2)
    new_data[::2] = data
    new_data[1::2] = data
    return new_data

def binned_average(data_x,data_y,xbins):
    bins = np.digitize(data_x,xbins)-1
    result = np.zeros(xbins.size-1)
    for i in range(0,result.size):
        slct = bins == i
        if np.sum(slct) > 0:
            result[i] = np.average(data_y[slct])
        else:
            result[i] = np.nan
    return result

def binned_median(data_x,data_y,xbins):
    bins = np.digitize(data_x,xbins)-1
    result = np.zeros(xbins.size-1)
    for i in range(0,result.size):
        slct = bins == i
        result[i] = np.median(data_y[slct])
    return result

def binned_std(data_x,data_y,xbins):
    bins = np.digitize(data_x,xbins)-1
    result = np.zeros(xbins.size-1)
    for i in range(0,result.size):
        slct = bins == i
        result[i] = np.std(data_y[slct])
    return result

def binned_percentile(data_x, data_y, xbins, percentile_list, minimum_number = 1):
    bins = np.digitize(data_x, xbins)-1
    result = np.zeros((xbins.size-1, len(percentile_list)))
    for i in range(0, xbins.size-1):
        slct = bins==i
        if np.sum(slct) >=minimum_number:
            result[i,:] = np.percentile(data_y[slct], percentile_list)
        else:
            result[i, :] = np.nan
    return result

        

def make_distribution(data,bin_num=10000,limits=None):
    if(limits == None):
        limits = (np.min(data),np.max(data))
    H,_ = np.histogram(data,bins =np.linspace(limits[0],limits[1],bin_num+1))
    bins = np.linspace(limits[0],limits[1],bin_num+1)
    H = np.concatenate(([0],H)) #adding a zero to the histogram for the first bin
    funct = interp1d(bins,H)
    return funct, limits
    

def resample_distribution(dist_src,dist_target,src_range=None,target_range=None,size=10000):
    if(src_range == None):
        src_x = np.linspace(0,1,size,endpoint=True)
    else:
        src_x = np.linspace(src_range[0],src_range[1],size,endpoint=True)
    if(target_range == None):
        target_x = np.linspace(0,1,size)
    else:
        target_x = np.linspace(target_range[0],target_range[1],size)
    dist_src_val = dist_src(src_x)
    dist_src_int = np.insert(cumtrapz(dist_src_val,src_x),0,0.0)
    dist_src_int /=dist_src_int[-1]
    dist_src_int_bad_slope = np.where(dist_src_int[1:]-dist_src_int[:-1]==0)
    src_x = np.delete(src_x,dist_src_int_bad_slope)
    dist_src_val = np.delete(dist_src_val,dist_src_int_bad_slope)
    dist_src_int = np.delete(dist_src_int,dist_src_int_bad_slope)
    
    dist_target_val = dist_target(target_x)
    dist_target_int = np.insert(cumtrapz(dist_target_val,target_x),0,0.0)
    dist_target_int /=dist_target_int[-1]
    dist_target_int_bad_slope = np.where(dist_target_int[1:]-dist_target_int[:-1]==0)
    target_x = np.delete(target_x,dist_target_int_bad_slope)
    dist_target_val = np.delete(dist_target_val,dist_target_int_bad_slope)
    dist_target_int = np.delete(dist_target_int,dist_target_int_bad_slope)
    # print "\n============"
    # print src_x
    # print dist_src_val
    # print dist_src_int
    # print dist_src_int_bad_slope
    # print "\n============"
    # print target_x
    # print dist_target_val
    # print dist_target_int
    # print dist_target_int_bad_slope
    # print "\n============"
    
    # print "src_x min max", np.min(src_x),np.max(src_x)
    # print "src_val min max",np.min(dist_src_val),np.max(dist_src_val)
    # print "src_int min max",np.min(dist_src_int),np.max(dist_src_int)
    # print "target_x min max", np.min(target_x),np.max(target_x)
    # print "target_val min max",np.min(dist_target_val),np.max(dist_target_val)
    # print "target_int min max",np.min(dist_target_int),np.max(dist_target_int)
    # print "\n =========="

    src2cum = interp1d(src_x,dist_src_int,bounds_error=True)
    cum2trg = interp1d(dist_target_int,target_x,bounds_error=True)
    src2trg = interp1d(src_x,cum2trg(src2cum(src_x)),bounds_error=True)

    # print "src2cum min", np.min(src_x),src2cum(np.min(src_x))
    # print "src2cum max", np.max(src_x),src2cum(np.max(src_x))
    # print "cum2trg min", np.min(dist_target_int),cum2trg(np.min(dist_target_int)),"should be:",dist_target_int[0]
    # print "cum2trg max", np.max(dist_target_int),cum2trg(np.max(dist_target_int))

    return src2trg
    
def save_dict_hdf5(fname, cat, verbose=True):
    if verbose:
        print("Saving to", fname)
        t0 = time.time()
    hfile = h5py.File(fname, 'w')
    for key in cat.keys():
        hfile[key] = cat[key]
    hfile.close()
    if verbose:
        t1 = time.time()
        print("\ttime:", t1-t0)

def load_dict_hdf5(fname, verbose=True):
    if verbose:
        print("Loading from", fname)
        t0 = time.time()

    cat = {}
    hfile = h5py.File(fname, 'r')
    for key in hfile.keys():
        cat[key] = hfile[key].value
    if verbose:
        t1 = time.time()
        print("\ttime:", t1-t0)

    return cat

def select_dict(dict_cat, slct):
    dict_result = {}
    for key in dict_cat.keys():
        dict_result[key] = dict_cat[key][slct]
    return dict_result

def reorder_dict(dict_cat, srt):
    dict_result={}
    for key in dict_cat.keys():
        dict_result[key] = dict_cat[key][srt]
    return dict_result

def decenter_bins(bin_cen):
    diff = np.diff(bin_cen)[0]
    bin_edges = np.zeros(len(bin_cen)+1)
    bin_edges[:-1] = bin_cen-diff/2.0
    bin_edges[-1] = bin_cen[-1]+diff/2.0
    return bin_edges
    
def decenter_log_bins(bin_cen):
    lg_bin_cen = np.log10(bin_cen)
    lg_bin_edges = decenter_bins(lg_bin_cen)
    return 10**lg_bin_edges

def diff_curves(x1, y1, x2, y2, bins = 100, log=False):
    x_min = max(np.min(x1), np.min(x2))
    x_max = min(np.max(x1), np.max(x2))
    if log:
        x = np.logspace(np.log10(x_min), np.log10(x_max), bins)
    else:
        x = np.linspace(x_min, x_max, bins)
    y1_new = np.interp(x, x1, y1)
    y2_new = np.interp(x, x2, y2)
    y_diff = y1_new - y2_new
    y_diff_relative = y_diff/y2_new
    return x, y_diff, y_diff_relative

def get_fill_between_limits(y, y_err):
    y_lower = y-y_err
    y_upper = y+y_err
    return y_lower, y_upper

def get_linbins(x, bins=100):
    min_x = np.nanmin(x)
    max_x = np.nanmax(x)
    return np.linspace(min_x, max_x, bins)

def get_logbins(x, bins=100):
    min_x = np.nanmin(x)
    max_x = np.nanmax(x)
    return np.logspace(np.log10(min_x), np.log10(max_x), bins)
    
class ETA:
    def __init__(self):
        self.t0 = time.time()
        
    def reset(self):
        self.t0 = time.time()

    def get_eta(self, i, i_tot):
        time_per_iter = self.get_per_iter(i)
        i_left = i_tot-i
        return time_per_iter*i_left
        
    def get_per_iter(self, i):
        if i == 0:
            return np.nan
        t1 = time.time()
        time_per_iter = (t1-self.t0)/i
        return time_per_iter
    
    def print_progress(self, i, i_tot, prefix=""):
        eta = convert_sec_to_time_string(self.get_eta(i, i_tot))
        per_iter = convert_sec_to_time_string(self.get_per_iter(i))
        print("{}{}/{} ETA: {} ({})".format(prefix, i, i_tot, eta, per_iter))
        return self
    
    def print_done(self, prefix=""):
        t_tot = time.time()-self.t0
        print("{}DONE. time: {}".format(prefix, convert_sec_to_time_string(t_tot)))
        return self

def convert_sec_to_time_string(t):
    if ~np.isfinite(t):
        return( "nan")
    if t<120:
        return("{:.2f}s".format(t))
    elif t<60*60*2:
        return("{:.0f}m:{:.0f}s".format(t//60, t%60))
    else:
        return("{:.0f}h:{:.0f}m".format(t//3600, t%(3600)))
    
def within_relative_tolerance(test_value, target_value, tolerance):
    diff = np.abs((test_value-target_value)/target_value)
    return diff<tolerance
    
def within_absolute_tolerance(test_value, target_value, tolerance):
    diff = np.abs(test_value, target_value)
    return diff<tolerance

def invert_sort(srt):
    return np.argsort(srt)


