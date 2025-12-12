#!/usr/bin/env python3
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ClaudeWebChat:
    def __init__(self, headless=True):
        # Opzioni ottimizzate per hardware limitato
        firefox_options = Options()
        if headless:
            firefox_options.add_argument("--headless")  # Modalità senza interfaccia grafica
        
        # Path modificabile per netbook
        firefox_path = "/usr/bin/firefox"  # Verifica il percorso esatto
        
        # Usa geckodriver (più leggero di Chrome)
        self.driver = webdriver.Firefox(options=firefox_options)
        
        # Login richiesto manualmente la prima volta
        self.login()

    def login(self):
        # Apri pagina di login
        self.driver.get("https://claude.ai/login")
        print("⚠️ ATTENZIONE: Effettua manualmente il login nel browser")
        input("Premi INVIO dopo aver completato il login...")
        
        # Attendi caricamento pagina principale
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='Scrivi un messaggio']"))
        )

    def send_message(self, message):
        try:
            # Trova textarea di input
            textarea = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='Scrivi un messaggio']"))
            )
            
            # Pulisci eventuale testo precedente
            textarea.clear()
            
            # Inserisci messaggio
            textarea.send_keys(message)
            textarea.send_keys(Keys.RETURN)
            
            # Attendi risposta
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'text-gray-900')]"))
            )
            
            # Estrai ultima risposta
            responses = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'text-gray-900')]")
            if responses:
                return responses[-1].text
            
        except Exception as e:
            print(f"Errore durante l'invio del messaggio: {e}")
            return None

    def close(self):
        self.driver.quit()

def main():
    # Installazione dipendenze
    try:
        import selenium
    except ImportError:
        print("Installo dipendenze...")
        os.system("pip3 install selenium --break-system-packages")

    chat = ClaudeWebChat(headless=False)  # Modalità visibile per debug
    
    while True:
        try:
            message = input("\n📨 Messaggio (o 'esci' per uscire): ")
            
            if message.lower() in ['esci', 'exit', 'quit']:
                break
            
            risposta = chat.send_message(message)
            
            if risposta:
                print("\n🤖 Risposta di Claude:")
                print(risposta)
        
        except KeyboardInterrupt:
            print("\n\nChiusura in corso...")
            break
    
    chat.close()

if __name__ == "__main__":
    main()