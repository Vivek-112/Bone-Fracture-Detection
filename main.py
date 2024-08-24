import customtkinter as ctk
import tkinter.messagebox as mb
import json
import os
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from keras import Sequential
from tensorflow.keras.layers import *
from tensorflow.keras.models import *
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.utils import load_img, img_to_array

uploaded_files = []

USER_DATA_FILE = 'user_data.json'
STORAGE_DIR = "storage"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    try:
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}

def save_user_data(user_data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_data, file)

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("User Authentication System")
        self.geometry("300x500")

        self.frame_login = ctk.CTkFrame(self)
        self.frame_login.pack(pady=20, padx=20, fill="both", expand=True)

        lbl_login_title = ctk.CTkLabel(self.frame_login, text="Login", font=("Arial", 20))
        lbl_login_title.pack(pady=12)

        self.entry_login_username = ctk.CTkEntry(self.frame_login, placeholder_text="Username")
        self.entry_login_username.pack(pady=12)

        self.entry_login_password = ctk.CTkEntry(self.frame_login, placeholder_text="Password", show="*")
        self.entry_login_password.pack(pady=12)

        btn_login = ctk.CTkButton(self.frame_login, text="Login", command=self.login)
        btn_login.pack(pady=12)

        self.lbl_login_message = ctk.CTkLabel(self.frame_login, text="")
        self.lbl_login_message.pack()

        lbl_signup_redirect = ctk.CTkLabel(self.frame_login, text="Don't have an account?")
        lbl_signup_redirect.pack(pady=12)

        btn_signup_redirect = ctk.CTkButton(self.frame_login, text="Signup", command=self.show_signup_page)
        btn_signup_redirect.pack()

        self.frame_signup = ctk.CTkFrame(self)

        lbl_signup_title = ctk.CTkLabel(self.frame_signup, text="Signup", font=("Arial", 20))
        lbl_signup_title.pack(pady=12)

        self.entry_signup_username = ctk.CTkEntry(self.frame_signup, placeholder_text="Username")
        self.entry_signup_username.pack(pady=12)

        self.entry_signup_password = ctk.CTkEntry(self.frame_signup, placeholder_text="Password", show="*")
        self.entry_signup_password.pack(pady=12)

        btn_signup = ctk.CTkButton(self.frame_signup, text="Signup", command=self.signup)
        btn_signup.pack(pady=12)

        self.lbl_signup_message = ctk.CTkLabel(self.frame_signup, text="")
        self.lbl_signup_message.pack()

        lbl_login_redirect = ctk.CTkLabel(self.frame_signup, text="Already have an account?")
        lbl_login_redirect.pack(pady=12)

        btn_login_redirect = ctk.CTkButton(self.frame_signup, text="Login", command=self.show_login_page)
        btn_login_redirect.pack()

        self.exit_btn = ctk.CTkButton(self, text="Exit", command=self.exit_app, width=150, fg_color="#A23E2A")  # Dark red
        self.exit_btn.pack(pady=10, side='bottom')

        self.frame_signup.pack_forget()

    def signup(self):
        username = self.entry_signup_username.get()
        password = self.entry_signup_password.get()

        if username and password:
            user_data = load_user_data()

            if username in user_data:
                self.lbl_signup_message.configure(text="Username already exists!", text_color="red")
            else:
                user_data[username] = password
                save_user_data(user_data)
                self.lbl_signup_message.configure(text="Signup successful!", text_color="green")
        else:
            self.lbl_signup_message.configure(text="Please fill out all fields.", text_color="red")

    def login(self):
        username = self.entry_login_username.get()
        password = self.entry_login_password.get()

        if username and password:
            user_data = load_user_data()

            if username in user_data and user_data[username] == password:
                self.lbl_login_message.configure(text="Login successful!", text_color="green")
                self.destroy()
                MergedApp().mainloop()  
            else:
                self.lbl_login_message.configure(text="Invalid username or password.", text_color="red")
        else:
            self.lbl_login_message.configure(text="Please fill out all fields.", text_color="red")

    def show_signup_page(self):
        self.frame_login.pack_forget()
        self.frame_signup.pack()

    def show_login_page(self):
        self.frame_signup.pack_forget()
        self.frame_login.pack()

    def exit_app(self):
        self.destroy()

