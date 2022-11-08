# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 11:13:40 2021

@author: Carlos
"""


import fiscalyear
import scipy.stats as st
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
fiscalyear.START_MONTH = 4


def best_fit_distribution(data, bins, DISTRIBUTIONS):
    '''
    Parameters
    ----------
    data : DataFrame
         Datos a ajsutar.
    bins : int
         bins.
    DISTRIBUTIONS : st
         Distribuciones de probabilidad candidatas.

    Returns
    -------
    None.

    '''

    """Model data by finding best fit distribution to data"""
    # Get ^ogram of original data
    y, x = np.histogram(data, bins=bins, density=True)
    indices = np.where(y == 0)
    x = (x + np.roll(x, -1))[:-1] / 2.0

    # Best holders
    best_distribution = st.lognorm
    best_params = (0.0, 1.0)
    best_sse = np.inf
    best_xi2 = np.inf

    # Estimate distribution parameters from data
    for distribution in DISTRIBUTIONS:
        sse = -1

        # Try to fit the distribution
        try:
            # Ignore warnings from data that can't be fit
            # fit dist to data
            if distribution == 'logpearson3':
                distribution_aux = st.pearson3
                data_aux = data.copy()
                data_aux[data_aux <= 0] = 10.**-10.
                data_aux = np.log(data_aux)
                params = distribution_aux.fit(data_aux.values)
            else:
                # cambiar esto
                params = distribution.fit(data.values)

            # Separate parts of parameters
            arg = params[:-2]
            loc = params[-2]
            scale = params[-1]

            # Test de Chi-cuadrado
            # Lognormal está programada distinto

            if distribution == st.lognorm:
                # Calculate fitted PDF and error with fit in distribution
                pdf = distribution.pdf(x, loc=loc, scale=scale, s=1.)
                xi2 = np.sum(np.power(y - pdf, 2.0)/pdf)
                sse = np.sum(np.power(y - pdf, 2.0))
            elif distribution == 'logpearson3':
                y, x = np.histogram(data_aux, bins=bins, density=True)
                x = (x + np.roll(x, -1))[:-1] / 2.0
                pdf = distribution_aux.pdf(x, loc=loc, scale=scale, *arg)
                y[y <= 0] = 10.**-10.
                xi2 = np.sum(np.power(y - pdf, 2.0)/pdf)
                sse = np.sum(np.power(y - pdf, 2.0))
            else:
                # Calculate fitted PDF and error with fit in distribution
                pdf = distribution.pdf(x, loc=loc, scale=scale, *arg)
                xi2 = np.sum(np.power(y - pdf, 2.0)/pdf)
                sse = np.sum(np.power(y - pdf, 2.0))
            # identify if this distribution is better
            if best_xi2 > xi2 > 0:
                best_distribution = distribution
                best_params = params
                best_sse = sse
                best_xi2 = xi2

        except Exception as e:
            print(e)
            pass

    if best_distribution == 'logpearson3':
        xi2_max = st.chi2.ppf(0.05, df=3)
        return ('logpearson3', best_params)
    elif best_distribution == st.pearson3:
        xi2_max = st.chi2.ppf(0.05, df=3)
        return (best_distribution.name, best_params)
    else:
        xi2_max = st.chi2.ppf(0.05, df=2)
        return (best_distribution.name, best_params)


def CVE_pdf(df_relleno, pbbs, distr):
    '''

    Parameters
    ----------
    df_relleno : DataFrame
        caudales rellenados
    pbb : List
        Probabilidades de excedencia.
    distr : st 
        Funciones de distribucion de probabilidad.

    Returns
    -------
    best_fit_name : string
        Nombre de la distribucion de probabilidad ajustada.
    cve_pdf : DataFrame
        Curva de variación estacional usando la distribución de probabilidad ajustada.

    '''        

    # -------------------------------------------------------------------------
    # distribuciones
    # -------------------------------------------------------------------------
    distr_backup = distr.copy()
    best_dist_list = []

    # bins según Gabriel Castro, Uch.
    bins = 50

    # iniciarlizar df y recorrer meses
    cve_pdf = pd.DataFrame(
        [], index=[4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3], columns=pbbs)

    for mes in range(1, 13):
        
        # Rio Laja en Tucapel
        if df_relleno.columns.str.contains('Laja En Tucapel 2'):
            distr=[x for x in distr if x not in [st.pearson3]]
        
        data = pd.DataFrame(
            df_relleno[df_relleno.index.month == mes].values.ravel())
        best_fit_name, best_fit_params = best_fit_distribution(
            data, bins, distr)

        # Separate parts of parameters
        arg=best_fit_params[:-2]
        loc=best_fit_params[-2]
        scale=best_fit_params[-1]
        
        # aca se calcularse todas las pbb y no iterar
        if best_fit_name == 'logpearson3':
            best_dist = getattr(st, 'pearson3')
            func=lambda x: np.exp(best_dist.ppf(1-x,loc=loc,scale=scale,*arg))
        else:
            best_dist = getattr(st, best_fit_name)
            func=lambda x:best_dist.ppf(1-x,*best_fit_params)
        cve_pdf.loc[mes]=cve_pdf.columns.to_series().apply(func).values

        distr_corr=distr.copy()

        while (cve_pdf.loc[mes].min()<0) | (any(cve_pdf.loc[mes].diff()>0)) | (any(cve_pdf.loc[mes].isna())) | any(np.abs((cve_pdf.loc[mes]/cve_pdf.loc[mes].max()))<1e-1):
                        
            if best_fit_name=='logpearson3':
                distr_corr.remove('logpearson3')
            else:
                distr_corr.remove(best_dist)
                
            if mes==11:
                # Ñuble en San Fabián
                if df_relleno.columns.str.contains('San Fabian'):
                    try:
                        distr_corr=[x for x in distr_corr if x not in [st.pearson3,
                                                                st.gumbel_l]]
                    except:
                        pass
                                                
            best_fit_name,best_fit_params=best_fit_distribution(data, bins,
                                                                   distr_corr)

            # Separate parts of parameters
            arg=best_fit_params[:-2]
            loc=best_fit_params[-2]
            scale=best_fit_params[-1]
                            
            if best_fit_name == 'logpearson3':
                best_dist = getattr(st, 'pearson3')
                func=lambda x:np.exp(best_dist.ppf(1-x,loc=loc,scale=scale,*arg))
            else:
                best_dist = getattr(st, best_fit_name)
                func=lambda x:best_dist.ppf(1-x,*best_fit_params)
            
            cve_pdf.loc[mes]=cve_pdf.columns.to_series().apply(func).values

        best_dist_list.append(best_fit_name)

        distr = distr_backup.copy()

    return best_dist_list, cve_pdf

def CVE_pdf_yr(df_relleno, pbbs, distr):
    '''

    Parameters
    ----------
    df_relleno : DataFrame
        caudales rellenados
    pbb : List
        Probabilidades de excedencia.
    distr : st 
        Funciones de distribucion de probabilidad.

    Returns
    -------
    best_fit_name : string
        Nombre de la distribucion de probabilidad ajustada.
    cve_pdf : DataFrame
        Curva de variación estacional usando la distribución de probabilidad ajustada.

    '''

    # -------------------------------------------------------------------------
    # distribuciones
    # -------------------------------------------------------------------------
    distr_backup = distr.copy()
    best_dist_list = []

    # bins según Gabriel Castro, Uch.
    bins = 50

    # iniciarlizar df y recorrer meses
    cve_pdf = pd.DataFrame(
        [], index=[0], columns=pbbs)

    data = pd.DataFrame(
        df_relleno.values.ravel())
    best_fit_name, best_fit_params = best_fit_distribution(
        data, bins, distr)

    # Separate parts of parameters
    arg=best_fit_params[:-2]
    loc=best_fit_params[-2]
    scale=best_fit_params[-1]

    # aca se calcularse todas las pbb y no iterar
    
    if best_fit_name == 'logpearson3':
        best_dist = getattr(st, 'pearson3')
        func=lambda x: np.exp(best_dist.ppf(1-x,loc=loc,scale=scale,*arg))
    else:
        best_dist = getattr(st, best_fit_name)
        func=lambda x:best_dist.ppf(1-x,*best_fit_params)
    cve_pdf.loc[0]=cve_pdf.columns.to_series().apply(func)

    distr_corr=distr.copy()

    while (cve_pdf.loc[0].min()<0) | (any(cve_pdf.loc[0].diff()>0)) | (any(cve_pdf.loc[0].isna())):
                    
        if best_fit_name=='logpearson3':
            distr_corr.remove('logpearson3')
        else:
            distr_corr.remove(best_dist)
            
        best_fit_name, best_fit_params=best_fit_distribution(data, bins,
                                                               distr_corr)
        
        # Separate parts of parameters
        arg=best_fit_params[:-2]
        loc=best_fit_params[-2]
        scale=best_fit_params[-1]
            
        if best_fit_name == 'logpearson3':
            best_dist = getattr(st, 'pearson3')
            func=lambda x:np.exp(best_dist.ppf(1-x,loc=loc,scale=scale,*arg))
        else:
            best_dist = getattr(st, best_fit_name)
            func=lambda x:best_dist.ppf(1-x,*best_fit_params)
        
        cve_pdf.loc[0]=cve_pdf.columns.to_series().apply(func)

    best_dist_list.append(best_fit_name)

    distr = distr_backup.copy()

    return best_dist_list, cve_pdf
