# Bot Discord - Videl

Este é um bot multifuncional para **Discord**, desenvolvido em **Python**, com funcionalidades como moderação, reprodução de música e mensagens secretas.

---

## Funcionalidades

### Administração
- `v!ban <@usuário>` - Bane um usuário do servidor (Apenas Administradores).
- `v!kick <@usuário>` - Expulsa um usuário do servidor (Apenas Administradores).
- `v!clear <número>` - Apaga um número específico de mensagens (Necessita permissão de Gerenciar Mensagens).

### Música
- `v!join` - O bot entra no canal de voz do usuário.
- `v!leave` - O bot sai do canal de voz.
- `v!play <url/nome>` - Reproduz música do YouTube ou Spotify.
- `v!skip` - Pula para a próxima música da fila.
- `v!pause` - Pausa a música em reprodução.
- `v!resume` - Retoma a música pausada.
- `v!stop` - Para a música e limpa a fila.

### Mensagens Secretas
- Palavras-chave específicas ativam mensagens ocultas.

### Informações do Servidor
- `v!serverinfo` - Exibe detalhes do servidor.
- `v!userinfo <@usuário>` - Exibe informações de um usuário.

### Outros Comandos
- `v!ping` - Mede a latência do bot.
- `v!commands` - Lista todos os comandos disponíveis.

---

## Requisitos
- **Python 3.9+**
- Bibliotecas necessárias:
  - `discord.py`
  - `yt-dlp`
  - `spotipy`
  - `python-dotenv`
  - `tkinter`
- **Conta no Discord** para registrar o bot.
- **Credenciais do Spotify API** (para busca de músicas no Spotify).

---

## Instalação

1. Clone este repositório:
```
git clone https://github.com/seu-repositorio/bot-discord.git
cd bot-discord
```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```
pip install -r requirements.txt
```

4. Configure o arquivo `.env` com suas credenciais:
```
DISCORD_TOKEN=SEU_TOKEN_DISCORD
SPOTIFY_CLIENT_ID=SEU_CLIENT_ID_SPOTIFY
SPOTIFY_CLIENT_SECRET=SEU_CLIENT_SECRET_SPOTIFY
```

5. Execute o bot:
```
python main.py
```
Ou utilize o **Launcher** para gerenciar o bot graficamente:
```
python bot_launcher.py
```

---

## Estrutura do Projeto
```
📂 bot-discord
│── 📄 .env                      # Configurações de credenciais
│── 📄 requirements.txt          # Dependências do projeto
│── 📄 README.txt                # Este arquivo
│── 📜 main.py                   # Arquivo principal do bot
│── 📜 bot_launcher.py            # Launcher GUI para gerenciamento do bot
│── 📜 admin_module.py            # Módulo de administração
│── 📜 music_module.py            # Módulo de música
│── 📜 secret_messages.py         # Mensagens secretas e interações especiais
```

---

## Solução de Problemas

- **Comando não reconhecido?** Verifique se os módulos estão carregados corretamente.
- **O bot não responde?** Confirme se o token no `.env` está correto.
- **Erro ao tocar música?** Verifique se `yt-dlp` está instalado e atualizado:
```
pip install -U yt-dlp
```

---

## Tecnologias Utilizadas
- **Linguagem:** Python
- **Bibliotecas:** discord.py, yt-dlp, spotipy, dotenv, tkinter
- **APIs:** Discord, Spotify

---

## Contribuição
Se quiser contribuir:
1. Faça um fork do repositório.
2. Crie uma branch (`git checkout -b feature-nova`).
3. Faça o commit (`git commit -m 'Adicionando nova feature'`).
4. Envie um pull request.

---

### Desenvolvido por Marcelo "Xinous" Pessoa

