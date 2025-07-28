import os
import requests
import concurrent.futures
from time import time

# Pasta de saída
output_dir = "cpf_results"
os.makedirs(output_dir, exist_ok=True)

# Cálculo de dígitos verificadores do CPF
def calc_dv(cpf_base, fator):
    total = sum(int(d) * f for d, f in zip(cpf_base, range(fator, 1, -1)))
    resto = total % 11
    return '0' if resto < 2 else str(11 - resto)

# Geração de CPFs válidos
def gerar_cpfs_validos():
    for i in range(1, 1_000_000_000):  # de 000000001 até 999999999
        base = f"{i:09}"
        d1 = calc_dv(base, 10)
        d2 = calc_dv(base + d1, 11)
        cpf = base + d1 + d2
        yield f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

# Consulta e salvamento
def consultar_cpf(cpf):
    url = f"https://valores-nu.it.com/consult/consulta.php?cpf={cpf}"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        if "nome" in data:
            meio = cpf[4:11].replace('.', '')
            caminho = os.path.join(output_dir, f"{meio}.txt")
            with open(caminho, "w", encoding="utf-8") as f:
                f.write("--------------------------\n")
                for k, v in data.items():
                    f.write(f"{k.upper()}: {v}\n")
                f.write("--------------------------\n")
            print(f"[✅] {cpf} → {data['nome']}")
        else:
            print(f"[⚠️] {cpf} sem dados.")
    except Exception as e:
        print(f"[❌] {cpf} ERRO: {e}")

# Execução com 400 threads
def main():
    print("🔍 Iniciando consultas com 400 threads...")
    cpfs = gerar_cpfs_validos()
    with concurrent.futures.ThreadPoolExecutor(max_workers=400) as executor:
        executor.map(consultar_cpf, cpfs)

if __name__ == "__main__":
    inicio = time()
    main()
    print(f"\n⏱️ Finalizado em {time() - inicio:.2f} segundos")
