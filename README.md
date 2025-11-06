# Trello to Planka Migration Script v2

## Description
This script is designed to transfer data from Trello to Planka v2.x. It automatically migrates workspaces, boards, lists, cards, comments, attachments, labels, and card covers from Trello to Planka v2.x while preserving structure and important information.
- **Important: If you are using **Planka v1.x**, see another repository: https://github.com/John-Gear/Trello_to_Planka_migration_script/tree/main**
- **If you are using **Planka v2.x**, this script is for you**

---

## Features

- Migration of Trello workspaces as Planka projects
- Migration of boards and lists
- Migration of cards while preserving order and due dates
- Migration of checklists and tasks
- Migration of labels and card covers
- Migration of attachments
- Migration of comments (preserving author's name, username, and date)
- Logging of all actions (`log.txt`)
- Simple GUI interface

---

## Program Interface
Below is an example of the application interface where you can enter data for migration:

![Interface Example](https://github.com/John-Gear/Trello_to_Planka_migration_script_2/blob/main/window.png)

---

# How to use (2 options):

## 1. The easiest way – download the ready-to-use program

1. Go to Release and download the .exe file (for Windows): [Release v1.0](https://github.com/John-Gear/Trello_to_Planka_migration_script_2/releases/tag/v1.0)
2. Launch the program by double-clicking it
3. Enter:
- Planka URL (e.g., https://example.com, without the /api suffix)
- Your Planka username and password
- Trello API Key and Token (how to obtain — see below)
4. Click Start Migration
5. After completion, click Save Log to save the report

---

## Getting Trello API Key and Token
1. Go to [Trello Power-Ups](https://trello.com/power-ups/admin).
2. Click "Power-Ups" → "Create New".
3. Enter organization information.
4. Click "Create" and save it.
5. Copy the API-Key from the Power-Up you have created.
6. Open this URL to optain your Token (You have to login into the desired Trello Account): https://trello.com/1/authorize?expiration=never&name=PlankaMigrator&scope=read,write&response_type=token&key=YOUR_API_KEY
7. Copy the generated Token that will be shown after successfull Login.
---

## 2. Build the GUI yourself (for advanced users, Mac/Linux users, or if you don’t trust third-party .exe files)

1. Download the project:
```bash
git clone https://github.com/John-Gear/Trello_to_Planka_migration_script_2.0.git
```
2. Go to the folder and create a virtual environment:
```bash
python -m venv venv
```
3. Activate the environment:
```bash
- Windows: venv\Scripts\activate
- Mac/Linux: source venv/bin/activate
```
4. Install dependencies:
```bash
pip install -r requirements.txt
```
5. Build the .exe:
```bash
pyinstaller --onefile --noconsole migrator_gui.py
```
6. The created .exe file will appear in the /dist folder

---

## Possible issues and errors
- **Upload error in Planka `413 Client Error: Request Entity Too Large`**  
  Example solution: if your Planka is installed on `nginx` – increase `client_max_body_size` in the `nginx` config.
- **Trello board backgrounds are not transferred to Planka**  
  In Planka, background is set on the project, not the board.
- **Images in comments may not be displayed**  
  Images are transferred as attachments, but Planka does not support inserting images into comment text.
- **Link-attachments are not transferred**  
  Trello allows attaching links as attachments, but Planka does not support this.
- **Copied cards may lose comments**  
  This is a Trello bug: when copying a card, comments are not duplicated.
- **File not found when uploading attachment**  
  Example solution: make sure you use the GUI on Windows and have access to the TEMP folder.

---

## Not implemented
- **Member migration:**
  this feature was intentionally excluded.
  Trello is a centralized service with global accounts, users create their own logins and passwords.
  In Planka (self-hosted), each user is created manually and has no global account.
  Automatic member migration is not possible without access to the local database and generating email/login and password for each user server-side.
- **Migration of archived items (cards, boards):**  
  not implemented because it is not considered useful — the script focuses on active boards and tasks.

---

## License
  This project is distributed under the **MIT** license (if you plan to use the script for commercial purposes and adapt it for yourself, comply with the license terms and add a link to the author.)

---

## Contact the author and customization for your needs
  If you need to customize the migration for your needs — contact the author.

---

## If you found my project useful, you can support me financially — even a small donation matters
- **Crypto donation: USDT (TRC20):** `TCECqH8ZxXGCQuWZeto1nV9nawbeeV4fG8`
- **Crypto donation: Bitcoin (BTC):** `bc1q3lvprzayxd3qulk0epk5dh58zx36mfev76wj30`
- **Crypto donation: Ethereum (ETH):** `0x80DbC00Fd91bAb3D4FE6E6441Dae0719e6bF5c9e`
- **International card (Visa/Mastercard):**  
[https://www.donationalerts.com/r/johngear](https://www.donationalerts.com/r/johngear)

---

### If you have questions or issues – create an issue in the repository!
