# API de Precificação

API REST desenvolvida em Python com FastAPI. É o **serviço secundário** de um MVP de componentização: calcula o preço de venda de um produto a partir do seu custo, aplicando *markup* por categoria e imposto, e permite gerenciar as regras de *markup* (CRUD).

Faz parte de um sistema com dois serviços que se comunicam. A API principal ([Catálogo](https://github.com/edisonhc1998-spec/catalogo-api)) consome esta API para obter o preço de venda dos produtos.

## Tecnologias

- Python 3.11
- FastAPI
- Uvicorn
- Docker

## Rotas

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Verifica se a API está no ar |
| POST | `/precificar` | Calcula o preço de venda a partir do custo |
| GET | `/regras` | Lista as regras de *markup* por categoria |
| GET | `/regras/{categoria}` | Consulta o *markup* de uma categoria |
| PUT | `/regras/{categoria}` | Cria ou atualiza o *markup* de uma categoria |
| DELETE | `/regras/{categoria}` | Remove a regra de uma categoria |

### Exemplo de uso

Requisição para `POST /precificar`:

```json
{
  "custo": 10.0,
  "categoria": "bebidas",
  "imposto_percent": 0
}
```

Resposta:

```json
{
  "custo": 10.0,
  "categoria": "bebidas",
  "markup_percent": 45.0,
  "imposto_percent": 0.0,
  "preco_venda": 14.5,
  "margem_valor": 4.5,
  "margem_percent": 31.03
}
```

## Como executar

### Opção 1 — Local (Python)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### Opção 2 — Docker

```bash
docker build -t precificacao-api .
docker run -p 8001:8001 precificacao-api
```

## Documentação interativa (Swagger)

Com a API em execução, acesse a documentação gerada automaticamente pelo FastAPI:

```
http://localhost:8001/docs
```

## Autor

Edison Huarancca Chunga