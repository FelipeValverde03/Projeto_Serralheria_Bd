
import requests
#Tranformando CEP em Endereco usando API viacep
def gerador_endereco(cep):
    try:
        resposta = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        dados = resposta.json()
        if "erro" in dados:
            return None
        # Monta endereço completo
        endereco = f"{dados['logradouro']}, {dados['bairro']}, {dados['localidade']} - {dados['uf']}"
        return endereco
    except:
        return None
