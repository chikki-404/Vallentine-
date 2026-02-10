# -*- coding: utf-8 -*-
import telebot
import json
import os
from flask import Flask, request
import random
import string
import time
import threading

users = {}
active_process = {}
proposals = {}
# ================= CONFIG =================
BOT_TOKEN = "8329370399:AAEpImVot04S4OofAYzximVEcEAkPWJ_7ws"
WEBHOOK_URL = f"https://vallentine.onrender.com/8329370399:AAEpImVot04S4OofAYzximVEcEAkPWJ_7ws"
ADMIN_IDS = [6606949931,7636298287,7800914151,1241797478,7828872301]  # YOUR TELEGRAM USER ID
DATA_FILE = "data.json"

bot = telebot.TeleBot(8329370399:AAEpImVot04S4OofAYzximVEcEAkPWJ_7ws, parse_mode="Markdown")
app = Flask(__name__)

@app.route(f"/8329370399:AAEpImVot04S4OofAYzximVEcEAkPWJ_7ws", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=https://vallentine.onrender.com/8329370399:AAEpImVot04S4OofAYzximVEcEAkPWJ_7ws)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
# ================= DATABASE =================
def load():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(db, f, indent=2)

db = load()

def user(uid, name):
    uid = str(uid)
    if uid not in db:
        db[uid] = {
            "name": name,
            "code": None,
            "partner": None,
            "points": 0,
            "history": [],
            "married": False,
            "parent": False,
            "busy": None,
            "busy_until": 0
        }
        save()
    return db[uid]

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# ================= UTIL =================
def now():
    return int(time.time())

def is_busy(u):
    return u["busy"] and now() < u["busy_until"]

def clear_busy(uid):
    db[uid]["busy"] = None
    db[uid]["busy_until"] = 0

# ================= START =================
@bot.message_handler(commands=["start"])
def start_cmd(message):
    uid = message.from_user.id
    name = message.from_user.first_name

    if uid not in users:
        users[uid] = {
            "name": name,
            "partner": None,
            "points": 0,
            "married": False,
            "parent": False,
            "history": []
        }
        text = (
            f"ðŸ’– Welcome {name}!\n\n"
            "This is the *Valentine Love Game* ðŸ’•\n"
            "Find a partner, earn love points, get married,\n"
            "and maybeâ€¦ become parents ðŸ˜\n\n"
            "Start by using /propose ðŸ’Œ"
        )
    else:
        text = (
            f"ðŸ’ Welcome back {name}!\n"
            "Your love journey continues ðŸ’•"
        )

    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    
@bot.message_handler(commands=["propose"])
def propose_cmd(message):
    uid = message.from_user.id
    name = message.from_user.first_name

    # safety: user must exist
    if uid not in users:
        users[uid] = {
            "name": name,
            "partner": None,
            "points": 0,
            "married": False,
            "parent": False,
            "history": []
        }

    # already in relationship
    if users[uid]["partner"] is not None:
        bot.reply_to(message, "âŒ You already have a partner.")
        return

    # already generated a code
    if uid in proposals.values():
        bot.reply_to(message, "âŒ You already generated a love code.\nWait until someone accepts or you break up.")
        return

    # generate unique 5-char code
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if code not in proposals:
            break

    proposals[code] = uid

    bot.reply_to(
        message,
        f"ðŸ’Œ *Love Proposal Created!*\n\n"
        f"ðŸ” Your Love Code: `{code}`\n\n"
        "Ask your partner to accept it using:\n"
        "`/accept CODE`\n\n"
        "â¤ï¸ Only one person can accept this code.",
        parse_mode="Markdown"
    )
    
@bot.message_handler(commands=["accept"])
def accept_cmd(message):
    uid = message.from_user.id
    name = message.from_user.first_name
    parts = message.text.split()

    # validate format
    if len(parts) != 2:
        bot.reply_to(message, " Usage: /accept CODE")
        return

    code = parts[1].upper()

    # safety init
    if uid not in users:
        users[uid] = {
            "name": name,
            "partner": None,
            "points": 0,
            "married": False,
            "parent": False,
            "history": []
        }

    # already in relationship
    if users[uid]["partner"] is not None:
        bot.reply_to(message, " You already have a partner.")
        return

    # invalid code
    if code not in proposals:
        bot.reply_to(message, " Invalid or expired love code.")
        return

    proposer_id = proposals[code]

    # cannot accept own code
    if proposer_id == uid:
        bot.reply_to(message, " You cannot accept your own love code.")
        return

    # proposer safety check
    if proposer_id not in users:
        bot.reply_to(message, " Proposal owner not found.")
        return

    # proposer already partnered (edge case)
    if users[proposer_id]["partner"] is not None:
        del proposals[code]
        bot.reply_to(message, " This proposal is no longer valid.")
        return

    # bind partners
    users[uid]["partner"] = proposer_id
    users[proposer_id]["partner"] = uid

    # history log
    users[uid]["history"].append(
        f" Partnered with {users[proposer_id]['name']} (ID {proposer_id})"
    )
    users[proposer_id]["history"].append(
        f" Partnered with {users[uid]['name']} (ID {uid})"
    )

    # remove proposal
    del proposals[code]

    bot.send_message(
        message.chat.id,
        f" *It’s a Match!*\n\n"
        f" {users[proposer_id]['name']}  {users[uid]['name']}\n\n"
        "You are now partners!\n"
        "Start earning love points ",
        parse_mode="Markdown"
    )
    
@bot.message_handler(commands=["lovestatus"])
def lovestatus_cmd(message):
    uid = message.from_user.id
    name = message.from_user.first_name

    # safety init
    if uid not in users:
        users[uid] = {
            "name": name,
            "partner": None,
            "points": 0,
            "married": False,
            "parent": False,
            "history": []
        }

    user = users[uid]

    # stage detection
    if user["parent"]:
        stage = " Parent"
    elif user["married"]:
        stage = " Married"
    elif user["partner"]:
        stage = " In Relationship"
    else:
        stage = " Single"

    # partner info
    if user["partner"]:
        pid = user["partner"]
        pname = users.get(pid, {}).get("name", "Unknown")
        partner_info = f"{pname} (ID: {pid})"
    else:
        partner_info = "None"

    text = (
        f" *Love Status*\n\n"
        f" Name: {user['name']}\n"
        f" ID: {uid}\n"
        f" Stage: {stage}\n"
        f" Partner: {partner_info}\n"
        f" Love Points: {user['points']}\n"
        f" Past Relationships: {len(user['history'])}"
    )

    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    
@bot.message_handler(commands=["mylove"])
def mylove_cmd(message):
    uid = message.from_user.id
    name = message.from_user.first_name

    # safety init
    if uid not in users:
        users[uid] = {
            "name": name,
            "partner": None,
            "points": 0,
            "married": False,
            "parent": False,
            "history": []
        }

    history = users[uid]["history"]

    if not history:
        bot.reply_to(
            message,
            " *Love History*\n\nYou don’t have any past relationships yet.",
            parse_mode="Markdown"
        )
        return

    text = " *Your Love History*\n\n"
    for i, entry in enumerate(history, start=1):
        text += f"{i}. {entry}\n"

    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    
@bot.message_handler(commands=["partner"])
def partner_cmd(message):
    uid = message.from_user.id
    name = message.from_user.first_name

    # safety init
    if uid not in users:
        users[uid] = {
            "name": name,
            "partner": None,
            "points": 0,
            "married": False,
            "parent": False,
            "history": []
        }

    user = users[uid]

    if not user["partner"]:
        bot.reply_to(message, " You currently have no partner.")
        return

    pid = user["partner"]
    partner = users.get(pid)

    if not partner:
        bot.reply_to(message, " Partner data not found.")
        return

    text = (
        f" *Current Partner*\n\n"
        f" Name: {partner['name']}\n"
        f" ID: {pid}\n"
        f" Love Points: {partner['points']}"
    )

    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    
def add_points(user_id, partner_id, points, bot):
    """Add points to both partners, auto-parent at 1500, stop scoring after parent"""
    for uid in [user_id, partner_id]:
        # If already parent, skip scoring
        if users[uid]["parent"]:
            continue
        users[uid]["points"] += points
        # Auto-parent logic
        if users[uid]["points"] >= 1500:
            users[uid]["parent"] = True
            bot.send_message(
                uid,
                " Congratulations! You have reached 1500 points and are now a Parent! \n"
                "You can now use /punish commands on others."
            )
            
@bot.message_handler(commands=["kiss"])
def kiss(message):
    uid = message.from_user.id
    if uid not in users or not users[uid]["partner"]:
        bot.reply_to(message, " You have no partner.")
        return

    pid = users[uid]["partner"]

    # check if anyone is in active process
    if uid in active_process or pid in active_process:
        bot.reply_to(message, " Someone is already in a process.")
        return

    duration = random.randint(180, 300)  # 3–5 minutes
    end_time = time.time() + duration

    active_process[uid] = {"type": "kiss", "partner": pid, "end_time": end_time}
    active_process[pid] = {"type": "kiss", "partner": uid, "end_time": end_time}

    bot.reply_to(message, " Kiss started! Stay connected for 3–5 minutes.\nUse /cancel to stop.")

    def finish():
        time.sleep(duration)
        if uid in active_process:
            points = random.randint(10, 20)
            add_points(uid, pid, points, bot)
            del active_process[uid]
            del active_process[pid]
            bot.send_message(uid, f" Kiss completed! +{points} points")
            bot.send_message(pid, f" Kiss completed! +{points} points")

    threading.Thread(target=finish).start()
    
@bot.message_handler(commands=["holdhand"])
def holdhand(message):
    uid = message.from_user.id
    if uid not in users or not users[uid]["partner"]:
        bot.reply_to(message, " You have no partner.")
        return

    pid = users[uid]["partner"]

    if uid in active_process or pid in active_process:
        bot.reply_to(message, " Someone is already in a process.")
        return

    duration = random.randint(60, 180)  # 1–3 minutes
    end_time = time.time() + duration

    active_process[uid] = {"type": "holdhand", "partner": pid, "end_time": end_time}
    active_process[pid] = {"type": "holdhand", "partner": uid, "end_time": end_time}

    bot.reply_to(message, " Holding hands! Stay connected.\nUse /cancel to stop.")

    def finish():
        time.sleep(duration)
        if uid in active_process:
            points = random.randint(5, 10)
            add_points(uid, pid, points, bot)
            del active_process[uid]
            del active_process[pid]
            bot.send_message(uid, f" Hold hands done! +{points} points")
            bot.send_message(pid, f" Hold hands done! +{points} points")

    threading.Thread(target=finish).start()
    
@bot.message_handler(commands=["hug"])
def hug(message):
    uid = message.from_user.id
    if uid not in users or not users[uid]["partner"]:
        bot.reply_to(message, " You have no partner.")
        return

    pid = users[uid]["partner"]

    if uid in active_process or pid in active_process:
        bot.reply_to(message, " Someone is already in a process.")
        return

    duration = random.randint(300, 600)  # 5–10 minutes
    end_time = time.time() + duration

    active_process[uid] = {"type": "hug", "partner": pid, "end_time": end_time}
    active_process[pid] = {"type": "hug", "partner": uid, "end_time": end_time}

    bot.reply_to(message, " Hug started! Stay connected.\nUse /cancel to stop.")

    def finish():
        time.sleep(duration)
        if uid in active_process:
            points = random.randint(20, 40)
            add_points(uid, pid, points, bot)
            del active_process[uid]
            del active_process[pid]
            bot.send_message(uid, f" Hug completed! +{points} points")
            bot.send_message(pid, f" Hug completed! +{points} points")

    threading.Thread(target=finish).start()
    
@bot.message_handler(commands=["cancel"])
def cancel(message):
    uid = message.from_user.id
    if uid not in active_process:
        bot.reply_to(message, " No active process to cancel.")
        return

    pid = active_process[uid]["partner"]
    del active_process[uid]
    if pid in active_process:
        del active_process[pid]

    bot.reply_to(message, " Process cancelled. No points awarded.")
    
@bot.message_handler(commands=["punish_kiss"])
def punish_kiss(message):
    uid = message.from_user.id
    if uid not in users or not users[uid].get("parent", False):
        bot.reply_to(message, " Only parents can use this command.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, " Reply to the user you want to punish.")
        return

    target = message.reply_to_message.from_user.id
    if target not in active_process or active_process[target]["type"] != "kiss":
        bot.reply_to(message, " Target is not kissing.")
        return

    loss = random.randint(5, 10)
    users[target]["points"] -= loss
    users[uid]["points"] += loss

    bot.reply_to(message, f" Kiss punished!\nTarget lost {loss} points\nYou gained {loss} points")
    
@bot.message_handler(commands=["punish_holdhand"])
def punish_holdhand(message):
    uid = message.from_user.id
    if uid not in users or not users[uid].get("parent", False):
        bot.reply_to(message, " Only parents can use this command.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, " Reply to the user you want to punish.")
        return

    target = message.reply_to_message.from_user.id
    if target not in active_process or active_process[target]["type"] != "holdhand":
        bot.reply_to(message, " Target is not holding hands.")
        return

    loss = random.randint(1, 5)
    users[target]["points"] -= loss
    users[uid]["points"] += loss

    bot.reply_to(message, f" Hold hand punished!\nTarget lost {loss} points\nYou gained {loss} points")
    
@bot.message_handler(commands=["punish_hug"])
def punish_hug(message):
    uid = message.from_user.id
    if uid not in users or not users[uid].get("parent", False):
        bot.reply_to(message, " Only parents can use this command.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, " Reply to the user you want to punish.")
        return

    target = message.reply_to_message.from_user.id
    if target not in active_process or active_process[target]["type"] != "hug":
        bot.reply_to(message, " Target is not hugging.")
        return

    loss = random.randint(10, 20)
    users[target]["points"] -= loss
    users[uid]["points"] += loss

    bot.reply_to(message, f" Hug punished!\nTarget lost {loss} points\nYou gained {loss} points")
    
@bot.message_handler(commands=["marry"])
def marry_cmd(message):
    uid = message.from_user.id
    user = users.get(uid)

    if not user or not user["partner"]:
        bot.reply_to(message, " You have no partner to marry.")
        return

    pid = user["partner"]
    partner = users.get(pid)

    if user["married"] or partner["married"]:
        bot.reply_to(message, " You are already married.")
        return

    # check points requirement
    if user["points"] < 1000 or partner["points"] < 1000:
        bot.reply_to(message, " Both partners must have at least 1000 points to marry.")
        return

    # set married status
    user["married"] = True
    partner["married"] = True

    # optional: flag for double points in process logic
    user["marry_bonus"] = True
    partner["marry_bonus"] = True

    # update history
    user["history"].append(f" Married to {partner['name']} (ID {pid})")
    partner["history"].append(f" Married to {user['name']} (ID {uid})")

    bot.send_message(
        message.chat.id,
        f" Congratulations! You and {partner['name']} are now married! \n"
        " Both partners now earn double points and cooldowns are halved!"
    )
    
@bot.message_handler(commands=["breakup"])
def breakup_cmd(message):
    uid = message.from_user.id
    user = users.get(uid)

    if not user or not user["partner"]:
        bot.reply_to(message, " You have no partner to break up with.")
        return

    if user.get("married", False):
        bot.reply_to(message, " You cannot break up after marriage!")
        return

    pid = user["partner"]
    partner = users.get(pid)

    # remove partner bindings
    user["partner"] = None
    partner["partner"] = None

    # update history
    user["history"].append(f" Broke up with {partner['name']} (ID {pid})")
    partner["history"].append(f" Broke up with {user['name']} (ID {uid})")

    bot.send_message(
        message.chat.id,
        f" You and {partner['name']} are no longer together.\n"
        "You can now generate a new /propose code to find another partner."
    )
    
@bot.message_handler(commands=["global"])
def global_cmd(message):
    if not users:
        bot.reply_to(message, " No users found yet.")
        return

    # sort users by points descending
    top_users = sorted(users.items(), key=lambda x: x[1]["points"], reverse=True)[:10]

    text = " *Global Top 10 Love Points*\n\n"
    for i, (uid, data) in enumerate(top_users, start=1):
        text += f"{i}. {data['name']} (ID: {uid}) — {data['points']} points\n"

    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    
@bot.message_handler(commands=["cheat"])
def cheat_cmd(message):
    uid = message.from_user.id

    if uid not in admins:
        bot.reply_to(message, " Only admins can use /cheat.")
        return

    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, " Usage: /cheat USERID POINTS")
        return

    target_id = int(parts[1])
    points = int(parts[2])

    if target_id not in users:
        bot.reply_to(message, " Target user not found.")
        return

    users[target_id]["points"] += points
    bot.reply_to(message, f" Added {points} points to {users[target_id]['name']} (ID: {target_id})")
    
@bot.message_handler(commands=["reset"])
def reset_cmd(message):
    uid = message.from_user.id
    if uid not in admins:
        bot.reply_to(message, " Only admins can use /reset.")
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, " Usage: /reset USERID or /reset all")
        return

    target = parts[1].lower()

    if target == "all":
        users.clear()
        proposals.clear()
        bot.reply_to(message, " All user data has been reset. The game is fresh now!")
        return

    try:
        target_id = int(target)
    except:
        bot.reply_to(message, " Invalid USERID.")
        return

    if target_id not in users:
        bot.reply_to(message, " Target user not found.")
        return

    # Remove partner binding if exists
    partner_id = users[target_id].get("partner")
    if partner_id and partner_id in users:
        users[partner_id]["partner"] = None

    # Remove proposals by this user
    to_delete = [code for code, pid in proposals.items() if pid == target_id]
    for code in to_delete:
        del proposals[code]

    # Reset user data
    users[target_id] = {
        "name": users[target_id]["name"],
        "partner": None,
        "points": 0,
        "married": False,
        "parent": False,
        "history": []
    }

    bot.reply_to(message, f" User {target_id} data has been reset.")
    




