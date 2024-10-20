from flask import Flask, request, jsonify
from flask_cors import CORS
import serial
import threading
import time
import json
import os

app = Flask(__name__)
CORS(app)

students = {}
rfid_data = None  # Variável global para armazenar o ID lido
DATA_FILE = 'C:/Users/gusta/OneDrive/Desktop/bd-rfid/alunos.json'  # Nome do arquivo para persistência

def load_students():
    global students
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            students = json.load(file)
    else:
        students = {}  # Inicia um novo dicionário se o arquivo não existir

def save_students():
    with open(DATA_FILE, 'w') as file:
        json.dump(students, file, indent=4)

def read_rfid():
    global rfid_data
    ser = serial.Serial('COM4', 9600)  # Altere para a porta do seu leitor RFID
    while True:
        try:
            # Lê o ID do cartão
            raw_data = ser.readline().decode().strip()
            uid = extract_uid(raw_data)
            if uid:  # Se o UID for encontrado, armazena na variável global
                rfid_data = uid
                print(f"ID lido do cartão: {rfid_data}")  # Exibe o ID lido no console
        except Exception as e:
            print(f"Erro na leitura do cartão: {e}")  # Tratar erros de leitura

def extract_uid(raw_data):
    # Aqui você pode definir a lógica para extrair o UID do cartão
    if "UID do cartão: " in raw_data:
        return raw_data.split("UID do cartão: ")[1].strip()
    return None  # Retorna None se o UID não for encontrado

@app.route('/register', methods=['POST'])
def register_student():
    global rfid_data
    print("Aguardando leitura do cartão...")

    # Aguarda a leitura do cartão
    timeout = 10  # Tempo de espera em segundos
    start_time = time.time()

    # Aguarda o cartão ser lido por 10 segundos
    while rfid_data is None and (time.time() - start_time) < timeout:
        time.sleep(1)  # Espera 1 segundo antes de verificar novamente

    if rfid_data is None:
        return jsonify({"error": "ID do cartão RFID não lido"}), 400

    data = request.json
    name = data.get('name')

    if name:
        # Salva o aluno com o ID do cartão lido
        students[name] = rfid_data
        print(f"Aluno '{name}' cadastrado com ID {rfid_data}")
        save_students()  # Salva os dados dos alunos no arquivo
        rfid_data_to_return = rfid_data  # Armazena o ID para retornar
        rfid_data = None  # Limpa o ID após o registro
        return jsonify({"message": f"Aluno '{name}' cadastrado com ID '{rfid_data_to_return}'."}), 201
    else:
        return jsonify({"error": "Nome não fornecido"}), 400

@app.route('/access', methods=['POST'])
def access_student():
    global rfid_data
    print("Aguardando leitura do cartão...")

    # Aguarda a leitura do cartão
    timeout = 10  # Tempo de espera em segundos
    start_time = time.time()

    # Aguarda o cartão ser lido por 10 segundos
    while rfid_data is None and (time.time() - start_time) < timeout:
        time.sleep(1)  # Espera 1 segundo antes de verificar novamente

    if rfid_data is None:
        return jsonify({"error": "ID do cartão RFID não lido"}), 400

    # Verifica se o UID lido está no dicionário de alunos
    for name, uid in students.items():
        if uid == rfid_data:
            print(f"Acesso liberado para '{name}' com ID {rfid_data}")
            rfid_data = None  # Limpa o ID após a verificação
            return jsonify({"message": f"Acesso liberado para '{name}'"}), 200

    rfid_data = None  # Limpa o ID após a verificação falha
    return jsonify({"error": "Acesso negado"}), 403

@app.route('/list', methods=['GET'])
def list_students():
    return jsonify(students)

if __name__ == '__main__':
    load_students()  # Carrega os dados dos alunos no início
    threading.Thread(target=read_rfid, daemon=True).start()
    app.run(port=5000)
