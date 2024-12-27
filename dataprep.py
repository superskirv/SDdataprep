import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from natsort import natsorted
import natsort
import os

config = {
    'input_dir': None,
    'output_dir': "./",
    'resize_image_limit': 1536,
    'resize_image_delete_input_img': False,
    'convert_image_type': "png",
    'convert_image_delete_input_img': False,
    'delete_moves_to_temp': True,
    'displayed_image_maxsize': 512,
    'initial_dir': "./",
    'valid_img_types': ('.png', '.jpg', '.jpeg', '.gif', '.webp')
}
class ImageViewer:
    def __init__(self, root, config):
        self.root = root
        self.config = config

        self.version = "4.0.3"
        self.last_update = "20241227"

        self.root.title(f"Ski Dataprep v{self.version}")
        
        # Variables
        self.image_list = []
        self.current_image_index = -1
        self.current_dir = None
        self.text_data = []
        self.text_file_path = ""
        self.global_tags = {}  # Dictionary to store global tags and their counts
        self.undo_img_tags_history = []
        self.autocomplete_values = []  # List to hold autocomplete suggestions
        
        # Widgets
        self.frame_buttons = tk.Frame(root)
        self.btn_open_folder = tk.Button(self.frame_buttons, text="Open Folder", command=self.open_folder)
        self.btn_prev = tk.Button(self.frame_buttons, text="Previous", command=self.show_previous)
        self.btn_next = tk.Button(self.frame_buttons, text="Next", command=self.show_next)
        self.dropdown_images = ttk.Combobox(self.frame_buttons, state='readonly')
        self.dropdown_images.bind("<<ComboboxSelected>>", self.change_image)

        self.frame_buttons.pack(pady=0)
        self.btn_open_folder.pack(side=tk.LEFT, padx=0)
        self.btn_prev.pack(side=tk.LEFT, padx=0)
        self.btn_next.pack(side=tk.LEFT, padx=0)
        self.dropdown_images.pack(side=tk.LEFT, padx=0)

        self.frame_image = tk.Frame(root)
        self.frame_image.pack(side=tk.LEFT, padx=0, pady=0)
        self.frame_btn_image = tk.Frame(self.frame_image)
        self.frame_btn_image.pack(side=tk.TOP, pady=0, expand=True)
        self.btn_convert = tk.Button(self.frame_btn_image, text=f"Convert to [{self.config['convert_image_type']}]", command=self.click_convert_image)
        self.btn_convert.pack(side=tk.LEFT, padx=0)
        self.btn_shrink = tk.Button(self.frame_btn_image, text="Shrink Image", command=self.click_shrink_image)
        self.btn_shrink.pack(side=tk.LEFT, padx=0)

        self.frame_btn_img_res = tk.Frame(self.frame_btn_image)
        self.frame_btn_img_res.pack(side=tk.BOTTOM, pady=0, expand=True)
        self.label_resolution = tk.Label(self.frame_btn_img_res, text="", font=("Helvetica", 8))
        self.label_resolution.pack(side=tk.TOP, pady=(5, 0))
        self.label_resolution_new = tk.Label(self.frame_btn_img_res, text="", font=("Helvetica", 8))
        self.label_resolution_new.pack(side=tk.BOTTOM, pady=(5, 0))
        self.canvas = tk.Canvas(self.frame_image, width=self.config['displayed_image_maxsize'] + 5, height=self.config['displayed_image_maxsize'] + 5)
        self.canvas.pack(side=tk.BOTTOM)

        self.frame_text = tk.Frame(root)
        self.frame_text.pack(side=tk.RIGHT, pady=0, fill=tk.BOTH, expand=True)
        self.frame_btn_tags = tk.Frame(self.frame_text)
        self.frame_btn_tags.pack(side=tk.TOP, pady=0, fill=tk.BOTH, expand=True)

        self.frame_btn_tags_btns = tk.Frame(self.frame_btn_tags)
        self.frame_btn_tags_btns.pack(side=tk.TOP, pady=0, fill=tk.X)
        self.frame_btn_tags_btns_row1 = tk.Frame(self.frame_btn_tags_btns)
        self.frame_btn_tags_btns_row1.pack(side=tk.TOP, pady=0, fill=tk.BOTH, expand=True)
        self.frame_btn_tags_btns_row2 = tk.Frame(self.frame_btn_tags_btns)
        self.frame_btn_tags_btns_row2.pack(side=tk.TOP, pady=0, fill=tk.BOTH, expand=True)
        self.frame_btn_tags_btns_row3 = tk.Frame(self.frame_btn_tags_btns)
        self.frame_btn_tags_btns_row3.pack(side=tk.TOP, pady=0, fill=tk.BOTH, expand=True)

        self.entry_new_item = ttk.Combobox(self.frame_btn_tags_btns_row1, values=self.autocomplete_values)
        self.entry_new_item.pack(side=tk.TOP, fill=tk.X)
        self.entry_new_item.bind('<KeyRelease>', self.update_autocomplete)
        # self.entry_new_item.bind('<KeyRelease-Up>', self.on_entry_click)

        self.btn_save = tk.Button(self.frame_btn_tags_btns_row2, text="Save", command=self.save_txt_file)
        self.btn_save.pack(side=tk.LEFT, padx=0)
        self.btn_add = tk.Button(self.frame_btn_tags_btns_row2, text="Add Item", command=self.add_item)
        self.btn_add.pack(side=tk.LEFT, padx=0)
        self.btn_remove = tk.Button(self.frame_btn_tags_btns_row2, text="Remove Selected", command=self.remove_selected_items)
        self.btn_remove.pack(side=tk.LEFT, padx=0)
        self.btn_tag_move_up = tk.Button(self.frame_btn_tags_btns_row3, text="Move Up", command=self.move_item_up)
        self.btn_tag_move_up.pack(side=tk.LEFT, padx=0)
        self.btn_tag_move_down = tk.Button(self.frame_btn_tags_btns_row3, text="Move Down", command=self.move_item_down)
        self.btn_tag_move_down.pack(side=tk.LEFT, padx=0)

        self.frame_btn_tags_list = tk.Frame(self.frame_btn_tags)
        self.frame_btn_tags_list.pack(side=tk.BOTTOM, pady=0, fill=tk.BOTH, expand=True)

        min_width_chars = int(100 / 7) # min_width_pixels // avg_char_width
        self.img_tag_listbox = tk.Listbox(self.frame_btn_tags_list, selectmode=tk.MULTIPLE, width=min_width_chars)
        self.img_tag_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        img_tag_listbox_scrollbar = tk.Scrollbar(self.frame_btn_tags_list, orient=tk.VERTICAL, command=self.img_tag_listbox.yview)
        img_tag_listbox_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.img_tag_listbox.config(yscrollcommand=img_tag_listbox_scrollbar.set)
        self.img_tag_listbox.bind("<<ListboxSelect>>", self.on_img_tag_select)

        self.global_tag_listbox = tk.Listbox(self.frame_btn_tags_list, selectmode=tk.MULTIPLE, width=min_width_chars)
        self.global_tag_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        global_tag_listbox_scrollbar = tk.Scrollbar(self.frame_btn_tags_list, orient=tk.VERTICAL, command=self.global_tag_listbox.yview)
        global_tag_listbox_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.global_tag_listbox.config(yscrollcommand=global_tag_listbox_scrollbar.set)
        self.global_tag_listbox.bind("<<ListboxSelect>>", self.on_global_tag_select)
    def update_autocomplete(self, event=None):
        value = self.entry_new_item.get().strip()
        if value == '':
            data = list(self.global_tags.keys())
        else:
            # new_items = value.split(',')
            # value = new_items[-1].strip().lower()
            data = [item for item in self.global_tags.keys() if value in item.lower()]
        self.entry_new_item['values'] = data
    def move_item_up(self):
        selected_indices = self.img_tag_listbox.curselection()
        selected_items = []
        if not selected_indices:
            return
        for index in selected_indices:
            selected_items.append(self.img_tag_listbox.get(index))
        for index in selected_indices:
            if index > 0:
                value = self.img_tag_listbox.get(index)
                value_next = self.img_tag_listbox.get(index - 1)
                if value_next not in selected_items:
                    self.img_tag_listbox.delete(index)
                    self.img_tag_listbox.insert(index - 1, value)
                    self.img_tag_listbox.selection_set(index - 1)
        self.add_undo_img_tags_history(self.img_tag_listbox)
    def move_item_down(self):
        selected_indices = self.img_tag_listbox.curselection()
        selected_items = []
        if not selected_indices:
            return
        for index in selected_indices:
            selected_items.append(self.img_tag_listbox.get(index))
        for index in selected_indices:
            if index < self.img_tag_listbox.size() - 1:
                value = self.img_tag_listbox.get(index)
                value_next = self.img_tag_listbox.get(index + 1)
                if value_next not in selected_items:
                    self.img_tag_listbox.delete(index)
                    self.img_tag_listbox.insert(index + 1, value)
                    self.img_tag_listbox.selection_set(index + 1)
        self.add_undo_img_tags_history(self.img_tag_listbox)
    def on_img_tag_select(self, event):
        selected_indices = self.img_tag_listbox.curselection()
        if not selected_indices:
            return
        self.clear_selection(self.global_tag_listbox)
        selected_items = [self.img_tag_listbox.get(idx) for idx in selected_indices]
        self.populate_entry(selected_items)
    def on_global_tag_select(self, event):
        self.clear_selection(self.img_tag_listbox)
        selected_indices = self.global_tag_listbox.curselection()
        selected_items = [self.remove_count_from_tag(self.global_tag_listbox.get(idx)) for idx in selected_indices]
        self.populate_entry(selected_items)
    def clear_selection(self, listbox):
        listbox.selection_clear(0, tk.END)
    def populate_entry(self, items):
        self.entry_new_item.delete(0, tk.END)
        self.entry_new_item.insert(0, ', '.join(items))
    def remove_count_from_tag(self, tag):
        return tag.split(' - ')[-1]
    def round_to_nearest_64(self, value):
        return (value + 32) // 64 * 64
    def click_convert_image(self):
        self.convert_image(self.image_list[self.current_image_index], self.config['convert_image_type'])
    def convert_image(self, output_path, file_type_out="png", delete_old=False, input_path=None):
        img_path = output_path
        if input_path:
            img_path = input_path
        file_type_in = os.path.splitext(output_path)[1]

        if file_type_in != file_type_out:
            with Image.open(img_path) as img:
                output_path_filetype = os.path.splitext(output_path)[0] + '.' + file_type_out
                img.save(output_path_filetype, file_type_out)
                print(f"Converted and resized {img_path} from {file_type_in} to {file_type_out}")
                if self.config['convert_image_delete_input_img']:
                    self.delete_file(input_path)
        else:
            print(f"INFO: No changes, {img_path} filetype is already {file_type_in} filetype.")
    def get_new_resolution(self, max_dimension, original_width, original_height):
        reduced_width = original_width
        reduced_height = original_height

        if original_width > max_dimension or original_height > max_dimension:
            if original_width / original_height > 1:  # Landscape orientation
                reduced_width = max_dimension
                reduced_height = int(original_height * (max_dimension / original_width))
            else:  # Portrait or square orientation
                reduced_height = max_dimension
                reduced_width = int(original_width * (max_dimension / original_height))
        else:
            reduced_width, reduced_height = original_width, original_height

        new_width = self.round_to_nearest_64(reduced_width)
        new_height = self.round_to_nearest_64(reduced_height)

        return (new_width, new_height)
    def click_shrink_image(self):
        self.shrink_image(self.image_list[self.current_image_index], self.config['resize_image_limit'])
    def shrink_image(self, output_path, resize=1536, input_path=None):
        img_path = output_path
        if input_path:
            img_path = input_path
        with Image.open(img_path) as img:
            original_width, original_height = img.size

            (new_width, new_height) = self.get_new_resolution(resize, original_width, original_height)

            resized_img = img
            if original_width != new_width or original_height != new_height:
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                resized_img.save(output_path)
                print(f"Resized {img_path} from {original_width}x{original_height} to {new_width}x{new_height}")
            else:
                print(f"INFO: No changes, {img_path}: already at {original_width}x{original_height}")
            if self.config['resize_image_delete_input_img']:
                if input_path != output_path:
                    self.delete_file(input_path)
        self.load_image_and_text()
    def delete_file(self, file_path):
        if not self.config['delete_moves_to_temp']:
            # os.remove(file_path)
            print(f"(Pretending to) Deleted {file_path}")
        else:
            print(f"Failed to delete {file_path} due to global settings.")
            print("TODO: Move file to a safe location instead of deleting.")
    def open_folder(self):
        if not self.current_dir:
            self.current_dir = self.config['initial_dir']
        if not os.path.exists(self.current_dir):
            self.current_dir = os.getcwd()

        folder_path = filedialog.askdirectory(initialdir=self.current_dir)
        if not folder_path:
            return
        self.current_dir = folder_path

        self.image_list = []
        self.global_tags.clear()  # Clear the global tags dictionary before loading a new folder

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(self.config['valid_img_types']):
                image_path = os.path.join(folder_path, filename)
                self.image_list.append(image_path)
            elif filename.lower().endswith('.txt'):
                txt_path = os.path.join(folder_path, filename)
                with open(txt_path, 'r') as file:
                    tags = [tag.strip() for tag in file.read().split(',')]
                    for tag in tags:
                        if tag in self.global_tags:
                            self.global_tags[tag] += 1
                        else:
                            self.global_tags[tag] = 1

        if not self.image_list:
            messagebox.showinfo("No Images", "No image files found in the selected folder.")
            return
        # Sort the list of filenames alphabetically
        # self.dropdown_images['values'] = sorted([os.path.basename(img) for img in self.image_list])
        
        self.image_list = natsorted(self.image_list)
        self.dropdown_images['values'] = natsorted([os.path.basename(img) for img in self.image_list])

        self.current_image_index = 0
        self.load_image_and_text()
        self.update_global_tag_listbox()
    def update_global_tag_listbox(self):
        self.global_tag_listbox.delete(0, tk.END)
        for tag, count in sorted(self.global_tags.items(), key=lambda item: (-item[1], item[0])):
            self.global_tag_listbox.insert(tk.END, f"{count} - {tag}")
    def load_image_and_text(self):
        if self.current_image_index < 0 or self.current_image_index >= len(self.image_list):
            return

        # Load and display image
        image_path = self.image_list[self.current_image_index]
        image = Image.open(image_path)

        # Display the resolution of the original image
        original_width, original_height = image.size
        self.label_resolution.config(text=f"{original_width}x{original_height}")
        (new_width, new_height) = self.get_new_resolution(self.config['resize_image_limit'], original_width, original_height)
        self.label_resolution_new.config(text=f"{new_width}x{new_height}")

        max_size = (self.config['displayed_image_maxsize'], self.config['displayed_image_maxsize'])
        image.thumbnail(max_size, Image.LANCZOS)  # Scale down while maintaining aspect ratio
        photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.canvas.image = photo

        # Update dropdown menu
        self.dropdown_images.set(os.path.basename(image_path))

        # Load associated text file
        txt_path = os.path.splitext(image_path)[0] + '.txt'
        self.text_file_path = txt_path
        self.text_data = []
        if os.path.exists(txt_path):
            with open(txt_path, 'r') as file:
                self.text_data = [line.strip() for line in file.read().split(',')]

        # Update listbox
        self.img_tag_listbox.delete(0, tk.END)
        for item in self.text_data:
            self.img_tag_listbox.insert(tk.END, item)
    def show_previous(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image_and_text()
    def show_next(self):
        if self. current_image_index < len(self.image_list) - 1:
            self.current_image_index += 1
            self.load_image_and_text()
    def change_image(self, event):
        selected_image_base = self.dropdown_images.get()
        if not selected_image_base:
            return

        # Find the full path in image_list that matches the base name
        try:
            self.current_image_index = next(i for i, img_path in enumerate(self.image_list) if os.path.basename(img_path) == selected_image_base)
        except StopIteration:
            print("selected_image_base", selected_image_base)
            print("self.current_image_index", self.current_image_index)
            messagebox.showerror("Error", "Selected image not found.")
            return

        self.load_image_and_text()
    def add_item(self):
        new_items = self.entry_new_item.get().strip().split(',')
        added_items = []
        for new_item in new_items:
            new_item = new_item.strip()
            if new_item and new_item not in self.text_data:
                self.text_data.append(new_item)
                self.img_tag_listbox.insert(tk.END, new_item)
                added_items.append(new_item)
        #self.entry_new_item.delete(0, tk.END)
        self.add_undo_img_tags_history(self.img_tag_listbox)
        self.update_global_tags()  # Update global tags after adding items
    def remove_selected_items(self):
        selected_indices = sorted(self.img_tag_listbox.curselection(), reverse=True)
        for index in selected_indices:
            del self.text_data[index]
            self.img_tag_listbox.delete(index)
        self.add_undo_img_tags_history(self.img_tag_listbox)
        self.update_global_tags()  # Update global tags after removing items
    def update_global_tags(self):
        # Clear the global tags dictionary
        self.global_tags.clear()

        # Iterate over all text files and update the global tags
        for img_path in self.image_list:
            txt_path = os.path.splitext(img_path)[0] + '.txt'
            if os.path.exists(txt_path):
                with open(txt_path, 'r') as file:
                    tags = [tag.strip() for tag in file.read().split(',')]
                    for tag in tags:
                        if tag in self.global_tags:
                            self.global_tags[tag] += 1
                        else:
                            self.global_tags[tag] = 1
        #Autosave the current list.
        self.save_txt_file()
        # Update the global tag listbox
        self.update_global_tag_listbox()
    def save_txt_file(self):
        if not self.text_file_path:
            return

        # Retrieve the current order of tags from the img_tag_listbox
        tags_to_save = ','.join(self.img_tag_listbox.get(0, tk.END))

        with open(self.text_file_path, 'w') as file:
            file.write(tags_to_save)
        #messagebox.showinfo("Saved", "Text data saved successfully.")
    def add_undo_img_tags_history(self, old_list):
        # Convert the current state of the Listbox to a tuple or list to store in history
        current_state = list(old_list.get(0, tk.END))
        # Append the current state to the undo history
        self.undo_img_tags_history.append(current_state)
        # Ensure only the last 10 states are kept
        if len(self.undo_img_tags_history) > 10:
            self.undo_img_tags_history.pop(0)
    def recall_undo_img_tags_history(self):
        return self.undo_img_tags_history.pop()
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewer(root, config)
    root.mainloop()