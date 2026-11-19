# Mini sistema de arquivos inspirado em NTFS

Projeto de Sistemas Operacionais T303 — Unifor — Grupo 6. Alex Cabral, João Nelson, Davi de Paula e Pedro Luiz. Professor MSc. Felipe Jucá dos Santos. Apresentação: 24/11/2026.

## Execução

Requer Python 3.9 ou posterior, apenas biblioteca padrão. No PowerShell, a partir da raiz:

```powershell
python -m src disco.json --init --block-size 64 --blocks 128
```

A inicialização recusa um arquivo existente. Para reabrir o mesmo disco:

```powershell
python -m src disco.json
```

Digite `help`. Caminhos iniciados por `/` são absolutos; os demais partem do diretório atual (`cd`, `pwd`). Use aspas para texto ou nomes com espaços. `write` acrescenta bytes UTF-8; `overwrite` troca todo o conteúdo mantendo o identificador; `replace origem destino` remove o registro e os blocos do destino e coloca a origem no caminho do destino, mantendo o ID e blocos da origem. Ambos devem existir e ser arquivos. `mv` aceita um diretório existente ou um novo caminho; não substitui um destino existente. `rmdir` exige diretório vazio.

```powershell
python -m unittest discover -s tests -v
```

Abra `apresentacao/index.html` no navegador; setas, espaço, Page Up/Down e Home/End navegam. O roteiro detalhado e a demonstração estão em `ROTEIRO_APRESENTACAO.md`.

## Modelo e limites

O arquivo JSON contém cabeçalho, registros identificados por ID, relação pai/nome e vetor de blocos codificados em base64. Blocos livres são `null`; alocação first-fit usa os primeiros disponíveis. O limite de capacidade informado conta somente blocos de dados; JSON, metadados e codificação ocupam espaço adicional no disco real. Arquivos vazios não ocupam blocos. Não há limite simulado para metadados. Datas são UTC. Nomes distinguem maiúsculas e minúsculas. A CLI escreve texto UTF-8; a API aceita bytes.

Cada mutação prepara uma cópia em memória e grava um arquivo temporário no mesmo diretório antes de substituir o disco virtual. Falta de espaço é detectada antes da gravação. Isso reduz risco de estado parcial, mas não é journaling nem garantia de recuperação após queda de energia; não há bloqueio entre processos, validação completa de corrupção ou uso concorrente seguro. O disco virtual deve ser usado por uma instância por vez. Não há ACL, criptografia, compressão, índices NTFS, atributos residentes, extents ou compatibilidade com volumes NTFS. Apagar libera blocos na simulação, sem garantia de eliminação segura dos dados físicos.

O trabalho completo atende aos dois entregáveis do enunciado: apresentação técnica e implementação funcional. A pesquisa e suas fontes constam nos slides e em `docs/FONTES.md`.
