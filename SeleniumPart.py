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
from bs4 import BeautifulSoup
import DGA_dler

def main():
    # abrir la página de la DGA para parsear Cookies y postDATA
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://snia.mop.gob.cl/BNAConsultas/reportes")
    
    # esperar a que el usuario pase el reCaptcha
    wait = ui.WebDriverWait(driver,2147483646)
    wait.until(EC.presence_of_element_located((By.ID, "filtroscirhform:generarxls")))
    
    # esperar a que el usuario resuelva el reCaptcha por si cauducó de manera inesperada
    # captcha = driver.find_element_by_css_selector('iframe[role=presentation]')
    #
    # wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME,'rc-anchor-error-msg')))
    
    
    # wait.until(EC.text_to_be_present_in_element((By.ID, "recaptcha-accessible-status"), 'Estás verificado.'))
    # wait.until(EC.presence_of_element_located((By.CLASS_NAME, '.rc-anchor-error-msg-container:([style*="display: none"])')))    
    
    # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "rc-anchor-aria-status")))
        
    # clickear el boton si no se ha hecho
    # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "buttonsDiv"))).click()
    
    # parsear cookies
    cookiesSelenium=driver.get_cookies()
    cookies = {cookiesSelenium[0]['name']:cookiesSelenium[0]['value'],
                cookiesSelenium[1]['name']:cookiesSelenium[1]['value']}
    
    pageSource = driver.page_source
    soup = BeautifulSoup(pageSource, 'html.parser')
    
    # parsear postDATA
    javaxFaces=soup.find('input', {'name':'javax.faces.ViewState'})['value']
    
    # parsear region
    leftString=pageSource.index('" selected="selected">')-4
    rightString=pageSource.index('" selected="selected">')
    reg=pageSource[leftString:rightString].replace('"','').replace('=','').replace(' ','')
    
    DGA_dler.main(cookies,javaxFaces,int(reg))

if __name__=='__main__':
    main()