import httpx
import json

BASE_URL = "http://127.0.0.1:8000"


async def post_request(url: str, data: dict) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            if response.status_code != 200:
                raise Exception(f"{response.text}")
            return {"data": response.json(), "status": response.status_code}
    except httpx.ConnectError as e:
        return {"data": None, "msg": "No se pudo conectar al servidor.", "status": 500}
    except httpx.HTTPStatusError as e:
        return {"data": None, "msg": e.response.text, "status": e.response.status_code}
    except Exception as e:
        return {"data": None, "msg": f"Un error ha ocurrido: {e}", "status": 500}


async def get_request(url: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise Exception(f"{response.text}")
            return {"data": response.json(), "status": response.status_code}
    except httpx.ConnectError as e:
        return {"data": None, "msg": "No se pudo conectar al servidor.", "status": 500}
    except httpx.HTTPStatusError as e:
        return {"data": None, "msg": e.response.text, "status": e.response.status_code}
    except Exception as e:
        return {"data": None, "msg": f"Un error ha ocurrido: {json.loads(str(e))['detail']}", "status": 500}


async def create_rate(rate: float) -> dict:
    url = f"{BASE_URL}/rate"
    return await post_request(url, {'rate': rate})


async def get_today_rate() -> dict:
    url = f"{BASE_URL}/rate/today"
    return await get_request(url)


async def create_sale(sale_crate: dict) -> dict:
    url = f"{BASE_URL}/sales"
    return await post_request(url, sale_crate)


async def get_report() -> dict:
    url = f"{BASE_URL}/report/today"
    return await get_request(url)


async def get_history() -> dict:
    url = f"{BASE_URL}/history"
    return await get_request(url)
