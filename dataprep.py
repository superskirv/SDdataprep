import os
import tkinter as tk
from tkinter import ttk, Canvas, Text, Scrollbar, Menu, messagebox, filedialog
from PIL import Image, ImageTk

global img_dir, file_version
img_dir = "./working_dir/" # used for initial start up only.
file_version = "2023.08.27.B"

class Cell:
    def __init__(self, master, text):
        self.master = master
        self.text = text
        self.label = None
        self.selected = False

class ImageTextViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("SD Data Prep " + file_version)

        self.options = {
            "clean_tags": True,
            "tag_columns": 4,
            "style": "Black"
        }
        self.set_current_style()
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
        self.current_selected_cell = None

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

        self.toggle_style_button = tk.Button(self.top_frame, text="*", command=self.toggle_style)
        self.toggle_style_button.pack(side=tk.RIGHT)

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

        self.bottom_tag_canvas = Canvas(self.bottom_tag_frame)
        self.bottom_tag_scrollbar = Scrollbar(self.bottom_tag_frame, orient="vertical", command=self.bottom_tag_canvas.yview)
        self.bottom_tag_canvas.configure(yscrollcommand=self.bottom_tag_scrollbar.set)

        self.bottom_tag_canvas.pack(side="left", fill="both", expand=True)
        self.bottom_tag_scrollbar.pack(side="right", fill="y")

        self.tag_frame = tk.Frame(self.bottom_tag_canvas)
        self.tag_frame.pack(fill="both", expand=True)

        self.bottom_tag_canvas.create_window((0, 0), window=self.tag_frame, anchor="nw")
        self.tag_frame.bind("<Configure>", self.on_tag_frame_configure)

        self.cells = []
        self.apply_style()
        self.load_images()
        self.load_next()

    def on_tag_frame_configure(self, event):
        self.bottom_tag_canvas.configure(scrollregion=self.bottom_tag_canvas.bbox("all"))

    def handle_left_click(self, event, cell):
        if event.state & 0x4:  # Check if Ctrl is held
            if cell.selected:
                cell.label.config(relief="solid", borderwidth=1, bg=self.calculate_color(self.tag_counts[cell.text]))
                cell.selected = False
            else:
                cell.label.config(relief="solid", borderwidth=2, bg="yellow")
                cell.selected = True
            self.current_selected_cell = cell  # Update the current_selected_cell attribute
            self.update_selected_tags()
        else:
            self.select_cell(cell)

    def handle_right_click(self, event, cell):
        self.show_popup(event, cell)

    def select_cell(self, cell):
        if not cell.selected:
            for other_cell in self.cells:
                if other_cell.selected:
                    other_cell.label.config(relief="solid", borderwidth=1, bg=self.calculate_color(self.tag_counts[other_cell.text]))
                    other_cell.selected = False
            cell.label.config(relief="solid", borderwidth=2, bg="yellow")
            cell.selected = True
            self.current_selected_cell = cell  # Update the current_selected_cell attribute
        else:
            cell.label.config(relief="solid", borderwidth=1, bg=self.calculate_color(self.tag_counts[cell.text]))
            cell.selected = False
        # Construct the selected cells text from all selected cells
        self.update_selected_tags()

    def update_selected_tags(self):
        selected_cells = [selected_cell.text for selected_cell in self.cells if selected_cell.selected]
        selected_cells_text = ", ".join(selected_cells)
        self.tag_var.set(selected_cells_text)

    def add_tag_from_dropdown(self):
        tag_text = self.tag_var.get()
        tag_text = tag_text.rsplit(" - ")[-1]

        tags = tag_text.split(',')
        for tag in tags:
            tag = tag.strip()
            if tag and not self.tag_exists_in_cells(tag):
                self.add_cell(tag)

                # Update tag_counts dictionary
                if tag in self.tag_counts:
                    self.tag_counts[tag] += 1
                else:
                    self.tag_counts[tag] = 1

        self.tag_var.set("")
        self.update_tag_dropdown()

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

            if image_path != new_image_path:
                with open(image_path, 'rb') as src_image_file:
                    with open(new_image_path, 'wb') as dest_image_file:
                        dest_image_file.write(src_image_file.read())
        self.reload_tags_from_files()

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
        self.set_output_dir_color()

    def set_output_dir_color(self):
        if self.output_directory != self.source_directory:
            self.select_output_folder_button.config(fg="red")
        else:
            self.select_output_folder_button.config(fg=self.style["fg_color"])

    def select_output_folder(self):
        selected_output_folder = filedialog.askdirectory()
        if selected_output_folder:
            self.output_directory = selected_output_folder
        self.set_output_dir_color()

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
        self.reload_tags_from_files()

    def load_previous(self):
        if self.image_files:
            self.current_index = (self.current_index - 1) % len(self.image_files)
            self.load_image_and_text()
            self.load_cells()
        self.reload_tags_from_files()

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
        self.current_selected_cell = cell
        popup_menu = Menu(self.bottom_tag_frame, tearoff=0)
        popup_menu.add_command(label="Delete", command=lambda: self.delete_cell(cell))
        popup_menu.add_command(label="Delete All", command=lambda: self.delete_cell_all(cell))
        popup_menu.add_separator()
        popup_menu.add_command(label="Move Up", command=lambda: self.move_cell_up(cell))
        popup_menu.add_command(label="Move Down", command=lambda: self.move_cell_down(cell))
        popup_menu.add_command(label="Move to Front", command=lambda: self.move_cell_to_front(cell))
        popup_menu.add_command(label="Move to Back", command=lambda: self.move_cell_to_back(cell))
        popup_menu.add_separator()
        popup_menu.add_command(label="Swap Spaces and Underscores", command=lambda: self.swap_spaces_underscores_selected_cells())
        popup_menu.add_command(label="Change Case", command=lambda: self.change_case_selected_cells())
        popup_menu.add_command(label="Split Words into New Tags", command=lambda: self.split_tags_into_new_tags())

        popup_menu.tk_popup(event.x_root, event.y_root)

    def move_cell_up(self, this_cell):
        selected_cells = [cell for cell in self.cells if cell.selected]
        last = 0
        if selected_cells:
            for cell in selected_cells:
                index = self.cells.index(cell)
                last = index
                if index > 0 and last+1 < index:
                    self.cells.pop(index)
                    self.cells.insert(index - 1, cell)
        else:
            index = self.cells.index(this_cell)
            if index > 0:
                index = self.cells.index(this_cell)
                self.cells.pop(index)
                self.cells.insert(index - 1, this_cell)
        self.rearrange_cells()

    def move_cell_down(self, this_cell):
        selected_cells = [cell for cell in self.cells if cell.selected]
        if selected_cells:
            for cell in selected_cells:
                index = self.cells.index(cell)
                if index < len(self.cells) - 1:
                    self.cells.pop(index)
                    self.cells.insert(index + len(selected_cells), cell)
        else:
            index = self.cells.index(this_cell)
            if index < len(self.cells) - 1:
                index = self.cells.index(this_cell)
                self.cells.pop(index)
                self.cells.insert(index + 1, this_cell)
        self.rearrange_cells()

    def move_cell_to_front(self, this_cell):
        selected_cells = [cell for cell in self.cells if cell.selected]
        mov_cnt = 0
        if selected_cells:
            for cell in selected_cells:
                self.cells.remove(cell)
                self.cells.insert(mov_cnt, cell)
                mov_cnt += 1
        else:
            self.cells.remove(this_cell)
            self.cells.insert(0, this_cell)
        self.rearrange_cells()

    def move_cell_to_back(self, this_cell):
        selected_cells = [cell for cell in self.cells if cell.selected]
        if selected_cells:
            for cell in selected_cells:
                self.cells.remove(cell)
                self.cells.append(cell)
        else:
            self.cells.remove(this_cell)
            self.cells.append(this_cell)
        self.rearrange_cells()

    def swap_spaces_underscores_selected_cells(self):
        selected_cells = [cell for cell in self.cells if cell.selected]
        if not selected_cells:
            selected_cells = [self.current_selected_cell]

        replace = "False"
        if "_" in selected_cells[0].text:
            replace = "space"
        elif " " in selected_cells[0].text:
            replace = "underscores"
        else:
            replace = "False"

        for cell in selected_cells:
            new_text = cell.text
            if replace == "space":
                new_text = cell.text.replace('_', ' ')
            elif replace == "underscores":
                new_text = cell.text.replace(' ', '_')
            else:
                new_text = new_text

            if cell.text in self.tag_counts:
                self.tag_counts[cell.text] -= 1

            cell.text = new_text
            cell.label.config(text=new_text)

            if new_text in self.tag_counts:
                self.tag_counts[new_text] += 1
            else:
                self.tag_counts[new_text] = 1

        self.update_selected_tags()

    def change_case_selected_cells(self):
        selected_cells = [cell for cell in self.cells if cell.selected]
        if not selected_cells:
            selected_cells = [self.current_selected_cell]

        first_cell_text = selected_cells[0].text
        if first_cell_text.islower():
            change_function = str.title
        else:
            change_function = str.lower

        for cell in selected_cells:
            new_text = change_function(cell.text)
            if cell.text in self.tag_counts:
                self.tag_counts[cell.text] -= 1  # Decrement count for the old text
            cell.text = new_text
            cell.label.config(text=new_text)
            if new_text in self.tag_counts:
                self.tag_counts[new_text] += 1  # Increment count for the new text
            else:
                self.tag_counts[new_text] = 1
        self.update_selected_tags()

    def split_tags_into_new_tags(self):
        selected_cells = [cell for cell in self.cells if cell.selected]
        if not selected_cells:
            selected_cells = [self.current_selected_cell]

        for cell in selected_cells:
            words = cell.text.split()  # Split text into words
            if cell.text in self.tag_counts:
                self.tag_counts[cell.text] -= 1
            for word in words:
                cleaned_word = self.clean_tag(word)
                if cleaned_word in self.tag_counts:
                    self.tag_counts[cleaned_word] += 1
                else:
                    self.tag_counts[cleaned_word] = 1
                self.add_cell(cleaned_word)
            self.delete_cell(cell)  # Delete the original cell after splitting words
        self.reload_tags_from_files()
        self.update_selected_tags()
        self.rearrange_cells()

    def sort_cells(self):
        self.cells.sort(key=lambda cell: cell.text.lower())
        self.rearrange_cells()

    def sort_cells_by_frequency(self):
        sorted_tags_by_frequency = sorted(self.tag_counts.keys(), key=lambda tag: self.tag_counts[tag], reverse=True)
        self.cells.sort(key=lambda cell: sorted_tags_by_frequency.index(cell.text))
        self.rearrange_cells()

    def add_cell(self, text):
        if not self.tag_exists_in_cells(text):
            new_cell = Cell(self.tag_frame, text)
            new_cell.label = tk.Label(new_cell.master, text=text, relief="solid", borderwidth=1)

            if text in self.tag_counts:
                self.tag_counts[text] += 1
            else:
                self.tag_counts[text] = 1

            tag_frequency = self.tag_counts[text]
            color = self.calculate_color(tag_frequency)
            new_cell.label.config(bg=color, fg="black")

            new_cell.label.grid(row=len(self.cells) // self.cols, column=len(self.cells) % self.cols, padx=2, pady=2)
            new_cell.label.bind("<Button-1>", lambda event, cell=new_cell: self.handle_left_click(event, cell))
            new_cell.label.bind("<Button-3>", lambda event, cell=new_cell: self.handle_right_click(event, cell))
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

    def delete_cell(self, this_cell):
        selected_cells = [cell for cell in self.cells if cell.selected]
        if selected_cells and len(selected_cells) > 1:
            confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete these cell?")
            if confirm:
                for cell in selected_cells:
                    cell.label.destroy()
                    self.cells.remove(cell)
        else:
            confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete this cell?")
            if confirm:
                this_cell.label.destroy()
                self.cells.remove(this_cell)
        self.rearrange_cells()

    def delete_cell_all(self, cell):
        confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete all cells?")
        if confirm:
            for cell in self.cells:
                cell.label.destroy()
            self.cells.clear()

    def rearrange_cells(self):
        for idx, cell in enumerate(self.cells):
            row = idx // self.cols
            col = idx % self.cols
            cell.label.grid(row=row, column=col, padx=1, pady=1)

    def load_cells(self):
        self.cols = self.options["tag_columns"]
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
                                item = self.clean_tag(item)
                                self.add_cell(item.strip())

    def load_tags_from_files(self):
        for txt_filename in os.listdir(self.source_directory):
            if txt_filename.lower().endswith('.txt'):
                txt_path = os.path.join(self.source_directory, txt_filename)
                with open(txt_path, 'r') as txt_file:
                    tags = txt_file.read().split(',')
                    for tag in tags:
                        clean_tag = self.clean_tag(tag)
                        if clean_tag:
                            if clean_tag in self.tag_counts:
                                self.tag_counts[clean_tag] += 1
                            else:
                                self.tag_counts[clean_tag] = 1

    def clean_tag(self, tag):
        if(self.options["clean_tags"] == True):

            clean_tag = tag.strip()
            clean_tag = clean_tag.replace("Prompt: ", "")
            clean_tag = clean_tag.replace(":", "")
            clean_tag = clean_tag.replace("(", "")
            clean_tag = clean_tag.replace(")", "")
            clean_tag = clean_tag.replace("{", "")
            clean_tag = clean_tag.replace("}", "")
            clean_tag = clean_tag.replace("+", "")
        return(clean_tag)

    def update_tag_dropdown(self):
        sorted_tags = sorted(self.tag_counts.keys(), key=lambda tag: self.tag_counts[tag], reverse=True)
        tag_with_count = [f"{self.tag_counts[tag]} - {tag}" for tag in sorted_tags]
        self.tag_dropdown['values'] = tag_with_count

        self.tag_dropdown.bind("<Return>", lambda event: self.add_tag_from_dropdown())

    def reload_tags_from_files(self):
        self.tag_counts = {}

        self.load_tags_from_files()
        self.update_tag_dropdown()

    def open_help_dialog(self):
        help_image_path = "help.webp"
        if os.path.exists(help_image_path):
            help_image = Image.open(help_image_path)
            help_image.thumbnail((800, 600))
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

    def toggle_style(self):
        if self.options["style"] == "Normal":
            self.options["style"] = "Black"
        else:
            self.options["style"] = "Normal"
        self.set_current_style()
        self.apply_style()

    def apply_style(self):
        bg_color = self.style["bg_color"]
        fg_color = self.style["fg_color"]

        self.root.configure(bg=bg_color)
        self.top_frame.configure(bg=bg_color)
        self.text_frame.configure(bg=bg_color)
        self.top_tag_frame.configure(bg=bg_color)
        self.tag_dropdown_frame.configure(bg=bg_color)
        self.bottom_tag_frame.configure(bg=bg_color)
        self.tag_frame.configure(bg=bg_color)
        self.bottom_tag_canvas.configure(bg=bg_color)

        style = ttk.Style()
        style.configure("TScale", background=bg_color, troughcolor=bg_color, sliderbackground=fg_color)

        self.toggle_style_button.configure(bg=bg_color, fg=fg_color)
        self.help_button.configure(bg=bg_color, fg=fg_color)
        self.prev_button.configure(bg=bg_color, fg=fg_color)
        self.next_button.configure(bg=bg_color, fg=fg_color)
        self.select_source_folder_button.configure(bg=self.style["btn_bg_color"], fg=self.style["btn_fg_color"])
        self.select_output_folder_button.configure(bg=self.style["btn_bg_color"], fg=self.style["btn_fg_color"])
        self.save_button.configure(bg=bg_color, fg=fg_color)
        self.image_label.configure(bg=bg_color, fg=fg_color)
        self.image_name_label.configure(bg=bg_color, fg=fg_color)
        self.freq_tag_label.configure(bg=bg_color, fg=fg_color)
        #self.tag_var.configure(bg=bg_color, fg=fg_color)
        #self.tag_dropdown.configure(bg=bg_color, fg=fg_color)
        self.add_tag_from_dropdown_button.configure(bg=bg_color, fg=fg_color)
        self.sort_button.configure(bg=bg_color, fg=fg_color)
        self.sort_by_frequency_button.configure(bg=bg_color, fg=fg_color)
        self.bottom_tag_canvas.configure(bg=bg_color)

        self.set_output_dir_color()
        self.update_cell_style()

    def update_cell_style(self):
        for cell in self.cells:
            if cell.selected:
                cell.label.config(relief="solid", borderwidth=2, bg="yellow", fg="black")
            else:
                tag_frequency = self.tag_counts[cell.text]
                cell.label.configure(bg=self.calculate_color(self.tag_counts[cell.text]), fg="black")

    def set_current_style(self):
        style = self.options["style"]
        if style == "White":
            self.style = {
                "bg_color": "white",
                "fg_color": "black",
                "btn_bg_color": "white",
                "btn_fg_color": "black"
            }
        elif style == "Black":
            self.style = {
                "bg_color": "black",
                "fg_color": "white",
                "btn_bg_color": "black",
                "btn_fg_color": "white"
            }
        elif style == "Dark":
            self.style = {
                "bg_color": "darkgrey",
                "fg_color": "white",
                "btn_bg_color": "darkgrey",
                "btn_fg_color": "white"
            }
        elif style == "Normal":
            self.style = {
                "bg_color": "lightgrey",
                "fg_color": "black",
                "btn_bg_color": "SystemButtonFace",
                "btn_fg_color": "black"
            }
        else:
            self.style = {
                "bg_color": "lightgrey",
                "fg_color": "black",
                "btn_bg_color": "lightgrey",
                "btn_fg_color": "black"
            }

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x600")
    app = ImageTextViewer(root)
    root.mainloop()
