# 🐍 TermuXport v4.4

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://www.python.org/)  
[![Termux](https://img.shields.io/badge/Termux-Compatible-brightgreen?logo=termux)](https://termux.com/)  
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ⚡ Features

- ✅ Copy all files and folders **recursively** from any directory  
- ✅ **Multi-level navigation** for selecting files/folders  
- ✅ **Color-coded file types** (directories, scripts, media, others)  
- ✅ **Total and per-file progress bars** for large copies  
- ✅ AES-256 **encryption support** for exported files  
- ✅ **Undo last export**  
- ✅ Dry-run mode to preview copy operations  
- ✅ Exclude file types dynamically  
- ✅ **Notifications** on copy completion (optional, requires Termux API)  
- ✅ Fully **Termux-safe paths** (`~/TermuXport` by default)  

---

## 📦 Installation

1. Install Python 3 in Termux:

```bash
pkg update
pkg install python git
```

Optional (for notifications):

```bash
pkg install termux-api
```

2. Clone the repository:

```bash
git clone https://github.com/ridhinva/TermuXport.git
cd TermuXport
```

3. Make the script executable:

```bash
chmod +x termuxport.py
```

4. Add it to PATH:

```bash
mv termuxport.py $PREFIX/bin/termuxport
```

Or create a symlink:

```bash
ln -s ~/TermuXport/termuxport.py $PREFIX/bin/termuxport
chmod +x ~/TermuXport/termuxport.py
```

---

## 🚀 Usage

### Interactive Mode

```bash
termuxport
```

- Browse directories, select files/folders, copy with progress bars.

### Command-Line Mode

```bash
termuxport /source/path /destination/path
```

- Recursively copy all files/folders with a single command.
- Example:

```bash
termuxport ~/ /sdcard/termux_backup
```

---

### Quick Alias (Optional)

```bash
echo 'alias tport="termuxport ~/ /sdcard/termux_backup"' >> ~/.zshrc
source ~/.zshrc
```

Now just run:

```bash
tport
```

---

## 🖼 Screenshots

**Multi-Level Navigation**

```
Current folder: /home/user/TermuXport
[DIR] 1. plugins/
[DIR] 2. tmp/
[FILE] 3. termuxport.py
[FILE] 4. termuxport.conf
[..] 0. Go up
Select numbers to copy:
```

**Progress Bars**

```
Total Progress: 45%|███████▍         | 4.12k/9.14k [00:01<00:01, 2.1kB/s]
```

---

## ⚡ Notes

- Fully compatible with Termux  
- Supports copying large folders safely  
- Encryption uses `openssl` AES-256-CBC  
- Notifications require **Termux API**  

---

## 📝 License

MIT License © RIDHIN V A
