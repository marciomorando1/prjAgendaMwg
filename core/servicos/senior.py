import json
import logging
import requests

logger = logging.getLogger(__name__)

SENIOR_AUTH_URL = "https://platform.senior.com.br/t/senior.com.br/bridge/1.0/rest/platform/authentication/actions/login"
SENIOR_PROCESS_URL = "https://platform.senior.com.br/t/senior.com.br/bridge/1.0/rest/platform/workflow/actions/startProcess"

SENIOR_USER = "marcio.morando@magnus-demo.com.br"
SENIOR_PASS = "Mmo@2018"

def get_access_token():
    """Autentica e retorna o access_token (string)."""
    payload = {"username": SENIOR_USER, "password": SENIOR_PASS}
    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(SENIOR_AUTH_URL, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.exception("Erro ao autenticar na Senior")
        raise Exception(f"Erro de conexão/HTTP na autenticação Senior: {e}")

    # extrair JSON
    try:
        data = resp.json()
    except ValueError:
        raise Exception(f"Resposta inválida da Senior (não-JSON): {resp.text}")

    json_token = data.get("jsonToken")
    if not json_token:
        raise Exception(f"Campo 'jsonToken' não encontrado na resposta de autenticação: {data}")

    # jsonToken vem como string JSON 
    try:
        token_data = json.loads(json_token)
    except (TypeError, ValueError) as e:
        raise Exception(f"Erro ao parsear jsonToken: {e}. Conteúdo: {json_token}")

    access_token = token_data.get("access_token") or token_data.get("accessToken") or token_data.get("token")
    if not access_token:
        raise Exception(f"access_token não encontrado dentro de jsonToken: {token_data}")

    return access_token


def start_workflow(activity):
    """
    Dispara o workflow.
    Retorna o JSON da resposta em caso de sucesso ou lança Exception com a mensagem da API.
    """
    token = get_access_token()

    # tenta converter orcamento para número (se for string numérica)
    orcamento = activity.numero_orcamento
    try:
        orcamento = int(orcamento)
    except Exception:
        pass

    business_data = {
        "root": {
            "orcamento": orcamento,
            "servico": str(activity.servico or ""),
            "descricao_da_atividade": str(activity.descricao or "")
        }
    }

    payload = {
        "generateRecord": True,
        "processId": 11,
        
        "businessData": json.dumps(business_data),
        "flowExecutionData": {"actionToExecute": "Prosseguir","nextSubject": "marcio.morando"},
        "title": f"{activity.nome_cliente} {activity.numero_orcamento}",
        "externalServiceOverrideBusinessData": True,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    logger.debug("Chamando Senior startProcess - headers=%s payload=%s", headers, payload)

    try:
        resp = requests.post(SENIOR_PROCESS_URL, json=payload, headers=headers, timeout=30)
    except requests.RequestException as e:
        logger.exception("Erro de conexão ao chamar startProcess")
        raise Exception(f"Erro de conexão ao chamar Senior startProcess: {e}")

    logger.debug("Resposta startProcess status=%s texto=%s", resp.status_code, resp.text)

    if resp.status_code not in (200, 201, 202):
        # devolve a mensagem de erro completa para debug
        raise Exception(f"Erro ao iniciar processo (status {resp.status_code}): {resp.text}")

    # tenta retornar JSON; se não for JSON, retorna texto dentro de um dict
    try:
        return resp.json()
    except ValueError:
        return {"raw_response": resp.text}
