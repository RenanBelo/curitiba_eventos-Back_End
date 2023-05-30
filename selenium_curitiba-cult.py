from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import json
import time

url = "https://curitibacult.com.br/agenda-de-shows/"

driver = webdriver.Chrome()
driver.get(url)
time.sleep(15)

eventos = []
scroll_pause_time = 1

while True:
    try:
        nome_eventos = driver.find_elements_by_css_selector("#ano-2023 h4")
        datas_horarios = driver.find_elements_by_css_selector("#ano-2023 p.data")
        enderecos_locais = driver.find_elements_by_css_selector("#ano-2023 p.local")

        for nome_evento, data_horario, endereco_local in zip(nome_eventos, datas_horarios, enderecos_locais):
            nome_evento = nome_evento.text
            data_horario = data_horario.text.split(": ")[1]
            endereco_local = endereco_local.text.split(": ")[1]

            dados = {
                "nome_evento": nome_evento,
                "data_horario": data_horario,
                "endereco_local": endereco_local
            }
            eventos.append(dados)

        # Verificar se há um botão "Carregar mais" e clicar nele
        load_more_button = driver.find_element_by_css_selector("#ano-2023 .load-more")
        if not load_more_button.is_displayed():
            break
        driver.execute_script("arguments[0].click();", load_more_button)
        time.sleep(scroll_pause_time)

    except NoSuchElementException:
        break

with open("eventos_teste.json", "w", encoding="utf-8") as f:
    json.dump(eventos, f, ensure_ascii=False)

driver.close()
