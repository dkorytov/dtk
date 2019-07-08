import numpy as np
from scipy.interpolate import interp1d


#converts simulations steps into z/a and
#vice versa
class StepZ:
    def __init__(self,start_z=None,end_z=None,num_steps=None,sim_name=None):
        if(sim_name != None):
            if sim_name == 'AlphaQ':
                start_z = 200
                end_z = 0
                num_steps = 500
            else:
                raise 
        self.z_in = float(start_z)
        self.z_out = float(end_z)
        self.num_steps = float(num_steps)
        self.a_in = 1./(1.+start_z)
        self.a_out = 1./(1.+end_z)
        self.a_del = (self.a_out- self.a_in)/(self.num_steps-1)
    
    def get_z(self,step):
        #to get rid of annoying rounding errors on z=0 (or other ending values)
        #if(step == self.num_steps-1):
        #    return 1./self.a_out -1. 
        a = self.a_in+step*self.a_del
        return 1./a-1.
    def get_step(self,z):
        a = 1./(z+1.)
        return (a-self.a_in)/self.a_del

    def get_a(self,step):
        return 1./(self.get_z(step)+1.)

def z_from_a(a):
    return 1.0/a-1.0

def a_from_z(z):
    return 1.0/(z+1.0)

b=0.168
Hubble=0.71
Omega_DM = 0.22
Omega_BM = 0.02258/Hubble**2
Omega_M  = Omega_DM+Omega_BM
Omega_L = 1-Omega_M
prtcl_mass = 1491.**3/3200.**3*(Omega_M*2.77536627e11)

def get_rho_crit_z0():
    return 2.77536627e11 #(h^-1 Msun)/(h^-3 Mpc^3)

def get_rho_crit(z=None,a=None):
    if(z==None and a==None):
        raise Exception("rho_crit: z or a must be defined")
    elif(z!=None and a!=None):
        raise Exception("rho_crit: both z and a can't be defined")
    if(z!=None):
        a= a_from_z(z)
    r0 = get_rho_crit_z0()
    return r0*(Omega_M/a**3+Omega_L)
    

def NFW_enclosed_mass(r,c):
    alpha = r*c
    Ac = np.log(1+c)-c/(1.0+c)
    M_enclosed = (np.log(1.0+alpha) - alpha/(1.0+alpha))
    return M_enclosed/Ac

def NFW_slope(r,c):
    alpha = r*c
    return alpha/(1+alpha)**2

# def NFW_enclosed_mass(r,c):
#     rs = r/c
#     M = np.log((rs+r)/rs) - r
#     return M_enclosed

def nfw_mass_enclosed_scale(r, Rs):
    """The relative amount of mass enclosed of a nfw profile as a
    function of Rs. This function is not normalized to any value, so
    only relative comparisons should be made

    """
    return np.log((Rs+r)/Rs) - r/(Rs+r)

def nfw_density_enclosed_scale(r, Rs):
    """The relative average density of enclosed mass of a nfw profile as
    a function of Rs. This function is not normalized to any value, so
    only relative comparisons should be made.

    """
    return nfw_mass_enclosed_scale(r, Rs)/r**3

class NFWConverter:
    def __init__(self,lower_limit = 0.001, upper_limit = 10):
        """The input parameters are scale radius limits where this converter
        works. Going beyond this radius either on the input or output
        will cause an exception.

        """
        radius = np.linspace(lower_limit, upper_limit, 50000)
        #Unitless density
        enclosed_density = nfw_density_enclosed_scale(radius, 1.0)
        log10_enclosed_density = np.log10(enclosed_density)
        # print("max/min of enclosed density: ",np.max(log10_enclosed_density), np.min(log10_enclosed_density))
        self.enclosed_density_from_radius = interp1d(radius, log10_enclosed_density)
        self.radius_from_enclosed_density = interp1d(log10_enclosed_density, radius)

    def get_target_overdensity_radius(self, starting_delta, R_delta, conc, target_delta):
        """We take a nfw halo with a known R200c and concetration and find
        the R(delta)c, where delta is a specified over density. The function
        return the radius were the target overdensity is reached"""
        # print("we are converting R_{:.0f} = {:.2f}, c={:.2f} to R_{:.0f}".format(starting_delta, R_delta, conc, target_delta))
        R_delta_Rs_units = R_delta*conc ; print("...")
        print(np.min(conc), np.max(conc))
        # print("R_{:.0f} in units of Rs is {:.2f}".format(starting_delta, R_delta_Rs_units))
        starting_density = self.enclosed_density_from_radius(R_delta_Rs_units) ; print("...")
        # print("The average over log10 density at R_{:.0f} is {:.2f}".format(starting_delta, starting_density))
        target_density = starting_density+np.log10(target_delta/starting_delta) ; print("...")
        # print("If we are going from R_{:.0f} to R_{:.0f}, the new log10 density should be {:.2f}".format(starting_delta, target_delta, target_density))
        print(starting_density)
        print(np.min(target_density), np.max(target_density))
        R_target_delta_Rs_units = self.radius_from_enclosed_density(target_density) ; print("...")
        return R_target_delta_Rs_units/conc
