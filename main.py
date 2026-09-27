from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title="API de Precificação",
    description="Calcula o preço de venda a partir do custo, aplicando markup "
                "por categoria e imposto. Também gerencia as regras de markup (CRUD).",
    version="1.0.0",
)

# "Banco" de regras de markup em memória (volta a estes valores a cada restart).
# markup em % sobre o custo. "padrao" é o fallback quando a categoria não tem regra própria.
regras_markup: dict[str, float] = {
    "padrao": 25.0,
    "alimentos": 30.0,
    "bebidas": 45.0,
    "limpeza": 35.0,
}


# ---------- Modelos (o "contrato" de entrada e saída) ----------

class PrecificacaoRequest(BaseModel):
    custo: float = Field(..., gt=0, description="Custo do produto (deve ser > 0)")
    categoria: Optional[str] = Field(None, description="Categoria; define qual markup usar")
    markup_percent: Optional[float] = Field(None, ge=0, description="Markup manual em %; se enviado, ignora a regra da categoria")
    imposto_percent: float = Field(0, ge=0, description="Imposto em % aplicado sobre o preço")


class PrecificacaoResponse(BaseModel):
    custo: float
    categoria: str
    markup_percent: float
    imposto_percent: float
    preco_venda: float
    margem_valor: float
    margem_percent: float


class RegraRequest(BaseModel):
    markup_percent: float = Field(..., ge=0, description="Markup em % para a categoria")


# ---------- Rotas ----------

@app.get("/health", tags=["status"], summary="Verifica se a API está no ar")
def health():
    return {"status": "ok"}


@app.post("/precificar", response_model=PrecificacaoResponse, tags=["precificação"],
          summary="Calcula o preço de venda")
def precificar(req: PrecificacaoRequest):
    """
    Calcula o preço de venda:
    - Se **markup_percent** for enviado, usa ele direto.
    - Senão, usa a regra de markup da **categoria** (ou a regra "padrao").
    - Aplica o **imposto_percent** sobre o preço já com markup.
    """
    categoria = (req.categoria or "padrao").strip().lower()

    if req.markup_percent is not None:
        markup = req.markup_percent
    else:
        markup = regras_markup.get(categoria, regras_markup["padrao"])

    preco_com_markup = req.custo * (1 + markup / 100)
    preco_venda = preco_com_markup * (1 + req.imposto_percent / 100)
    margem_valor = preco_venda - req.custo
    margem_percent = (margem_valor / preco_venda) * 100 if preco_venda > 0 else 0

    return PrecificacaoResponse(
        custo=round(req.custo, 2),
        categoria=categoria,
        markup_percent=round(markup, 2),
        imposto_percent=round(req.imposto_percent, 2),
        preco_venda=round(preco_venda, 2),
        margem_valor=round(margem_valor, 2),
        margem_percent=round(margem_percent, 2),
    )


@app.get("/regras", tags=["regras"], summary="Lista todas as regras de markup")
def listar_regras():
    return regras_markup


@app.get("/regras/{categoria}", tags=["regras"], summary="Consulta o markup de uma categoria")
def obter_regra(categoria: str):
    chave = categoria.strip().lower()
    if chave not in regras_markup:
        raise HTTPException(status_code=404, detail=f"Categoria '{chave}' não tem regra cadastrada")
    return {"categoria": chave, "markup_percent": regras_markup[chave]}


@app.put("/regras/{categoria}", tags=["regras"], summary="Cria ou atualiza o markup de uma categoria")
def salvar_regra(categoria: str, regra: RegraRequest):
    chave = categoria.strip().lower()
    regras_markup[chave] = regra.markup_percent
    return {"categoria": chave, "markup_percent": regra.markup_percent}


@app.delete("/regras/{categoria}", tags=["regras"], summary="Remove a regra de uma categoria")
def remover_regra(categoria: str):
    chave = categoria.strip().lower()
    if chave == "padrao":
        raise HTTPException(status_code=400, detail="A regra 'padrao' não pode ser removida")
    if chave not in regras_markup:
        raise HTTPException(status_code=404, detail=f"Categoria '{chave}' não tem regra cadastrada")
    del regras_markup[chave]
    return {"removida": chave}