class MergedApp(TkinterDnD.Tk):  
    def __init__(self):
        super().__init__()
        self.geometry("700x700")
        self.title("File Upload with Drag-and-Drop")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue") 

        self.configure(bg="black")

        self.drop_frame = ctk.CTkFrame(self, fg_color="gray20", bg_color="black", width=600, height=400, corner_radius=10)
        self.drop_frame.pack(pady=20)

        self.drop_label = ctk.CTkLabel(self.drop_frame, text="Drag and drop files here", font=("Arial", 16), width=400, height=100, fg_color="gray30", corner_radius=10, bg_color="black")
        self.drop_label.pack(pady=20)

        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.drop)

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent", bg_color="black")
        self.button_frame.pack(pady=20)

        self.upload_new_btn = ctk.CTkButton(self.button_frame, text="Upload File", command=self.open_file_dialog, width=150)
        self.upload_new_btn.pack()

        self.exit_btn = ctk.CTkButton(self, text="Exit", command=self.exit_app, width=150, fg_color="#A23E2A")  # Dark red
        self.exit_btn.pack(pady=10, side='bottom')

    def drop(self, event):
        file_paths = self.split_paths(event.data)
        for file_path in file_paths:
            self.upload_file(file_path)

    def split_paths(self, paths):
        return self.tk.splitlist(paths)

    def upload_file(self, file_path):
        global uploaded_files
        if os.path.isfile(file_path):
            file_name = os.path.basename(file_path)
            destination = os.path.join(STORAGE_DIR, file_name)
            shutil.copy(file_path, destination)
            uploaded_files.append(destination) 
            mb.showinfo(f"File '{file_name}' uploaded.")

    def open_file_dialog(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.upload_file(file_path)

    def exit_app(self):
        self.destroy()

app = LoginApp()
app.mainloop()

def print_uploaded_files():
    global uploaded_files
    for file in uploaded_files:
        print(file)

print_uploaded_files()


Data_path_1='E:\Bone Fracture Dataset\Data\Data_1'
Data_path_2='E:\Bone Fracture Dataset\Data\Data_2'

Data_1_datagen = image.ImageDataGenerator(rotation_range=15,shear_range=0.2,
                                          zoom_range=0.2,horizontal_flip=True,
                                          fill_mode='nearest',width_shift_range=0.1,
                                          height_shift_range=0.1)

Data_2_datagen= image.ImageDataGenerator(rotation_range=15,shear_range=0.2,
                                         zoom_range=0.2,horizontal_flip=True,
                                         fill_mode='nearest',width_shift_range=0.1,
                                         height_shift_range=0.1)

Data_1_generator = Data_1_datagen.flow_from_directory(Data_path_1,target_size = (224,224),
                                                      batch_size = 4,class_mode = 'binary')

Data_2_generator = Data_1_datagen.flow_from_directory(Data_path_2,target_size = (224,224),
                                                      batch_size = 4,shuffle=True,class_mode = 'binary')

base_model = tf.keras.applications.EfficientNetB3(weights='imagenet', input_shape=(224,224,3), include_top=False)

input_tensor = Input(shape=(224, 224, 3))
base_model = EfficientNetB3(weights='imagenet', include_top=False, input_tensor=input_tensor)
for layer in base_model.layers:
    layer.trainable = False

x = base_model.output
x = GaussianNoise(0.25)(x)
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu')(x)
x = BatchNormalization()(x)
x = GaussianNoise(0.25)(x)
x = Dropout(0.25)(x)
output = Dense(1, activation='sigmoid')(x)
model = Model(inputs=base_model.input, outputs=output)
model.summary()

model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy','Precision','Recall','AUC'])

lrp = ReduceLROnPlateau(monitor="val_loss", factor=0.1, patience=2)
filepath = 'best_model.keras'
checkpoint = ModelCheckpoint(filepath, monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')
call = [checkpoint, lrp]

history = model.fit(
    Data_1_generator,
    epochs=10,
    validation_data=Data_2_generator,
    steps_per_epoch=50,
    callbacks=call
)

for file_path in uploaded_files:
    img_4 = load_img(file_path)
    imag_4 = img_to_array(img_4)
    imaga_4 = np.expand_dims(imag_4, axis=0)
    ypred_4 = model.predict(imaga_4)
    print(ypred_4)
    a_4 = ypred_4[0]
    if a_4<0.5:
        op="Fracture"
    else:
        op="Normal"
    plt.imshow(img_4)
    message = "THE UPLOADED X-RAY IMAGE IS: " + str(op)
    mb.showinfo("X-Ray Image Result", message)
