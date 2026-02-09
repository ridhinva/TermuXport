#!/usr/bin/env python3
import os, subprocess, sys, getpass, shutil
from pathlib import Path
from tqdm import tqdm

# ---------------- CONFIG ----------------
CONF = Path(__file__).parent / "termuxport.conf"
DEFAULT_DEST = Path.home() / "TermuXport" / "export"
ENABLE_NOTIFY = True
CREATOR = "RIDHIN V"
VERSION = "v4.4"

if CONF.exists():
    with open(CONF) as f:
        for line in f:
            if "DEFAULT_DEST=" in line: DEFAULT_DEST = Path(line.strip().split("=")[1].strip('"'))
            if "ENABLE_NOTIFY=" in line: ENABLE_NOTIFY = line.strip().split("=")[1].strip() == "1"
            if "CREATOR=" in line: CREATOR = line.strip().split("=")[1].strip('"')
            if "VERSION=" in line: VERSION = line.strip().split("=")[1].strip('"')

# ---------------- PATHS ----------------
TMP = Path.home() / "TermuXport" / "tmp"
TMP.mkdir(parents=True, exist_ok=True)
DEFAULT_DEST.mkdir(parents=True, exist_ok=True)
UNDO = DEFAULT_DEST / ".undo_list"
LOG = DEFAULT_DEST / "termuxport.log"

# ---------------- COLORS ----------------
BLUE = "\033[94m"
GREEN = "\033[92m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
CYAN = "\033[96m"
RESET = "\033[0m"

# ---------------- BANNER ----------------
def banner():
    print(f"""
████████╗███████╗██████╗ ███╗   ███╗██╗   ██╗██╗  ██╗██████╗
╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║   ██║╚██╗██╔╝██╔══██╗
   ██║   █████╗  ██████╔╝██╔████╔██║██║   ██║ ╚███╔╝ ██████╔╝
   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║   ██║ ██╔██╗ ██╔═══╝
   ██║   ███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██╔╝ ██╗██║
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝
TermuXport {VERSION} – Created by {CREATOR}
""")

# ---------------- UTILITIES ----------------
def get_items(current_path):
    dirs, files = [], []
    for f in sorted(os.listdir(current_path)):
        if f.startswith('.'):
            continue
        full_path = current_path / f
        if full_path.is_dir():
            dirs.append(full_path)
        else:
            files.append(full_path)
    return dirs, files

def display_items(dirs, files):
    print("\nCurrent folder:")
    for idx, d in enumerate(dirs, 1):
        print(f"{BLUE}[DIR] {idx}. {d.name}{RESET}")
    offset = len(dirs)
    for idx, f in enumerate(files, 1):
        color = WHITE
        if f.suffix in [".py", ".sh"]:
            color = GREEN
        elif f.suffix in [".jpg",".png",".mp4",".mp3"]:
            color = MAGENTA
        print(f"{color}[FILE] {idx+offset}. {f.name}{RESET}")
    print(f"{CYAN}[..] 0. Go up / exit{RESET}")
    return dirs, files

def choose_files(current_path):
    selected = []
    while True:
        dirs, files = get_items(current_path)
        dirs, files = display_items(dirs, files)
        choice = input("Select numbers (space-separated) to copy, or 0 to go up: ").split()
        if "0" in choice:
            if current_path.parent != current_path:
                current_path = current_path.parent
            else:
                break
        else:
            all_items = dirs + files
            for c in choice:
                try:
                    idx = int(c)-1
                    selected.append(all_items[idx])
                except:
                    continue
            break
    return selected

# ---------------- COPY WITH PROGRESS ----------------
def get_total_size(items):
    total = 0
    for item in items:
        if item.is_file():
            total += item.stat().st_size
        elif item.is_dir():
            for root, dirs, files in os.walk(item):
                for f in files:
                    total += (Path(root)/f).stat().st_size
    return total

