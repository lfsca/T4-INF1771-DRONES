#!/usr/bin/env python

"""GameAI.py: INF1771 GameAI File - Where Decisions are made."""
#############################################################
#Copyright 2020 Augusto Baffa
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#############################################################
__author__      = "Augusto Baffa"
__copyright__   = "Copyright 2020, Rio de janeiro, Brazil"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "abaffa@inf.puc-rio.br"
#############################################################
#
# Grupo: Nattanzinho Carpinteiro: Movidos pela paixão
# Integrantes: Bruno Coutinho, Henrique Peres e Luiz Fellipe Augusto
#

import random
from Map.Position import Position
from queue import PriorityQueue

# <summary>
# Game AI Example
# </summary>
class GameAI():
    """
    Variáveis da classe:
        (obs: para acessar qualquer uma dessas dentro das funções, usar self.<nome_da_variavel>)

        player: player.x indica posicao x atual, player.y indica posicao y atual
        state: não importa
        dir: string com a direção em inglês para onde está apontando
        score: int com pontuação atual
        energy: int com hp

        current_action: string com a ação que será executada a seguir. Pode ser
            qualquer uma destas: ("pegar_ouro", "virar_direita", "virar_esquerda",
            "andar", "atacar", "pegar_anel", "pegar_powerup", "andar_re")
        current_state: string com o estado atual. Por enquanto, estados podem ser
            qualquer um destes: ("grab", "avoid_hole", "escape", "search_power_up",
            "attack", "random_explore", "search_gold")
        past_state: string com estado anterior. Mesmas opções do current_state

        golds_found: int. quantidade de ouros diferentes já encontrados. Por enquanto não
            é usada para nada, pensei que poderia ser útil no futuro
        powerups_found: int. quantidade de powerups diferentes já encontrados. Por enquanto
            não é usada para nada, pensei que poderia ser útil no futuro
        number_of_moves: int. quantidade de ações executadas até o momento. Por enquanto
            é usado para determinar até quando explorar aleatoriamente o mapa
        
        escape_ticks: int. O estado "escapar" requer várias ações seguidas. Não adianta alguém
            te atacar, você dar um passo para fugir e depois parar de fugir, é um estado que
            precisa de continuidade para realmente escapar de quem tá te atirando. Aí, essa
            variável conta quantas ações você realizou desde que começaram a te atirar para
            garantir essa continuidade
        avoid_hole_ticks: int. O jeito (que deve ser melhorado) que estou fazendo para o estado
            evitar buracos é girar duas vezes e andar um número x de casas para frente, por isso
            também é um estado que precisa de continuidade. Contador que nem a variável anterior
        
        max_escape_ticks: int estático. determina quantas ações o bot deve fazer no estado de
            escapar de inimigos
        max_avoid_hole_ticks: análogo ao anterior para estado de evitar buraco
        max_exploration_ticks: depois que o bot executa ao todo esse número de ações, ele para
            de explorar aleatoriamente e passa a procurar ouro (se não tiver nenhuma outra
            condição anterior mais importante). Essa lógica pode ser melhorada
        
        current_observations: dicionário que é atualizado a cada "jogada" com as observações atuais
            Chaves deste dicionário (todas booleanas):
                {
                blocked         => casa para onde tentou andar está bloqueada (tem parede ou fim do mapa)
                steps           => inimigo nas adjacências (frente, direita, trás ou esquerda)
                breeze          => buraco nas adjacências (frente, direita, trás ou esquerda)
                flash           => teletransporte nas adjacências (frente, direita, trás ou esquerda)
                blueLight       => tesouro na posição atual
                redLight        => powerup (+50 de vida) na posição atual
                damage          => recebeu dano (ai ai ai)
                hit             => acertou tiro
                enemy_in_front  => tem um inimigo a até 10 passos na direção para onde está apontando
                }
            
        map: lista de listas 59 x 34, cada posição é um caractere. Inicialmente tudo "#", que significa
            pos. desconhecida (pode trocar o simbolo). Pensei em fazer caracteres para cada tipo de 
            posição diferente, por ex. "O" sendo ouro, "." sendo posição descoberta sem item, etc.

    """
    
    player = Position()
    state = "ready"
    dir = "north"
    score = 0
    energy = 0

    current_action = ""
    current_state = "random_explore"
    past_state = ""

    golds_found = 0
    powerups_found = 0
    number_of_moves = 0

    escape_ticks = 0
    avoid_hole_ticks = 0

    max_escape_ticks = 8
    max_avoid_hole_ticks = 3
    max_exploration_ticks = 500

    current_observations = {
                            "blocked": False,
                            "steps": False,
                            "breeze": False,
                            "flash": False,
                            "blueLight": False,
                            "redLight": False,
                            "damage": False,
                            "hit": False,
                            "enemy_in_front": False
    }

    # inicializa mapa com todas posições "#", indicando desconhecido.
    map = [["#"] * 34 for _ in range(59)]

    # <summary>
    # Refresh player status
    # </summary>
    # <param name="x">player position x</param>
    # <param name="y">player position y</param>
    # <param name="dir">player direction</param>
    # <param name="state">player state</param>
    # <param name="score">player score</param>
    # <param name="energy">player energy</param>
    def SetStatus(self, x, y, dir, state, score, energy):
    
        self.player.x = x
        self.player.y = y
        self.dir = dir.lower()

        self.state = state
        self.score = score
        self.energy = energy


    # <summary>
    # Get list of observable adjacent positions
    # </summary>
    # <returns>List of observable adjacent positions</returns>
    def GetObservableAdjacentPositions(self):
        """ Função auxiliar"""

        ret = []

        ret.append(Position(self.player.x - 1, self.player.y))
        ret.append(Position(self.player.x + 1, self.player.y))
        ret.append(Position(self.player.x, self.player.y - 1))
        ret.append(Position(self.player.x, self.player.y + 1))

        return ret


    # <summary>
    # Get list of all adjacent positions (including diagonal)
    # </summary>
    # <returns>List of all adjacent positions (including diagonal)</returns>
    def GetAllAdjacentPositions(self):
        """ Função auxiliar"""

        ret = []

        ret.Add(Position(self.player.x - 1, self.player.y - 1))
        ret.Add(Position(self.player.x, self.player.y - 1))
        ret.Add(Position(self.player.x + 1, self.player.y - 1))

        ret.Add(Position(self.player.x - 1, self.player.y))
        ret.Add(Position(self.player.x + 1, self.player.y))

        ret.Add(Position(self.player.x - 1, self.player.y + 1))
        ret.Add(Position(self.player.x, self.player.y + 1))
        ret.Add(Position(self.player.x + 1, self.player.y + 1))

        return ret
    

    # <summary>
    # Get next forward position
    # </summary>
    # <returns>next forward position</returns>
    def NextPosition(self):
        """ Função auxiliar"""

        ret = None
        
        if self.dir == "north":
            ret = Position(self.player.x, self.player.y - 1)
                
        elif self.dir == "east":
                ret = Position(self.player.x + 1, self.player.y)
                
        elif self.dir == "south":
                ret = Position(self.player.x, self.player.y + 1)
                
        elif self.dir == "west":
                ret = Position(self.player.x - 1, self.player.y)

        return ret
    

    # <summary>
    # Player position
    # </summary>
    # <returns>player position</returns>
    def GetPlayerPosition(self):
        """ Função auxiliar"""
        return self.player


    # <summary>
    # Set player position
    # </summary>
    # <param name="x">x position</param>
    # <param name="y">y position</param>
    def SetPlayerPosition(self, x, y):
        """ Função auxiliar"""
        self.player.x = x
        self.player.y = y

    def SetPlayerDirection(self, direcao):
        """ Função auxiliar"""
        self.dir = direcao
    

    # <summary>
    # Observations received
    # </summary>
    # <param name="o">list of observations</param>
    def GetObservations(self, o):
        """ Função chamada pelo Bot.py para atualizar as observações a cada jogada.
            Só é chamada se algo foi observado.
        """
        
        possible_observations = [
                                 "blocked",
                                 "steps",
                                 "breeze",
                                 "flash",
                                 "blueLight",
                                 "redLight",
                                 "damage",
                                 "hit",
                                 "enemy_in_front",
        ]
        
        # Isso aqui é pq a string da observação que recebemos de q tem inimigo na sua frente
        #  varia de acordo com qual o inimigo, mas todas começam com "enemy"
        is_enemy_in_front = [i for i in o if i.startswith('enemy')]
        if is_enemy_in_front:
            o.append("enemy_in_front")

        # se observação foi recebida, seta como true, senão, seta como false
        for possible_obs in possible_observations:
            if possible_obs in o:
                self.current_observations[possible_obs] = True
            else:
                self.current_observations[possible_obs] = False


    # <summary>
    # No observations received
    # </summary>
    def GetObservationsClean(self):
        """ Função praticamente igual à anterior, mas indica que não há
            nada a ser observado no momento (pq a posição atual não tem nada
            e não tem buraco, teletransporte nem inimigo ao redor)
        """

        possible_observations = [
                                 "blocked",
                                 "steps",
                                 "breeze",
                                 "flash",
                                 "blueLight",
                                 "redLight",
                                 "damage",
                                 "hit",
                                 "enemy_in_front",
        ]

        # seta todas as observações como false
        for possible_obs in possible_observations:
            self.current_observations[possible_obs] = False


    # aqui começam as funções de cada estado. Os estados devem decidir qual a próxima
    # ação que deve ser tomada e alterar a variável self.current_action de acordo

    def StateGrab(self):
        self.current_action = "pegar_ouro"

    def StateEscape(self):
        # TODO: implementar isso na moral
        pos = self.GetPlayerPosition()

        if self.dir == "north":
            self.SetPlayerDirection("west")
            self.current_action = "virar_esquerda"
            self.SetPlayerPosition(pos.x - 1, pos.y)
            self.current_action = "andar"
                
        elif self.dir == "east":
            self.SetPlayerDirection("south")
            self.current_action = "virar_esquerda"
            self.SetPlayerPosition(pos.x, pos.y + 1)
            self.current_action = "andar"
                
        elif self.dir == "south":
            self.SetPlayerDirection("east")
            self.current_action = "virar_esquerda"
            self.SetPlayerPosition(pos.x + 1, pos.y)
            self.current_action = "andar"
                
        elif self.dir == "west":
            self.SetPlayerDirection("north")
            self.current_action = "virar_esquerda"
            self.SetPlayerPosition(pos.x, pos.y - 1)
            self.current_action = "andar"

    def StateAttack(self):
        self.current_action = "atacar"


    def StateSearchPowerUp(self):
        # TODO: implementar isso na moral, usando a* para chegar no powerup mais próximo
        n = random.randint(0,7)
        if n == 0:
            self.current_action = "virar_direita"
        elif n == 1:
            self.current_action = "virar_esquerda"
        else:
            self.current_action = "andar"


    def StateSearchGold(self):
        # TODO: implementar isso na moral, usando a* para chegar no ouro mais próximo
        n = random.randint(0,7)
        if n == 0:
            self.current_action = "virar_direita"
        elif n == 1:
            self.current_action = "virar_esquerda"
        else:
            self.current_action = "andar"


    def StateRandomExplore(self):
        # TODO: implementar isso melhor, pelo menos evitar de ir para posições já visitadas
        n = random.randint(0,7)
        if n == 0:
            self.current_action = "virar_direita"
        elif n == 1:
            self.current_action = "virar_esquerda"
        else:
            self.current_action = "andar"


    def StateAvoidHole(self):
        # TODO: dá pra implementar isso melhor. Do jeito que tá, quando chega num buraco
        # ou tp vira 180° e anda uma quantidade x de passos (até chegar no self.max_avoid_hole_ticks)
        if self.avoid_hole_ticks <= 1:
            self.current_action = "virar_esquerda"
        else:
            self.current_action = "andar"


    def UpdateMap(self):
        # TODO: essa função aqui eu pensei para ser chamada no início de cada jogada, para atualizar
        # o mapa (que ainda não implementamos) com o conteudo da posição atual e marcando as posições 
        # adjacentes como perigosas se tiver algum "cheirinho" (de buraco ou tp) e também marcando se for
        # parede. Pensei em marcar no mapa posições q são possíveis buracos com um ! ou algo assim para
        # indicar que são posições possivelmente perigosas e que devem ser evitadas. Pensei também que, se
        # você está em uma posição e não está sentindo cheirinho de buraco nem tp, você pode marcar as
        # posições adjacentes como "seguras", mesmo sem saber o que são exatamente (mas vc sabe q pelo
        # menos não são buraco nem tp)
        pass


    def print_map(self):
        for a in range(34):
            for b in self.map:
                print (b[a], end = "")
            print("")
        print("")

    def DecideState(self):
        """ Máquina de estados. É chamada a cada jogada para decidir qual deve ser o estado atual
        e chamar a função correspondente, que determinará qual ação será tomada. Dá pra melhorar
        bastante a lógica dela, é um esboço
        """

        # de qq jeito, se passar literalmente por cima de um ouro acho que sempre vale a pena pegar
        if self.current_observations["blueLight"]:
            self.current_state = "grab"
            self.StateGrab()

        # analogamente, se passar por cima de poção e n tiver com vida cheia, acho que vale tb
        elif self.current_observations["redLight"] and self.energy < 80:
            self.current_state = "grab"
            self.StateGrab()

        # se ainda não terminou de desviar de um buraco ou tp, continua no estado de evitá-lo
        elif self.past_state == "avoid_hole" and self.avoid_hole_ticks <= self.max_avoid_hole_ticks:
            self.current_state = "avoid_hole"
            self.avoid_hole_ticks += 1
            self.StateAvoidHole()

        # se sentiu cheirinho de buraco ou tp, entra no estado de desviar dele
        elif self.current_observations["breeze"] or self.current_observations["flash"]:
            self.current_state = "avoid_hole"
            self.avoid_hole_ticks = 0
            self.StateAvoidHole()
        
        # se sofreu dano, entra no estado de fugir (da pra melhorar essa logica aqui)
        elif self.current_observations["damage"]:
            self.current_state = "escape"
            self.escape_ticks = 0
            self.StateEscape()

        # se ainda não terminou de fugir, continua fugindo
        elif self.past_state == "escape" and self.escape_ticks < self.max_escape_ticks:
            self.current_state = "escape"
            self.escape_ticks += 1
            self.StateEscape()
        
        # se vida tá baixa, procura por powerup
        elif self.energy < 50:
            self.current_state = "search_power_up"
            self.StateSearchPowerUp()

        # se tem inimigo na frente & a vida ta razoavelmente alta & se última ação não
        # tiver sido um tiro que errou, atira. Isso do tiro que errou é pra tentar evitar
        # de ficar atirando na parede se tiver inimigo atrás dela, mas não sei se é uma boa,
        # tem que testar. Talvez seja melhor fazer tipo, se últimas 5 ações tiverem sido tiros
        # errados em vez de só checar a última
        elif (self.current_observations["enemy_in_front"] and self.energy > 50 and
              not (self.past_state == "attack" and not self.current_observations["hit"])):
            self.current_state = "attack"
            self.StateAttack()

        # se ainda tiver no começo do jogo e não tiver caído em nenhuma das condições
        # anteriores, sai explorando
        elif self.number_of_moves <= self.max_exploration_ticks:
            self.current_state = "random_explore"
            self.StateRandomExplore()

        # se não tiver mais no começo do jogo e não tiver caído em nenhuma das condições
        # anteriores, tenta achar ouro
        else:
            self.current_state = "search_gold"
            self.StateSearchGold()


    def GetDecision(self):
        """ Essa é a função que faz o "meio-campo" todo. Ela é chamada pelo
        Bot.py a cada 0.1s e deve informar qual deve ser a próxima ação a ser tomada.
        """
        
        # printa mapa na tela a cada 300 ações
        if self.number_of_moves % 300 == 0:
            self.print_map()

        self.number_of_moves += 1
        self.UpdateMap()
        self.past_state = self.current_state
        self.DecideState()

        return self.current_action


    # TODO: só copiei e colei o a* igualzinho ao do T1, acho q deve ter bastante coisa pra
    # adaptar. A ideia é usar ele pra encontrar o melhor caminho até uma posição p (em geral
    # é uma posição onde a gente já sabe que tem ouro ou então powerup)

    def a_estrela(self):
        """
        Implementação do A*, atualiza a parte gráfica ao longo da execução.
        """

        # para cada posição p, gScore[p] é o custo do caminho da posicao inicial até p
        gScore = dict()
        # para cada posição p, count_ginasios_passados[p] é o número de ginásios passados até chegar em p
        count_ginasios_passados = dict()
        # para cada posição p, pos_anterior[p] é a posição precedente no mais caminho mais curto da origem
        pos_anterior = dict()
        # para cada posição p, se blocos_passados[p] então p nao sera mais visitado
        blocos_passados = dict()
        # fila ordenada pelo menor f(n). Cada elemento é da forma (f(n), (x_pos, y_pos))
        posicoes_em_aberto = PriorityQueue()

        for pos, _ in self.campo:
            gScore[pos] = 10000000
            pos_anterior[pos] = None
            count_ginasios_passados[pos] = 0
        gScore[self.campo.inicio] = 0
        fScore_inicio = 0 + self.campo.distancia(self.campo.inicio, self.campo.fim, 'manhattan')
        posicoes_em_aberto.put((fScore_inicio, self.campo.inicio))
        
        while not posicoes_em_aberto.empty():
            self.desenha_campo()                                            # parte grafica
            self.wait(5)                                                    # parte grafica

            # pega a posicao com o menor fscore no momento
            pos_atual = posicoes_em_aberto.get()[1]
            blocos_passados[pos_atual] = True
            
            self.atualiza_bloco(pos_atual, 'verificado')                    # parte grafica
            self.custo_total_atual = gScore[pos_atual]                      # parte grafica
            self.ginasios_passados = count_ginasios_passados[pos_atual]     # parte grafica

            if self.campo.get_bloco(pos_atual) == 'F':
                while pos_atual is not None:
                    self.atualiza_bloco(pos_atual, 'caminho')               # parte grafica
                    pos_atual = pos_anterior[pos_atual]
                self.desenha_campo()                                        # parte grafica
                return
            
            elif self.campo.get_bloco(pos_atual) == 'B':
                count_ginasios_passados[pos_atual] += 1
            
            for vizinho in self.campo.get_vizinhos(pos_atual):
                if vizinho in blocos_passados:
                    continue
                self.atualiza_bloco(vizinho, 'verificar')                   # parte grafica
                
                tipo = self.campo.get_bloco(vizinho)
                if tipo == 'B':
                    custo = self.lista_custos[count_ginasios_passados[pos_atual] + 1 - 1]  # -1 pois a lista comeca em 0
                    if custo is None:
                        custo = 10000  # ginasio nulo, que nao da para passar
                else:
                    custo = self.campo.CUSTO[tipo]
                
                possivel_novo_gScore = gScore[pos_atual] + custo
                if possivel_novo_gScore < gScore[vizinho]:
                    pos_anterior[vizinho] = pos_atual
                    gScore[vizinho] = possivel_novo_gScore
                    fScore = gScore[vizinho] + self.campo.distancia(vizinho, self.campo.fim, 'manhattan')
                    posicoes_em_aberto.put((fScore, vizinho))
                    count_ginasios_passados[vizinho] = count_ginasios_passados[pos_atual]
        return