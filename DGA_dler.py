# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 10:25:23 2020
@author: ccalvo
Version 1.4.0
"""

from datetime import date
import requests #librería para hacer consultas https
import pandas as pd
from time import sleep
import random
import os
import sys

#Variables globales

'''La página necesita las Cookies de la sesión en que uno pasó el reCaptcha. 
Pueden ir aquí o en los encabezados, pero por orden prefiero en este diccionario.
'''
####### CAMBIAR, una Cookie por region #######
# inputs=pickle.load(open("inputs.pkl", "rb"))

# cookies = {inputs[0][0]['name']:inputs[0][0]['value'],
#            inputs[0][1]['name']:inputs[0][1]['value']}

# # POST data de la sesión ####### CAMBIAR, un post data por region #######
# javaxfacesViewState = inputs[1]
# ####### Region: 1 a 15 #######
# region = inputs[2]

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
            # 'filtroscirhform:j_idt366' :		'on',
            'filtroscirhform:fechaDesdeInputDate' :		fechaIni,
            'filtroscirhform:fechaDesdeInputCurrentDate':date.today().strftime("%m/%Y"),
            'filtroscirhform:fechaHastaInputDate' :		fechaFin,
            'filtroscirhform:fechaHastaInputCurrentDate':date.today().strftime("%m/%Y"),
            'filtroscirhform:generarxls' :		'Generar+XLS', 
            'javax.faces.ViewState' :	javax_faces_ViewState , #Este se genera al momento de bajar el reporte en xls
            'javax.faces.source' :	'j_idt26',
            'javax.faces.partial.execute' :	'j_idt26 @component',
            'javax.faces.partial.render' :	'@component',
            'org.richfaces.ajax.component' :	'j_idt26',
            'j_idt26' :	'j_idt26',
            'rfExt' :	'null',
            'AJAX:EVENTS_COUNT' :	'1',
            'javax.faces.partial.ajax'	: 'true'
            } 
    data.update(data_complementary)
    return data

def POSTdataEmb(reg,nSubC,dicEstaciones,fechaIni,fechaFin,javax_faces_ViewState):
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
            # 'filtroscirhform:j_idt366' :		'on',
            'filtroscirhform:fechaDesdeInputDate' :		fechaIni,
            'filtroscirhform:fechaDesdeInputCurrentDate':date.today().strftime("%m/%Y"),
            'filtroscirhform:fechaHastaInputDate' :		fechaFin,
            'filtroscirhform:fechaHastaInputCurrentDate':date.today().strftime("%m/%Y"),
            'filtroscirhform:generarxls' :		'Generar+XLS', 
            'javax.faces.ViewState' :	javax_faces_ViewState , #Este se genera al momento de bajar el reporte en xls
            'javax.faces.source' :	'j_idt26',
            'javax.faces.partial.execute' :	'j_idt26 @component',
            'javax.faces.partial.render' :	'@component',
            'org.richfaces.ajax.component' :	'j_idt26',
            'j_idt26' :	'j_idt26',
            'rfExt' :	'null',
            'AJAX:EVENTS_COUNT' :	'1',
            'javax.faces.partial.ajax'	: 'true'
            } 
    data.update(data_complementary)
    return data

#%% rutas
def main(cookies,javaxfacesViewState,region):
    
    # ruta
    wd = os.path.join('.','outputs')
    
    # variables
    # diccionario de regiones
    dict_reg={
    	15:['DE_ARICA_Y_PARINACOTA',36],
    	1:['DE_TARAPACA',26],
    	2:['DE_ANTOFAGASTA',79],
    	3:['DE_ATACAMA',59],
    	4:['DE_COQUIMBO',98],
    	5:['DE_VALPARAISO',66],
    	13:['METROPOLITANA',62],
    	6:['DEL_LIB.BDO.O\'HIGGINS',109],
    	7:['DEL_MAULE',115],
    	16:['DE_NUBLE',38],
    	8:['DEL_BIOBIO',103],
    	9:['DE_LA_ARAUCANIA',71],
    	14:['DE_LOS_RIOS',33],
    	10:['DE_LOS_LAGOS',50],
    	11:['DE_AISEN_DEL_GRAL.CARLOS_IBANEZ',57],
    	12:['DE_MAGALLANES_Y_DE_LA_ANTARTICA',59]}

    # Número de estaciones por cuenca, la fórmula es (idt-171)/5
    estCuencaQ = {(region,-1) : [dict_reg[region][1], dict_reg[region][0]]}

    # URL
    URL='https://snia.mop.gob.cl/BNAConsultas/reportes'
    
    #%% Caudales
    
    folder=os.path.join(wd,estCuencaQ[region,-1][-1])
    
    try:
        os.makedirs(folder)
    except:
        pass
    
    # nombres de estaciones
    nEstaciones=[177+5*(indice-1)-min(indice-1,1) for indice in range(1,estCuencaQ[region,-1][0]+1)] 
    
    # cargar el año en que expiró la cookie, si no existe es 1972
    path_last_yr=os.path.join('.','outputs','last_year.csv')
    if os.path.isfile(path_last_yr):
        year_ini=int(pd.read_csv(path_last_yr).columns[0])
    else:
        year_ini=1972
        
    # recorrer años
    for yr in list(range(year_ini,date.today().year,4)):
        fechaini = pd.to_datetime('01/01/'+str(yr))
        if yr < date.today().year:
            fechafin = (fechaini+pd.DateOffset(years=4)-pd.DateOffset(days=1))
        else:
            fechafin = date.today()
    
        # descargar por estacion
        for i,x in enumerate(nEstaciones):
            estaciones = ["filtroscirhform:j_idt"+str(int(x))]
            dictEstaciones = dict(zip(estaciones, ["on" for x in range(len(estaciones))]))
                               
            data = POSTdata(region,-1,dictEstaciones,fechaini.strftime("%d/%m/%Y"),
fechafin.strftime("%d/%m/%Y"), javaxfacesViewState)
            sleep(random.randint(120,180)) #NO CAMBIAR
            r = requests.post(URL,headers=get_headers(),cookies=cookies,
data=data,stream=True)
            
        # chequear errores del servidor
            while any(x in r.text for x in ['Se ha producido un error en el Sistema',
'502 Bad Gateway']):
                sleep(random.randint(70,120)) #NO CAMBIAR
                r = requests.post(URL,headers=get_headers(),cookies=cookies,
data=data,stream=True)
            
        # ya que no hay error, revisar el output
            if 'No se encontraron registros' in r.text:
                continue
            elif '<title>MOP - Chile</title>' in r.text:
                    pd.DataFrame([yr],columns=['Yr']).to_csv(path_last_yr,
index=None,header=None,columns=None)
                    sys.exit('¡Actualizar Cookies y Javax faces!, Descarga hasta '+str(fechaini))
            else:
                with open(os.path.join(folder,'Q_'+str(region)+'_'+str(int(x))+'_'+fechaini.strftime("%d-%m-%Y")+'_'+fechafin.strftime("%d-%m-%Y")+'.xls'), 'wb') as f:
                    f.write(r.content)
                    continue
    # cuando termina, borrar el año
    os.remove(path_last_yr)

# if __name__=='__main__':
#     main(cookies,javaxfacesViewState, region)