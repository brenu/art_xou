# :art: Art Xou

Jogo criado como um dos créditos a serem avaliados para a disciplina Rede de Computadores I.

## :national_park: Ideia Geral

Se trata de um jogo com ideia semelhante ao gartic, em que os jogadores entram em uma sala, e a cada turno um deles é responsável por desenhar, enquanto os outros jogadores tentam acertar o que está sendo desenhado. Na implementação atual, as partidas ocorrem indefinidamente, pois elas não possuem uma regra estabelecida para seu fim.

## :pencil: Requisitos

Para jogar o game, é necessário ter o Python 3 instalado, assim como todos os requisitos presentes no arquivo `requirements.txt`. Além disso, é necessária a biblioteca netifaces, que está sendo utilizada na busca de partidas como um meio de obter o gateway padrão da rede em que o computador está, visto que todas as partidas ocorrem em LAN/WLAN.

Para instalar as dependências, presumindo que você já tem o Python 3 em seu computador, basta executar os seguintes comandos:

```console
foo@bar:~/art_xou$ sudo apt-get update
foo@bar:~/art_xou$ sudo apt-get install -y python3-netifaces
foo@bar:~/art_xou$ pip3 install -r requirements.txt 
```

Após isso, para rodar o game, execute:

```console
foo@bar:~/art_xou$ python3 main.py
```

## :monocle_face: Funcionamento Básico

Ao executar o game, um menu é aberto com duas opções principais:

* Criar uma partida - nesse modo, um servidor é criado na sua máquina, e você acessa automaticamente a partida como um jogador normal. A diferença aqui é que como você está sendo o host, se você sair da "sala", ninguém mais pode jogar nela.
* Entrar em uma partida já existente - nesse modo, o jogo escaneia a rede local, procurando por máquinas que estejam atuando como servidores, a fim de se conectar ao escolhido pelo usuário.

## :gear: Protocolo

Para a comunicação entre as partes envolvidas, desenvolvemos um protocolo da camada de aplicação. Nosso protocolo é baseado no TCP, porque queríamos evitar a necessidade de enviar o estado completo do jogo a cada atualização (abordagem comum em games que usam UDP), visto que o Python não é uma linguagem muito performática, em especial quando lidamos com interfaces, então renderizar a tela inteira a cada atualização atrapalharia muito a experiência, em especial do jogador a desenhar. Ao utilizar o TCP, tomamos a liberdade de enviar somente os novos pontos no quadro de desenho, e esses pontos são desenhados na tela individualmente, sem precisarmos renderizar o quadro inteiro N vezes por segundo.

As mensagens trocadas por meio do protocolo possuem uma estrutura sempre bastante semelhante. Seus primeiros 128 bytes são todos dígitos, que indicam o tamanho da mensagem que estará chegando a seguir, no formato JSON. Abaixo, temos um exemplo de mensagem que pode ser enviada entre cliente/servidor:

`00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000097{"type": "ranking_update", "data": [{"name": "Erika", "score": 10}, {"name": "Eu", "score": 10}]}`

Analisando o objeto JSON que contém as mensagens trocadas durante a partida, temos somente dois campos principais:
* type - indica qual a operação a ser realizada com os dados do campo `data`
* data - carrega consigo os dados a serem processados

A seguir, temos um exemplo do objeto melhor formatado, para mais simples entendimento:

```javascript
{
  "type": "ranking_update",
  "data": [
    {"name": "Erika", "score": 10},
    {"name": "Eu", "score": 10}
  ]
}
```

O campo `type` possui como válidos os valores abaixo:
* `match_info` - representa um pedido por informações da partida. Durante a busca por partidas, o cliente envia mensagens com esse type para todos os IPs da rede, e os servidores disponíveis responderão com o nome da sala em uma mensagem com type idêntico.
* `join` - é um pedido para fazer parte da partida. Essa mensagem somente é enviada por clientes, e não pelo servidor. Se o servidor identificar que não existe nenhum jogador com o mesmo nome informado, ele devolve uma mensagem com o mesmo type e um dado de sucesso.
* `answer` - é uma possível resposta para o desenho que está sendo feito. Essa mensagem somente é enviada por clientes, e não pelo servidor. Se o servidor identificar que a palavra está certa, ele retorna um type ranking_update com o novo ranking atualizado. Caso contrário, ele retorna o mesmo type para todos os jogadores poderem ver que aquela palavra não é uma resposta correta.
* `board_update` - é uma atualização do quadro de desenho. Essa mensagem somente é enviada pelo cliente que foi selecionado para desenhar no turno. Essa mensagem é repassada para todos os outros jogadores, com o mesmo type, de modo a permitir que o desenho chegue à tela de cada um.
* `ranking_update` - representa uma atualização do ranking para ser exibido para os jogadores. Esse valor só é válido quando enviado pelo servidor, e nada irá acontecer se um jogador enviar uma mensagem com esse type.

O campo `data` tem seu conteúdo bastante variado, a depender do valor de `type`. Seguem, abaixo, alguns exemplos:

* `match_info` - no caso desse type, a requisição costuma ter seu campo data como um objeto vazio. No entanto, a resposta do servidor contém o nome da sala, no seguinte formato:

```javascript
{
  "type": "match_info",
  "data": {"name": "Nome aqui"}
}
```
* `join` - para entrar em partidas, é necessário informar o seu nome de jogador. Em caso de sucesso, o servidor te retornará o estado atual do quadro. Seguem exemplos de requisição e resposta, respectivamente:


```javascript
{
  "type": "join",
  "data": {"name": "NomeJogador"}
}
```

```javascript
{
  "type": "join",
  "data": {
    "success": true,
    "board": [{
      "color":"#000",
      "radius": 5,
      "x": 100,
      "y": 200 
    }]
  }
}
```
* `answer` - este type, quando possui sua mensagem repassada para os outros usuários (respostas incorretas), possui exatamente o mesmo formato durante todo seu caminho. Segue, abaixo, um exemplo:

```javascript
{
  "type": "answer",
  "data": "abacate"
}
```

* `board_update` - a atualização do quadro tem sempre somente um ponto a ser desenhado no quadro dos jogadores, assim como no objeto a seguir:

```javascript
{
  "type": "board_update",
  "data": {
    "color": "#fff",
    "radius": 5,
    "x": 10,
    "y": 20
  }
}
```

* `ranking_update` - a atualização do ranking contém uma lista dos jogadores, contendo também a pontuação de cada um no momento da atualização. A seguir, um exemplo:

```javascript
{
  "type": "ranking_update",
  "data": [
    {"name": "Erika", "score": 10},
    {"name": "Eu", "score": 10}
  ]
}
```
