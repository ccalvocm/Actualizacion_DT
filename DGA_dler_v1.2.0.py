# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 10:25:23 2020
@author: ccalvo
"""

from datetime import date
import requests #librería para hacer consultas https
import pandas as pd
from time import sleep
import random
import os
import numpy as np
import sys

#Variables globales

'''La página necesita las Cookies de la sesión en que uno pasó el reCaptcha. 
Pueden ir aquí o en los encabezados, pero por orden prefiero en este diccionario.'''
####### CAMBIAR, una Cookie por cuenca #######

cookies = {'_ga' : 'GA1.1.15729720.1657635782', 
'cookiesession1' : '252721ECCWZQRSL47VOD6OACDJE741C0', 
'JSESSIONID' : '0000U477SjgAIZp8oaWd5uAt2en:-1'} 

# POST data de la sesión ####### CAMBIAR, un post data por cuenca #######
javaxfacesViewState = '-5835537762767622976:-3219113667535008740'

####### Region: 5, 13, 6, 7 y 8 #######

region = 5

####### Cuenca, CAMBIAR A GUSTO #######

# cuencas_region = {5 : [0, 5, 3, 8, 6, 4, 2, 7, 1], 13: [8], 6 : [1], 7 : [0, 2, 4],  8 : [2, 0, 4, 1]}
cuencas_region = {5 : [0, 5, 3, 8, 6, 4, 2, 7, 1], 13: [7, 8], 6 : [1 , 0], 7 : [0, 2, 4, 1, 3],  8 : [2, 0, 4, 1, 3, 3]} #en orden DGA

# Número de estaciones por cuenca, la fórmula es (idt-171)/5
estCuencaQ = {(13,7) : [55, 'RIO MAIPO'] , (6,0) : [33,'RIO RAPEL'], (7,1) : [21,'RIO MATAQUITO'], (7,3) : [88,'RIO MAULE']}

# Número de estaciones por cuenca, la fórmula es (idt-171)/5
estCuencaPp = {(5,0) : [1,'COSTERA QUILIMARI-PETORCA'], (5,5) : [12,'COSTERAS ACONCAGUA-MAIPO'], (5,3) : [2,'COSTERAS LIGUA-ACONCAGUA'],
               (5,8) : [1,'COSTERAS MAIPO-RAPEL'], (5,6) :  [2,'ISLAS DEL PACIFICO'], (5,4) : [27,'RIO ACONCAGUA'], (5,2) : [12,'RIO LIGUA'], (5,7) : [3,'RIO MAIPO'], 
               (5,1) : [17,'RIO PETORCA'], (13,7) : [65,'RIO MAIPO'], (6,1) : [6,'COSTERAS RAPEL-E. NILAHUE'], (6,0) : [38,'RIO RAPEL'], (7,2) : [2,'COSTERAS MATAQUITO-MAULE'],
               (7,1) : [15,'RIO MATAQUITO'], (7,3) : [57,'RIO MAULE']}

estCuencaPp={(5,0):[77,'VALPARAISO']}

# Número de estaciones por cuenca, la fórmula es (idt-171)/5
estCuencaTex = {(5,5) : [6,'COSTERAS ACONCAGUA-MAIPO'],  (5,6) :  [2,'ISLAS DEL PACIFICO'], (5,4) : [12,'RIO ACONCAGUA'], 
                (5,2) : [1,'RIO LIGUA'],  (6,1) : [3,'COSTERAS RAPEL-E. NILAHUE']} #Maipo, Rapel, Mataquito y Maule ya se descargaron
# estCuencaTex = {(5,5) : 9, (5,3) : 2, (5,6) :  2, (5,4) : 12, (5,2) : 1, 
#                (13,7) : 45, (6,1) : 3, (6,0) : 18, (7,2) : 2, (7,1) : 6, (7,3) : 25}
estCuencaTex={(5,0):[22,'VALPARAISO']}

# Número de estaciones por cuenca, la fórmula es (idt-171)/5
estCuencaTmed = {(5,5) : [6,'COSTERAS ACONCAGUA-MAIPO'], (5,6) :  [2,'ISLAS DEL PACIFICO'], (5,4) : [12,'RIO ACONCAGUA'], (5,2) : [1,'RIO LIGUA'],
               (13,7) : [45,'RIO MAIPO'], (6,1) : [3,'COSTERAS RAPEL-E. NILAHUE'], (6,0) : [18,'RIO RAPEL'], (7,1) : [6,'RIO MATAQUITO'], (7,3) : [25,'RIO MAULE']}

#Número de estaciones de nivel por cuenca, la fórmula es (idt-171)/5
estCuencaTmed={(5,0):[22,'VALPARAISO']}

estCuencaNEP = {(5,5) : [28,'COSTERAS ACONCAGUA-MAIPO'], (5,8) : [1,'COSTERAS MAIPO-RAPEL'], (5,4) : [90,'RIO ACONCAGUA'], (5,30) : [18,'RIO LIGUA'], (5,7) : [1,'RIO MAIPO'],
                (5, 1) : [20, 'RIO PETORCA'], (13, 8) : [1,'COSTERAS MAIPO-RAPEL'], (13,7) : [135,'RIO MAIPO'], (6,1) : [8,'COSTERAS RAPEL-E. NILAHUE'], (6,0) : [178,'RIO RAPEL'], 
                (7,0) : [2,'COSTERAS LIMITE SEPTIMA R.-RIO MATAQUITO'], (7,1) : [21,'RIO MATAQUITO'],   (7,3) : [12,'RIO MAULE']}

estCuencaNEP={(5,0):[162,'VALPARAISO']}

#%% funciones
#Estos son los encabezados del método POST
def get_headers():
    user_agent_list = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'
    ]
    
    User_agent =  random.choice(user_agent_list)
    
    headers = {
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding' : 'gzip, deflate, br',
        'Accept-Language' : 'en-US,en;q=0.5',
        'Cache-Control' : 'no-cache',
        'Connection': 'keep-alive',  
        'Content-Length': '1002',
        'Content-Type' : 'application/x-www-form-urlencoded',
        'Host' : 'snia.mop.gob.cl',
        'Origin' : 'https://snia.mop.gob.cl',
        'Pragma' : 'no-cache',
        'Referer' : 'https://snia.mop.gob.cl/BNAConsultas/reportes',
        'TE' : 'Trailers',
        'Upgrade-Insecure-Requests' : '1',
        'User-Agent': User_agent,
    }
    
    return headers


'''
POST data, corresponde a los filtros por región (filtroscirhform:número de region)
Los filtros de estaciones corresponden a j_idtNNN, donde NNN es el número de la estación, el cual comienza en 177 
y avanza cada 5 unidades por estación, hasta la última estación de la cuenca. Se pueden bajar hasta 9 estaciones, en un
periodo de 4 años. 
FechaIni y fechaFin en formato dd/mm/aaaa '''

def POSTdata(reg, nSubC, dicEstaciones, fechaIni,fechaFin, javax_faces_ViewState):
    DesdeCurrentDate = fechaIni[-7:]
    HastaCurrentDate = fechaFin[-7:]
    data = {'filtroscirhform' : 'filtroscirhform', 
            'filtroscirhform:regionFieldSetId-value' :		'true',
            'filtroscirhform:j_idt30-value' :		'filtroscirhform:j_idt35',
            'filtroscirhform:j_idt43' :		'on', 
            'filtroscirhform:panelFiltroEstaciones-value':		'true',
            'filtroscirhform:region' :		reg,
            'filtroscirhform:selectBusqForEstacion' :	'1',
            'filtroscirhform:cuenca' :	nSubC,
            'filtroscirhform:estacion' :	'',
            'g-recaptcha-response' :		'',
            'filtroscirhform:j_idt100-value' :		'true',
            'filtroscirhform:j_idt102-value'	: 'true'}
    data.update(dicEstaciones)
    data_complementary = {
            'filtroscirhform:j_idt102-value' :		'true',
            'filtroscirhform:fechaDesdeInputDate' :		fechaIni,
            'filtroscirhform:fechaDesdeInputCurrentDate' :		DesdeCurrentDate,
            'filtroscirhform:fechaHastaInputDate' :		fechaFin,
            'filtroscirhform:fechaHastaInputCurrentDate' :		HastaCurrentDate,
            'filtroscirhform:generarxls' :		'Generar+XLS', 
            'javax.faces.ViewState' :	javax_faces_ViewState , #Este se genera al momento de bajar el reporte en xls
            'javax.faces.source' :	'j_idt26',
            'javax.faces.partial.execute' :	'j_idt26 @component',
            'javax.faces.partial.render' :	'@component',
            'org.richfaces.ajax.component' :	'j_idt26',
            'j_idt26' :	'j_idt26',
            'rfExt' :	'null',
            'AJAX:EVENTS_COUNT' :	'1',
            'javax.faces.partial.ajax'	: 'true'} 
    data.update(data_complementary)
    return data

def POSTdataPp(reg,nSubC,dicEstaciones,fechaIni,fechaFin,javax_faces_ViewState):
    data = {'filtroscirhform' : 'filtroscirhform', 
            'filtroscirhform:regionFieldSetId-value' :		'true',
            'filtroscirhform:j_idt30-value' :		'filtroscirhform:j_idt45',
            'filtroscirhform:j_idt62' :		'on', 
            'filtroscirhform:panelFiltroEstaciones-value':		'true',
            'filtroscirhform:region' :		reg,
            'filtroscirhform:selectBusqForEstacion' :	'1',
            'filtroscirhform:cuenca' :	nSubC,
            'filtroscirhform:estacion' :	'',
            'g-recaptcha-response' :		'',
            'filtroscirhform:j_idt100-value' :		'true'}
    data.update(dicEstaciones)
    data_complementary = {
            'filtroscirhform:j_idt102-value' :		'true',
            'filtroscirhform:fechaDesdeInputDate' :		fechaIni,
            'filtroscirhform:fechaDesdeInputCurrentDate' :		'11/2020',
            'filtroscirhform:fechaHastaInputDate' :		fechaFin,
            'filtroscirhform:fechaHastaInputCurrentDate' :		'11/2020',
            'filtroscirhform:generarxls' :		'Generar XLS', 
            'javax.faces.ViewState' :	javax_faces_ViewState }
    #, #Este se genera al momento de bajar el reporte en xls
    
    data.update(data_complementary)
    return data

def POSTdataTex(reg, nSubC, dicEstaciones, fechaIni,fechaFin, javax_faces_ViewState):
    data = {'filtroscirhform' : 'filtroscirhform', 
            'filtroscirhform:regionFieldSetId-value' :		'true',
            'filtroscirhform:j_idt30-value' :	'filtroscirhform:j_idt45',
            'filtroscirhform:j_idt53' :		'on', 
            'filtroscirhform:panelFiltroEstaciones-value':		'true',
            'filtroscirhform:region' :		reg,
            'filtroscirhform:selectBusqForEstacion' :	'1',
            'filtroscirhform:cuenca' :	nSubC,
            'filtroscirhform:estacion' :	'',
            'g-recaptcha-response' :		'',
            'filtroscirhform:j_idt100-value' :		'true'}
    data.update(dicEstaciones)
    data_complementary = {
            'filtroscirhform:j_idt102-value' :		'true',
            'filtroscirhform:fechaDesdeInputDate' :		fechaIni,
            'filtroscirhform:fechaDesdeInputCurrentDate' :		'10/2023',
            'filtroscirhform:fechaHastaInputDate' :		fechaFin,
            'filtroscirhform:fechaHastaInputCurrentDate' :		'10/2023',
            'filtroscirhform:generarxls' :		'Generar+XLS', 
            'javax.faces.ViewState' :	javax_faces_ViewState }#, #Este se genera al momento de bajar el reporte en xls
    data.update(data_complementary)
    return data

def POSTdataTmed(reg, dicEstaciones, fechaIni,fechaFin, javax_faces_ViewState):
    ini=pd.to_datetime(fechaIni)
    fin=pd.to_datetime(fechaFin)
    data = {'filtroscirhform' : 'filtroscirhform', 
            'filtroscirhform:regionFieldSetId-value' :		'true',
            'filtroscirhform:j_idt30-value' :		'filtroscirhform:j_idt45',
            'filtroscirhform:j_idt50' :		'on', 
            'filtroscirhform:panelFiltroEstaciones-value':		'true',
            'filtroscirhform:region' :		str(reg),
            'g-recaptcha-response' :		'',
            'filtroscirhform:j_idt100-value' :		'true'}
    data.update(dicEstaciones)
    data_complementary = {
            'filtroscirhform:j_idt102-value' :		'true',
            'filtroscirhform:fechaDesdeInputDate' :		fechaIni,
            'filtroscirhform:fechaDesdeInputCurrentDate':str(ini.month)+'/'+str(ini.year),
            'filtroscirhform:fechaHastaInputDate' :		fechaFin,
            'filtroscirhform:fechaHastaInputCurrentDate' :str(fin.month)+'/'+str(fin.year),
            'filtroscirhform:generarxls' :		'Generar+XLS', 
            'javax.faces.ViewState' :	javax_faces_ViewState,
            }#, #Este se genera al momento de bajar el reporte en xls
    data.update(data_complementary)
    return data

def POSTdataNEP(reg, nSubC, dicEstaciones, fechaIni,fechaFin, javax_faces_ViewState):
    ini=pd.to_datetime(fechaIni)
    fin=pd.to_datetime(fechaFin)
    data = {'filtroscirhform' : 'filtroscirhform', 
            'filtroscirhform:regionFieldSetId-value' :		'true',
            'filtroscirhform:j_idt30-value' :		'filtroscirhform:j_idt64',
            'filtroscirhform:j_idt66' :		'on', 
            'filtroscirhform:panelFiltroEstaciones-value':		'true',
            'filtroscirhform:region' :		reg,
            'filtroscirhform:selectBusqForEstacion' :	'1',
            'filtroscirhform:cuenca' :	nSubC,
            'filtroscirhform:estacion' :	'',
            'g-recaptcha-response' :		'',
            'filtroscirhform:j_idt100-value' :		'true'}
    data.update(dicEstaciones)
    data_complementary = {
            'filtroscirhform:j_idt102-value' :		'true',
            'filtroscirhform:fechaDesdeInputDate' :		fechaIni,
            'filtroscirhform:fechaDesdeInputCurrentDate' :str(ini.month)+'/'+str(ini.year),
            'filtroscirhform:fechaHastaInputDate' :		fechaFin,
            'filtroscirhform:fechaHastaInputCurrentDate' :str(fin.month)+'/'+str(fin.year),
            'filtroscirhform:generarxls' :		'Genera XLS', 
            'javax.faces.ViewState' :	javax_faces_ViewState }#, #Este se genera al momento de bajar el reporte en xls
    data.update(data_complementary)
    return data

#%% rutas

ruta_git = r'D:\GitHub'
ruta_git = r'C:\Users\ccalvo\Documents\GitHub'
wd = ruta_git+r'\Analisis-Oferta-Hidrica\DGA\datosDGA'
os.chdir(wd)

#%% Caudales

folder = './/datosDGA//Q//'+estCuencaQ[region,cuenca][-1]

try:
    os.makedirs(folder)
except:
    warning = 'Directorio ya existe'

# nombres de estaciones

nEstaciones = np.zeros(estCuencaQ[region,cuenca][0])

for indice in range(1,len(nEstaciones)+1):
    nEstaciones[indice-1] = 177+5*(indice-1)-min(indice-1,1)   
    
# recorrer años
for yr in np.arange(1979,2020,4):
    fechaini = pd.to_datetime('01/01/'+str(yr))
    if yr < 2018:
        fechafin = (fechaini+  pd.DateOffset(years=4)-pd.DateOffset(days=1))
    else:
        fechafin = date.today()


    for i,x in enumerate(nEstaciones):
        estaciones = ["filtroscirhform:j_idt"+str(int(x))]
        dictEstaciones = dict(zip(estaciones, ["on" for x in range(len(estaciones))]))
                           
        data = POSTdata(region, cuenca, dictEstaciones,  fechaini.strftime("%d/%m/%Y") , fechafin.strftime("%d/%m/%Y"), javaxfacesViewState)
        sleep(random.randint(60,120)) #NO CAMBIAR
        r = requests.post('https://snia.mop.gob.cl/BNAConsultas/reportes', headers = get_headers(), cookies=cookies, data=data, stream = True)
        
        if 'Se ha producido un error en el Sistema' in r.text:
                print('Error en el servidor DGA: error Se ha producido un error en el Sistema, archivo Q_'+str(region)+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y"))
                continue
        elif '502 Bad Gateway' in r.text:
                print('Error de conexión con servidor DGA: error 502 Bad Gateway, archivo Q_'+str(region)+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y"))
                continue
        elif not 'No se encontraron registros' in r.text:
            if '<title>MOP - Chile</title>' in r.text:
                sys.exit('¡Actualizar Cookies y Javax faces!, Descarga hasta '+str(fechaini))
            else:
                with open(folder+'//P_'+str(region)+'_'+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y")+'.xls', 'wb') as f:
                    f.write(r.content)
                    continue

#%% Bajar Pp

folderPp = './/Pp//mensuales//'+estCuencaPp[region,0][-1]

try:
    os.makedirs(folderPp)
except:
    warning = 'Directorio ya existe'

# recorrer años
delta=4
for yr in np.arange(2020,2023,delta):
    fechaini = pd.to_datetime('01/01/'+str(yr))
    if yr < 2021:
        fechafin = (fechaini+  pd.DateOffset(years=delta)-pd.DateOffset(days=1))
    else:
        fechafin = date.today()-pd.DateOffset(days=1)

        # nombres de estaciones
    
    nEstacionesPp = np.zeros(estCuencaPp[region, 0][0]) # borrar
    
    for indice in range(1,len(nEstacionesPp)+1):
        nEstacionesPp[indice-1] = 177+5*(indice-1)-min(indice-1,1)   
    
    for i,x in enumerate(nEstacionesPp):
        estacionesPp = ["filtroscirhform:j_idt"+str(int(x))]
        dictEstacionesPp = dict(zip(estacionesPp, ["on" for x in range(len(estacionesPp))]))
           
        dataPp = POSTdataPp(region, '-1', dictEstacionesPp, 
                             fechaini.strftime("%d/%m/%Y") , 
                             fechafin.strftime("%d/%m/%Y"),javaxfacesViewState)
        sleep(random.randint(30,60)) #NO CAMBIAR
        r = requests.post('https://snia.mop.gob.cl/BNAConsultas/reportes', headers = get_headers(), cookies=cookies, data=dataPp, stream = True)
        
        if 'Se ha producido un error en el Sistema' in r.text:
            print('Error en el servidor DGA: error \"Se ha producido un error en el Sistema\", archivo P_'+str(region)+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y"))
            continue
        elif '502 Bad Gateway' in r.text:
            print('Error de conexión con servidor DGA: error 502 Bad Gateway, archivo P_'+str(region)+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y"))
            continue
        elif not 'No se encontraron registros' in r.text:
            if '<title>MOP - Chile</title>' in r.text:
                sys.exit('¡Actualizar Cookies y Javax faces!, Descarga hasta '+str(fechaini))                    
            else:
                with open(folderPp+'//Pm_'+str(region)+'_'+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y")+'.xls', 'wb') as f:
                    f.write(r.content)
                    continue
        
#%% Bajar T extremas

folderTex = './/Tex//'+estCuencaTex[region,0][-1]

try:
    os.makedirs(folderTex)
except:
    warning = 'Directorio ya existe'

     
# recorrer años
for yr in np.arange(2020,2023,4):
    fechaini = pd.to_datetime('01/01/'+str(yr))
    if yr < 2019:
        fechafin = (fechaini+  pd.DateOffset(years=4)-pd.DateOffset(days=1))
    else:
        fechafin = date.today()

        # nombres de estaciones
        
    nEstacionesTex = np.zeros(estCuencaTex[region, 0][0])

    for indice in range(1,len(nEstacionesTex)+1):
        nEstacionesTex[indice-1] = 177+5*(indice-1)-min(indice-1,1)   
            
    for i,x in enumerate(nEstacionesTex):
        estacionesTex = ["filtroscirhform:j_idt"+str(int(x))]
        dictEstacionesTex = dict(zip(estacionesTex, ["on" for x in range(len(estacionesTex))]))
                
        dataTmax = POSTdataTex(region, '-1', dictEstacionesTex,  fechaini.strftime("%d/%m/%Y") , fechafin.strftime("%d/%m/%Y"), javaxfacesViewState)
        sleep(random.randint(60,120)) #NO CAMBIAR
        r = requests.post('https://snia.mop.gob.cl/BNAConsultas/reportes', headers = get_headers(), cookies=cookies, data=dataTmax, stream = True)
        
        
        if 'Se ha producido un error en el Sistema' in r.text:
            print('Error en el servidor DGA: error \"Se ha producido un error en el Sistema\", archivo Tex_'+str(region)+'_'+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y"))
            continue 
        elif '502 Bad Gateway' in r.text:
            print('Error de conexión con servidor DGA: error 502 Bad Gateway, archivo Tex_'+str(region)+'_'+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y"))
            continue
        elif not 'No se encontraron registros' in r.text:
            if '<title>MOP - Chile</title>' in r.text:
                sys.exit('¡Actualizar Cookies y Javax faces!, Descarga hasta '+str(fechaini))                    
            else:
                with open(folderTex+'//Tex_'+str(region)+'_'+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y")+'.xls', 'wb') as f:
                    f.write(r.content)
                    continue

#%% Bajar T medias diarias de valores sinópticos

folderTmed = './/Tmed//'+estCuencaTmed[region,0][-1]

try:
    os.makedirs(folderTmed)
except:
    warning = 'Directorio ya existe'
    print(warning)
     
# recorrer años
for yr in np.arange(2020,2023,4):
    fechaini = pd.to_datetime('01/01/'+str(yr))
    if yr < 2020:
        fechafin = (fechaini+  pd.DateOffset(years=4)-pd.DateOffset(days=1))
    else:
        fechafin = date.today()-pd.DateOffset(days=1)

    # nombres de estaciones
    nEstacionesTmed = np.zeros(estCuencaTmed[region, 0][0])

    
    for indice in range(1,len(nEstacionesTmed)+1):
        nEstacionesTmed[indice-1] = 177+5*(indice-1)-min(indice-1,1)   
            
    for i,x in enumerate(nEstacionesTmed):
        estacionesTmed = ["filtroscirhform:j_idt"+str(int(x))]
        dictEstacionesTmed = dict(zip(estacionesTmed, ["on" for x in range(len(estacionesTmed))]))
                
        dataTmed = POSTdataTmed(region, dictEstacionesTmed,  fechaini.strftime("%d/%m/%Y") , fechafin.strftime("%d/%m/%Y"), javaxfacesViewState)
        sleep(random.randint(60,120)) #NO CAMBIAR
        r = requests.post('https://snia.mop.gob.cl/BNAConsultas/reportes', headers = get_headers(), cookies=cookies, data=dataTmed, stream = True)
        
        if 'Se ha producido un error en el Sistema' in r.text:
            print('Error en el servidor DGA: error \"Se ha producido un error en el Sistema\", archivo Tmed_'+str(region)+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y"))
            continue
        elif '502 Bad Gateway' in r.text:
            print('Error de conexión con servidor DGA: error 502 Bad Gateway, archivo Tmed_'+str(region)+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y"))
            continue
        elif not 'No se encontraron registros' in r.text:
            if '<title>MOP - Chile</title>' in r.text:
                sys.exit('¡Actualizar Cookies y Javax faces!, Descarga hasta '+str(fechaini))
            else:
                with open(folderTmed+'//Tmed_'+str(region)+'_'+'_'+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y")+'.xls', 'wb') as f:
                    f.write(r.content)
                    continue
#%% Bajar Niveles Estáticos en Pozos (Mensual)

folderTmed = './/NEP//mensuales//'+estCuencaPp[region,0][-1]

try:
    os.makedirs(folderTmed)
except:
    warning = 'Directorio ya existe'

     
# recorrer años
#for yr in np.arange(1979,2020,10):
for yr in np.arange(2020,2023,10):
    fechaini = pd.to_datetime('01/01/'+str(yr))
    if yr < 2021:
        fechafin = (fechaini+  pd.DateOffset(years=10)-pd.DateOffset(days=1))
    else:
        fechafin = date.today()-pd.DateOffset(days=1)

        # nombres de estaciones
            
    nEstacionesNEP = np.zeros(estCuencaNEP[region, 0][0])
    
    for indice in range(1,len(nEstacionesNEP)+1):
        nEstacionesNEP[indice-1] = 177+5*(indice-1)-min(indice-1,1)   
            
    for i,x in enumerate(nEstacionesNEP):
        estacionesNEP = ["filtroscirhform:j_idt"+str(int(x))]
        dictEstacionesNEP = dict(zip(estacionesNEP, ["on" for x in range(len(estacionesNEP))]))
                
        dataTmed = POSTdataNEP(region, '-1', dictEstacionesNEP, 
                                fechaini.strftime("%d/%m/%Y") , 
                                fechafin.strftime("%d/%m/%Y"), javaxfacesViewState)
        sleep(random.randint(30,90)) #NO CAMBIAR
        r = requests.post('https://snia.mop.gob.cl/BNAConsultas/reportes', headers = get_headers(), cookies=cookies, data=dataTmed, stream = True)
        
        if 'Se ha producido un error en el Sistema' in r.text:
            print('Error en el servidor DGA: error \"Se ha producido un error en el Sistema\", archivo NEP_'+str(region)+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y"))
            continue
        elif '502 Bad Gateway' in r.text:
            print('Error de conexión con servidor DGA: error 502 Bad Gateway, archivo NEP_'+str(region)+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y"))
            continue
        elif not 'No se encontraron registros' in r.text:
            if '<title>MOP - Chile</title>' in r.text:
                sys.exit('¡Actualizar Cookies y Javax faces!, Descarga hasta '+str(fechaini))
            else:
                with open(folderTmed+'//NEP_'+str(region)+'_'+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y")+'.xls', 'wb') as f:
                    f.write(r.content)
                    continue