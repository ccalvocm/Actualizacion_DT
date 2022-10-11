# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 08:32:23 2020

@author: ccalvo
"""

#%%
import pandas as pd 
import matplotlib.pyplot as plt
import os
from hydroeval import evaluator, nse
import statsmodels.api as sm
import numpy as np
from scipy.signal import find_peaks
from scipy import interpolate
from hydrobox.discharge import flow_duration_curve
import fiscalyear
import scipy.stats as st
import locale
# Set to Spanish locale to get comma decimal separater
locale.setlocale(locale.LC_NUMERIC, "es_ES")

fiscalyear.START_MONTH = 4    

plt.rcdefaults()

# Tell matplotlib to use the locale we set above
plt.rcParams['axes.formatter.use_locale'] = True

def agnohidrologico(year_,month_):
    cur_dt = fiscalyear.FiscalDate(year_, month_, 1) 
    retornar = cur_dt.fiscal_year - 1
    return int(retornar)

def CVEParser(txt_):
    CVE = dict()
    n = 0
    station = None
    data = None
    with open(txt_, 'r') as f:
        for line in f:
            L = line.split()
            if len(L) == 1:
                station = L[0]
                data = []
            elif len(L) > 1:
                data.append(L)
                n +=1
            else:
                pass
            if n >= 7:
                n = 0
                CVE[station] = data
            else:
                pass

    return CVE


def CVE(dataframe, quantiles,aggregate, months = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                                        'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
                                        'Nov', 'Dec'],
         hydroyear = True):
    '''
    

 

    Parameters
    ----------
    dataframe : Pandas dataframe
        Pandas dataframe with index as datestamps and columns as stations
    quantiles : array or list
        List of quantiles from 0 to 1 e.g [0.85, 0.9]. 85 and 90 quantile
    months : array or list of months in english with 3 characters e.g 'Jan'
        List of months of the year.
    hydroyear : boolean, default to False
        Set to true if you wish to use the hydrologic year in the southern
        hemisphere: ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
                     'Nov', 'Dec', 'Jan', 'Feb', 'Mar']

 

    Returns
    -------
    mdf : list of Pandas dataframes
        returns list of dataframes showing the quantile month calculation
        for all stations.

 

    '''
    if hydroyear:
        months = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
                     'Nov', 'Dec', 'Jan', 'Feb', 'Mar']
    else:
        pass
    
    mdf = dict()
    if aggregate:
        for qtile in quantiles:
            MonthAV = dataframe.groupby(dataframe.index.month).quantile(q = 1-qtile)
            MonthAV['Total'] = MonthAV.mean(axis = 1)
            MonthAV.index = pd.to_datetime(MonthAV.index, format = '%m')
            MonthAV.index = MonthAV.index.month_name().str.slice(stop=3)
            MonthAV = MonthAV.reindex(months)
            mdf[str(qtile)] = MonthAV
    else:
        mdf = dict()
        for col in dataframe.columns:
            qtl_group = dict()
            for qtile in quantiles:
                MonthAV = dataframe[col].groupby(dataframe.index.month).quantile(q = 1-qtile)
                # MonthAV['Total'] = MonthAV.mean(axis = 1)
                MonthAV.index = pd.to_datetime(MonthAV.index, format = '%m')
                MonthAV.index = MonthAV.index.month_name().str.slice(stop=3)
                MonthAV = MonthAV.reindex(months)
                qtl_group[str(qtile)] = MonthAV
            mdf[col] = qtl_group
    return mdf

def NSE(nse, sim_flow, obs_flow, axis=1):
    serie_sim = sim_flow.values.ravel()
    serie_obs = obs_flow.values.ravel()
    my_nse = evaluator(nse, serie_sim, serie_obs, axis=1)
    return my_nse
    
def Qmm(df_, estacion):
  df = df_.groupby(df_.index.month).mean()
  df = df[estacion].reindex([4,5,6,7,8,9,10,11,12,1,2,3])
  df = df.reset_index()
  df = df.set_index(pd.Index(range(1,13)))
  del df['index']
  df.columns = [estacion]
  return df

def best_fit_distribution(data, bins, DISTRIBUTIONS):
#   DISTRIBUTIONS2 = [st.alpha,st.anglit,st.arcsine,st.argus,st.beta,st.betaprime,st.bradford,st.burr,st.burr12,st.cauchy,st.chi,st.chi2,st.cosine,st.crystalball,st.dgamma,st.dweibull,st.erlang,st.expon,st.exponnorm,st.exponweib,st.exponpow,st.f,st.fatiguelife,st.fisk,st.foldcauchy,st.foldnorm,st.genlogistic,st.gennorm,st.genpareto,st.genexpon,st.genextreme,st.gausshyper,st.gamma,st.gengamma,st.genhalflogistic,st.geninvgauss,st.gilbrat,st.gompertz,st.gumbel_r,st.gumbel_l,st.halfcauchy,st.halflogistic,st.halfnorm,st.halfgennorm,st.hypsecant,st.invgamma,st.invgauss,st.invweibull,st.johnsonsb,st.johnsonsu,st.kappa4,st.kappa3,st.ksone,st.kstwo,st.kstwobign,st.laplace,st.levy,st.levy_l,st.levy_stable,st.logistic,st.loggamma,st.loglaplace,st.lognorm,st.loguniform,st.lomax,st.maxwell,st.mielke,st.moyal,st.nakagami,st.ncx2,st.ncf,st.nct,st.norm,st.norminvgauss,st.pareto,st.pearson3,st.powerlaw,st.powerlognorm,st.powernorm,st.rdist,st.rayleigh,st.rice,st.recipinvgauss,st.semicircular,st.skewnorm,st.t,st.triang,st.truncexpon,st.truncnorm,st.tukeylambda,st.uniform,st.vonmises,st.vonmises_line,st.wald,st.weibull_min,st.weibull_max,st.wrapcauchy]
#   DISTRIBUTIONS = [st.norm,st.lognorm,st.pearson3, st.gumbel_r,st.gumbel_l]
   """Model data by finding best fit distribution to data"""
   # Get ^ogram of original data
   y, x = np.histogram(data, bins=bins, density=True)
   x = (x + np.roll(x, -1))[:-1] / 2.0
     
         # Best holders
   best_distribution = st.lognorm
   best_params = (0.0, 1.0)
   best_sse = np.inf
   
   
   # Estimate distribution parameters from data
   for distribution in DISTRIBUTIONS:
       # Try to fit the distribution
       try:
           # Ignore warnings from data that can't be fit
           # with warnings.catch_warnings():
           #     warnings.filterwarnings('ignore')
   
           # fit dist to data
           params = distribution.fit(data)

           # Separate parts of parameters
           arg = params[:-2]
           loc = params[-2]
           scale = params[-1]

           # Calculate fitted PDF and error with fit in distribution
           pdf = distribution.pdf(x, loc=loc, scale=scale, *arg)
           sse = np.sum(np.power(y - pdf, 2.0))

    
           # identify if this distribution is better
           if best_sse > sse > 0:
               best_distribution = distribution
               best_params = params
               best_sse = sse
   
       except Exception:
           pass
   return (best_distribution.name, best_params)
   
def CVE_pdf(df_relleno,df_target, pbb, distr):  
    cve_pdf = pd.DataFrame([],index = [4,5,6,7,8,9,10,11,12,1,2,3], columns = df_relleno.columns)
    for mes in range(1,13):
        data = pd.DataFrame(df_relleno[df_relleno.index.month == mes ].values.ravel())
        # Plot for comparison
#        plt.figure(figsize=(12,8))
#        ax = data.plot(kind='hist', bins=200, density=True, alpha=0.5)
        # Find best fit distribution
        best_fit_name, best_fit_params = best_fit_distribution(data, 200, distr)
        print(best_fit_name)
        best_dist = getattr(st, best_fit_name)
        cve_pdf.loc[mes, cve_pdf.columns] = best_dist.ppf(1-pbb, loc = best_fit_params[0], scale =  best_fit_params[1])
    cve_pdf.reset_index()
    cve_pdf.index = range(1,13)
#    #plotear
#    plt.close("all")
#    fig,ax = plt.subplots(1)
#    cve_pdf.plot(ax = ax)
#    df_target.plot(ax = ax)
#    
    return cve_pdf

#%%
def CVE_1979_2019(file, fig, axes, ene, flag):
     
  # inputs:
  
#  ruta_Q_rellenos = r'../Etapa 1 y 2/datos/'+file
  import freqAnalysis

  probabilidades_excedencia = [.2, .5, .85, .9,.95]
  
#  Q_relleno = pd.read_csv(ruta_Q_rellenos, index_col = 0,parse_dates=True)
  Q_relleno = file
  
  year_i = 1979
  year_f = 2020
    
  inicio = pd.to_datetime(str(year_i)+'-12-31',format='%Y-%m-%d')
  fin = pd.to_datetime(str(year_f)+'-12-31',format='%Y-%m-%d')
    
  Q_relleno = pd.DataFrame(Q_relleno[Q_relleno.index <= fin ],  index = pd.date_range(inicio, fin, freq=flag, closed='right'))
  
  pbb_mensuales = pd.DataFrame(columns=[probabilidades_excedencia], index = [0,1,2,3,4,5,6,7,8,9,10,11])
  
  distros = [st.norm,st.alpha,st.anglit,st.arcsine,st.argus,st.beta,st.betaprime,st.bradford,st.burr,st.burr12,st.cauchy,st.chi,st.chi2,st.cosine,st.crystalball,st.dgamma,st.dweibull,st.erlang,st.expon,st.exponnorm,st.exponweib,st.exponpow,st.f,st.fatiguelife,st.fisk,st.foldcauchy,st.foldnorm,st.genlogistic,st.gennorm,st.genpareto,st.genextreme,st.gausshyper,st.gamma,st.gengamma,st.genhalflogistic,st.geninvgauss,st.gilbrat,st.gompertz,st.gumbel_r,st.gumbel_l,st.halfcauchy,st.halflogistic,st.halfnorm,st.halfgennorm,st.hypsecant,st.invgamma,st.invweibull,st.kappa4,st.kappa3,st.ksone,st.levy,st.levy_l,st.logistic,st.loggamma,st.loglaplace,st.lognorm,st.loguniform,st.lomax,st.maxwell,st.mielke,st.moyal,st.nakagami,st.ncx2,st.ncf,st.nct,st.norminvgauss,st.pearson3,st.powerlaw,st.powerlognorm,st.powernorm,st.rdist,st.rice,st.semicircular,st.skewnorm,st.t,st.triang,st.truncexpon,st.truncnorm,st.tukeylambda,st.uniform,st.wald,st.weibull_min,st.weibull_max,st.wrapcauchy, 'logpearson3']

 # Graficar
 
  fs_titles = 10
  fs_labels = 10
  lw = 3
    
  caudales_pbb_mes = {x:'' for x in Q_relleno.columns}
    # iterar sobre estaciones
  for i,estacion in enumerate(Q_relleno.columns):
                     
    for index, pbb in enumerate(probabilidades_excedencia):
                
        # CVE_rellenada = freqAnalysis.CVE_pdf(pd.DataFrame(Q_relleno[estacion], columns = [estacion], index = Q_relleno.index), pbb, distros, estacion)[1]
           
        CVE_rellenada = CVE(pd.DataFrame(Q_relleno[estacion], columns = [estacion], index = Q_relleno.index), probabilidades_excedencia, aggregate = True)[str(probabilidades_excedencia[index])][estacion]
#        CVE_rellenada = CVE(pd.DataFrame(Q_relleno[estacion], columns = [estacion], index = Q_relleno.index), probabilidades_excedencia, aggregate = False)[estacion][str(probabilidades_excedencia[index])]
       
        pbb_mensuales.loc[pbb_mensuales.index, pbb] =  CVE_rellenada.to_list()
    
    caudales_pbb_mes[estacion] = pbb_mensuales
        
#Graficar

   
    axis = axes[i]
    
    axis.tick_params(axis='both', which='major', labelsize = fs_titles)
    axis.tick_params(axis='both', which='minor', labelsize = fs_titles)
    colores =  ['blue','magenta',  'yellow',  'cyan', 'purple', 'brown']
    caudales_pbb_mes[estacion].plot(ax = axis, color=colores, style='.-', legend=False, linewidth = lw, logy=False)
        
    if i >= len(Q_relleno.columns)-ene: 
    
        axis.set_xticks(range(12)) 
        axis.set_xticklabels(['A', 'M', 'J', 'J', 'A', 'S', 'O',
                     'N', 'D', 'E', 'F', 'M'], fontsize = fs_labels)
    
    else:
        
        axis.set_xticks(range(12)) 
        axis.set_xticklabels(['', '', '', '', '', '', '',
                     '', '', '', '', ''], fontsize = fs_labels)
        axis.set_xlabel(' ')
        
    if (i)%ene == 0:
        axis.set_ylabel('Q $(m^3/s)$',  fontsize = fs_labels)
        
    if i < len(Q_relleno.columns):
        # axis.set_title("\n".join(wrap(estacion.title(), 20)), fontsize = 11)
        axis.set_title(estacion.title().upper(), fontsize = 10)
    axis.set_ylim(bottom = 0)
    axis.grid()
    axis.legend(['Q5','Q10', 'Q20','Q50','Q85', 'Q95'], prop={'size': fs_titles})


# ------------------------------------------------------------------------------------------------

def CVE_mon(Q_relleno,fig,axes,ene,year_i,year_f,cuenca):
    
  import locale
    # Set to Spanish locale to get comma decimal separater
  locale.setlocale(locale.LC_NUMERIC, "es_ES")
         
  # inputs:
  import freqAnalysis

  # probabilidades de excedencia y distribuciones
  probabilidades_excedencia=[.2,.5,.85,.9,.95]
  distr=[st.norm,st.lognorm,st.gumbel_l,st.gumbel_r,st.pearson3,'logpearson3']   
    
  
  ini = pd.to_datetime(str(year_i)+'-04-01',format='%Y-%m-%d')
  fin = pd.to_datetime(str(year_f)+'-03-31',format='%Y-%m-%d')
    
  Q_relleno=Q_relleno.loc[(Q_relleno.index<=fin)&(Q_relleno.index>=ini)]
  
  pbb_mensuales=pd.DataFrame(columns=[probabilidades_excedencia], 
                             index=[0,1,2,3,4,5,6,7,8,9,10,11])
  
 # Graficar
  fs_titles = 10
  fs_labels = 10
  lw = 3
  caudales_pbb_mes = {x:'' for x in Q_relleno.columns}
  
  # crear archivo para guardar estaciones
  save_path=os.path.join('.','outputs','CVE_caudales_'+cuenca+'.xlsx')
  writer=pd.ExcelWriter(save_path, engine='xlsxwriter')

    # iterar sobre estaciones
  for i,estacion in enumerate(Q_relleno.columns):
                        
    df_q=pd.DataFrame(Q_relleno[estacion],columns=[estacion],
                      index=Q_relleno.index)
    distrs,CVE_rellenada=freqAnalysis.CVE_pdf(df_q,probabilidades_excedencia,
                                              distr)
    
    # QAQC de los ajustes
    diferencia=CVE_rellenada.diff(axis=1).iloc[:,1:]
    
    print(distrs)
 
    pbb_mensuales.loc[pbb_mensuales.index,probabilidades_excedencia]=CVE_rellenada.values
    
    caudales_pbb_mes[estacion] = pbb_mensuales

#Graficar

    axis = axes[i]
    
    axis.tick_params(axis='both', which='major', labelsize = fs_titles)
    axis.tick_params(axis='both', which='minor', labelsize = fs_titles)
    colores =  ['blue','magenta',  'yellow',  'cyan', 'purple', 'brown']
    caudales_pbb_mes[estacion].plot(ax=axis,color=colores,style='.-',
markersize=12, legend=False, linewidth = lw, logy=False)
        
    df_export = caudales_pbb_mes[estacion].copy()
    df_export['Distribución'] = distrs
    df_export.index = ['Abril','Mayo','Junio', 'Julio', 'Agosto', 'Septiembre',
                       'Octubre','Noviembre','Diciembre','Enero','Febrero','Marzo']

    # Write each dataframe to a different worksheet.
    df_export.index.names = ['Mes']
    df_export.to_excel(writer, sheet_name=estacion[0:31], encoding='latin1', startcol = 0, startrow = 1)
    
    worksheet = writer.sheets[estacion[0:31]]
    worksheet.write_string(0, 0, 'Curvas de variación estacional '+estacion)
    worksheet.getCells().deleteRows(2,1,True)

    axis.set_title(estacion.title().upper(), fontsize = 10)
    
    if i >= len(Q_relleno.columns)-ene: 
    
        axis.set_xticks(range(12)) 
        axis.set_xticklabels(['A', 'M', 'J', 'J', 'A', 'S', 'O',
                     'N', 'D', 'E', 'F', 'M'], fontsize = fs_labels)
    
    else:
        
        axis.set_xticks(range(12)) 
        axis.set_xticklabels(['', '', '', '', '', '', '',
                     '', '', '', '', ''], fontsize = fs_labels)
        axis.set_xlabel(' ')
        
    axis.set_ylabel('Caudal $(m^3/s)$',  fontsize = fs_labels)
    axis.set_ylim(bottom = 0)
    axis.grid()
    axis.legend(['Q20%','Q50%','Q85%','Q90%','Q95%'],
                prop={'size': fs_titles})

  writer.save()
  writer.close()
# ===================================================================================

def CDQ(file, lc, fig, axes):
      #%% Curvas de duración de caudales
  
# librerias
  import locale
    # Set to Spanish locale to get comma decimal separater
  locale.setlocale(locale.LC_NUMERIC, "es_ES")
  
  # promediar caudales si están diarios
  Q_relleno = file.resample('MS').mean()
  Q_relleno = Q_relleno.loc[Q_relleno.index < '2020-04-01']
  
  fs_titles = 10
  fs_labels = 10
  lw = 3     
  
  axes = axes.reshape(-1)
    
  for i,col in enumerate(Q_relleno.columns):
      Q = Q_relleno[col].copy().values
      fdc = 1-flow_duration_curve(x=Q, plot = False)
      
      Q.sort()
      axes[i].semilogy(fdc[fdc < 0.99],Q[fdc < 0.99], linewidth = lw)
      axes[i].set_title(col.title().upper(), fontsize = fs_titles)

      axes[i].grid(True, which="both", ls="-")

      if col in Q_relleno.columns[-lc:]:
          axes[i].set_xlabel('Probabilidad de excedencia',  fontsize = fs_labels)
    
      else:
        
          axes[i].set_xticks([])
          axes[i].set_xlabel(' ')
          
      axes[i].set_ylabel('Caudal ($m^3/s$)',  fontsize = fs_labels)
          

def CMA(file, w, h, nr, nc, cuenca):
  # lirerias
  import statsmodels.api as sm
  import locale
    # Set to Spanish locale to get comma decimal separater
  locale.setlocale(locale.LC_NUMERIC, "es_ES")
   
  # inputs:
 
#  ruta_Q_rellenos = r'../Etapa 1 y 2/datos/'+file
 
#  Q_relleno = pd.read_csv(ruta_Q_rellenos, index_col = 0,parse_dates=True)
  
  Q_relleno = file
  
  year_i = Q_relleno.index.year[0]
  year_f = Q_relleno.index.year[-1]
    
  inicio = pd.to_datetime(str(year_i)+'-04-01',format='%Y-%m-%d')
  fin = pd.to_datetime(str(year_f+1)+'-03-31',format='%Y-%m-%d')
  
   # Graficar
 
  fs_titles = 10
  fs_labels = 10
  lw = 3
    
  Q_relleno = pd.DataFrame(Q_relleno[(Q_relleno.index <= fin ) & (Q_relleno.index >= inicio)])
  for j, row in Q_relleno.iterrows():
    Q_relleno.loc[j,'hydro_year'] = int(agnohidrologico(j.year, j.month))
        
  Q_relleno_yr = Q_relleno.groupby('hydro_year').mean()
  Q_relleno_yr.index.names = ['']

  axes = Q_relleno_yr.plot(subplots = True, sharex=False, figsize = (w,h), linewidth = lw , layout = (nr , nc), title = Q_relleno_yr.columns.to_list(), legend = False, grid = True)
  axes = axes.reshape(-1)
  
  # xticks = axes[3].get_xticks()

  for i,ax in enumerate(axes):
       axes[i].set_ylim(bottom=0)
       axes[i].set_ylabel('Caudal medio anual $(m^3/s)$')
       axes[i].set_xlabel('Año hidrológico')
       axes[i].set_title(axes[i].get_title().upper(), fontsize = 10)
          
       y = Q_relleno_yr.iloc[:,i].values
       x = Q_relleno_yr.index.values
    
       X = sm.add_constant(x)
    
       model = sm.OLS(y[:-1],X[:-1])
       results  = model.fit()
       axes[i].plot(x,results.params[0]+x*results.params[1], linestyle = '-.', color = 'r')

  from unidecode import unidecode

  Q_relleno_yr.columns = [unidecode(x) for x in Q_relleno_yr.columns]
  Q_relleno_yr.to_csv(r'./outputs/caudales/QMA_cuenca_Río_'+cuenca+'_.csv')


def ANOM(file, w, h, locx, locy, thickness, freq, fig, axes):
    #%%
    
    import locale
    locale.setlocale(locale.LC_NUMERIC, "es_ES")
          
    import warnings
    warnings.filterwarnings("ignore")
        
    if freq == 'D':
        Q_relleno = file.resample('MS').mean()
    else:
        Q_relleno = file
        
    Q_relleno_promedio = Q_relleno.groupby(Q_relleno.index.month).mean()
    Q_relleno_std = Q_relleno.groupby(Q_relleno.index.month).std()

    Diff = Q_relleno.copy()

    for ind,col in Diff.iterrows():
        Diff.loc[ind] = (Q_relleno.loc[ind] - Q_relleno_promedio.loc[ind.month])/Q_relleno_std.loc[ind.month]
        
    Diff.index = Diff.index.strftime('%y-%m')
    Diff = Diff.iloc[0:,:]
      
    nticks = 24
    fs = 10

    Diff.index.names = ['']
    for ind,col in enumerate(Q_relleno.columns):
        Diff['positive'] = Diff[col] > 0
        axes[ind].axvline(x=479, color = 'k', alpha = 0.2, linewidth = thickness)
        Diff[col].plot.bar(color=Diff.positive.map({True: 'b', False: 'r'}), width = 1.2, grid = True, rot = 50, ax = axes[ind])

        ticks = axes[ind].xaxis.get_ticklocs()[::nticks]
        fig.canvas.draw()
        ticklabels = [l.get_text() for l in axes[ind].xaxis.get_ticklabels()][::nticks]
        yticks = [l.get_text() for l in axes[ind].yaxis.get_ticklabels()]
        
        axes[ind].xaxis.set_ticks(ticks)
        axes[ind].xaxis.set_ticklabels(ticklabels, fontsize = fs)
        axes[ind].set_yticklabels(yticks,  fontsize=fs)
        axes[ind].set_ylabel('$(Q_{mensual}-\overline{Q})/\sigma_{Q}$', fontsize = fs)
        axes[ind].figure.show()
        axes[ind].set_title(col.upper(), fontsize = fs)
        axes[ind].text(locx,locy,'2010-Abr',  transform=axes[ind].transAxes, fontsize = fs, weight='bold').set_alpha(.8)

#%%
    
def CDA(file):
       
    
    #%%
    # seleccionar grupo con estaciones mejores correlación (candidatas)
    # promediar las estaciones seleccionadas
    
    def linear_reg(x, m):
        """Linear regression with intercept 0: 
                y = m · x
        
        Input:
        ------
        x:         float. Independet value
        m:         float. Slope of the linear regression
        
        Output:
        -------
        y:         float. Regressed value"""
        
        y = m * x
        
        return y    
    
    def regresion(x_,y_):
        x__= sm.add_constant(x_)
        resultados_fit = sm.OLS(y_,x__,missing='drop').fit()
        N = resultados_fit.params['const']
        M = resultados_fit.params[0]
        return [M,N]
    
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)
        
    Q_relleno_orig = file
    Q_relleno = Q_relleno_orig.copy()
    
    for j, row in Q_relleno.iterrows():
        Q_relleno.loc[j,'hydro_year'] = int(agnohidrologico(j.year, j.month))
        
    Q_anual = Q_relleno.copy()
    Q_anual = Q_anual.groupby('hydro_year').mean()
    CAA = Q_anual.cumsum()
    
    corr = Q_anual.corr()

    for i_col,col in enumerate(Q_relleno.columns[:-1]):

        candidatas = corr[col][corr[col] > 0.8].index
        CAA_candidatas = CAA[candidatas].mean(axis=1)
        x = CAA_candidatas
        y = CAA[col]      
        
        tck = interpolate.splrep(x, y, k=2, s=0)
        dev_2 = np.diff(interpolate.splev(x, tck, der=1))
        
        peaks_max, maximums = find_peaks(dev_2, height=0)
        peaks_min, minimums = find_peaks(-dev_2, height=0)
        maximos = pd.DataFrame( [x for x in maximums['peak_heights']], index = peaks_max, columns = ['max'])
        minimos = pd.DataFrame( [-x for x in minimums['peak_heights']], index = peaks_min, columns = ['max'])
        
        df_max_min = pd.concat([maximos, minimos])[np.abs(pd.concat([maximos, minimos])['max']) >= 0.2].sort_index()
    
        indices = df_max_min.index.to_list()
        indices.insert(0,0)
        indices.append(-1)
        years = CAA_candidatas.index[indices].to_list()
        
        pendientes_corregidas = []
         
        for i,indice in enumerate(indices[:-1]):
            if i > len(indices)-3:
                X = x.iloc[indice:indices[i+1]]
                Y = y.iloc[indice:indices[i+1]]       
            else:
                X = x.iloc[indice:indices[i+1]+1]
                Y = y.iloc[indice:indices[i+1]+1]
            
            m = regresion(X,Y)[0]
       
            m = sm.OLS(endog=Y, exog=X).fit().params.values
            if i < 1:
                m_0 = m
                pendientes_corregidas.append(1.)
            else:
                pendientes_corregidas.append(m_0/m)

    #        
        for ind,yr in enumerate(years[:-1]):
            Q_relleno.loc[((Q_relleno['hydro_year'] >= years[ind]) & (Q_relleno['hydro_year'] <= years[ind+1])), col] = Q_relleno.loc[((Q_relleno['hydro_year'] >= years[ind]) & (Q_relleno['hydro_year'] <= years[ind+1])), col]*pendientes_corregidas[ind]
    
        #%%
    del Q_relleno['hydro_year']
    return Q_relleno

    
def get_names(Q,df):
    for columna in Q.columns:
        Q = Q.rename(columns={columna: df['Estacion'].loc[df['rut'] == columna].values[0]})
        
    return Q
        


