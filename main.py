from collector import ApiConection
from get_factory import GetDistribution
import os
import sys
import argparse
from dotenv import load_dotenv

#extrair as variaveis de ambiente + libs relevantes

load_dotenv()
    #token de auth e url da API
api_token = os.getenv('SPTRANS_API_TOKEN')
base_url = os.getenv('OLHO_VIVO_URL')

def get_parse (): 
    parser = argparse.ArgumentParser(description='Extrai o GET a ser executado')
    parser.add_argument('--get', type=str, required=True, help='Metodo que será utilizada no GET da API')
    parser.add_argument('--linha', type=str, required=False, help='Parametro de GETs da API')
    parser.add_argument('--empresa', type=str, required=False, help='Parametro de GETs da API')
    parser.add_argument('--sentido', type=str, required=False, help='Parametro de GETs da API')
    parser.add_argument('--parada', type=str, required=False, help='Parametro de GETs da API')
    parser.add_argument('--corredor', type=str, required=False, help='Parametro de GETs da API')
    return parser.parse_args()

def main():
    args = get_parse()
    get_instance = GetDistribution().new_instance(api_token, base_url, args)
    get_instance.run()

if __name__ == "__main__":
    main()