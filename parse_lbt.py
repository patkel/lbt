import pandas as pd
import numpy as np

tab = pd.read_csv('sync.csv')

overcount = 2 * np.ones( len(tab['piname']) ) # for both telescopes 

mods_mask = np.array(tab['instrument'].str.contains('MODS', na=False), dtype=bool)

overcount[mods_mask] = 4 # MODS has a dichroic


yrs = 5

osurc_mask = np.array(tab['partner'].str.contains('OSURC', na=False), dtype=bool)
date_mask = np.array(pd.to_datetime(tab['date_obs']) > pd.Timestamp(2023 - yrs,1,1), dtype=bool)
sci_mask = ~np.array(tab['imagetyp'].str.contains('CALIB', na=False), dtype=bool)
not_cal_mask = ~np.array(tab['short_program'].str.contains('Calib', na=False), dtype=bool)
mask_exptime = tab['exptime'] > 0



mask_shared = osurc_mask * date_mask * mask_exptime * sci_mask * not_cal_mask




def count_hrs_pi(pi, mask_use=None, quiet=False):

    if not quiet: print('===== %s =====\n' % pi)

    pi_mask = np.zeros( len(tab['short_program']), dtype=bool)

    if len(pi.split(' ')) > 1: pi_use = [pi, pi.split(' ')[1]]
    else: pi_use = [pi]
                                                                                                             
    for name in pi_use:
    
        pi_mask = np.logical_or(pi_mask, np.array(tab['piname'].str.startswith(name, na=False), dtype=bool))
                                                                                                             
    mask = pi_mask * mask_shared 

    if mask_use is not None: 
        mask *= mask_use
                                                                                                             
    objects = set(tab['object'][mask])
                                                                                                             
    tot_sci_run = 0
                                                                                                             
    for obj in objects:
                                                                                                             
        obj_mask = np.array(tab['object'] == str(obj), dtype=bool)
    
        tot_sci = np.sum((tab['exptime'] / overcount)[obj_mask * mask]) 
                                                                                                             
        inst = list(tab['instrument'][obj_mask * mask])[0]
                                                                                                             
        if not quiet: print('%s %s %.3f hrs' % (obj, inst, tot_sci / 3600.) )
                                                                                                             
        tot_sci_run += tot_sci
                                                                                                             
    if not quiet: print('tot_sci %s %.1f hrs\n' % (pi, tot_sci_run / 3600.) )

    return tot_sci_run














hours_all = 0.

for pi in ['Patrick Kelly','Evan Skillman','Claudia Scarlata', 'Chick Woodward', 'Michael Coughlin']:

    #umn_mask = np.array(tab['short_program'].str.startswith('UM', na=False), dtype=bool)
   
    tot_sci_run =  count_hrs_pi(pi, mask_use=None, quiet=False)

    hours_all += tot_sci_run

print('UMN time per year over last %.1f year: %.1f hrs / yr' % (yrs, hours_all / 3600. / yrs ) )






                                                                                                 
tot_sci_osurc = np.sum((tab['exptime'] / overcount)[mask_shared]) / 3600.

print('tot sci osurc %.1f' % tot_sci_osurc)

print('\n')

tot_all_schools = 0.

accounted_for = np.zeros( len(tab['short_program']), dtype=bool)

for school in ['UV', 'UM', 'ND', 'OSU_']:

    school_mask = np.array(tab['short_program'].str.startswith(school + '', na=False), dtype=bool)

    
    all_school_pis = np.zeros( len(tab['short_program']), dtype=bool)

    if school == 'UM':
        pis = ['Patrick Kelly','Evan Skillman','Claudia Scarlata', 'Chick Woodward', 'Michael Coughlin', 'Roberta Humphreys']
    elif school == 'UV':
        pis = ['Anne Verbiscer', 'Trinh Thuan']
    elif school == 'ND':
        pis = ['Peter Garnavich', 'Howk']
    elif school == 'OSU_':
        pis = ['Chris Kochanek', 'Richard Pogge', 'Danielle Berg', 'Kris Stanek', 'Annika Peter', 'CKochanek', 'Martini', 'Marshall Johnson']

    
    

    ''' add in PI's '''                                                                            
    for pi in pis:

        if len(pi.split(' ')) > 1: pi_use = [pi, pi.split(' ')[1]]
        else: pi_use = [pi]

        for name in pi_use:
            all_school_pis = np.logical_or( all_school_pis, np.array(tab['piname'].str.startswith(name, na=False), dtype=bool))

    school_mask = np.logical_or(school_mask, all_school_pis)


    accounted_for = np.logical_or( accounted_for, school_mask )

    tot_sci_school = np.sum((tab['exptime'] / overcount)[school_mask * mask_shared]) / 3600.
    
    print('tot sci %s %.1f' % (school, tot_sci_school) )
    
    print('%s frac of OSURC %.3f' % (school, tot_sci_school / tot_sci_osurc) )

    tot_all_schools += tot_sci_school / tot_sci_osurc

tot_sci_other = np.sum((tab['exptime'] / overcount)[~accounted_for * mask_shared]) / 3600.


print('breakdown by school')

print('tot sci other %.1f' % (tot_sci_other) )

print('unattributed frac of OSURC %.3f' % (tot_sci_other / tot_sci_osurc) )

tot_all_schools += tot_sci_other / tot_sci_osurc

print('total among all schools + unattributed (consistency check)', tot_all_schools)

#print(tab[ ['piname', 'object', 'program', 'short_program', 'exptime'] ][~accounted_for * mask].to_string())

other_pis = set(tab['piname'][~accounted_for * mask_shared] )

print('\n\n Unattributed Time by PI')

for pi in other_pis:

    print('%s %.2f hrs' % (pi, count_hrs_pi(pi, mask_use=~accounted_for, quiet=True) / 3600.) )




