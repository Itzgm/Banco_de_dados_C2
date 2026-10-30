import re


def texto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} é obrigatório.")
    return valor.strip()


def email(valor):
    valor = texto(valor, "Email").casefold()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
        raise ValueError("Informe um email válido.")
    return valor


def telefone(valor):
    valor = texto(valor, "Telefone")
    if not re.fullmatch(r"[0-9+(). \-]+", valor) or not any(caractere.isdigit() for caractere in valor):
        raise ValueError("Telefone deve conter dígitos e apenas símbolos usuais de telefone.")
    return valor


def identificador(valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("O identificador deve ser um inteiro positivo.")
    return valor


def senha(valor):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError("Senha é obrigatória.")
    return valor
