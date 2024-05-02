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

cookies = {'_ga' : 'GA1.1.294899385.1693404770', 
# 'cookiesession1' : '252721ECCWZQRSL47VOD6OACDJE741C0', 
'JSESSIONID' : '0000Fdj3Vjxgt_y6i8BVljrH9hI:-1'} 

# POST data de la sesión ####### CAMBIAR, un post data por cuenca #######
javaxfacesViewState = '6490663781052664366:-80079624678642493'

####### Region: 5, 13, 6, 7 y 8 #######

region = 15

####### Cuenca, CAMBIAR A GUSTO #######

# Número de estaciones por cuenca, la fórmula es (idt-171)/5
estCuencaPpMon = { 15: 49
}
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

def POSTdataPpMon(reg, dicEstaciones, fechaIni,fechaFin, javax_faces_ViewState):
    DesdeCurrentDate = fechaIni[-7:]
    HastaCurrentDate = fechaFin[-7:]
    data = {'filtroscirhform' : 'filtroscirhform', 
            'filtroscirhform:regionFieldSetId-value' :		'true',
            'filtroscirhform:j_idt30-value' :		'filtroscirhform:j_idt45',
            'filtroscirhform:j_idt56' :		'on', 
            'filtroscirhform:panelFiltroEstaciones-value':		'true',
            'filtroscirhform:region' :		reg,
            'filtroscirhform:estacion' :	'',
            'g-recaptcha-response' :		'',
            'filtroscirhform:j_idt100-value' :		'true'}
    data.update(dicEstaciones)
    data_complementary = {
            'filtroscirhform:j_idt102-value' :		'true',
            'filtroscirhform:fechaDesdeInputDate' :		fechaIni,
            'filtroscirhform:fechaDesdeInputCurrentDate' :		DesdeCurrentDate,
            'filtroscirhform:fechaHastaInputDate' :		fechaFin,
            'filtroscirhform:fechaHastaInputCurrentDate' :		HastaCurrentDate,
            'filtroscirhform:generarxls' :		'Generar+XLS', 
            'javax.faces.ViewState' :	javax_faces_ViewState , 
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

def descarga(region, x, fechaini, fechafin, folderPp, dictEstacionesPp, javaxfacesViewState):
    dataPp = POSTdataPpMon(region, dictEstacionesPp, 
                        fechaini.strftime("%d/%m/%Y") , 
                        fechafin.strftime("%d/%m/%Y"),javaxfacesViewState)
    sleep(random.randint(60,90)) #NO CAMBIAR
    req = requests.post('https://snia.mop.gob.cl/BNAConsultas/reportes', headers = get_headers(), cookies=cookies, data=dataPp, stream = True)
    return req

def main():
    #%% rutas

    ruta=r'/Users/farrospide/'
    wd=os.path.join(ruta,'DGA')
    try:
        os.makedirs(wd)
    except:
        warning = 'Directorio ya existe'
    os.chdir(wd)

    folder = os.path.join(wd,'ppMon',str(region))

    try:
        os.makedirs(folder)
    except:
        warning = 'Directorio ya existe'

    # nombres de estaciones
    nEstaciones = np.zeros(estCuencaPpMon[region])

    for indice in range(1,len(nEstaciones)+1):
        nEstaciones[indice-1] = 177+5*(indice-1)-min(indice-1,1)   
        
    # recorrer años
    delta=10
    for yr in np.arange(2020,2024,delta):
        fechaini = pd.to_datetime('01/01/'+str(yr))
        if yr < 2024:
            fechafin = (fechaini+  pd.DateOffset(years=delta)-pd.DateOffset(days=1))
        else:
            fechafin = date.today()-pd.DateOffset(days=1)

        # nombres de estaciones
        nEstacionesPp = np.zeros(estCuencaPpMon[region]) # borrar
        
        for indice in range(1,len(nEstacionesPp)+1):
            nEstacionesPp[indice-1] = 177+5*(indice-1)-min(indice-1,1)   
        
        # comienza la descarga
        for i,x in enumerate(nEstacionesPp):
            estacionesPp = ["filtroscirhform:j_idt"+str(int(x))]
            dictEstacionesPp = dict(zip(estacionesPp, ["on" for x in range(len(estacionesPp))]))
            
            retryWords=['Se ha producido un error en el Sistema','502 Bad Gateway','Forbidden',"You don't have permission to access this resource."]

            # primer intento
            r=descarga(region, x, fechaini, fechafin, folder, dictEstacionesPp, javaxfacesViewState)
            rWhile=r.text[:]

            for loop_count in range(10):
                if any(word in rWhile for word in retryWords):
                    print('Error en el servidor DGA: error archivo P_'+str(region)+'_'+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y"))
                    sleep(random.randint(60,90)) #NO CAMBIAR
                    r=descarga(region, x, fechaini, fechafin, folder, dictEstacionesPp, javaxfacesViewState)
                    rWhile=r.text[:]
                else:
                    break

            if not 'No se encontraron registros' in r.text:
                if '<title>MOP - Chile</title>' in r.text:
                    sys.exit('¡Actualizar Cookies y Javax faces!, Descarga hasta '+str(fechaini))                    
                else:
                    with open(folder+'//Pm_'+str(region)+'_'+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y")+'.xls', 'wb') as f:
                        f.write(r.content)
                        continue
            
if __name__=='__main__':
    main()