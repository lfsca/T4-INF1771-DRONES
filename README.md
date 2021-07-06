# T4-INF1771-DRONES

Trabalho 4 de Inteligência Artificial (INF1771) - 21.1<br>
desenvolvido por Luiz Fellipe Augusto (1711256) , Bruno Coutinho (1910392) e Henrique Peres (1711899)

A Inteligência Artificial escolhida para este projeto foi a máquina de estados.

# Estados utilizados: #
**Pegar**: Pega um item na mesma casa que o bot<br>
**Escapar**: Escapa ao perceber um tiro<br>
**Atacar**: Ataca ao encontrar um oponente<br>
**Procurar Power-Up**: Procura um Power-Up(vida) quando a vida está baixa<br>
**Procurar Ouro**: Procura por ouro no mapa<br>
**Explorar**: Explora novos locais do mapa<br>
**Desviar de Buraco**: Desvia de buracos ao notar sua presença<br>
**Desprender**: Impede que o bot fique preso por muito tempo em um local<br>

# Movimentação #

**Explorar**: Dá prioridade a posições desconhecidas (marcadas com "?"), sempre buscando andar para frente ao invés de virar pois gasta menos ações. Se a frente já é conhecida, checa um dos lados desconhecidos e torna este o seu novo trajeto.

**Procurar Ouro**: Busca no mapa o ouro mais próximo descoberto e disponível (que já tenha *spawnado*) e executa movimentos que deixem o bot mais próximo dele até alcançá-lo.

**Procurar Power-Up**: Semelhante ao "Procurar Ouro" mas leva em consideração se a vida do bot está baixa.

**Escapar e Desprender**: Ao perceber um tiro (Escapar) ou se demorar muito para encontrar um item especifico (Desprender), executa ações de movimento aleatórias (customizáveis) com maior peso em "andar".

**Desviar de Buraco**: Ao encontrar um buraco, gira 180º e dá dois passos.

# Mapa #

O mapa é uma lista de listas com o tamanho do mapa (59x34) que possui inicialmente todos os valores iguais a "#".<br>
Assim que o bot explorar o mapa, ele será preenchido com símbolos equivalentes aos objetos do mapa.

Tesouro: "T"<br>
Power-Up (vida): "L"<br>
Parede: "W"<br>
Espaço livre: "."<br>
Possível Buraco ou Teleporte: "!"<br>
Local desconhecido (seguro): "?"<br>
<br>

Ao sentir uma "brisa"(buraco) ou "flash"(teleporte), todos os tiles na horizontal e vertical (exceto o último que o bot andou) serão marcados com "!" indicando que são possíveis buracos ou teleportes. Se que o bot não sentir "brisa" ou "flash" e estiver adjacente a um "!", trocará ele por um "?". 

# Estratégia #

o bot **Nattanzinho Carpinteiro** tem como estratégia:<br>
-Explora o mapa em busca de ouros.<br>
-Pega ouros que encontra.<br>
-Após encontrar 3 ouros ou executar 300 ações, entra no modo de busca por ouros.<br>
-Se desloca entre os ouros que conhece e os pega.<br>
-Caso esteja com pouca vida, se desloca até um Power-Up para pegá-lo.<br>
-Retorna a busca por ouros já conhecidos.<br>

**PS**: Foram criadas diversas variáveis de estado (presentes no início do código) que podem ser customizadas para alterar o comportamento do bot.

**Atenção: Este documento é referente ao bot "Nattanzinho Carpinteiro" presente na branch "main", o outro bot "Elias Carpinteiro" está na branch "Elias" e possui uma estratégia diferente (camper).**



# Estratégia do Segundo bot (camper) #

O bot **Elias Carpinteiro** tem como estratégia:<br>
-Buscar Ouro.<br>
-Ao encontrar ouro, fica parado em cima dele.<br>
-Pega o ouro apenas quando ele *spawna*<br>
-Ao perceber um tiro, desvia.<br>
-Retorna ao local do ouro.<br>
