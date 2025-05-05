# Xadrez-IAC

Implementação do jogo de Xadrez usando a linguagem Python,através de bibliotecas específicas. O jogo é executado seguindo as regras do Xadrez convencional e fazendo as leituras das jogadas que forem possíveis para cada uma das peças a serem mexidas .
Jogadas que não forem permitidas geram a perda instantânea do jogo ,estando em desacordo com as regras . Para realizar cada jogada tem-se um tempo de 2 minutos , excedendo esse tempo e não realizando a jogada , também resulta na perda do jogo. 

## Pré-requisitos

- Python 3.x
- Bibliotecas: `pygame`, `python-chess`

## Como Jogar

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd Xadrez-IAC
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv .venv
    # Linux/macOS
    source .venv/bin/activate
    # Windows
    # .\.venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install pygame python-chess
    ```

4.  **Execute o jogo:**
    ```bash
    python xadrez_pygame.py
    ```
A interface gráfica do jogo será iniciada.
