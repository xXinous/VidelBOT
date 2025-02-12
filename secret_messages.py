import time
from typing import Tuple, List

# Dicionário que associa "triggers" (geralmente IDs ou combinações) a mensagens secretas
secret_messages: dict[str, str] = {
    "821909378746941441": "AND I KNOW XINOUS",
    "217213953854406657": "Dedo no nariz dá choque, rsrs⚡",
    "143829617789239297": "POR BAHAMUT!!🐲",
    "291345643698389003": "Bahamut te ajudará a durar mais de 3 segundos🐇",
    "363416246848323585": "Não vai me comer não, bardo fudido🥵",
    "821909378746941441_shurima": "Devolva a calcinha da Irene!👺"
}

# Dicionário para gerenciar cooldowns de usuários
user_cooldowns: dict[str, float] = {}

async def handle_secret_message(message) -> bool:
    """
    Verifica se a mensagem enviada corresponde a uma trigger secreta e, se for o caso,
    responde com a mensagem secreta associada ao usuário.

    Parâmetros:
        message: Objeto de mensagem (por exemplo, discord.Message).

    Retorna:
        True se a mensagem for processada como secreta, False caso contrário.
    """
    user_id: str = str(message.author.id)
    # Se o conteúdo da mensagem, sem espaços nas extremidades, corresponder a uma das triggers
    if message.content.strip() in get_secret_triggers():
        response: str | None = secret_messages.get(user_id)
        if response:
            await message.channel.send(response)
            return True
    return False

def get_secret_triggers() -> List[str]:
    """
    Retorna todas as triggers que ativam as mensagens secretas.

    Retorna:
        Uma lista contendo todas as chaves do dicionário secret_messages.
    """
    return list(secret_messages.keys())

def handle_user_cooldowns(user_id: str, cooldown_time: float = 60) -> Tuple[bool, float]:
    """
    Gerencia o cooldown de um usuário específico.

    Parâmetros:
        user_id: Identificador do usuário.
        cooldown_time: Tempo de cooldown em segundos (padrão 60 segundos).

    Retorna:
        Uma tupla contendo:
            - Um booleano que indica se o usuário pode executar a ação (True = liberado).
            - Um float representando o tempo restante de cooldown (0 se liberado).
    """
    current_time: float = time.time()
    last_used: float = user_cooldowns.get(user_id, 0)

    if current_time - last_used < cooldown_time:
        remaining_time: float = round(cooldown_time - (current_time - last_used), 1)
        return False, remaining_time

    user_cooldowns[user_id] = current_time  # Atualiza o timestamp do último uso
    return True, 0.0
