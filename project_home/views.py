from operator import methodcaller
from asyncio import timeouts
from asyncio import timeouts
from django.shortcuts import render
from django.http import JsonResponse
import httpx
import asyncio



# Create your views here.

def home(request):
    return render(request, 'home/index.html')


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def oque_eu_sei_sobre_voce(request):
    
    if request.method == 'GET':
        return render(request, 'home/oque_eu_sei_sobre_voce.html')

    if request.method == 'POST':

        async def get_geo_location(request, client_ip):
            url = f"http://ip-api.com/json/{client_ip}"
        
            # We use 'async with' to ensure the session is closed after the request
            # This is similar to managing resources in an engineering project
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(url, timeout=5.0)
                    response.raise_for_status() # Check for HTTP errors (4xx, 5xx)
                    geo_data = response.json()
                except httpx.HTTPError as e:
                    # Operational failure handling
                    return {"error": f"API connection failed: {e}"}
                except Exception as e:
                    return {"error": "Internal system error"}

                return geo_data
                
        client_ip = request.META.get('REMOTE_ADDR')
        # A API do ip-api falha se enviarmos "127.0.0.1" (localhost)
        if client_ip == '127.0.0.1':
            client_ip = '' # Vazio faz a API pegar seu IP público automaticamente
            
        geo_data = asyncio.run(get_geo_location(request, client_ip))
        
       
            
        request_body = request.body
        print("=== DADOS RECEBIDOS ===")
        print(request_body.decode('utf-8'))
        import json
        dados_json = json.loads(request_body.decode('utf-8'))
        
        # Adiciona tudo o que veio do geo_data para dentro do nosso dicionário principal
        if isinstance(geo_data, dict):
            dados_json.update(geo_data)
            
        print("\n=== TODOS OS DADOS (NAVEGADOR + GEO) ===")
        print(json.dumps(dados_json, indent=4, ensure_ascii=False))
        print("========================================\n")
        return JsonResponse(
            {"message": dados_json}
        )
