from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def fill_job_application_form(job_url, user_data):
    """
    İş başvuru formunu otomatik olarak doldurur.
    """
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(job_url)
    
    # Form alanlarını doldur
    driver.find_element(By.NAME, "name").send_keys(user_data['name'])
    driver.find_element(By.NAME, "email").send_keys(user_data['email'])
    driver.find_element(By.NAME, "phone").send_keys(user_data['phone'])
    driver.find_element(By.NAME, "location").send_keys(user_data['location'])
    driver.find_element(By.NAME, "experience").send_keys(user_data['experience'])
    driver.find_element(By.NAME, "education").send_keys(user_data['education'])
    
    # Başvuru butonuna tıkla
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    # Tarayıcıyı kapat
    driver.quit() 