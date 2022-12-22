# Actualizacion_DT

## Códigos del convenio ACTUALIZACIÓN DT-01 “CAUDALES 85 % DE SEGURIDAD” Y DT-02 “ESTACIONES FLUVIOMÉTRICAS PRINCIPALES CON SU RESPECTIVO ANÁLISIS DE FRECUENCIA (DATOS SIIR)"

### Instrucciones de la herramienta de descarga de caudales medios diarios de la DGA y MOP

Descargar el archivo https://github.com/ccalvocm/Actualizacion_DT/blob/main/DMDownloader.zip?raw=true

#### Descarga de registros fluviométricos de la DGA:
- Descomprimir el archivo .zip en su computador
- Modificar el archivo de la carpeta "outputs/lastYearDGA.csv" e ingresar el año desde el cual se requiere bajar información.
- Ejectutar SeleniumDGA.exe
- En la ventana emergente:
    * Seleccionar "Reportes Fluviométricos" 
    * Seleccionar "Caudales Medios Diarios"
    * Seleccionar la región de la cual quiere descargar los datos fluviométricos.
    * Presionar el cuadro "No soy un robot" y resolver el reCAPTCHA.
- Esperar. Los resultados se descargarán en la carpeta "outputs" ubicada donde ejecutaron SeleniumDGA.exe

#### Descarga de registros fluviométricos del MOP:
- Descomprimir el archivo .zip en su computador
- Modificar el archivo de la carpeta "outputs/lastYearMOP.csv" e ingresar el año desde el cual se requiere bajar información.
- Ejectutar SeleniumMOP.exe
- En la ventana emergente:
    * Seleccionar cualquier estación en el menú "- Seleccione Estación 1 -" 
    * Seleccionar "Ver Parámetros"
    * Presionar el cuadro "No soy un robot" y resolver el reCAPTCHA.
- Esperar. Los resultados se descargarán en la carpeta "outputs" ubicada donde ejecutaron SeleniumMOP.exe
