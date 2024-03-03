"""Permissões de usuário para definição de papéis"""

CONVIDAR = "cus_pode_convidar"
ALMOXARIFE = "cus_almoxarife"
ADM_PESSOAS = "cus_adm_pessoas"

roles = {
    CONVIDAR: ("Pode convidar", "Usuário tem permissão de criar e enviar convites"),
    ALMOXARIFE: (
        "Gerenciamento de trajes",
        "Efetua empréstimo, recebimento, avaliação e manutenção de trajes, e recebimento das taxas de uso",
    ),
    ADM_PESSOAS: (
        "Administrador de pessoas",
        "Gerencia as pessoas cadastradas, quanto aos papéis e permissões",
    ),
}

pessoa_roles = [(key, desc[1]) for key, desc in roles.items()]
