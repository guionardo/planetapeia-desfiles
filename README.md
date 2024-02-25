# planetapeia-desfiles

[![CodeQL](https://github.com/guionardo/planetapeia-desfiles/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/guionardo/planetapeia-desfiles/actions/workflows/github-code-scanning/codeql)

Sistema de gestão de desfiles do Planetapéia

## Fluxos dos Usuários Administrativos

Os usuários administrativos acessarão o sistema pela url ```/admin```

### Cadastro de Veículo

```mermaid
classDiagram
class Veiculo {
    + string nome
    + string imagem
    + int capacidade
    + int qtd_staffs [1 condutor + X staff]
    + int qtd_max_homens
    + int qtd_max_mulheres
    + int qtd_max_criancas
    + int peso_total_max
    + int peso_individual_max
}

note for Veiculo "A inscrição das pessoas num veículo deve\nser validada pelo número de indivíduos,\nsegundo gênero e peso"
```

### Cadastro de Grupos

```mermaid
classDiagram
class Grupo {
    + string nome
    + string imagem
    + TipoCobrancaTraje cobrar_taxa_traje
    + Pessoa[] anfitrioes
}

class TipoCobrancaTraje {
    <<enumeration>>
    SIM
    NÃO
}

Grupo .. TipoCobrancaTraje
Grupo "1" --> "1..*" Pessoa: contém
```

### Cadastro de Desfile

```mermaid
classDiagram
class Desfile {
    + string nome
    + string local
    + date data
    + Veiculo[] veiculos
    + bool confirmado
    + User aprovador
    + datetime data_aprovacao
}
class VeiculoDesfile {
    + int id_veiculo
}
class PessoaVeiculo {
    + int id_pessoa
}

class InscricaoDesfile {
    + Desfile desfile
    + Pessoa pessoa
    + TipoPessoa tipo_pessoa
    + Veiculo veiculo
    + Aprovacao aprovacao
    + User aprovador
    + datetime data_aprovacao
    + Convite convite
    + Grupo grupo
}
Desfile "1" --> "1..*" VeiculoDesfile: contém
VeiculoDesfile "1" --> "1..*" PessoaVeiculo: contém
VeiculoDesfile "1" --> "1..*" InscricaoDesfile: contém
```

### Cadastro de Traje

```mermaid
classDiagram
class Traje {
    + string nome
    + Veiculo veiculo
}

class TrajeInventario {
    + int num_inventario
    + Traje traje
    + TamanhoTraje tamanho
    + SituacaoTraje situacao
}

class SituacaoTraje {
    <<enumeration>>
    DISPONIVEL
    EMPRESTADO
    MANUTENCAO
    DESCARTADO
}

class TrajeHistorico {
    + TrajeInventario traje
    + date data
    + string observacao
    + TrajeMovimento movimento
    + User usuario
    + Pessoa pessoa
}

class TrajeMovimento {
    <<enumeration>>
    ENTRADA
    EMPRESTIMO
    DEVOLUCAO
    MANUTENCAO
    DESCARTE
}

class TrajeTaxa {
    + Desfile desfile
    + TrajeHistorico traje
    + decimal valor_taxa
    + decimal valor_pago
    + TrajeSituacaoTaxa situacao
    + date data_pagamento
    + User usuario
}

class TrajeSituacaoTaxa {
    <<enumeration>>
    PENDENTE
    PAGO
    ABONADO
}

class TamanhoTraje {
    <<enumeration>>
    P
    M
    G
    GG
}

Traje "1" --> "1..*" TrajeInventario: contém
TrajeInventario "1" --> "1..*" TrajeHistorico
TrajeInventario -- SituacaoTraje
TrajeInventario -- TamanhoTraje

TrajeHistorico -- TrajeMovimento
TrajeHistorico "1" -- "1..*" TrajeTaxa : empréstimo/devolução
TrajeTaxa -- TrajeSituacaoTaxa
```

## Fluxos dos Convidados

### Cadastro pessoal

* Ação para o convidado

O convidado receberá um link, onde poderá inscrever seus dados que serão utilizados em todos os desfiles.

Sua chave de acesso será o CPF, dado obrigatório para evitar duplicação.

O link será gerado por uma pessoa Padrinho/Madrinha de grupo, e incluirá o convidado automaticamente no grupo, após a validação dos dados.

### Inscrição no desfile

## Cadastro Pessoal

```mermaid
classDiagram
class Pessoa {
    * string cpf
    + string nome
    + string telefone
    + date data_nascimento
    + Genero genero
    + int peso [kg]
    + int altura [cm]
    + TamanhoTraje tamanho_traje
    + bool e_pcd
    + Grupo grupo
    + TipoPessoa tipo
    + TipoCobrancaTrajePessoa cobrar_taxa_traje
    + bool e_crianca() computado a partir da idade < 12 anos
    + bool cobrar_taxa_traje_efetiva() computado a partir do campo local e do grupo
    + Pessoa padrinho
}

class Genero {
    <<enumeration>>
    MASCULINO
    FEMININO
}

class TamanhoTraje {
    <<enumeration>>
    P
    M
    G
    GG
}

class TipoPessoa {
    <<enumeration>>
    CONDUTOR
    STAFF
    CONVIDADO
}

class TipoCobrancaTrajePessoa {
    <<enumeration>>
    SIM
    NÃO
    SEGUIR GRUPO
}

Pessoa -- Genero
Pessoa -- TamanhoTraje
Pessoa -- TipoPessoa
Pessoa -- TipoCobrancaTrajePessoa

```
