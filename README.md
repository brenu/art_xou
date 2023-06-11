# :art: Art Xou

![Partida do game em execução](./assets/doc_pictures/doc_logo.png)

Jogo sério, com temática de desenhos, para ser jogado em sala de aula ou em laboratórios. É inspirado no Gartic, e segue uma dinâmica semelhante, mas foi desenvolvido para ser jogado em rede local, de forma com que não seja necessária uma conexão com a internet para ser jogado. Dessa forma, espera-se que ele seja uma ferramenta de auxílio na educação infantil mais acessível às escolas que não possuem internet banda larga.

Classificação indicativa: 8+ anos.

## :national_park: Regras

Como já mencionado, se trata de um jogo com ideia semelhante ao Gartic, em que os jogadores entram em uma sala, e a cada turno um deles é responsável por desenhar, enquanto os outros jogadores tentam acertar o que está sendo desenhado. As partidas no Art Xou apresentam a seguinte dinâmica:

1. O Art Xou pode ser disputado individualmente, ou entre equipes. No caso das
partidas entre equipes, as próximas regras devem ser interpretadas de forma com
que um jogador represente uma equipe;
2. Existe um número indefinido de rodadas, cada uma durando 3 minutos, a menos
que todos os jogadores acertem o desenho antes desse tempo;
3. A cada rodada, um dos jogadores recebe uma palavra, e precisa fazer na lousa um
desenho que represente a mesma. No caso das partidas entre equipes, um jogador
diferente fica responsável pelo desenho a cada rodada, até que todos da equipe já
tenham desenhado;
4. Enquanto isso, os outros jogadores tentam acertar, no chat, qual é a palavra sendo
representada;
5. O primeiro jogador a acertar o desenho ganha 10 pontos, o segundo jogador ganha
9 pontos, e assim se segue até a pontuação mínima de 1 ponto por acerto;
6. O jogador que está desenhando recebe 11 pontos com o primeiro acerto de um outro
jogador, e mais 2 pontos para cada próximo acerto;
7. O jogador a desenhar pode dar até duas dicas aos outros jogadores, por meio de um
botão na interface, mas ao fazer isso, os acertos passam a valer um ponto a menos
para cada dica dada;
8. A partida tem seu fim quando uma rodada se encerra e ao menos um dos jogadores
possui 120 pontos ou mais;
9. Vence a partida quem tiver mais pontos.

## 🎮 Como Jogar

