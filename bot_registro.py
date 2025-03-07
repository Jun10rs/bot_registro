import discord
import os
import asyncio
import json
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Carregar variáveis de ambiente (.env)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("❌ ERRO: O token do bot não foi encontrado no arquivo .env!")
    exit()

# Configuração do bot
GUILD_ID = 1221457783518662696  # ID do servidor
ROLE_ID = 1339685802149679224   # ID da role de membro
CATEGORY_ID = 1332555989152436355  # ID da categoria onde os canais de registro serão criados
RULES_CHANNEL_ID = 1332504780064428114  # ID do canal de regras
TEAM_CHANNEL_ID = 1332507838811213844  # ID do canal de time
FIRST_STEPS_CHANNEL_ID = 1332555967925063753  # ID do canal primeiros passos

# Arquivo JSON para armazenar registros
DATA_FILE = "registros.json"

def carregar_registros():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def salvar_registro(novo_registro):
    registros = carregar_registros()
    registros.append(novo_registro)
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(registros, file, indent=4, ensure_ascii=False)

# Ativar intents antes de criar o bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True  # Ativar captura de reações

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # Usado para comandos Slash

# Lista para armazenar os usuários que concluíram as reações
usuarios_completos = {}

async def check_reactions(member):
    guild = bot.get_guild(GUILD_ID)
    required_channels = [RULES_CHANNEL_ID, TEAM_CHANNEL_ID, FIRST_STEPS_CHANNEL_ID, 1332555989152436355]
    
    for channel_id in required_channels:
        channel = guild.get_channel(channel_id)
        if not channel:
            return False
        
        async for message in channel.history(limit=1):  # Buscar a última mensagem do canal
            reaction = discord.utils.get(message.reactions, emoji="✅")
            if not reaction:
                return False
            
            users = [user async for user in reaction.users()]
            if member not in users:
                return False
    
    return True

class RegistroModal(discord.ui.Modal, title="Registre-se no Servidor"):
    nome = discord.ui.TextInput(label="Seu Nome", required=True)
    telefone = discord.ui.TextInput(label="Seu Número de Telefone", required=True, placeholder="Ex: 47 99999-9999")
    motivo = discord.ui.TextInput(label="Por que quer entrar?", style=discord.TextStyle.long, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        guild = bot.get_guild(GUILD_ID)
        role = guild.get_role(ROLE_ID)
        member = interaction.user
        telefone = self.telefone.value.strip()
        
        # Validar telefone
        if not telefone[:2].isdigit() or not telefone[3:].replace(" ", "").replace("-", "").isdigit():
            await interaction.response.send_message("⚠️ Erro: Número de telefone inválido! Use o formato correto, por exemplo: 47 99999-9999", ephemeral=True)
            return
        
        # Criar registro e salvar no JSON
        novo_registro = {
            "usuario_id": member.id,
            "nome": self.nome.value,
            "telefone": telefone,
            "motivo": self.motivo.value,
            "usuario_mencao": member.mention,
            "data_registro": interaction.created_at.strftime("%d/%m/%Y")
        }
        
        salvar_registro(novo_registro)

        # Adicionar a role e excluir canal
        if role:
            await member.add_roles(role)
            await interaction.response.send_message(
                f"✅ Registro completo, {self.nome.value}! Agora você tem acesso ao servidor.", ephemeral=True
            )
            if interaction.channel:
                await interaction.channel.delete()
        else:
            await interaction.response.send_message("⚠️ Erro ao adicionar a role. Contate um administrador.", ephemeral=True)

class BotaoRegistro(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📋 Registrar-se", style=discord.ButtonStyle.green, custom_id="botao_registro")
    async def abrir_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RegistroModal())

@tree.command(name="dashboard", description="Acesse a dashboard do sistema")
async def dashboard(interaction: discord.Interaction):
    dashboard_url = "http://127.0.0.1:5000"  # URL local
    await interaction.response.send_message(f"🖥️ Acesse os registros aqui: [Clique aqui]({dashboard_url})", ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectado como {bot.user}")

bot.run(TOKEN)
