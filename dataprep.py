import os
import tkinter as tk
from tkinter import ttk
from tkinter import Text, Scrollbar, Menu
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter import filedialog

global img_dir, file_version
img_dir = "./working_img/" # used for initial start up only.
file_version = "2023.08.21.D"

class Cell:
    def __init__(self, master, text):
        self.master = master
        self.text = text
        self.label = None

class ImageTextViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Text Viewer " + file_version)

        self.root.pack_propagate(False)

        self.top_frame = tk.Frame(root, relief="solid")
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)

        self.source_directory = img_dir

        if not os.path.exists(self.source_directory):
            self.source_directory = "./"

        self.image_files = []
        self.current_index = -1
        self.tag_counts = {}
        self.load_tags_from_files()

        if self.check_for_image_files(self.source_directory) <= 1:
            self.source_directory = "./"
            self.min_tag_count = 0
            self.max_tag_count = 1
        else:
            self.min_tag_count = min(self.tag_counts.values())
            self.max_tag_count = max(self.tag_counts.values())

        self.output_directory = self.source_directory

        self.slider = ttk.Scale(self.top_frame, from_=0, to=0, orient=tk.HORIZONTAL, length=400, command=self.slider_callback)
        self.slider.pack(fill=tk.X)

        self.help_button = tk.Button(self.top_frame, text="?", command=self.open_help_dialog)
        self.help_button.pack(side=tk.RIGHT)

        self.prev_button = tk.Button(self.top_frame, text="Previous", command=self.load_previous)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(self.top_frame, text="Next", command=self.load_next)
        self.next_button.pack(side=tk.LEFT)

        self.select_source_folder_button = tk.Button(self.top_frame, text="Select Source Folder", command=self.select_source_folder)
        self.select_source_folder_button.pack(side=tk.RIGHT)

        self.select_output_folder_button = tk.Button(self.top_frame, text="Select Output Folder", command=self.select_output_folder)
        self.select_output_folder_button.pack(side=tk.RIGHT)

        self.save_button = tk.Button(self.top_frame, text="Save TXT File", command=self.save_text)
        self.save_button.pack(side=tk.RIGHT)

        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, padx=0, pady=0)

        self.image_label = tk.Label(self.right_frame)
        self.image_label.pack()

        self.text_frame = tk.Frame(root, relief="solid")
        self.text_frame.pack(padx=0, pady=0, fill=tk.BOTH, expand=True)

        self.top_tag_frame = tk.Frame(self.text_frame)
        self.top_tag_frame.pack(side=tk.TOP, fill=tk.X)

        self.image_name_label = tk.Label(self.top_tag_frame, text="Files: ")
        self.image_name_label.pack(side=tk.TOP)

        self.tag_dropdown_frame = tk.Frame(self.top_tag_frame)
        self.tag_dropdown_frame.pack(side=tk.TOP, fill=tk.X)

        self.freq_tag_label = tk.Label(self.tag_dropdown_frame, text="Add Tags: ")
        self.freq_tag_label.grid(row=0, column=0)

        self.tag_var = tk.StringVar(self.tag_dropdown_frame)
        self.tag_dropdown = ttk.Combobox(self.tag_dropdown_frame, textvariable=self.tag_var)
        self.update_tag_dropdown()
        self.tag_dropdown.grid(row=0, column=1, sticky="ew")
        self.tag_dropdown_frame.columnconfigure(1, weight=1)

        self.add_tag_from_dropdown_button = tk.Button(self.tag_dropdown_frame, text="+", command=self.add_tag_from_dropdown)
        self.add_tag_from_dropdown_button.grid(row=0, column=2)

        self.sort_button = tk.Button(self.top_tag_frame, text="Sort Alphabetical", command=self.sort_cells)
        self.sort_button.pack(side=tk.LEFT)

        self.sort_by_frequency_button = tk.Button(self.top_tag_frame, text="Sort Frequency", command=self.sort_cells_by_frequency)
        self.sort_by_frequency_button.pack(side=tk.LEFT)

        self.bottom_tag_frame = tk.Frame(self.text_frame, relief="solid")
        self.bottom_tag_frame.pack(padx=0, pady=0, fill=tk.BOTH, expand=True)

        self.cells = []
        self.load_images()
        self.load_next()

    def add_tag_from_dropdown(self):
        selected_tag = self.tag_var.get()
        selected_tag = selected_tag.rsplit(" - ")[-1]

        selected_tags = selected_tag.split(',')
        for selected_tag in selected_tags:
            selected_tag = selected_tag.strip()
            if selected_tag and not self.tag_exists_in_cells(selected_tag):
                self.add_cell(selected_tag)

    def save_text(self):
        if self.image_files and 0 <= self.current_index < len(self.image_files):
            image_filename = self.image_files[self.current_index]
            txt_filename = os.path.splitext(image_filename)[0] + ".txt"

            image_path = os.path.join(self.source_directory, image_filename)
            txt_path = os.path.join(self.source_directory, txt_filename)

            new_image_path = os.path.join(self.output_directory, image_filename)
            new_txt_path = os.path.join(self.output_directory, txt_filename)

            tags = [cell.text for cell in self.cells]
            image_text = ", ".join(tags)

            with open(new_txt_path, 'w') as txt_file:
                txt_file.write(image_text)

            if not os.path.exists(new_image_path): #Checks to see if this file name exists.
                os.rename(image_path, new_image_path) #This will not overwrite an existing image

    def select_source_folder(self):
        selected_folder = filedialog.askdirectory()
        if selected_folder:
            self.source_directory = selected_folder
            self.load_images()
            self.current_index = -1
            self.load_next()

        self.image_files = []
        self.current_index = -1
        self.tag_counts = {}
        self.load_tags_from_files()

        if not self.check_for_image_files(self.source_directory):
            self.min_tag_count = 0
            self.max_tag_count = 1
        else:
            self.min_tag_count = min(self.tag_counts.values())
            self.max_tag_count = max(self.tag_counts.values())

        self.update_tag_dropdown()
        for cell in self.cells:
            cell.label.destroy()
        self.cells.clear()
        self.load_images()
        self.load_next()

        if self.output_directory != self.source_directory:
            self.select_output_folder_button.config(bg="green")
        else:
            self.select_output_folder_button.config(bg="SystemButtonFace")

    def select_output_folder(self):
        selected_output_folder = filedialog.askdirectory()
        if selected_output_folder:
            self.output_directory = selected_output_folder
        if self.output_directory != self.source_directory:
            self.select_output_folder_button.config(bg="green")
        else:
            self.select_output_folder_button.config(bg="SystemButtonFace")

    def load_images(self):
        self.image_files = [file for file in os.listdir(self.source_directory) if file.lower().endswith(('.jpg', '.png', '.jpeg', '.webp'))]
        self.slider.config(to=len(self.image_files) - 1)

    def check_for_image_files(self, directory):
        image_extensions = ('.jpg', '.png', '.jpeg', '.webp')
        files = os.listdir(directory)
        image_files = [file for file in files if file.lower().endswith(image_extensions)]
        return len(image_files)

    def load_next(self):
        if self.image_files:
            self.current_index = (self.current_index + 1) % len(self.image_files)
            self.load_image_and_text()
            self.load_cells()

    def load_previous(self):
        if self.image_files:
            self.current_index = (self.current_index - 1) % len(self.image_files)
            self.load_image_and_text()
            self.load_cells()

    def slider_callback(self, value):
        if self.image_files:
            new_index = int(round(float(value)))
            if new_index != self.current_index:
                self.current_index = new_index
                self.load_image_and_text()
                self.load_cells()

    def load_image_and_text(self):
        if self.image_files:
            image_filename = self.image_files[self.current_index]
            self.image_name_label.config(text="Image: " + image_filename)
            image_path = os.path.join(self.source_directory, image_filename)
            txt_filename = os.path.splitext(image_filename)[0] + ".txt"
            txt_path = os.path.join(self.source_directory, txt_filename)

            if os.path.exists(txt_path):
                with open(txt_path, 'r') as txt_file:
                    image_text = txt_file.read()
            else:
                image_text = "No text file exists for this image."

            image = Image.open(image_path)
            aspect_ratio = image.width / image.height
            new_width = 400
            new_height = int(new_width / aspect_ratio)
            image.thumbnail((new_width, new_height))

            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo

            self.slider.set(self.current_index)

        else:
            self.image_name_label.config(text="Image: ")
            self.image_label.config(image=None)
            self.slider.set(0)

    def show_popup(self, event, cell):
        popup_menu = Menu(self.bottom_tag_frame, tearoff=0)
        popup_menu.add_command(label="Delete", command=lambda: self.delete_cell(cell))
        popup_menu.add_separator()
        popup_menu.add_command(label="Move Up", command=lambda: self.move_cell_up(cell))
        popup_menu.add_command(label="Move Down", command=lambda: self.move_cell_down(cell))
        popup_menu.add_command(label="Move to Front", command=lambda: self.move_cell_to_front(cell))
        popup_menu.add_command(label="Move to Back", command=lambda: self.move_cell_to_back(cell))
        popup_menu.add_separator()
        popup_menu.add_command(label="Swap Spaces and Underscores", command=lambda: self.swap_spaces_underscores_all_cells())
        popup_menu.add_command(label="Change Case", command=lambda: self.change_case_all_cells(cell))
        popup_menu.tk_popup(event.x_root, event.y_root)

    def move_cell_up(self, cell):
        index = self.cells.index(cell)
        if index > 0:
            self.cells.pop(index)
            self.cells.insert(index - 1, cell)
            self.rearrange_cells()

    def move_cell_down(self, cell):
        index = self.cells.index(cell)
        if index < len(self.cells) - 1:
            self.cells.pop(index)
            self.cells.insert(index + 1, cell)
            self.rearrange_cells()

    def move_cell_to_front(self, cell):
        self.cells.remove(cell)
        self.cells.insert(0, cell)
        self.rearrange_cells()

    def move_cell_to_back(self, cell):
        self.cells.remove(cell)
        self.cells.append(cell)
        self.rearrange_cells()

    def swap_spaces_underscores_all_cells(self):
        replace = "False"
        for cell in self.cells:
            new_text = cell.text
            if replace == "False":
                if " " in cell.text:
                    replace = "space"
                elif "_" in cell.text:
                    replace = "underscores"
                else:
                    replace = "False"
            if replace != "False":
                if replace == "space":
                    new_text = cell.text.replace(' ', '_')
                else:
                    new_text = cell.text.replace('_', ' ')

            cell.text = new_text
            cell.label.config(text=new_text)

    def change_case_all_cells(self, cell):
        first_cell_text = self.cells[0].text
        if first_cell_text.islower():
            change_function = str.title
        else:
            change_function = str.lower

        for cell in self.cells:
            new_text = change_function(cell.text)
            cell.text = new_text
            cell.label.config(text=new_text)

    def sort_cells(self):
        self.cells.sort(key=lambda cell: cell.text.lower())
        self.rearrange_cells()

    def sort_cells_by_frequency(self):
        sorted_tags_by_frequency = sorted(self.tag_counts.keys(), key=lambda tag: self.tag_counts[tag], reverse=True)
        self.cells.sort(key=lambda cell: sorted_tags_by_frequency.index(cell.text))
        self.rearrange_cells()

    def add_cell(self, text):
        if not self.tag_exists_in_cells(text):
            new_cell = Cell(self.bottom_tag_frame, text)
            new_cell.label = tk.Label(new_cell.master, text=text, relief="solid", borderwidth=1)

            tag_frequency = self.tag_counts.get(text, 0)
            color = self.calculate_color(tag_frequency)

            new_cell.label.config(bg=color, fg="black")

            new_cell.label.grid(row=len(self.cells) // self.cols, column=len(self.cells) % self.cols, padx=2, pady=2)  # Adjust padding values here
            new_cell.label.bind("<Button-3>", lambda event, cell=new_cell: self.show_popup(event, cell))
            self.cells.append(new_cell)

    def tag_exists_in_cells(self, text):
        for cell in self.cells:
            if cell.text == text:
                return True
        return False

    def calculate_color(self, frequency):
        normalized_value = (frequency - self.min_tag_count) / (self.max_tag_count - self.min_tag_count)

        red = int(255 * (1 - normalized_value))
        green = int(200 * normalized_value)
        blue = 0

        if frequency <= 2:
            red = 255
            green = 255
            blue = 255

        red = max(0, min(255, red))
        green = max(0, min(255, green))

        color_code = "#{:02X}{:02X}{:02X}".format(red, green, blue)
        return color_code

    def delete_cell(self, cell):
        cell.label.destroy()
        self.cells.remove(cell)
        self.rearrange_cells()

    def rearrange_cells(self):
        for idx, cell in enumerate(self.cells):
            row = idx // self.cols
            col = idx % self.cols
            cell.label.grid(row=row, column=col, padx=1, pady=1)

    def load_cells(self):
        self.cols = 4
        for cell in self.cells:
            cell.label.destroy()
        self.cells.clear()

        if self.image_files:
            txt_filename = os.path.splitext(self.image_files[self.current_index])[0] + ".txt"
            txt_path = os.path.join(self.source_directory, txt_filename)

            if os.path.exists(txt_path):
                with open(txt_path, 'r') as txt_file:
                    lines = txt_file.readlines()
                    for line in lines:
                        line = line.strip()
                        if line:
                            items = line.split(',')
                            for item in items:
                                self.add_cell(item.strip())

    def load_tags_from_files(self):
        for txt_filename in os.listdir(self.source_directory):
            if txt_filename.lower().endswith('.txt'):
                txt_path = os.path.join(self.source_directory, txt_filename)
                with open(txt_path, 'r') as txt_file:
                    tags = txt_file.read().split(',')
                    for tag in tags:
                        clean_tag = tag.strip()
                        if clean_tag:
                            if clean_tag in self.tag_counts:
                                self.tag_counts[clean_tag] += 1
                            else:
                                self.tag_counts[clean_tag] = 1

    def update_tag_dropdown(self):
        sorted_tags = sorted(self.tag_counts.keys(), key=lambda tag: self.tag_counts[tag], reverse=True)
        tag_with_count = [f"{self.tag_counts[tag]} - {tag}" for tag in sorted_tags]
        self.tag_dropdown['values'] = tag_with_count

        self.tag_dropdown.bind("<Return>", lambda event: self.add_tag_from_dropdown())

    def open_help_dialog(self):
        help_image_path = "help.webp"
        if os.path.exists(help_image_path):
            help_image = Image.open(help_image_path)
            help_image.thumbnail((800, 600))  # Resize the image if needed
            help_image = ImageTk.PhotoImage(help_image)

            help_message = tk.Toplevel(self.root)
            help_message.title("Help")

            help_label = tk.Label(help_message, image=help_image)
            help_label.image = help_image
            help_label.pack()

            ok_button = tk.Button(help_message, text="OK", command=help_message.destroy)
            ok_button.pack()
        else:
            messagebox.showerror("Error", "Help image not found!")

        # Create a simple dialog with the example text
        tkinter.simpledialog.messagebox.showinfo("Help", example_text)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = ImageTextViewer(root)
    root.mainloop()
