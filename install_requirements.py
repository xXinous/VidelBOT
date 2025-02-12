import tkinter as tk
import ttkbootstrap as ttk  # Importa o ttkbootstrap para um visual moderno
import subprocess
import threading
import sys
import os

class BotLauncher:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("Gerenciador do Bot - Launcher Moderno")
        self.master.geometry("900x500")
        self.master.resizable(False, False)
        self.bot_process = None  # Armazena o processo do bot

        # Configuração do estilo com ttkbootstrap já definido pelo tema
        self.style = ttk.Style()  # Para configurações adicionais, se necessário

        # Frame principal com padding
        self.main_frame = ttk.Frame(master, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de botões (lado esquerdo)
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Botões de controle do bot
        self.btn_start = ttk.Button(self.button_frame, text="Iniciar Bot", command=self.start_bot)
        self.btn_start.pack(pady=5, fill=tk.X)

        self.btn_stop = ttk.Button(self.button_frame, text="Parar Bot", command=self.stop_bot)
        self.btn_stop.pack(pady=5, fill=tk.X)

        self.btn_restart = ttk.Button(self.button_frame, text="Reiniciar Bot", command=self.restart_bot)
        self.btn_restart.pack(pady=5, fill=tk.X)

        self.btn_shutdown = ttk.Button(self.button_frame, text="Desligar Bot", command=self.shutdown_bot)
        self.btn_shutdown.pack(pady=5, fill=tk.X)

        # Botão para instalar dependências
        self.btn_install = ttk.Button(self.button_frame, text="Instalar Dependências", command=self.install_dependencies)
        self.btn_install.pack(pady=5, fill=tk.X)

        # Frame de logs (lado direito)
        self.log_frame = ttk.Frame(self.main_frame)
        self.log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Widget de log (Text) – personalizando fundo e fonte
        self.log_box = tk.Text(self.log_frame, wrap=tk.WORD, bg="#1E1E1E", fg="white", font=("Helvetica", 10))
        self.log_box.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Scrollbar para o log
        self.scrollbar = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.log_box.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_box.config(yscrollcommand=self.scrollbar.set)

        # Configuração de tags de cores para diferenciar mensagens
        self.log_box.tag_config("red", foreground="red")
        self.log_box.tag_config("yellow", foreground="yellow")
        self.log_box.tag_config("white", foreground="white")
        self.log_box.tag_config("gray", foreground="gray")

    def update_log(self, message: str, color: str = "white") -> None:
        """Insere uma mensagem no log e realiza o scroll automático."""
        self.log_box.insert(tk.END, f"{message}\n", color)
        self.log_box.see(tk.END)

    def install_dependencies(self) -> None:
        """
        Instala automaticamente as dependências necessárias.
        Essa função é executada em uma thread separada para não travar a interface.
        """
        def run_install():
            self.update_log("🔄 Atualizando pip...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                               check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                self.update_log("✅ Pip atualizado com sucesso!")
            except subprocess.CalledProcessError as e:
                self.update_log(f"❌ Erro ao atualizar pip: {e}")
                return

            # Lista atualizada de bibliotecas necessárias
            required_libraries = [
                "discord.py",
                "python-dotenv",
                "yt-dlp",
                "spotipy",
                "ttkbootstrap"
            ]
            self.update_log("📦 Instalando bibliotecas necessárias...")
            for lib in required_libraries:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", lib],
                                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    self.update_log(f"✅ {lib} instalado com sucesso!")
                except subprocess.CalledProcessError as e:
                    self.update_log(f"❌ Erro ao instalar {lib}: {e}")
            self.update_log("🎉 Todas as bibliotecas foram instaladas!")
            self.update_log("OBS: 'ffmpeg' e 'tkinter' devem ser instalados via sistema, se necessário.")

        threading.Thread(target=run_install, daemon=True).start()

    def start_bot(self) -> None:
        """Inicia o bot em um subprocesso e começa a capturar os logs."""
        if self.bot_process is None:
            try:
                self.bot_process = subprocess.Popen(
                    [sys.executable, "main.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                threading.Thread(target=self.capture_logs, daemon=True).start()
                self.update_log("[INFO] Bot conectado ao servidor!")
            except Exception as e:
                self.update_log(f"[ERROR] Falha ao iniciar o bot: {e}")
        else:
            self.update_log("[WARNING] O bot já está em execução!")

    def stop_bot(self) -> None:
        """Para o processo do bot, se estiver em execução."""
        if self.bot_process is not None:
            self.bot_process.terminate()
            self.bot_process = None
            self.update_log("[INFO] Bot desconectado do servidor!")
        else:
            self.update_log("[WARNING] O bot não está rodando!")

    def restart_bot(self) -> None:
        """Reinicia o bot."""
        self.stop_bot()
        self.start_bot()
        self.update_log("[INFO] Bot reiniciado!")

    def shutdown_bot(self) -> None:
        """Desliga completamente o bot sem fechar a interface do launcher."""
        self.stop_bot()
        self.update_log("[INFO] Bot desligado!")

    def capture_logs(self) -> None:
        """
        Captura os logs gerados pelo bot (stdout) e os exibe na área de logs.
        Essa função roda em uma thread separada.
        """
        if self.bot_process is None:
            return

        for line in iter(self.bot_process.stdout.readline, ""):
            line = line.strip()
            if "ERROR" in line:
                self.update_log(line, "red")
            elif "WARNING" in line:
                self.update_log(line, "yellow")
            elif "INFO" in line:
                self.update_log(line, "white")
            else:
                self.update_log(line, "gray")
        self.bot_process.stdout.close()

def main() -> None:
    # Cria a janela com ttkbootstrap utilizando o tema "darkly" (você pode escolher outros, como "cyborg", "flatly", etc.)
    root = ttk.Window(themename="darkly")
    launcher = BotLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()
