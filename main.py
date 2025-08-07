import discord
from discord.ext import commands
import json, os, random, asyncio
from datetime import datetime, timedelta

# Chargement ou initialisation des coins
if os.path.exists("coins.json"):
    with open("coins.json", "r") as f:
        user_coins = json.load(f)
else:
    user_coins = {}

# Chargement ou initialisation des derniers daily
if os.path.exists("daily.json"):
    with open("daily.json", "r") as f:
        last_daily = json.load(f)
else:
    last_daily = {}

# Chargement ou initialisation des derniers travail (cooldown 2h)
if os.path.exists("travail.json"):
    with open("travail.json", "r") as f:
        last_work = json.load(f)
else:
    last_work = {}

# Chargement ou initialisation de l'inventaire
if os.path.exists("inventaire.json"):
    with open("inventaire.json", "r") as f:
        inventaire = json.load(f)
else:
    inventaire = {}

en_prison = set()

def save_data():
    with open("coins.json", "w") as f:
        json.dump(user_coins, f)

def save_daily():
    with open("daily.json", "w") as f:
        json.dump(last_daily, f)

def save_work():
    with open("travail.json", "w") as f:
        json.dump(last_work, f)

def save_inventaire():
    with open("inventaire.json", "w") as f:
        json.dump(inventaire, f)

# Boutique mise à jour
shop_items = {
    "peluche": {"name": "Peluche mignonne", "price": 50_000, "desc": "Un adorable doudou tout doux."},
    "fleur": {"name": "Bouquet de fleurs", "price": 30_000, "desc": "Un joli bouquet coloré."},
    "teddy": {"name": "Teddy mignon", "price": 80_000, "desc": "Un nounours câlin."},
    "chaussure": {"name": "Chaussure sale", "price": 10_000, "desc": "Pas très joli, mais c'est un item !"},
    "cafard": {"name": "Cafard dégoûtant", "price": 40_000, "desc": "Un insecte peu charmant."},
    "slibard_ad": {"name": "Le slibard de AD", "price": 25_000, "desc": "Un slip légendaire et mythique."},
    "cours_pimprenelle": {"name": "Cours Pimprenelle", "price": 70_000, "desc": "Un cours de 'L'école c'est gratuit en Belgique' avec Pimprenelle."},
    "peches_thon_mike": {"name": "Les pêches au thon de Mike", "price": 35_000, "desc": "Une recette secrète de Mike qui fait sensation."},
    "riz_au_lait_mike": {"name": "Le riz au lait de Mike", "price": 30_000, "desc": "Un dessert traditionnel revisité par Mike."},
    "seance_psy_imene": {"name": "Séance de psy avec Imene", "price": 60_000, "desc": "Un moment pour parler et se libérer avec Imene."},
    "cours_poterie_razmo": {"name": "Cours de poterie avec Razmo", "price": 45_000, "desc": "Apprends l'art de la poterie avec Razmo."},
    "divorce_express_razmo": {"name": "Divorce express avec Razmo", "price": 55_000, "desc": "Pour régler les choses rapidement avec Razmo."},
    "voile_arrache_sysaa": {"name": "Le voile arraché de Sysaa", "price": 40_000, "desc": "Un mystère dévoilé par Sysaa."},
    "cours_muscu_wshtim": {"name": "Cours de muscu avec Wshtim", "price": 70_000, "desc": "Deviens plus fort avec Wshtim."},
    "visite_corse_bree": {"name": "Visite de la Corse sur le dos de Bree", "price": 90_000, "desc": "Un voyage inoubliable à dos de Bree."},
    "sortie_bar_bree": {"name": "Sortie au bar avec Bree","price": 65_000,"desc": "Une soirée arrosée qui finit toujours par des pas de danse… ou par terre. 🥴"},
    "humiliation_mike": {"name": "L'humiliation de Mike","price": 75_000,"desc": "Invoque un screen humiliant."},
}