O Art Xou está publicado no [itch.io](https://brenu.itch.io/art-xou), e lá é possível baixar o executável do game compatível com seu sistema operacional. Até o presente momento, o jogo já foi testado nos sistemas operacionais Windows 10, Windows 11, e Pop!_OS 2022.4.

## :pencil: Como Executar o Código do Repositório

Para rodar o game a partir do seu código-fonte, é necessário ter o Python 3 instalado, assim como todos os requisitos presentes no arquivo `requirements.txt`. Além disso, é necessária a biblioteca netifaces, que está sendo utilizada na busca de partidas como um meio de obter o gateway padrão da rede em que o computador está, visto que todas as partidas ocorrem em LAN/WLAN.

Para instalar as dependências, presumindo que você já tem o Python 3.9 em seu computador, basta executar os seguintes comandos:

### Linux (distribuições baseadas em Debian)
```console
foo@bar:~/art_xou$ sudo apt-get update
foo@bar:~/art_xou$ sudo apt-get install -y python3-netifaces
foo@bar:~/art_xou$ pip3 install -r requirements.txt 
```

### Windows (necessita também do Visual C++, que pode ser baixado [aqui](https://visualstudio.microsoft.com/visual-cpp-build-tools/). Outra opção, para lidar com erros de build do netifaces, é utilizar seus binários pré-compilados que podem ser acessados através [desse projeto](https://www.lfd.uci.edu/~gohlke/pythonlibs/) do Christoph Gohlke, da Universidade da California. Na segunda opção, basta baixar o arquivo .whl e clicar duas vezes no mesmo, não sendo mais necessário instalar o netifaces pelo pip)

```powershell
PS C:\Users\you\art_xou> pip3 install netifaces
PS C:\Users\you\art_xou> pip3 install -r requirements.txt
```

Após isso, para rodar o game, execute (independente do sistema operacional):

```console
foo@bar:~/art_xou$ python3 main.py
```

## :monocle_face: Funcionamento Básico

Ao executar o game, um menu é aberto com duas opções principais:

* Criar uma partida - nesse modo, um servidor é criado na sua máquina, e você acessa automaticamente a partida como um jogador normal. A diferença aqui é que como você está sendo o host, se você sair da "sala", ninguém mais pode jogar nela.
* Entrar em uma partida já existente - nesse modo, o jogo escaneia a rede local, procurando por máquinas que estejam atuando como servidores, a fim de se conectar ao escolhido pelo usuário.

## :gear: Protocolo

Para a comunicação entre as partes envolvidas, desenvolvemos um protocolo da camada de aplicação. Nosso protocolo é baseado no TCP, pois a outra opção de transporte (UDP) não oferece garantia de transferência confiável de dados, e parte essencial do funcionamento das partidas é um chat, onde são enviadas as respostas. Nesse cenário queríamos evitar a necessidade de enviar o estado completo do jogo a cada atualização (abordagem comum em games que usam UDP), visto que o Python não é uma linguagem muito performática, em especial quando lidamos com interfaces, então renderizar a tela inteira a cada atualização atrapalharia muito a experiência, em especial do jogador a desenhar. Ao utilizar o TCP, tomamos a liberdade de enviar somente os novos pontos no quadro de desenho, e esses pontos são desenhados na tela individualmente, sem precisarmos renderizar o quadro inteiro N vezes por segundo.

As mensagens trocadas por meio do protocolo possuem uma estrutura sempre bastante semelhante. Seus primeiros 8 bytes são todos dígitos, que indicam o tamanho da mensagem que estará chegando a seguir, no formato JSON. Abaixo, temos um exemplo de mensagem que pode ser enviada entre cliente/servidor:

`00000097{"type": "ranking_update", "data": [{"name": "Erika", "score": 10}, {"name": "Breno", "score": 10}]}`

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
* `match_info` - representa um pedido por informações da partida. Durante a busca por partidas, o cliente envia mensagens com esse type para todos os IPs da rede, e os servidores disponíveis responderão com o nome da sala em uma mensagem com type idêntico;
* `join` - é um pedido para fazer parte da partida. Essa mensagem somente é enviada por clientes, e não pelo servidor. Se o servidor identificar que não existe nenhum jogador com o mesmo nome informado, ele devolve uma mensagem com o mesmo type e um dado de sucesso;
* `answer` - é uma possível resposta para o desenho que está sendo feito. Essa mensagem somente é enviada por clientes, e não pelo servidor. Se o servidor identificar que a palavra está certa, ele retorna um type ranking_update com o novo ranking atualizado. Caso contrário, ele retorna o mesmo type para todos os jogadores poderem ver que aquela palavra não é uma resposta correta;
* `board_update` - é uma atualização do quadro de desenho. Essa mensagem somente é enviada pelo cliente que foi selecionado para desenhar no turno. Essa mensagem é repassada para todos os outros jogadores, com o mesmo type, de modo a permitir que o desenho chegue à tela de cada um;
* `ranking_update` - representa uma atualização do ranking para ser exibido para os jogadores. Esse valor só é válido quando enviado pelo servidor, e nada irá acontecer se um jogador enviar uma mensagem com esse type;
* `new_round` - representa o fim da rodada atual, e o início de uma nova. Esse valor só é válido quando enviado pelo servidor, e nada irá acontecer se um jogador enviar uma mensagem com esse type;
* `match_end` - representa o fim da partida. Esse valor só é válido quando enviado inicialmente pelo jogador criador da partida, e nada irá ocorrer se outro jogador enviar uma mensagem de mesmo type;
* `match_reset` - representa um pedido para recomeçar a partida. Este valor também só é interpretado pelo servidor como válido se enviado pelo jogador que criou a partida.

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
* `new_round` - o início de uma nova rodada contém somente um objeto vazio, como exemplificado a seguir:

```javascript
{
  "type": "new_round",
  "data": {}
}
```
* `match_end` - o fim de uma partida contém somente um objeto vazio em todo o seu caminho, desde a mensagem do criador da partida até o repasse do servidor para os outros jogadores, como exemplificado a seguir:

```javascript
{
  "type": "match_end",
  "data": {}
}
```
* `match_reset` - o início de uma nova partida contém somente um objeto vazio em todo o seu caminho, desde a mensagem do criador da partida até o repasse do servidor para os outros jogadores, como exemplificado a seguir:

```javascript
{
  "type": "match_reset",
  "data": {}
}
```

## :pray: Créditos

As músicas e efeitos sonoros utilizados no Art Xou vieram dos seguintes autores/lugares:


* [Audio Hero](https://www.zapsplat.com/author/audio-hero/)
* [ZapSplat](https://www.zapsplat.com/author/zapsplat/)
* [freesound](https://freesound.org/)

Todos os ícones e figuras utilizados no game vieram diretamente ou indiretamente do [FontAwesome](https://fontawesome.com/)