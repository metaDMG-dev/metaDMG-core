import customtkinter


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("400x240")
app.grid_columnconfigure((0, 1), weight=1)


def hide_show_passwd():
    if hide_show_switch.get() == 0:
        passwd_entry.configure(show="")
    else:
        passwd_entry.configure(show="•")


passwd_entry = customtkinter.CTkEntry(app, placeholder_text="Password")
passwd_entry.grid(row=0, column=0, pady=20, padx=0)

hide_show_switch = customtkinter.CTkSwitch(app, text="Hide", command=hide_show_passwd)
hide_show_switch.grid(row=0, column=1, pady=20, padx=0)
# hide_show_switch.select()

app.mainloop()