def copy_with_progress(items, dest):
    total_bytes = get_total_size(items)
    copied_bytes = 0

    with open(UNDO, 'w') as undo_file:
        with tqdm(total=total_bytes, unit='B', unit_scale=True, desc="Total Progress") as pbar:
            for item in items:
                if item.is_file():
                    shutil.copy2(item, dest / item.name)
                    undo_file.write(f"{dest}/{item.name}\n")
                    pbar.update(item.stat().st_size)
                    with open(LOG,'a') as log_file:
                        log_file.write(f"{item} COPIED\n")
                elif item.is_dir():
                    for root, dirs, files in os.walk(item):
                        rel_root = Path(root).relative_to(item.parent)
                        dest_root = dest / rel_root
                        dest_root.mkdir(parents=True, exist_ok=True)
                        for f in files:
                            src_file = Path(root)/f
                            dst_file = dest_root/f
                            shutil.copy2(src_file, dst_file)
                            undo_file.write(str(dst_file)+"\n")
                            pbar.update(src_file.stat().st_size)
                            with open(LOG,'a') as log_file:
                                log_file.write(f"{src_file} COPIED\n")
    if ENABLE_NOTIFY:
        subprocess.run(["termux-notification","--title","TermuXport v4.4","--content","Copy Completed"])

# ---------------- ENCRYPT ----------------
def encrypt_and_copy(items, dest):
    passw = getpass.getpass("Set encryption password: ")
    tarfile = TMP / "export.tar.gz"
    encfile = dest / f"export_{int(os.times()[4])}.tar.gz.enc"
    subprocess.run(["tar","cz"] + [str(i) for i in items] + ["-f", str(tarfile)])
    subprocess.run(["openssl","enc","-aes-256-cbc","-salt","-pbkdf2",
                    "-pass",f"pass:{passw}","-in",str(tarfile),"-out",str(encfile)])
    with open(LOG,'a') as log_file:
        log_file.write(f"{encfile} ENCRYPTED\n")
    with open(UNDO,'w') as undo_file:
        undo_file.write(str(encfile)+"\n")
    if ENABLE_NOTIFY:
        subprocess.run(["termux-notification","--title","TermuXport v4.4",
                        "--content","Encrypted Copy Completed"])

# ---------------- OTHER UTILITIES ----------------
def undo_last():
    if not UNDO.exists():
        print("Nothing to undo")
        return
    with open(UNDO) as f:
        for line in f:
            path = line.strip()
            if os.path.exists(path):
                subprocess.run(["rm","-rf",path])
    with open(LOG,'a') as log_file:
        log_file.write("UNDO executed\n")
    print("Undo completed")

def dry_run(items, dest):
    print("Dry Run: Showing what would be copied")
    for item in items:
        print(f"{item} -> {dest}")

def filter_exclude(items):
    exts = input("Enter extensions to exclude (space-separated, e.g., mp4 jpg): ").split()
    filtered = [i for i in items if not any(i.name.endswith(f".{e}") for e in exts)]
    return filtered

# ---------------- MENU ----------------
def menu():
    banner()
    dest_input = input(f"Destination folder [{DEFAULT_DEST}]: ").strip()
    dest = Path(dest_input) if dest_input else DEFAULT_DEST
    dest.mkdir(parents=True, exist_ok=True)

    print("\nMain menu:")
    print("[1] Copy all files/folders")
    print("[2] Select files/folders (multi-level)")
    print("[3] Encrypt & export")
    print("[4] Dry run / preview")
    print("[5] Exclude file types")
    print("[6] Undo last export")
    print("[0] Exit")
    choice = input("Choose: ").strip()
    
    cwd = Path('.')
    items = get_items(cwd)[0] + get_items(cwd)[1]  # flat list for copy all

    if choice=="1":
        copy_with_progress(items,dest)
    elif choice=="2":
        selected = choose_files(cwd)
        if selected:
            copy_with_progress(selected,dest)
    elif choice=="3":
        encrypt_and_copy(items,dest)
    elif choice=="4":
        dry_run(items,dest)
    elif choice=="5":
        filtered = filter_exclude(items)
        copy_with_progress(filtered,dest)
    elif choice=="6":
        undo_last()
    elif choice=="0":
        sys.exit()
    else:
        print("Invalid choice")

if __name__=="__main__":
    menu()
