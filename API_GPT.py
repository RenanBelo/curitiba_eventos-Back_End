# Configuração da API da OpenAI
import json
import openai
import speech_recognition as sr
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import api_key

# Carrega os dados do arquivo JSON
with open('eventos_teste.json', encoding="utf-8") as file:
    eventos_data = json.loads(file.read())

# Configuração da API da OpenAI
openai.api_key = api_key

# Inicialização do servidor Flask
app = Flask(__name__)
CORS(app)  # Adicione esta linha para habilitar o CORS

# Histórico inicial vazio
historico = []
eventos = eventos_data.copy()  # Cópia dos eventos do JSON

# Função para calcular o número de tokens em uma lista de mensagens
def calcular_numero_tokens(mensagens):
    return sum(len(msg['content'].split()) for msg in mensagens)

# Função para enviar a pergunta para a API do ChatGPT
def enviar_pergunta(pergunta):
    # Adiciona a pergunta ao histórico
    historico.append({"role": "user", "content": pergunta})

    # Calcula o número de tokens utilizados no histórico atual
    num_tokens_historico = calcular_numero_tokens(historico)

    # Remove mensagens mais antigas do histórico, se o número de tokens ultrapassar um limite
    limite_tokens = 4000  # Defina o limite de tokens desejado
    while num_tokens_historico > limite_tokens:
        primeira_mensagem = historico.pop(0)
        num_tokens_historico = calcular_numero_tokens(historico)

    # Realiza a chamada à API do ChatGPT com o histórico completo e os eventos
    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=historico + [{"role": "system", "content": json.dumps(eventos)}]
    )

    # Obtém a resposta do modelo
    resposta_modelo = resposta.choices[0].message.content

    # Adiciona a resposta do modelo ao histórico
    historico.append({"role": "system", "content": resposta_modelo})

    return resposta_modelo

# Rota para obter a lista de eventos
@app.route('/eventos', methods=['GET'])
def obter_eventos():
    return jsonify(eventos)

# Rota para lidar com as perguntas sobre eventos
@app.route('/pergunta-evento', methods=['POST'])
def pergunta_evento():
    pergunta = request.json['pergunta']
    resposta = enviar_pergunta(pergunta)
    return jsonify({'resposta': resposta})

# Rota para lidar com as perguntas por voz
@app.route('/pergunta-voz', methods=['POST'])
def pergunta_voz():
    recognizer = sr.Recognizer()
    audio = request.files['audio']

    # Salva o áudio em um arquivo temporário
    with sr.AudioFile(audio) as source:
        audio_data = recognizer.record(source)

    # Realiza o reconhecimento de voz
    pergunta = recognizer.recognize_google(audio_data, language='pt-BR')
    resposta = enviar_pergunta(pergunta)
    return jsonify({'resposta': resposta})

# Execução do servidor Flask em modo de depuração
if __name__ == '__main__':
    app.run(debug=True)
