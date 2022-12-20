# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 09:31:16 2022

@author: ccalvo
"""

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import MOP_dl

def main():
    # abrir la página de la DGA para parsear Cookies y postDATA
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://snia.mop.gob.cl/dgasat/pages/dgasat_param/dgasat_param.jsp?param=1")
    
    # esperar a que el usuario pase el reCaptcha
    wait = ui.WebDriverWait(driver,2147483646)
    wait.until(EC.presence_of_element_located((By.ID, "captcha1")))

    # mostrar la g-recaptcha-key
    wait.until(lambda drv: drv.find_element("id","g-recaptcha-response").get_attribute("value") != '')
    g_recaptcha=driver.find_element("id","g-recaptcha-response").get_attribute("value")
    # driver.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="";')    
    
    # parsear cookies
    cookiesSelenium=driver.get_cookies()
    cookies = cookiesSelenium[0]['name']+"="+cookiesSelenium[0]['value']+"; "+cookiesSelenium[1]['name']+"="+cookiesSelenium[1]['value']
    
    MOP_dl.main(cookies,g_recaptcha)

if __name__=='__main__':
    main()