# Items de combat avec effets rigolos
combat_items = [
    {"name": "Chaussette puante", "desc": "Inflige 10-20 dégâts et fait perdre un tour à l'adversaire", "damage_min":10, "damage_max":20, "effect":"skip"},
    {"name": "Teddy câlin", "desc": "Soigne 15 PV", "heal":15},
    {"name": "Cafard dégoûtant", "desc": "Inflige 5-25 dégâts et peut paniquer l'adversaire (diminue ses dégâts au prochain tour)", "damage_min":5, "damage_max":25, "effect":"panic"},
    {"name": "Bouquet de fleurs", "desc": "Soigne 10 PV et boost les dégâts au prochain tour", "heal":10, "effect":"boost"},
    {"name": "Le slibard de AD", "desc": "Coup critique avec jusqu'à 30 dégâts", "damage_min":15, "damage_max":30},
    {"name": "Cours Pimprenelle", "desc": "Confond l'adversaire, son attaque rate", "effect":"miss"},
    {"name": "Gourdin en mousse", "desc": "Inflige 12-18 dégâts, mais fait rire l'adversaire, qui rate son prochain coup", "damage_min":12, "damage_max":18, "effect":"miss"},
    {"name": "Canard en plastique", "desc": "Inflige 5 dégâts, mais le canard fait coin-coin, boost tes dégâts au prochain tour", "damage_min":5, "effect":"boost"},
    {"name": "Pistolet à eau", "desc": "Inflige 8-12 dégâts, et mouille l'adversaire, qui perd son prochain tour", "damage_min":8, "damage_max":12, "effect":"skip"},
    {"name": "Tarte à la crème", "desc": "Inflige 10 dégâts et rend l'adversaire aveugle (diminue ses dégâts)", "damage_min":10, "damage_max":10, "effect":"panic"},
    {"name": "Poisson mort", "desc": "Inflige 15 dégâts nauséabonds", "damage_min":15, "damage_max":15},
    {"name": "Baguette magique cassée", "desc": "Lance un sort raté : soigne 10 PV", "heal":10},
    {"name": "Peluche géante", "desc": "Soigne 20 PV et donne un boost de courage", "heal":20, "effect":"boost"},
    {"name": "Bouclier en carton", "desc": "Protège ton prochain tour : annule les dégâts du prochain coup", "effect":"shield"},
    {"name": "Banane glissante", "desc": "Fait glisser l'adversaire, il rate son tour", "effect":"skip"},

    # Ajout des items boutique dans le même format (exemples génériques)
    {"name": "Peluche mignonne", "desc": "Un adorable doudou tout doux.", "damage_min":10, "damage_max":20},
    {"name": "Bouquet de fleurs", "desc": "Un joli bouquet coloré.", "damage_min":10, "damage_max":20},
    {"name": "Teddy mignon", "desc": "Un nounours câlin.", "damage_min":10, "damage_max":20},
    {"name": "Chaussure sale", "desc": "Pas très joli, mais c'est un item !", "damage_min":10, "damage_max":20},
    {"name": "Cafard dégoûtant", "desc": "Un insecte peu charmant.", "damage_min":10, "damage_max":20},
    {"name": "Le slibard de AD", "desc": "Un slip légendaire et mythique.", "damage_min":10, "damage_max":20},
    {"name": "Cours Pimprenelle", "desc": "Un cours de 'L'école c'est gratuit en Belgique' avec Pimprenelle.", "damage_min":10, "damage_max":20},
    {"name": "Les pêches au thon de Mike", "desc": "Une recette secrète de Mike qui fait sensation.", "damage_min":10, "damage_max":20},
    {"name": "Le riz au lait de Mike", "desc": "Un dessert traditionnel revisité par Mike.", "damage_min":10, "damage_max":20},
    {"name": "Séance de psy avec Imene", "desc": "Un moment pour parler et se libérer avec Imene.", "damage_min":10, "damage_max":20},
    {"name": "Cours de poterie avec Razmo", "desc": "Apprends l'art de la poterie avec Razmo.", "damage_min":10, "damage_max":20},
    {"name": "Divorce express avec Razmo", "desc": "Pour régler les choses rapidement avec Razmo.", "damage_min":10, "damage_max":20},
    {"name": "Le voile arraché de Sysaa", "desc": "Un mystère dévoilé par Sysaa.", "damage_min":10, "damage_max":20},
    {"name": "Cours de muscu avec Wshtim", "desc": "Deviens plus fort avec Wshtim.", "damage_min":10, "damage_max":20},
    {"name": "Visite de la Corse sur le dos de Bree", "desc": "Un voyage inoubliable à dos de Bree.", "damage_min":10, "damage_max":20},
    {"name": "Sortie au bar avec Bree", "desc": "Une soirée arrosée qui finit toujours par des pas de danse… ou par terre. 🥴", "damage_min":10, "damage_max":20},
    {"name": "L'humiliation de Mike", "desc": "Invoque un screen humiliant.", "damage_min":10, "damage_max":20},
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------
# Commandes classiques (coins, daily, travail, give, etc.) - inchangées
# ------------------

# Gestion des animaux
if os.path.exists("animals.json"):
    with open("animals.json", "r") as f:
        user_animals = json.load(f)
else:
    user_animals = {}

def save_animals():
    with open("animals.json", "w") as f:
        json.dump(user_animals, f, indent=4)
        
@bot.event
async def on_ready():
    print(f"✅ Connecté comme {bot.user.name}")

@bot.command()
async def coins(ctx):
    uid = str(ctx.author.id)
    user_coins.setdefault(uid, 100)
    save_data()
    await ctx.send(f"{ctx.author.mention}, tu as **{user_coins[uid]} coins** !")

@bot.command()
async def daily(ctx):
    uid = str(ctx.author.id)
    now = datetime.utcnow()
    last = last_daily.get(uid)
    if last and now.date() == datetime.strptime(last, "%Y-%m-%d").date():
        await ctx.send("⏳ Tu as déjà pris ton daily aujourd'hui !")
        return
    reward = random.randint(100, 300)
    user_coins[uid] = user_coins.get(uid, 0) + reward
    last_daily[uid] = now.strftime("%Y-%m-%d")
    save_data()
    save_daily()
    await ctx.send(f"🎁 Tu as reçu **{reward} coins** aujourd'hui, {ctx.author.mention} !")

@bot.command()
async def travail(ctx):
    uid = str(ctx.author.id)
    now = datetime.utcnow()
    last = last_work.get(uid)
    if last and now < datetime.strptime(last, "%Y-%m-%d %H:%M:%S") + timedelta(hours=2):
        reste = datetime.strptime(last, "%Y-%m-%d %H:%M:%S") + timedelta(hours=2) - now
        await ctx.send(f"⏳ Reviens dans {reste.seconds // 60} minutes et {reste.seconds % 60} secondes.")
        return
    gain = random.randint(50, 200)
    user_coins[uid] = user_coins.get(uid, 0) + gain
    last_work[uid] = now.strftime("%Y-%m-%d %H:%M:%S")
    save_data()
    save_work()
    await ctx.send(f"🛠️ Tu as gagné **{gain} coins** en travaillant, {ctx.author.mention} !")

@bot.command()
async def give(ctx, member: discord.Member, amount: int):
    role_banque = discord.utils.get(ctx.guild.roles, name="banque")
    if role_banque not in ctx.author.roles:
        await ctx.send("🚫 Seuls les membres avec le rôle 'banque' peuvent utiliser cette commande.")
        return
    uid = str(member.id)
    user_coins[uid] = user_coins.get(uid, 0) + amount
    save_data()
    await ctx.send(f"💸 {amount} coins ont été donnés à {member.mention} !")

@bot.command(name="retirer_tout")
async def retirer_tout(ctx, member: discord.Member):
    if ctx.author.name.lower() != "kameliaaddams":
        await ctx.send("🚫 Seule KameliaAddams peut utiliser cette commande.")
        return
    uid = str(member.id)
    amount = user_coins.get(uid, 0)
    user_coins[uid] = 0
    save_data()
    await ctx.send(f"💀 {amount} coins ont été entièrement retirés à {member.mention}.")

@bot.command()
async def retirer(ctx, member: discord.Member, amount: int):
    if ctx.author.name.lower() != "kameliaaddams":
        await ctx.send("🚫 Seule KameliaAddams peut utiliser cette commande.")
        return
    uid = str(member.id)
    user_coins[uid] = max(0, user_coins.get(uid, 0) - amount)
    save_data()
    await ctx.send(f"❌ {amount} coins ont été retirés à {member.mention}.")

en_prison = set()

@bot.command()
async def voler(ctx, member: discord.Member):
    voleur_id = str(ctx.author.id)
    victime_id = str(member.id)

    if voleur_id == victime_id:
        await ctx.send("🙄 Tu ne peux pas te voler toi-même.")
        return

    if voleur_id in en_prison:
        await ctx.send("🚨 Tu es actuellement en prison ! Attends ta libération avant de recommencer.")
        return

    if random.randint(1, 100) <= 25:  # 25% de chance de réussite
        vol_possible = max(1, user_coins.get(victime_id, 0) // 4)
        montant_volee = random.randint(1, vol_possible)
        user_coins[victime_id] = max(0, user_coins.get(victime_id, 0) - montant_volee)
        user_coins[voleur_id] = user_coins.get(voleur_id, 0) + montant_volee
        save_data()
        await ctx.send(f"🕵️‍♂️ {ctx.author.mention} a réussi à voler **{montant_volee} coins** à {member.mention} !")
    else:
        solde_voleur = user_coins.get(voleur_id, 0)
        pourcentage = random.uniform(0.05, 0.15)  # 5% à 15%
        dommage = int(solde_voleur * pourcentage)
        dommage = min(solde_voleur, dommage)

        user_coins[voleur_id] -= dommage
        user_coins[victime_id] = user_coins.get(victime_id, 0) + dommage
        save_data()

        en_prison.add(voleur_id)
        await ctx.send(
            f"🚓 {ctx.author.mention} a raté son vol et est envoyé en prison pour 60 secondes !\n"
            f"💸 Il verse **{dommage} coins** à {member.mention} en dommages et intérêts."
        )

        await asyncio.sleep(60)
        en_prison.remove(voleur_id)
        await ctx.send(f"🔓 {ctx.author.mention} est sorti de prison ! Il est libre de voler à nouveau.")

@bot.command()
async def boutique(ctx):
    embed = discord.Embed(title="🛒 Boutique", color=0xFF69B4)
    for key, item in shop_items.items():
        embed.add_field(name=f"{item['name']} - {item['price']} coins", value=item['desc'], inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def acheter(ctx, *, item_name: str):
    uid = str(ctx.author.id)

    # Chercher l'item soit par clé, soit par nom visible
    item_key = None
    for key, item in shop_items.items():
        if key.lower() == item_name.lower() or item['name'].lower() == item_name.lower():
            item_key = key
            break

    if not item_key:
        await ctx.send("❌ Cet item n'existe pas.")
        return

    item = shop_items[item_key]

    if user_coins.get(uid, 0) < item['price']:
        await ctx.send("❌ Tu n'as pas assez de coins.")
        return

    user_coins[uid] -= item['price']

    # Ajout dans inventaire
    inventaire.setdefault(uid, [])
    inventaire[uid].append(item_key)
    save_inventaire()

    save_data()
    await ctx.send(f"✅ Tu as acheté **{item['name']}** pour {item['price']} coins !")

@bot.command()
async def classement(ctx):
    classement = sorted(user_coins.items(), key=lambda x: x[1], reverse=True)
    embed = discord.Embed(title="🏆 Classement des joueurs", color=0xFFD700)
    for uid, coins in classement[:10]:
        member = ctx.guild.get_member(int(uid)) or await ctx.guild.fetch_member(int(uid))
        name = member.display_name if member else f"Utilisateur inconnu ({uid})"
        embed.add_field(name=name, value=f"{coins} coins", inline=False)
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    uid = str(ctx.author.id)
    if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.MissingPermissions):
        if user_coins.get(uid, 0) >= 100:
            user_coins[uid] -= 100
            save_data()
            await ctx.send(f"🚫 {ctx.author.mention}, 100 coins ont été retirés pour cette erreur de commande.")
        else:
            await ctx.send(f"🚫 {ctx.author.mention}, commande interdite, mais tu n'avais pas assez de coins pour la pénalité.")
        return
    raise error

# Commande inventaire corrigée pour éviter conflit de nom
@bot.command(name="inventaire")
async def voir_inventaire(ctx):
    uid = str(ctx.author.id)
    items = inventaire.get(uid, [])
    if not items:
        await ctx.send("🎒 Ton inventaire est vide.")
        return

    counts = {}
    for i in items:
        counts[i] = counts.get(i, 0) + 1

    msg = "🎒 **Ton inventaire :**\n"
    for key, count in counts.items():
        item = shop_items.get(key, {"name": key, "desc": "Aucun détail."})
        msg += f"- {item['name']} x{count}\n"

    await ctx.send(msg)

# Système de combat PvP drôle

import asyncio

@bot.command()
async def combat(ctx, adversaire: discord.Member):
    uid1 = str(ctx.author.id)
    uid2 = str(adversaire.id)
    if uid1 == uid2:
        await ctx.send("🤡 Tu ne peux pas te battre contre toi-même !")
        return

    if user_coins.get(uid1, 0) < 10 or user_coins.get(uid2, 0) < 10:
        await ctx.send("⚠️ Les deux joueurs doivent avoir au moins 10 coins pour se battre.")
        return

    armes_neutres = {
        "Gourdin": {"pv": 8, "degats_min": 4, "degats_max": 8},
        "Chaussure sale": {"pv": 7, "degats_min": 3, "degats_max": 7},
        "Canard en plastique": {"pv": 6, "degats_min": 2, "degats_max": 6},
        "Poisson mort": {"pv": 6, "degats_min": 3, "degats_max": 6},
        "Épée en mousse": {"pv": 9, "degats_min": 5, "degats_max": 9},
        "Balai magique": {"pv": 9, "degats_min": 4, "degats_max": 8},
        "Oreiller volant": {"pv": 6, "degats_min": 2, "degats_max": 5},
        "Poêle à frire": {"pv": 10, "degats_min": 6, "degats_max": 10}
    }

    armes_boutique = {
        "peluche": {"name": "Peluche mignonne", "pv": 20, "degats_min": 8, "degats_max": 14},
        "fleur": {"name": "Bouquet de fleurs", "pv": 20, "degats_min": 8, "degats_max": 14},
        "teddy": {"name": "Teddy mignon", "pv": 20, "degats_min": 8, "degats_max": 14},
        "chaussure": {"name": "Chaussure sale", "pv": 20, "degats_min": 8, "degats_max": 14},
        "cafard": {"name": "Cafard dégoûtant", "pv": 20, "degats_min": 8, "degats_max": 14},
        "slibard_ad": {"name": "Le slibard de AD", "pv": 20, "degats_min": 8, "degats_max": 14},
        "cours_pimprenelle": {"name": "Cours Pimprenelle", "pv": 20, "degats_min": 8, "degats_max": 14},
        "peches_thon_mike": {"name": "Les pêches au thon de Mike", "pv": 20, "degats_min": 8, "degats_max": 14},
        "riz_au_lait_mike": {"name": "Le riz au lait de Mike", "pv": 20, "degats_min": 8, "degats_max": 14},
        "seance_psy_imene": {"name": "Séance de psy pour Imene", "pv": 20, "degats_min": 8, "degats_max": 14},
        "cours_poterie_razmo": {"name": "Cours de poterie avec Razmo", "pv": 20, "degats_min": 8, "degats_max": 14},
        "divorce_express_razmo": {"name": "Divorce express avec Razmo", "pv": 20, "degats_min": 8, "degats_max": 14},
        "voile_arrache_sysaa": {"name": "Le voile arraché de Sysaa", "pv": 20, "degats_min": 8, "degats_max": 14},
        "cours_muscu_wshtim": {"name": "Cours de muscu avec Wshtim", "pv": 20, "degats_min": 8, "degats_max": 14},
        "visite_corse_bree": {"name": "Visite de la Corse sur le dos de Bree", "pv": 20, "degats_min": 8, "degats_max": 14},
        "sortie_bar_bree": {"name": "Sortie au bar avec Bree", "pv": 20, "degats_min": 8, "degats_max": 14},  # Nouveau
        "humiliation_mike": {"name": "L'humiliation de Mike", "pv": 20, "degats_min": 8, "degats_max": 14},    # Nouveau
    }

    def choisir_arme(uid):
        items = inventaire.get(uid, [])
        # Filtrer les items que le joueur possède et qui sont dans la boutique
        items_possibles = [cle for cle in items if cle in armes_boutique]
        if items_possibles:
            cle_choisie = random.choice(items_possibles)
            return armes_boutique[cle_choisie]["name"], armes_boutique[cle_choisie]
        # Sinon arme neutre aléatoire
        nom, stats = random.choice(list(armes_neutres.items()))
        return nom, stats

    nom1, arme1 = choisir_arme(uid1)
    nom2, arme2 = choisir_arme(uid2)

    pv1 = arme1["pv"]
    pv2 = arme2["pv"]

    await ctx.send(f"⚔️ **Combat épique** entre {ctx.author.display_name} (armé de **{nom1}**) et {adversaire.display_name} (armé de **{nom2}**) !")

    phrases_coup = [
        "{attaquant} balance un coup magistral avec {arme}, infligeant {degats} dégâts à {defenseur} !",
        "Ouh là ! {defenseur} reçoit {degats} dégâts de la part de {attaquant} et son fidèle {arme}.",
        "{attaquant} enchaîne avec un coup de {arme} qui fait perdre {degats} PV à {defenseur}.",
        "Coup de théâtre : {defenseur} encaisse {degats} dégâts de {attaquant} armé de son {arme} !",
        "{attaquant} rigole en frappant avec {arme}, {defenseur} perd {degats} PV.",
        "Surprise ! {attaquant} utilise {arme} et inflige {degats} dégâts à {defenseur}.",
        "{defenseur} vacille sous les coups de {arme} de {attaquant} (-{degats} PV).",
        "{attaquant} lance un coup puissant avec {arme}, faisant {degats} dégâts à {defenseur}."
    ]

    phrases_ambiances = [
        "🔥 Le public est en feu, ça tape fort !",
        "😵 Ça va mal finir pour l'un des combattants...",
        "💥 Les coups pleuvent sans pitié !",
        "🎉 Quel combat spectaculaire, bravo les artistes !",
        "⚡ L'air est chargé d'électricité, tension maximale !",
        "🥳 Les fans crient, encouragent, vibrent !"
    ]

    narration = []

    for tour in range(1, 11):
        if pv1 <= 0 or pv2 <= 0:
            break
        if tour % 2 == 1:
            attaquant = ctx.author.display_name
            defenseur = adversaire.display_name
            pv_def = pv2
            arme_attaquant = arme1
            pv_def_key = "pv2"
            nom_arme = nom1
        else:
            attaquant = adversaire.display_name
            defenseur = ctx.author.display_name
            pv_def = pv1
            arme_attaquant = arme2
            pv_def_key = "pv1"
            nom_arme = nom2

        degats = random.randint(arme_attaquant["degats_min"], arme_attaquant["degats_max"])
        pv_def -= degats
        if pv_def_key == "pv2":
            pv2 = max(0, pv_def)
        else:
            pv1 = max(0, pv_def)

        phrase = random.choice(phrases_coup).format(attaquant=attaquant, defenseur=defenseur, arme=nom_arme, degats=degats)
        narration.append(phrase)

        # Phrase ambiance tous les 2 tours
        if tour % 2 == 0:
            narration.append(random.choice(phrases_ambiances))

    # Envoie par blocs de 3 phrases, pause 2s
    for i in range(0, len(narration), 3):
        await ctx.send("\n".join(narration[i:i+3]))
        await asyncio.sleep(2)

    if pv1 > pv2:
        gagnant = ctx.author
        perdant = adversaire
    elif pv2 > pv1:
        gagnant = adversaire
        perdant = ctx.author
    else:
        gagnant = None

    if gagnant:
        user_coins[str(gagnant.id)] = user_coins.get(str(gagnant.id), 0) + 5000
        save_data()
        await ctx.send(f"🏆 **{gagnant.display_name} remporte le combat et gagne 5000 coins !** {perdant.display_name} est KO.")
    else:
        await ctx.send("🤝 Le combat se termine par un match nul.")

@bot.command(name="barman")
async def barman(ctx, *, nom_boisson: str = None):
    boissons = {
        "café serré": ("☕ Tu pètes le feu !", 10),
        "café allongé": ("🚽 Urgence toilettes !", -5),
        "irish coffee": ("🍀 Tu danses une gigue sans raison.", 15),
        "cappuccino": ("✨ Tu es soudainement très stylé.e.", 5),
        "thé vert": ("🍃 Une vague de sagesse t’envahit.", 8),
        "expresso double": ("⚡ Tu veux conquérir le monde.", 12),
        "rhum arrangé": ("🥴 Tu roules sous la table.", -10),
        "lait fraise": ("🍼 Tu régresses à l’âge de 6 ans.", -3),
        "mojito": ("🎉 Tu proposes une soirée à tout le monde.", 7),
        "eau pétillante": ("💨 Tu lâches un petit rot, discret (ou pas).", 2),
        "chocolat chaud": ("🍫 Tu as envie de câliner quelqu’un.", 6),
        "red bull": ("🦅 Tu crois que tu peux voler.", 9),
        "jus multifruits": ("🍹 Tu gagnes un boost de bonne humeur.", 10),
        "thé noir": ("😐 T’as envie de philosopher sur la vie.", 4),
        "shot vodka-get 27": ("🤢 Tu vomis dans un coin… mais dignement.", -15)
    }

    # Chargement ou initialisation des énergies
    if os.path.exists("energy.json"):
        with open("energy.json", "r") as f:
            user_energy = json.load(f)
    else:
        user_energy = {}

    user_id = str(ctx.author.id)

    if user_id not in user_energy:
        user_energy[user_id] = 50  # énergie de base

    if nom_boisson is None:
        nom, (effet, modif) = random.choice(list(boissons.items()))
    else:
        nom_normalise = nom_boisson.strip().lower()
        if nom_normalise not in boissons:
            await ctx.send("❌ Cette boisson n’est pas servie ici !")
            return
        nom = nom_normalise
        effet, modif = boissons[nom]

    user_energy[user_id] += modif
    if user_energy[user_id] < 0:
        user_energy[user_id] = 0

    action = "gagné" if modif > 0 else "perdu"

    await ctx.send(
        f"🥤 **Tu as bu : {nom.title()}**\n"
        f"{effet}\n"
        f"⚡ Tu as {action} **{abs(modif)}** points d’énergie."
    )

    with open("energy.json", "w") as f:
        json.dump(user_energy, f)

@bot.command(name="energie")
async def energie(ctx):
    # Chargement ou création du fichier energy.json
    if os.path.exists("energy.json"):
        with open("energy.json", "r") as f:
            user_energy = json.load(f)
    else:
        user_energy = {}

    user_id = str(ctx.author.id)

    # Si l'utilisateur n'a pas encore d'énergie enregistrée
    if user_id not in user_energy:
        user_energy[user_id] = 50  # Valeur de départ
        with open("energy.json", "w") as f:
            json.dump(user_energy, f)

    await ctx.send(f"⚡ **{ctx.author.display_name}**, ton niveau d’énergie est de **{user_energy[user_id]}** points.")



@bot.event
async def on_command_error(ctx, error):
    uid = str(ctx.author.id)
    if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.MissingPermissions):
        if user_coins.get(uid, 0) >= 100:
            user_coins[uid] -= 100
            save_data()
            await ctx.send(f"🚫 {ctx.author.mention}, 100 coins ont été retirés pour cette erreur de commande.")
        else:
            await ctx.send(f"🚫 {ctx.author.mention}, commande interdite, mais tu n'avais pas assez de coins pour la pénalité.")
        return
    raise error

class RouletteView(discord.ui.View):
    def __init__(self, author_id, gain, count):
        super().__init__(timeout=60)
        self.author_id = author_id
        self.gain = gain
        self.count = count

    @discord.ui.button(label="🔫 Rejouer", style=discord.ButtonStyle.danger)
    async def relancer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("🚫 Ce bouton est réservé à l'utilisateur qui a lancé la roulette.", ephemeral=True)
            return

        if self.count >= 5:
            await interaction.response.edit_message(content=f"💥 Tu as atteint la limite de relance (5 fois). Tu gardes tes **{self.gain} coins**.", view=None)
            return

        resultat = "gagner" if random.random() < 0.65 else "perdre"
        if resultat == "gagner":
            nouveau_gain = int(self.gain * 1.5)
            user_coins[str(self.author_id)] += nouveau_gain
            save_data()
            await interaction.response.edit_message(
                content=f"🎯 Tu as gagné **{nouveau_gain} coins** ! Tu veux tenter encore ?",
                view=RouletteView(self.author_id, nouveau_gain, self.count + 1)
            )
        else:
            await interaction.response.edit_message(content=f"💀 Tu as tout perdu... ({self.gain} coins)", view=None)
            return

@bot.command()
async def roulette(ctx, mise: int):
    uid = str(ctx.author.id)
    if mise <= 0 or user_coins.get(uid, 0) < mise:
        await ctx.send("❌ Mise invalide ou solde insuffisant.")
        return

    resultat = "gagner" if random.random() < 0.65 else "perdre"
    if resultat == "gagner":
        gain = mise * 3
        user_coins[uid] += gain
        save_data()
        await ctx.send(
            f"🔫 Bang ! Tu as survécu et gagné **{gain} coins** !",
            view=RouletteView(ctx.author.id, gain, 1)
        )
    else:
        perte = mise * 2
        user_coins[uid] -= perte
        save_data()
        await ctx.send(f"💥 Boum ! Tu as perdu **{perte} coins** dans cette roulette russe...")

from discord.ui import View, Button
from discord import ButtonStyle
import random

@bot.command()
async def ppc(ctx, adversaire: discord.Member, mise: int):
    """Jeu Pierre-Papier-Ciseaux avec mise, boutons partagés et gain aléatoire."""

    if adversaire.bot:
        await ctx.send("Tu ne peux pas jouer contre un bot.")
        return

    if ctx.author == adversaire:
        await ctx.send("Tu ne peux pas jouer contre toi-même.")
        return

    uid1 = str(ctx.author.id)
    uid2 = str(adversaire.id)

    if user_coins.get(uid1, 0) < mise or user_coins.get(uid2, 0) < mise:
        await ctx.send("💸 Les deux joueurs doivent avoir assez de coins pour miser cette somme.")
        return

    choix = {}

    class PPCView(View):
        def __init__(self):
            super().__init__(timeout=30)

        async def interaction_handler(self, interaction: discord.Interaction, coup):
            if interaction.user.id not in [ctx.author.id, adversaire.id]:
                await interaction.response.send_message("Ce jeu ne te concerne pas !", ephemeral=True)
                return

            if str(interaction.user.id) in choix:
                await interaction.response.send_message("Tu as déjà choisi !", ephemeral=True)
                return

            choix[str(interaction.user.id)] = coup
            await interaction.response.send_message(f"Choix enregistré : {coup} !", ephemeral=True)

            if len(choix) == 2:
                self.stop()

        @discord.ui.button(label="🪨 Pierre", style=ButtonStyle.secondary)
        async def pierre(self, interaction: discord.Interaction, button: Button):
            await self.interaction_handler(interaction, "pierre")

        @discord.ui.button(label="📄 Papier", style=ButtonStyle.primary)
        async def papier(self, interaction: discord.Interaction, button: Button):
            await self.interaction_handler(interaction, "papier")

        @discord.ui.button(label="✂️ Ciseaux", style=ButtonStyle.danger)
        async def ciseaux(self, interaction: discord.Interaction, button: Button):
            await self.interaction_handler(interaction, "ciseaux")

    view = PPCView()
    await ctx.send(f"{ctx.author.mention} vs {adversaire.mention} - Choisissez votre coup en cliquant sur un bouton !", view=view)

    await view.wait()

    if len(choix) < 2:
        await ctx.send("⏱️ L’un des deux joueurs n’a pas répondu à temps, partie annulée.")
        return

    emojis = {"pierre": "🪨", "papier": "📄", "ciseaux": "✂️"}
    gagne_sur = {"pierre": "ciseaux", "papier": "pierre", "ciseaux": "papier"}

    coup1 = choix[uid1]
    coup2 = choix[uid2]

    if coup1 == coup2:
        await ctx.send(f"🤝 Égalité ! Vous avez tous les deux choisi {emojis[coup1]}.")
        return

    if gagne_sur[coup1] == coup2:
        gagnant = ctx.author
        perdant = adversaire
        choix_g, choix_p = coup1, coup2
    else:
        gagnant = adversaire
        perdant = ctx.author
        choix_g, choix_p = coup2, coup1

    gain = random.randint(300, 700)

    user_coins[str(gagnant.id)] += gain
    user_coins[str(perdant.id)] -= mise
    save_data()

    await ctx.send(
        f"🎉 {gagnant.mention} gagne {gain} coins avec {emojis[choix_g]} contre {emojis[choix_p]} de {perdant.mention} ! "
        f"{perdant.mention} perd sa mise de {mise} coins."
    )



@bot.command()
async def adopter(ctx, animal: str = None, *, nom: str = None):
    user_id = str(ctx.author.id)
    if user_id in user_animals:
        await ctx.send("Tu as déjà un animal ! Utilise `!animal` pour le voir.")
        return

    if animal is None or nom is None:
        await ctx.send("Utilisation : `!adopter [type d'animal] [nom]`.\nExemple : `!adopter chat Biscotte`")
        return

    now = datetime.utcnow().isoformat()
    user_animals[user_id] = {
        "type": animal.lower(),
        "nom": nom,
        "dernier_repas": now
    }
    save_animals()
    await ctx.send(f"Tu as adopté un **{animal}** nommé **{nom}** ! 🐾 Prends-en soin avec `!nourrir`.")

@bot.command()
async def nourrir(ctx):
    user_id = str(ctx.author.id)
    if user_id not in user_animals:
        await ctx.send("Tu n’as pas encore d’animal ! Utilise `!adopter`.")
        return

    dernier_repas = datetime.fromisoformat(user_animals[user_id]["dernier_repas"])
    now = datetime.utcnow()
    delta = now - dernier_repas

    if delta < timedelta(hours=3):
        heures_restantes = 3 - delta.total_seconds() // 3600
        await ctx.send(f"Ton animal a déjà mangé récemment. Réessaie dans {int(heures_restantes)}h.")
        return

    user_animals[user_id]["dernier_repas"] = now.isoformat()
    save_animals()
    await ctx.send(f"Tu as nourri {user_animals[user_id]['nom']} ! ❤️ Il est heureux et repu.")

@bot.command()
async def animal(ctx):
    user_id = str(ctx.author.id)
    if user_id not in user_animals:
        await ctx.send("Tu n’as pas encore d’animal. Utilise `!adopter`.")
        return

    data = user_animals[user_id]
    dernier_repas = datetime.fromisoformat(data["dernier_repas"])
    delta = datetime.utcnow() - dernier_repas

    if delta > timedelta(hours=48):
        await ctx.send(f"😢 {data['nom']} s’est enfui car tu ne l’as pas nourri depuis trop longtemps...")
        del user_animals[user_id]
        save_animals()
        return

    heures_depuis = int(delta.total_seconds() // 3600)
    await ctx.send(
        f"🐾 Ton animal : **{data['type']}** nommé **{data['nom']}**\n"
        f"🥣 Dernier repas : il y a {heures_depuis}h.\n"
        f"😊 Niveau de bonheur : {data.get('bonheur', 50)} / 100"
    )

@bot.command()
async def abandonner(ctx):
    user_id = str(ctx.author.id)
    if user_id not in user_animals:
        await ctx.send("Tu n’as pas d’animal à abandonner.")
        return

    animal = user_animals[user_id]["nom"]
    del user_animals[user_id]
    save_animals()
    await ctx.send(f"😢 Tu as abandonné **{animal}**. Prends bien soin de ton prochain compagnon !")

@bot.command()
async def jouer(ctx):
    user_id = str(ctx.author.id)
    if user_id not in user_animals:
        await ctx.send("Tu n’as pas d’animal à qui jouer. Adopte-en un avec `!adopter` !")
        return

    animal = user_animals[user_id]

    # Augmente bonheur, max 100
    animal["bonheur"] = min(100, animal.get("bonheur", 50) + random.randint(5, 15))

    save_animals()
    await ctx.send(f"🎾 Tu as joué avec **{animal['nom']}** ! Son bonheur est maintenant à {animal['bonheur']} / 100.")

traque_target = None
traque_active = False

@bot.command()
async def traque(ctx, membre: discord.Member):
    global traque_target, traque_active
    if traque_active:
        await ctx.send(f"Quelqu’un est déjà traqué... laisse-lui souffler un peu.")
    else:
        traque_target = membre.id
        traque_active = True
        await ctx.send(f"👁️ La traque commence... {membre.mention} est désormais observé de très près.")
        await asyncio.sleep(3600)  # 1 heure
        traque_target = None
        traque_active = False
        await ctx.send("La traque est terminée. Pour l’instant...")

@bot.command()
@commands.has_permissions(administrator=True)
async def stoptraque(ctx):
    global traque_target, traque_active
    if traque_active:
        traque_target = None
        traque_active = False
        await ctx.send("🛑 La traque a été interrompue. La cible peut respirer.")
    else:
        await ctx.send("Il n’y a personne sous surveillance pour le moment.")

@bot.event
async def on_message(message):
    global traque_target, traque_active

    await bot.process_commands(message)  # Nécessaire pour ne pas bloquer les autres commandes

    if traque_active and message.author.id == traque_target:
        if random.random() < 0.6:  # 70% de chance
            phrases = [
                "Je te vois.",
                "Encore toi...",
                "T’as pas honte ?",
                "Respire pendant que tu peux.",
                "Tu crois qu’ils t’aiment vraiment ici ?",
                "👀",
                "Même ton clavier en a marre.",
                "Tu fais vraiment des efforts là ?",
                "T’es la raison pour laquelle le serveur lag.",
                "On murmure ton pseudo dans les salons secrets.",
                "Ton ombre a honte de toi.",
                "Chut... ils écoutent.",
                "J’aurais préféré traquer un pigeon, mais bon...",
                "Tu sens le désespoir dans tes messages.",
                "Quelqu’un t’a autorisé à parler ?",
                "T’as déjà essayé de te taire ? C’est magique.",
                "Chaque message que tu envoies... c’est une erreur.",
                "Tes touches doivent pleurer à chaque frappe.",
                "Même ton micro veut couper le son.",
                "C’est fascinant à quel point tu peux être gênant sans faire exprès.",
                "Parfois, je me demande si t'es généré par une IA ratée.",
                "On a lancé la traque, mais on regrette déjà.",
                "Tu parles, mais personne ne t’écoute. Littéralement.",
                "Je préférerais lire les CGU de Discord que tes messages.",
                "Tu veux une pelle ? T’as l’air de creuser tout seul.",
                "On dirait que t’as mangé un bug Discord.",
                "Chaque mot que tu tapes est un cri à l’aide.",
                "Même la corbeille refuse tes idées.",
                "T'es comme une mise à jour foirée : lourd et inutile.",
                "T’écris comme si t’étais payé pour embêter tout le monde.",
                "Tu veux un cookie ? Non. T’as rien mérité.",
                "Si le cringe était une personne, ce serait toi.",
                "On devrait te bannir juste pour le bien de l’esthétique.",
                "Parle plus fort, ton ego a du mal à t'entendre.",
                "On a pensé à te mettre dans un salon isolé. Pour toujours.",
                "On dirait Mike, le mytho qui croit qu’il est le héros d’un film... Spoiler : personne n’a demandé.",
                "T’es tellement dans ton monde, on dirait Mike avec son syndrome du personnage principal en pleine crise.",
                "Imene serait fière de ton niveau drama, tu peux t’embrouiller avec l’air ambiant, champion(ne) du monde.",
                "Si Imene te voyait, elle t’appellerait pour un duel dramatique épique, même pour une faute de frappe.",
                "Clavier veut déjà porter plainte, mais bon, on sait qu’il pleure à chaque notification, pauvre chou.",
                "T’as peur de tout, on dirait Clavier quand on lui parle d’un petit problème... Respire un coup."
            ]
            await message.reply(random.choice(phrases))

@bot.command()
async def jugement(ctx, membre: discord.Member):
    verdicts = [
        "COUPABLE DE NULLITÉ ABSOLUE.",
        "ACCUSÉ D’AVOIR VOLÉ L’OXYGÈNE INUTILEMENT.",
        "JUGÉ POUR CRIME CONTRE LA DIGNITÉ DU SERVEUR.",
        "CONDAMNÉ À RÉFLÉCHIR AVANT DE PARLER. PEINE IMPOSSIBLE.",
        "INNOCENT... MAIS ÇA RESTE LOUCHE.",
        "DÉCLARÉ COUPABLE DE CRINGE AGGRAVÉ.",
        "RECHERCHÉ POUR SPAMAGE INTENSIF DE MÉDIOCRITÉ.",
        "BANNI MENTALEMENT PAR LA COUR.",
        "A TENTÉ D’ÊTRE DRÔLE. A ÉCHOUÉ.",
        "DÉNONCÉ PAR TOUT LE MONDE SAUF SA PROPRE CONSCIENCE.",
        "CONDAMNÉ À 30 MESSAGES SANS RÉACTION.",
        "JUGEMENT RENDU : TAIS-TOI.",
        "RESPONSABLE MAIS PAS COUPABLE... COMME D’HAB.",
        "CRIMINEL DU BON GOÛT DEPUIS 2017.",
        "ON N’A PAS DE PREUVES, MAIS ON SAIT QUE C’EST TOI.",
        "PUNI D’AVOIR EXISTÉ TROP BRUYAMMENT.",
        "CONDAMNÉ À ÊTRE @ À CHAQUE FAUTE D’ORTHOGRAPHE.",
        "VERDICT : TROP CHIANT POUR ÊTRE ACQUITTÉ.",
        "LE TRIBUNAL TE REGARDE. AVEC HONTE.",
        "EXILÉ DANS LE CHAN #GÊNE POUR 24H."
    ]

    emoji = "⚖️"
    verdict = random.choice(verdicts)

    # Espaces insécables pour centrer approximativement (pas parfait mais mieux)
    espace = "\u2800" * 10

    embed = discord.Embed(
        title=f"{emoji} TRIBUNAL DISCORDIEN",
        description=f"{espace}\n**__{verdict}__**\n{espace}",
        color=discord.Color.red()
    )
    embed.set_footer(text=f"Jugement rendu pour {membre.display_name} — Qu’il en soit ainsi.")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def nom(ctx, membre: discord.Member, nouveau_nom: str):
    ancien_nom = membre.display_name
    duree = 120  # 2 minutes en secondes
    try:
        await membre.edit(nick=nouveau_nom)
        await ctx.send(f"Le pseudo de {membre.mention} a été changé en **{nouveau_nom}** pendant 2 minutes.")
        await asyncio.sleep(duree)
        await membre.edit(nick=ancien_nom)
        await ctx.send(f"Le pseudo de {membre.mention} a été remis à **{ancien_nom}**.")
    except discord.Forbidden:
        await ctx.send("Je n'ai pas la permission de modifier ce pseudo.")
    except Exception as e:
        await ctx.send(f"Une erreur est survenue : {e}")

# Liste globale des phrases cinglantes
raisons = [
    "{membre} spamme comme s’il/elle avait un quota à remplir, c’est insupportable.",
    "{membre} écrit comme un captcha illisible, sérieusement ?",
    "{membre} est une présence toxique, mais bizarrement divertissante.",
    "Merci {membre} d’avoir pingé tout le monde pour rien, on t’adore.",
    "La tentative de blague de {membre} était nulle, même le 18 mai à 14h37.",
    "{membre} respire trop fort sur les vocs, on t’entend venir.",
    "Le pseudo de {membre} fait mal aux yeux, vraiment.",
    "Même son bot veut ignorer {membre}.",
    "{membre} existe, c’est une faute grave.",
    "{membre} croit encore que c’est le personnage principal, pauvre rêveur.",
    "{membre} a tenté de réfléchir... mais ça n’a pas duré longtemps.",
    "La connexion internet de {membre} est plus intelligente que lui/elle, ça fait peur.",
    "{membre} arrive à être cringe même en silence, un vrai talent.",
    "{membre} a ruiné 3 canaux en moins de 2 minutes avec ses idées.",
    "Clavier a dit à {membre} : 'calme-toi, s’il te plaît'.",
    "Imene a bloqué {membre} par réflexe dramatique.",
    "Mike refuse d’inclure {membre} dans son délire, c’est grave.",
    "Le pseudo de {membre} est un crime visuel.",
    "{membre} n’a jamais rien apporté de positif, c’est officiel.",
    "{membre} poste '😂😂' après une blague sur la mort, tact zéro.",
    "{membre} est un fantôme relou dans les salons.",
    "À chaque message de {membre}, l’ambiance chute de 20%.",
    "On a testé un bot IA pour remplacer {membre}... c’était mieux.",
    "On hésite à renommer {membre} en 'Erreur 404'.",
    "Le clavier de {membre} veut faire un burn-out.",
    "{membre} dit 'je suis chill' juste avant de créer une guerre civile.",
    "{membre} dit 'moi j’suis mature' toutes les 2 phrases, c’est faux.",
    "L’existence de {membre} est un spoiler gênant.",
    "{membre} demande 't’es qui toi ?' à chaque nouveau membre. Super accueil.",
    "{membre} mérite un mute... existentiel.",

    # Mike
    "{membre} pense être le personnage principal. Mike approuve pas.",
    "Même Mike a dit à {membre} de se calmer, trop de drama.",

    # Imene
    "Imene a désavoué {membre} pour excès de drama non validé.",
    "{membre} peut s’embrouiller avec un panneau de signalisation. Imene est fière.",

    # Clavier
    "Clavier veut porter plainte à cause de la voix de {membre}.",
    "{membre} fait des crises d’angoisse quand on hausse un sourcil, style Clavier.",

    # AD - le slibard
    "Même Le Slibard de AD demande une trêve olfactive pour {membre}.",
    "Atteinte à l’humanité : slip antique de {membre} en cause — signé AD.",

    # Pimprenelle - l'école gratuite
    "{membre} regrette d’être allé(e) à l’école... même gratuite.",
    "En Belgique, l’école est gratuite, mais {membre} fait payer tout le monde avec ses paroles.",

    # Mayer / Romy
    "Mayer a distribué plus de râteaux à {membre} qu’un jardinier sous acide.",
    "{membre} utilise ‘non’ comme ponctuation quand Romy parle.",

    # Célia
    "Même Célia a dit à {membre} : ‘j’suis pas si conne’, et tout le monde a ri... sauf elle.",
    "{membre} pense qu’un neurone, c’est un Pokémon rare."
]

@bot.command()
async def classementdesboulets(ctx):
    membres = [m for m in ctx.guild.members if not m.bot]

    if len(membres) < 5:
        await ctx.send("Pas assez de boulets sur ce serveur. Engagez-en plus.")
        return

    random.shuffle(membres)
    top_boulets = membres[:5]

    raisons_choisies = random.sample(raisons, 5)

    description = ""
    for i in range(5):
        membre = top_boulets[i]
        raison = raisons_choisies[i].format(membre=membre.mention)
        description += f"**#{i+1}** - {raison}\n"

    embed = discord.Embed(
        title="💩 Classement Officiel des Boulets Discord",
        description=description,
        color=discord.Color.dark_magenta()
    )
    embed.set_footer(text="Félicitations aux gagnants. Ou pas.")
    await ctx.send(embed=embed)

@bot.command()
async def boulet(ctx, membre: discord.Member):
    raison = random.choice(raisons).format(membre=membre.mention)
    await ctx.send(raison)



import os
bot.run(os.getenv("DISCORD_TOKEN"))

