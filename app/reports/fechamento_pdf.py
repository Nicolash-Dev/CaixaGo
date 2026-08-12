from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def formatar_moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    texto = (
        texto.replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {texto}"


def converter_data_local(
    data_sqlite: str | None,
) -> str:
    if not data_sqlite:
        return "--"

    try:
        data = datetime.fromisoformat(
            data_sqlite
        )

        if data.tzinfo is None:
            data = data.replace(
                tzinfo=timezone.utc
            )

        data = data.astimezone()

        return data.strftime(
            "%d/%m/%Y às %H:%M"
        )

    except (TypeError, ValueError):
        return "--"


def converter_horario_local(
    data_sqlite: str | None,
) -> str:
    if not data_sqlite:
        return "--:--"

    try:
        data = datetime.fromisoformat(
            data_sqlite
        )

        if data.tzinfo is None:
            data = data.replace(
                tzinfo=timezone.utc
            )

        return data.astimezone().strftime(
            "%H:%M"
        )

    except (TypeError, ValueError):
        return "--:--"


def gerar_pdf_fechamento(
    detalhes: dict,
) -> Path:
    caixa = detalhes["caixa"]
    resumo = detalhes["resumo"]
    movimentacoes = detalhes["movimentacoes"]

    project_root = Path(__file__).resolve().parents[2]

    reports_dir = project_root / "relatorios"
    reports_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    caixa_id = int(
        caixa["id"]
    )

    arquivo = (
        reports_dir
        / f"Fechamento_Caixa_{caixa_id}.pdf"
    )

    documento = SimpleDocTemplate(
        str(arquivo),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "CaixaGoTitulo",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#08111F"
        ),
        spaceAfter=6,
    )

    estilo_subtitulo = ParagraphStyle(
        "CaixaGoSubtitulo",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#475569"
        ),
        spaceAfter=16,
    )

    estilo_secao = ParagraphStyle(
        "CaixaGoSecao",
        parent=estilos["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor(
            "#1E3A5F"
        ),
        spaceBefore=10,
        spaceAfter=8,
    )

    estilo_rodape = ParagraphStyle(
        "CaixaGoRodape",
        parent=estilos["Normal"],
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#64748B"
        ),
    )

    elementos = []

    elementos.append(
        Paragraph(
            "CaixaGo",
            estilo_titulo,
        )
    )

    elementos.append(
        Paragraph(
            "Conte o dinheiro. O resto é com a gente.",
            estilo_subtitulo,
        )
    )

    elementos.append(
        Paragraph(
            f"Fechamento do Caixa #{caixa_id}",
            estilo_secao,
        )
    )

    dados_expediente = [
        [
            "Operador",
            str(caixa["operador"]),
        ],
        [
            "Abertura",
            converter_data_local(
                caixa["aberto_em"]
            ),
        ],
        [
            "Fechamento",
            converter_data_local(
                caixa["fechado_em"]
            ),
        ],
        [
            "Status",
            str(caixa["status"]),
        ],
    ]

    tabela_expediente = Table(
        dados_expediente,
        colWidths=[
            45 * mm,
            120 * mm,
        ],
    )

    tabela_expediente.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor(
                        "#E2E8F0"
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(
                        "#0F172A"
                    ),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (1, 0),
                    (1, -1),
                    "Helvetica",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#CBD5E1"
                    ),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    elementos.append(
        tabela_expediente
    )

    elementos.append(
        Spacer(
            1,
            8 * mm,
        )
    )

    elementos.append(
        Paragraph(
            "Resumo financeiro",
            estilo_secao,
        )
    )

    dados_financeiros = [
        [
            "Valor inicial",
            formatar_moeda(
                float(
                    caixa["valor_inicial"]
                )
            ),
        ],
        [
            "Faturamento total",
            formatar_moeda(
                float(
                    resumo["faturamento"]
                )
            ),
        ],
        [
            "Dinheiro",
            formatar_moeda(
                float(
                    resumo["vendas_dinheiro"]
                )
            ),
        ],
        [
            "PIX",
            formatar_moeda(
                float(
                    resumo["vendas_pix"]
                )
            ),
        ],
        [
            "Débito",
            formatar_moeda(
                float(
                    resumo["vendas_debito"]
                )
            ),
        ],
        [
            "Crédito",
            formatar_moeda(
                float(
                    resumo["vendas_credito"]
                )
            ),
        ],
        [
            "Sangrias",
            formatar_moeda(
                float(
                    resumo["sangrias"]
                )
            ),
        ],
        [
            "Suprimentos",
            formatar_moeda(
                float(
                    resumo["suprimentos"]
                )
            ),
        ],
        [
            "Saldo esperado",
            formatar_moeda(
                float(
                    resumo["saldo_esperado"]
                )
            ),
        ],
    ]

    tabela_financeira = Table(
        dados_financeiros,
        colWidths=[
            95 * mm,
            70 * mm,
        ],
    )

    tabela_financeira.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(
                        "#F8FAFC"
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(
                        "#0F172A"
                    ),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica",
                ),
                (
                    "FONTNAME",
                    (1, 0),
                    (1, -1),
                    "Helvetica-Bold",
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#CBD5E1"
                    ),
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    elementos.append(
        tabela_financeira
    )

    elementos.append(
        Spacer(
            1,
            8 * mm,
        )
    )

    elementos.append(
        Paragraph(
            "Movimentações",
            estilo_secao,
        )
    )

    dados_movimentacoes = [
        [
            "Horário",
            "Tipo",
            "Pagamento",
            "Descrição",
            "Valor",
        ]
    ]

    for movimentacao in movimentacoes:
        tipo = str(
            movimentacao["tipo"]
        ).upper()

        valor = float(
            movimentacao["valor"]
        )

        forma_pagamento = (
            movimentacao.get(
                "forma_pagamento"
            )
            or "-"
        )

        descricao = (
            movimentacao.get(
                "descricao"
            )
            or "-"
        )

        sinal = ""

        if tipo == "VENDA":
            sinal = "+"

        elif tipo == "SUPRIMENTO":
            sinal = "+"

        elif tipo == "SANGRIA":
            sinal = "-"

        dados_movimentacoes.append(
            [
                converter_horario_local(
                    movimentacao.get(
                        "criado_em"
                    )
                ),
                tipo.title(),
                str(
                    forma_pagamento
                ).title(),
                str(descricao),
                (
                    f"{sinal}"
                    f"{formatar_moeda(valor)}"
                ),
            ]
        )

    tabela_movimentacoes = Table(
        dados_movimentacoes,
        repeatRows=1,
        colWidths=[
            20 * mm,
            27 * mm,
            32 * mm,
            55 * mm,
            31 * mm,
        ],
    )

    tabela_movimentacoes.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#1E3A5F"
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica",
                ),
                (
                    "ALIGN",
                    (4, 1),
                    (4, -1),
                    "RIGHT",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#CBD5E1"
                    ),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    elementos.append(
        tabela_movimentacoes
    )

    if caixa.get("observacao"):
        elementos.append(
            Spacer(
                1,
                8 * mm,
            )
        )

        elementos.append(
            Paragraph(
                "Observação",
                estilo_secao,
            )
        )

        elementos.append(
            Paragraph(
                str(
                    caixa["observacao"]
                ),
                estilos["Normal"],
            )
        )

    elementos.append(
        Spacer(
            1,
            12 * mm,
        )
    )

    elementos.append(
        Paragraph(
            (
                "Relatório gerado automaticamente "
                "pelo CaixaGo."
            ),
            estilo_rodape,
        )
    )

    documento.build(
        elementos
    )

    return arquivo