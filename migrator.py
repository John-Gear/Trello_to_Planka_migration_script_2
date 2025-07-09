import requests
from tqdm import tqdm
import os
import unidecode
import urllib
import tempfile
import datetime

# Function: logging messages to a log file and output to the console and GUI
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "log.txt")
log_gui = None
def log_message(message):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(message + "\n")
    print(message)
    if log_gui is not None:
        try:
            log_gui(message)
        except:
            pass



# Functions for working with api Trello 

# Function: get a list of Trello workspaces
def get_workspaces():
    url = f"{TRELLO_URL}members/me/organizations"
    params = {"key": APIKEY, "token": APITOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function: get list of boards from Trello
def get_boards(workspace_id):
    url = f"{TRELLO_URL}organizations/{workspace_id}/boards"
    params = {"key": APIKEY, "token": APITOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function: retrieve list from Trello
def get_lists(board_id):
    url = f"{TRELLO_URL}boards/{board_id}/lists"
    params = {"key": APIKEY, "token": APITOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function: retrieve cards from Trello
def get_cards(list_id):
    url = f"{TRELLO_URL}lists/{list_id}/cards"
    params = {"key": APIKEY, "token": APITOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function: retrieves card comments from Trello
def get_card_comments(card_id):
    url = f"{TRELLO_URL}cards/{card_id}/actions"
    params = {"key": APIKEY, "token": APITOKEN, "filter": "commentCard", "limit": 50}

    all_comments = []
    while True:
        response = requests.get(url, params=params)
        response.raise_for_status()
        comments = response.json()

        if not comments:
            break

        all_comments.extend(comments)
        params["before"] = comments[-1]["id"]

    return all_comments

# Function: retrieves all checklists (task list) from a Trello card
def get_card_checklists(card_id):
    url = f"{TRELLO_URL}cards/{card_id}/checklists"
    params = {"key": APIKEY, "token": APITOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function: get attachments from cards from Trello
def get_card_attachments(card_id, APIKEY, APITOKEN):
    url = f"https://api.trello.com/1/cards/{card_id}/attachments"
    params = {
        "key": APIKEY,
        "token": APITOKEN
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function: gets the ID of an attachment that is a card cover in Trello to transfer it as a cover to a card in Planka
def get_card_cover_attachment_id(card_id):
    url = f"{TRELLO_URL}cards/{card_id}"
    params = {"key": APIKEY, "token": APITOKEN, "fields": "idAttachmentCover"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("idAttachmentCover")



# Functions for working with api Planka

# Function: authenticate and retrieve a Bearer token for Planka
def get_token():
    url = f"{PLANKA_URL}/access-tokens"
    payload = {"emailOrUsername": USERNAME, "password": PASSWORD}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        for key in ["token", "item", "id"]:
            if key in data:
                return data[key]
    except requests.RequestException as e:
        log_message(f"Error while retrieving token: {e}")
        return None
    return None

# Function: create a project in Planka based on Trello workspace
def create_planka_project(trello_ws, token):
    url = f"{PLANKA_URL}/projects"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    description = trello_ws.get("name", "")
    if not description.strip():
        description = None

    payload = {
        "type": "private",
        "name": trello_ws.get("displayName", "Unnamed Workspace")[:128],
        "description": description,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        project = response.json()["item"]
        log_message(f"Project '{payload['name']}' created successfully")
        return project
    except requests.RequestException as e:
        log_message(f"Error creating project '{payload['name']}': {e}")
        return None

# Function: create a board in Planka for the given project
def create_planka_board(project_id, project_name, board_data, token, position=65536):
    url = f"{PLANKA_URL}/projects/{project_id}/boards"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    name = board_data.get("name", "Unnamed Board")[:128]

    payload = {
        "name": name,
        "position": position,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        log_message(f"Board '{name}' created in project '{project_name}'")
        return response.json()["item"]
    except requests.HTTPError as e:
        log_message(f"Error creating board '{name}': {e}")
        log_message(f"Server response: {response.text}")
        return None

# Function: create a list in Planka for the given board
def create_planka_list(board_id, board_name, list_data, token, position=65536):
    url = f"{PLANKA_URL}/boards/{board_id}/lists"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    name = list_data.get("name", "Unnamed List")[:128]

    payload = {
        "type": "active",  # standard list: "active" (there are also "closed" lists)
        "name": name,
        "position": position,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        log_message(f"List '{name}' created in board '{board_name}'")
        return response.json()["item"]
    except requests.RequestException as e:
        log_message(f"Error creating list '{name}': {e}")
        log_message(f"Server response: {response.text}")
        return None

# Function: create a card in Planka under a specified list
def create_planka_card(list_id, list_name, card_data, token, position=65536):
    url = f"{PLANKA_URL}/lists/{list_id}/cards"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    name = card_data.get("name", "Unnamed Card")[:1024]
    description = card_data.get("desc", "")
    due_date = card_data.get("due")
    if not description.strip():
        description = None

    payload = {
        "type": "project",  # card types in Planka: project or history (Trello does not distinguish)
        "name": name,
        "description": description,
        "position": position,
    }

    if due_date:
        payload["dueDate"] = due_date
        log_message(f"Due date set for card '{name}': {due_date}")

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        log_message(f"Card '{name}' created in list '{list_name}'")
        return response.json()["item"]
    except requests.RequestException as e:
        log_message(f"Error creating card '{name}': {e}")
        log_message(f"Server response: {response.text}")
        return None

# Function: create a comment in a Planka card (with optional Trello metadata)
def create_planka_comment(card_id, comment_text, token, author_name=None, author_username=None, date=None):
    if author_name and author_username and date:
        try:
            formatted_date = datetime.datetime.fromisoformat(date.replace("Z", "")).strftime("%d-%m-%Y %H:%M:%S")
        except ValueError:
            formatted_date = date
        comment_text = f"""{comment_text}

---
*Imported comment from Trello, originally posted by*  
{author_name} ({author_username})  
{formatted_date}"""

    url = f"{PLANKA_URL}/cards/{card_id}/comments"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {
        "text": comment_text[:1048576],
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        log_message("Comment added")
        return response.json()["item"]
    except requests.RequestException as e:
        log_message(f"Error adding comment: {e}")
        log_message(f"Server response: {response.text}")
        return None

# Function: create a checklist in a Planka card
def create_planka_task_list(card_id, checklist_data, token, position=65536):
    url = f"{PLANKA_URL}/cards/{card_id}/task-lists"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    name = checklist_data.get("name", "Unnamed Checklist")[:128]

    payload = {
        "name": name,
        "position": position,
        "showOnFrontOfCard": False,  # or "True" for it visible on the card front
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        log_message(f"Checklist '{name}' created")
        return response.json()["item"]
    except requests.RequestException as e:
        log_message(f"Error creating checklist '{name}': {e}")
        log_message(f"Server response: {response.text}")
        return None

# Function: create a task in a checklist in Planka
def create_planka_task(task_list_id, item_data, token, position=65536):
    url = f"{PLANKA_URL}/task-lists/{task_list_id}/tasks"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    name = item_data.get("name", "Unnamed Task")[:1024]

    payload = {
        "name": name,
        "position": position,
        "isCompleted": item_data.get("state") == "complete",  # Trello: "complete" / "incomplete"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        log_message(f"Task '{name}' added to checklist")
        return response.json()["item"]
    except requests.RequestException as e:
        log_message(f"Error creating task '{name}': {e}")
        log_message(f"Server response: {response.text}")
        return None

# Function: create a label in Planka (if it does not exist)
def create_label(token, board_id, name, color, position):
    url = f"{PLANKA_URL}/boards/{board_id}/labels"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": name if name else None,
        "color": color,
        "position": position
    }
    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        item = response.json().get("item")
        log_message(f"Label '{name}' ({color}) created")
        return item
    else:
        log_message(f"Error creating label '{name}' ({color}): {response.status_code}")
        log_message(f"Server response: {response.text}")
    return None

# Function: bind an existing label to a card in Planka
def add_label_to_card(token, card_id, label_id, name, color):
    url = f"{PLANKA_URL}/cards/{card_id}/card-labels"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"labelId": label_id}
    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        log_message(f"Label '{name}' ({color}) added to the card")
        return True
    else:
        log_message(f"Error binding label {label_id} to the card")
        log_message(f"Server response: {response.text}")
    return False

# Function: creating card attachments in Planka
def add_attachment(token, card_id, file_path, original_date):
    url = f"{PLANKA_URL}/cards/{card_id}/attachments"
    headers = {"Authorization": f"Bearer {token}"}
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as file:
        files = {
            "file": (filename, file, "application/octet-stream")
        }
        data = {
            "type": "file",
            "name": filename
        }
        try:
            response = requests.post(url, headers=headers, data=data, files=files)
            response.raise_for_status()
            attachment = response.json()["item"]
            log_message(f"Attachment '{filename}' added to the card")
            return attachment
        except requests.RequestException as e:
            log_message(f"Error adding attachment '{filename}' to card {card_id}: {e}")
            return None

# Function: converts the file name to Latin if it contains non-Latin characters (file name transliteration)
def transliterate_filename(filename):
    base, ext = os.path.splitext(filename)
    transliterated = unidecode.unidecode(base)
    safe_name = transliterated.replace(" ", "_")
    return safe_name + ext

# Function: update or remove a card cover in Planka (if a cover was found in the original Trello card)
def update_card_cover(token, card_id, cover_attachment_id):
    url = f"{PLANKA_URL}/cards/{card_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "coverAttachmentId": cover_attachment_id if cover_attachment_id else None
    }

    try:
        response = requests.patch(url, json=payload, headers=headers)
        response.raise_for_status()
        log_message(f"A cover was found and set for the card")
    except requests.RequestException as e:
        log_message(f"Error setting cover for card {card_id}: {e}")

# Matching tags in Trello with tags in Planka
TRELLO_TO_PLANKA_COLORS = {
    "green": "tank-green",
    "yellow": "egg-yellow",
    "orange": "pumpkin-orange",
    "red": "berry-red",
    "purple": "midnight-blue",
    "blue": "lagoon-blue",
    "sky": "morning-sky",
    "pink": "pink-tulip",
    "black": "dark-granite",
    "lime": "bright-moss"
}

# The function matches the colour of a label in Planka to a label from Trello
def get_planka_label_color(trello_color):
    return TRELLO_TO_PLANKA_COLORS.get(trello_color, "desert-sand")  # fallback



# Migration functions

# Function: migrate labels from Trello to Planka while preserving their order
label_cache = {}  # Global cache to avoid creating duplicate labels
def migrate_card_labels(token, board_id, card_id_planka, card_trello):
    global label_cache

    labels = card_trello.get("labels", [])
    if not labels:
        return

    log_message(f"Migrating labels for card '{card_trello['name']}'")

    for idx, label in enumerate(labels):
        trello_color = label.get("color", "gray")
        label_name = label.get("name", "").strip()
        planka_color = get_planka_label_color(trello_color)
        position = (idx + 1) * 65536

        label_key = f"{board_id}_{label_name}_{planka_color}"
        if label_key in label_cache:
            label_id = label_cache[label_key]
        else:
            new_label = create_label(token, board_id, label_name, planka_color, position)
            if not new_label:
                log_message(f"Failed to create label '{label_name}' ({planka_color})")
                continue
            label_id = new_label["id"]
            label_cache[label_key] = label_id

        add_label_to_card(token, card_id_planka, label_id, label_name, planka_color)

# Function: transfers attachments from Trello to Planka, preserving the cover if applicable
def migrate_attachments(token, card_id_planka, card_id_trello):
    attachments = get_card_attachments(card_id_trello, APIKEY, APITOKEN)
    cover_attachment_id = get_card_cover_attachment_id(card_id_trello)

    planka_attachments = {}

    for attachment in attachments:
        attachment_id = attachment["id"]

        raw_file_name = attachment.get("name") or urllib.parse.unquote(attachment.get("fileName", "attachment"))
        MAX_FILENAME_LENGTH = 200
        if len(raw_file_name) > MAX_FILENAME_LENGTH:
            raw_file_name = raw_file_name[:MAX_FILENAME_LENGTH] + "..."
        file_name_translit = transliterate_filename(raw_file_name)
        # Remove invalid filename characters for Windows
        invalid_chars = r'<>:"/\|?*'
        for ch in invalid_chars:
            file_name_translit = file_name_translit.replace(ch, "_")

        file_path = os.path.join(tempfile.gettempdir(), file_name_translit)
        if len(file_path) > 255:
            log_message(f"Skipped file '{raw_file_name}' — path length too long")
            continue

        download_url = f"https://api.trello.com/1/cards/{card_id_trello}/attachments/{attachment_id}/download/{urllib.parse.quote(raw_file_name)}"
        headers = {"Authorization": f'OAuth oauth_consumer_key="{APIKEY}", oauth_token="{APITOKEN}"'}

        try:
            with requests.get(download_url, headers=headers, stream=True) as r:
                r.raise_for_status()
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except requests.exceptions.RequestException:
            log_message(f"Failed to download file '{raw_file_name}'")
            continue

        try:
            planka_attachment = add_attachment(token, card_id_planka, file_path, None)
            if planka_attachment is not None:
                planka_attachments[attachment_id] = planka_attachment["id"]
            else:
                log_message(f"Failed to upload attachment '{raw_file_name}' to card")
                continue
        except requests.exceptions.RequestException:
            log_message(f"Failed to upload attachment '{raw_file_name}' to card")
            continue

        os.remove(file_path)

    cover_planka_id = planka_attachments.get(cover_attachment_id)
    if cover_planka_id:
        update_card_cover(token, card_id_planka, cover_planka_id)
    else:
        log_message(f"Cover not set: no corresponding attachment found")

# Function: Main migration from Trello to Planka
def migrate_workspaces():
    open(LOG_FILE, "w", encoding="utf-8").close()
    log_message("Starting migration Trello → Planka")

    trello_workspaces = get_workspaces()
    log_message(f"Retrieved workspaces: {len(trello_workspaces)}")

    token = get_token()
    if token:
        log_message("Bearer token successfully obtained")
    else:
        log_message("Failed to obtain token")
        return

    for ws in trello_workspaces:
        log_message(f"\nMigrating workspace: {ws.get('displayName')}")
        project = create_planka_project(ws, token)
        if not project:
            log_message(f"Failed to create project for workspace: {ws.get('displayName')}")
            continue

        boards = get_boards(ws["id"])
        log_message(f"Boards found: {len(boards)}")

        for idx, board in enumerate(boards):
            position = (idx + 1) * 65536
            planka_board = create_planka_board(project["id"], ws["displayName"], board, token, position)
            if not planka_board:
                log_message(f"Skipped board: {board.get('name')}")
                continue

            trello_lists = get_lists(board["id"])
            log_message(f"Lists found in board '{board.get('name')}': {len(trello_lists)}")

            for i, trello_list in enumerate(trello_lists):
                list_position = (i + 1) * 65536
                planka_list = create_planka_list(planka_board["id"], board["name"], trello_list, token, list_position)
                if not planka_list:
                    log_message(f"Skipped list: {trello_list.get('name')}")
                    continue

                trello_cards = get_cards(trello_list["id"])
                log_message(f"Cards found in list '{trello_list.get('name')}': {len(trello_cards)}")

                for j, trello_card in enumerate(trello_cards):
                    card_position = (j + 1) * 65536
                    planka_card = create_planka_card(planka_list["id"], trello_list["name"], trello_card, token, card_position)
                    if not planka_card:
                        log_message(f"Skipped card: {trello_card.get('name')}")
                        continue

                    migrate_attachments(token, planka_card["id"], trello_card["id"])
                    migrate_card_labels(token, planka_board["id"], planka_card["id"], trello_card)

                    checklists = get_card_checklists(trello_card["id"])
                    if checklists:
                        log_message(f"Checklists found in card '{trello_card.get('name')}': {len(checklists)}")
                        for k, checklist in enumerate(checklists):
                            checklist_position = (k + 1) * 65536
                            planka_task_list = create_planka_task_list(planka_card["id"], checklist, token, checklist_position)
                            if not planka_task_list:
                                log_message(f"Failed to create checklist: {checklist.get('name')}")
                                continue

                            for m, item in enumerate(checklist.get("checkItems", [])):
                                task_position = (m + 1) * 65536
                                create_planka_task(planka_task_list["id"], item, token, task_position)
                            
                    comments = get_card_comments(trello_card["id"])
                    for comment in reversed(comments):
                        data = comment.get("data", {})
                        text = data.get("text")
                        author = comment.get("memberCreator", {})
                        if text:
                            create_planka_comment(
                                planka_card["id"],
                                text,
                                token,
                                author_name=author.get("fullName"),
                                author_username=author.get("username"),
                                date=comment.get("date")
                            )

    log_message("\nMigration completed")