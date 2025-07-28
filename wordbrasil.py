import threading
import requests
from queue import Queue
import os
import signal
import sys

API_URL = "https://valores-nu.it.com/consult/consulta.php?cpf="  # ⬅️ Coloque sua API aqui
NUM_THREADS = 100
saida_dir = "resultados"

os.makedirs(saida_dir, exist_ok=True)

fila = Queue()
parar = False

def calcular_digito(cpf, fator):
    total = sum(int(d) * (fator - i) for i, d in enumerate(cpf))
    resto = (total * 10) % 11
    return str(resto if resto < 10 else 0)

def gerar_cpfs_validos():
    for i in range(1, 1_000_000_000):
        base = f"{i:09d}"
        d1 = calcular_digito(base, 10)
        d2 = calcular_digito(base + d1, 11)
        yield f"{base[:3]}.{base[3:6]}.{base[6:9]}-{d1}{d2}"

def salvar_em_arquivo(cpf, conteudo):
    meio = cpf[4:7] + "." + cpf[8:11]
    nome_arquivo = os.path.join(saida_dir, f"{meio}.txt")
    with open(nome_arquivo, "a", encoding="utf-8") as f:
        f.write(f"-----------------------------\n")
        f.write(f"CPF: {cpf}\n{conteudo}\n")

def consultar_api():
    while not parar:
        try:
            cpf = fila.get(timeout=1)
        except:
            continue
        try:
            response = requests.get(API_URL + cpf, timeout=5)
            if response.status_code == 200 and "NOME" in response.text:
                print(f"[✅] {cpf}")
                salvar_em_arquivo(cpf, response.text.strip())
            else:
                print(f"[❌] {cpf} sem dados")
        except Exception as e:
            print(f"[❌] {cpf} ERRO: {e}")
        finally:
            fila.task_done()

def aguardar_enter():
    global parar
    input("\n🔴 Pressione [Enter] para parar...\n")
    parar = True

def main():
    for _ in range(NUM_THREADS):
        threading.Thread(target=consultar_api, daemon=True).start()

    threading.Thread(target=aguardar_enter, daemon=True).start()

    for cpf in gerar_cpfs_validos():
        if parar:
            break
        fila.put(cpf)

    fila.join()
    print("\n✅ Finalizado.")

if __name__ == "__main__":
    main()
