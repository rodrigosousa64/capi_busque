from django.shortcuts import render
from django.http import JsonResponse
import asyncio
from project_home.services.get_datas_with_ip.service import get_datas_with_ip
import json
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def home(request):
    return render(request, 'home/index.html')




@csrf_exempt
def oque_eu_sei_sobre_voce(request):
    
    if request.method == 'GET':
        return render(request, 'home/oque_eu_sei_sobre_voce.html')


        
    if request.method == 'POST':
        geo_data = asyncio.run(get_datas_with_ip(request))   

        request_body = request.body
        dados_json = json.loads(request_body.decode('utf-8'))
        
        # Adiciona tudo o que veio do geo_data para dentro do nosso dicionário principal
        if isinstance(geo_data, dict):
            dados_json.update(geo_data)
            
        print("\n=== TODOS OS DADOS (NAVEGADOR + GEO) ===")
        print(json.dumps(dados_json, indent=4, ensure_ascii=False))
        print("========================================\n")
    return JsonResponse({"message": dados_json})
