# Roteiro de apresentação — Grupo 6

A ordem abaixo distribui blocos temáticos entre os integrantes; ensaiem as transições sem presumir limite de tempo. Abrir `apresentacao/index.html` e usar as setas.

## Alex Cabral — slides 1 a 4

Apresente os integrantes e o objetivo: entender como o NTFS organiza e protege dados e demonstrar um sistema educacional. Explique que surgiu com Windows NT e é nativo no Windows; o suporte em outros sistemas depende dos drivers. Mostre a hierarquia e depois a MFT: há ao menos um registro por arquivo, e atributos descrevem dados e metadados. Pequenos dados podem ser residentes; maiores são referenciados fora do registro. O diagrama é conceitual.

## João Nelson — slides 5 a 7

Explique clusters como unidades de alocação, o bitmap como mapa de ocupação e a possibilidade de fragmentação. Diferencie o log de transações de metadados, utilizado na recuperação de consistência, do diário USN, que registra alterações. Recuperar consistência não significa recuperar todo conteúdo de usuário. Apresente descritores de segurança e ACLs, compressão e EFS como recursos sujeitos a configuração e edição do sistema.

## Davi de Paula — slides 8 a 10

Compare NTFS, FAT32 e exFAT pela tabela; FAT32 limita cada arquivo a menos de 4 GiB, exFAT suporta arquivos maiores, e ambos carecem das ACLs e do journaling de metadados do NTFS no comparativo Microsoft. Desempenho depende do cenário. Explique o desenho do simulador e o fluxo: caminho → registro → blocos → persistência. Ressalte que o formato é JSON próprio, não NTFS, e não há journaling ou ACL.

## Pedro Luiz — slides 11 a 12 e demonstração

Explique os comandos e a diferença entre `overwrite` (mesmo ID, novo conteúdo) e `replace` (a origem assume o caminho do destino, preservando seu ID). Mostre os blocos e reinicie para demonstrar persistência. Conclua com as limitações e abra para perguntas.

## Demonstração reproduzível

Na raiz do projeto, crie um disco com um nome ainda inexistente:

```powershell
python -m src demonstracao.json --init --block-size 8 --blocks 16
```

No prompt interativo, execute em ordem:

```text
mkdir /documentos
mkdir /destino
touch /documentos/nota.txt
write /documentos/nota.txt "Ola mundo"
read /documentos/nota.txt
info /documentos/nota.txt
status
overwrite /documentos/nota.txt "Novo texto"
read /documentos/nota.txt
rename /documentos/nota.txt exemplo.txt
mv /documentos/exemplo.txt /destino
touch /documentos/novo.txt
write /documentos/novo.txt "Substituto"
info /documentos/novo.txt
replace /documentos/novo.txt /destino/exemplo.txt
info /destino/exemplo.txt
read /destino/exemplo.txt
touch /descartavel
write /descartavel "temporario"
status
rm /descartavel
status
tree
exit
```

Reabra com `python -m src demonstracao.json`, execute `tree`, `read /destino/exemplo.txt` e `info /destino/exemplo.txt`. O ID corresponde ao da origem de `replace`. Para repetir do zero, escolha outro nome de arquivo; não apague dados de uma demonstração que deseje preservar.

## Perguntas prováveis

**A MFT contém todos os dados?** Não necessariamente. Registros contêm atributos; dados pequenos podem ser residentes e outros ficam fora, descritos pelos atributos.

**Journaling é backup?** Não. O log ajuda a recuperar consistência de metadados; não substitui backup nem promete recuperar conteúdo perdido.

**O simulador é NTFS?** Não. É um formato próprio em JSON com conceitos simplificados de registros e blocos; não monta volumes NTFS.

**Qual a diferença entre sobrescrever e substituir?** Sobrescrever troca os bytes de um registro existente; substituir remove o destino e move a origem para o seu caminho, preservando o ID da origem.

**Por que falta espaço se poucos bytes são usados?** Cada bloco ocupado reserva uma unidade de capacidade simulada; o último pode ficar parcialmente cheio.

**O que ocorre se a escrita não couber?** Ela falha antes da gravação, preservando conteúdo e alocação anteriores.

**NTFS é sempre mais rápido?** Não. Arquivos, cache, dispositivo e carga influenciam; os recursos adicionais podem ter custos e benefícios.
