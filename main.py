#!/usr/bin/env python3
import os
import shlex
import tkinter as tk
from tkinter import scrolledtext
import sys

VFS_NAME = "VFS"

class VFS:
    def __init__(self):
        self.fs = {'/': {}}
        self.current_path = '/'

    def _resolve(self, path):
        if not path.startswith('/'):
            path = self.current_path.rstrip('/') + '/' + path
        parts = [p for p in path.split('/') if p]
        node = self.fs['/']
        for p in parts:
            if p in node and isinstance(node[p], dict):
                node = node[p]
            else:
                return None
        return node

    def ls(self, path=None):
        path = path or self.current_path
        node = self._resolve(path)
        if node is None:
            return f"No such directory: {path}"
        return '  '.join(node.keys()) if node else "(empty)"

    def cd(self, path):
        node = self._resolve(path)
        if node is None:
            return f"No such directory: {path}"
        self.current_path = path if path.startswith('/') else self.current_path.rstrip('/') + '/' + path
        return None

    def mkdir(self, path):
        parts = [p for p in path.split('/') if p]
        node = self._resolve(self.current_path if not path.startswith('/') else '/')
        if node is None:
            return f"Cannot create directory: {path}"
        for p in parts:
            if p not in node:
                node[p] = {}
            node = node[p]
        return None

    def touch(self, path):
        parts = [p for p in path.split('/') if p]
        node = self._resolve(self.current_path if not path.startswith('/') else '/')
        if node is None:
            return f"Cannot create file: {path}"
        for p in parts[:-1]:
            if p not in node or not isinstance(node[p], dict):
                node[p] = {}
            node = node[p]
        node[parts[-1]] = ""
        return None

    def cat(self, path):
        node = self._resolve('/'.join(path.split('/')[:-1]) or self.current_path)
        if node is None or path.split('/')[-1] not in node:
            return f"No such file: {path}"
        content = node[path.split('/')[-1]]
        return content if isinstance(content, str) else "(directory)"

class ShellApp:
    def __init__(self, root):
        self.root = root
        root.title(f"{VFS_NAME} - Shell")
        self.vfs = VFS()
        self.build_ui()

    def build_ui(self):
        self.output = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=20, width=80)
        self.output.pack(padx=8, pady=8)
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(self.root, textvariable=self.input_var)
        self.input_entry.bind("<Return>", self.on_enter)
        self.input_entry.pack(fill=tk.X, padx=8, pady=(0,8))
        self.input_entry.focus()
        self.print_intro()

    def print_intro(self):
        self.write("Welcome to the VFS Shell prototype.\n")
        self.write("Supported commands: ls, cd, mkdir, touch, cat, exit\n")
        self.prompt()

    def prompt(self):
        self.write(f"{self.vfs.current_path}$ ")

    def write(self, text):
        self.output.insert(tk.END, text)
        self.output.see(tk.END)

    def on_enter(self, event):
        raw = self.input_var.get()
        self.input_var.set("")
        self.write(raw + "\n")

        try:
            expanded = os.path.expandvars(raw)
            parts = shlex.split(expanded) if expanded.strip() else []
        except Exception as e:
            self.write(f"Parse error: {e}\n")
            self.prompt()
            return

        if not parts:
            self.prompt()
            return

        cmd, *args = parts

        if cmd == "exit":
            self.write("Exiting...\n")
            self.root.quit()
            return

        elif cmd == "ls":
            result = self.vfs.ls(args[0] if args else None)
            self.write(result + "\n")

        elif cmd == "cd":
            result = self.vfs.cd(args[0]) if args else "Usage: cd <path>"
            if result:
                self.write(result + "\n")

        elif cmd == "mkdir":
            result = self.vfs.mkdir(args[0]) if args else "Usage: mkdir <dir>"
            if result:
                self.write(result + "\n")

        elif cmd == "touch":
            result = self.vfs.touch(args[0]) if args else "Usage: touch <file>"
            if result:
                self.write(result + "\n")

        elif cmd == "cat":
            result = self.vfs.cat(args[0]) if args else "Usage: cat <file>"
            self.write(result + "\n")

        else:
            self.write(f"Unknown command: {cmd}\n")

        self.prompt()

def main():
    root = tk.Tk()
    app = ShellApp(root)

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1]) as f:
            for line in f:
                line = line.strip()
                if line:
                    app.input_var.set(line)
                    app.on_enter(None)

    root.mainloop()

if __name__ == "__main__":
    main()
