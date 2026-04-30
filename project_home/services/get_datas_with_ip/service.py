import httpx

async def get_datas_with_ip(request):
    client_ip = request.META.get('REMOTE_ADDR')  
    if client_ip == '127.0.0.1':
        client_ip = '' 
    url = f"http://ip-api.com/json/{client_ip}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5.0)
            response.raise_for_status() 
            geo_data = response.json()
        except httpx.HTTPError as e:
            return {"error": f"API connection failed: {e}"}
        except Exception as e:
            return {"error": "Internal system error"}

    return geo_data