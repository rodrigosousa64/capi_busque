import hashlib

def gerar_identidade_robusta(gpu, nucleos, memoria):
    # 1. Normalização do Payload
    dna_maquina = f"{gpu}{nucleos}{memoria}".lower().replace(" ", "")
    
    # 2. Geração do Hash (MD5 é suficiente para distribuição fonética aqui)
    hash_obj = hashlib.md5(dna_maquina.encode()).hexdigest()
    seed_nome = int(hash_obj[:8], 16)
    seed_sobrenome = int(hash_obj[8:16], 16)
    
    # 3. Dicionários Expandidos (Keyspace)
    # Adicionamos o 'C' e o 'J' para nomes como Caio, Julio, etc.
    consonants = ["B", "C", "D", "F", "G", "J", "L", "M", "N", "P", "R", "S", "T", "V", "Z"]
    vowels = ["a", "e", "i", "o", "u"]
    
    # Terminações clássicas de nomes latinos/brasileiros
    terminacoes = [
        "an", "el", "io", "on", "as", "er", "os", "us", 
        "im", "in", "am", "is", "al", "or", "ur", "en",
        "ardo", "aldo", "ano", "ito"
    ]
    
    # Sufixos que simulam sobrenomes reais (ex: C + V + sufixo = P+e+reira = Pereira)
    sufixos_sobrenome = [
        "rros", "lho", "reira", "lva", "nto", "nha", "rais", 
        "uza", "veira", "gues", "mes", "nes", "tes", "res", 
        "tos", "va", "ra", "ros", "no", "co"
    ]
    
    # 4. Engine do Nome Principal
    c1 = consonants[seed_nome % len(consonants)]
    v1 = vowels[(seed_nome // 3) % len(vowels)]
    t1 = terminacoes[(seed_nome // 7) % len(terminacoes)]
    nome_final = f"{c1}{v1}{t1}"
    
    # 5. Engine do Sobrenome
    s_cons = consonants[seed_sobrenome % len(consonants)]
    s_vow = vowels[(seed_sobrenome // 5) % len(vowels)]
    sufixo_final = sufixos_sobrenome[(seed_sobrenome // 11) % len(sufixos_sobrenome)]
    sobrenome_final = f"{s_cons}{s_vow}{sufixo_final}"
    
    return f"{nome_final.capitalize()} {sobrenome_final.capitalize()}"

# Teste Operacional
id_unidade = gerar_identidade_robusta(
    gpu="8",
    nucleos=7,
    memoria="8GB"
)

print(f"[STATUS] OPERADOR IDENTIFICADO: {id_unidade}")