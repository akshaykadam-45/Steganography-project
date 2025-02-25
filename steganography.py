import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np

def select_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png")])
    entry_path.delete(0, tk.END)
    entry_path.insert(0, file_path)

def message_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

def binary_to_message(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join(chr(int(char, 2)) for char in chars if int(char, 2) != 0)

def encrypt():
    img_path = entry_path.get()
    msg = entry_msg.get()
    password = entry_pass.get()
    
    if not img_path or not msg or not password:
        messagebox.showerror("Error", "All fields are required for encryption!")
        return
    
    img = cv2.imread(img_path)
    binary_msg = message_to_binary(msg) + '1111111111111110'  # Add delimiter to mark end
    data_index = 0
    data_len = len(binary_msg)
    
    for row in img:
        for pixel in row:
            for color in range(3):
                if data_index < data_len:
                    pixel[color] = (pixel[color] & 254) | int(binary_msg[data_index])
                    data_index += 1
                else:
                    break
    
    encrypted_path = "encryptedImage.png"
    cv2.imwrite(encrypted_path, img)
    with open("password.txt", "w") as f:
        f.write(password)
    
    messagebox.showinfo("Success", "Message encrypted and saved as encryptedImage.png")
    os.system("start " + encrypted_path)

def decrypt():
    try:
        with open("password.txt", "r") as f:
            stored_password = f.read().strip()
    except FileNotFoundError:
        messagebox.showerror("Error", "No password file found! Encryption might not have been performed.")
        return
    
    entered_pass = entry_pass.get()
    if stored_password != entered_pass:
        messagebox.showerror("Error", "Incorrect password!")
        return
    
    img = cv2.imread(entry_path.get())
    binary_msg = []
    
    for row in img:
        for pixel in row:
            for color in range(3):
                binary_msg.append(str(pixel[color] & 1))
                if ''.join(binary_msg[-16:]) == '1111111111111110':  # Stop if delimiter found
                    break
    
    message = binary_to_message(''.join(binary_msg).split('1111111111111110')[0])
    messagebox.showinfo("Decryption", f"Decrypted Message: {message}")

def select_mode():
    mode = mode_var.get()
    if mode == "Encrypt":
        label_msg.pack()
        entry_msg.pack()
        btn_encrypt.pack(pady=5)
        btn_decrypt.pack_forget()
    else:
        label_msg.pack_forget()
        entry_msg.pack_forget()
        btn_encrypt.pack_forget()
        btn_decrypt.pack(pady=5)

# GUI Setup
root = tk.Tk()
root.title("Steganography GUI")
root.geometry("400x300")

mode_var = tk.StringVar(value="Encrypt")
tk.Label(root, text="Select Mode:").pack()
tk.Radiobutton(root, text="Encrypt", variable=mode_var, value="Encrypt", command=select_mode).pack()
tk.Radiobutton(root, text="Decrypt", variable=mode_var, value="Decrypt", command=select_mode).pack()

tk.Label(root, text="Select Image:").pack()
entry_path = tk.Entry(root, width=40)
entry_path.pack()
tk.Button(root, text="Browse", command=select_image).pack()

label_msg = tk.Label(root, text="Enter Message:")
entry_msg = tk.Entry(root, width=40)

label_pass = tk.Label(root, text="Enter Password:")
label_pass.pack()
entry_pass = tk.Entry(root, width=40, show="*")
entry_pass.pack()

btn_encrypt = tk.Button(root, text="Encrypt", command=encrypt)
btn_decrypt = tk.Button(root, text="Decrypt", command=decrypt)

select_mode()
root.mainloop()
