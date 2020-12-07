import binascii
import os
import sys

from dearpygui import core as dpg
from dearpygui import simple

import trackers


class MainGui:
    def __init__(self, width=200, height=200, theme="Dark"):
        self.theme = theme
        self.height = height
        self.width = width
        self.category_tracker = trackers.CategoryTracker()

    def make_gui(self):
        dpg.set_main_window_size(self.width, self.height)
        dpg.set_theme(self.theme)
        with simple.window("Main", no_title_bar=True):
            with simple.menu_bar("Menu"):
                with simple.menu("File"):
                    dpg.add_menu_item("New")
                    dpg.add_menu_item("Load")
                    dpg.add_separator()
                    dpg.add_menu_item("Quit", callback=self.exit_program)
                with simple.menu("Themes"):
                    dpg.add_menu_item("Dark", callback=self.theme_callback)
                    dpg.add_menu_item("Light", callback=self.theme_callback)
                    dpg.add_menu_item("Classic", callback=self.theme_callback)
                    dpg.add_menu_item("Dark 2", callback=self.theme_callback)
                    dpg.add_menu_item("Grey", callback=self.theme_callback)
                    dpg.add_menu_item("Dark Grey", callback=self.theme_callback)
                    dpg.add_menu_item("Cherry", callback=self.theme_callback)
                    dpg.add_menu_item("Purple", callback=self.theme_callback)
                    dpg.add_menu_item("Gold", callback=self.theme_callback)
                    dpg.add_menu_item("Red", callback=self.theme_callback)

            dpg.set_main_window_title("pytasker")
            dpg.add_text("Hello!")
            with simple.group("Categories"):
                dpg.add_spacing(name="AddCategorySpace", count=1)
                dpg.add_button(
                    "AddCategory", callback=self.add_category, label="Add New Category"
                )
            dpg.add_spacing(name="", count=10)

    def start_gui(self):
        dpg.start_dearpygui(primary_window="Main")

    def theme_callback(self, sender, data):
        dpg.set_theme(sender)

    def generate_random_string(self):
        return binascii.b2a_hex(os.urandom(8)).decode("utf-8")

    def exit_program(self, sender, data):
        sys.exit()

    def add_category(self, sender, data):
        random_id = self.generate_random_string()
        with simple.group(f"newcategory{random_id}", before="AddCategorySpace"):
            dpg.add_input_text(f"catlabel{random_id}", label="")
            dpg.add_same_line(spacing=10)
            dpg.add_button("Done", callback=self.submit_category)
            dpg.add_color_picker4(
                f"catcolor{random_id}",
                default_value=[255, 0, 0, 255],
                height=200,
                width=200,
                label="",
            )

    def submit_category(self, sender, data):
        input_id = dpg.get_item_parent(sender).replace("newcategory", "")
        category = trackers.Category()
        self.category_tracker.add_category(category)
        category.label = dpg.get_value(f"catlabel{input_id}")
        category.color = dpg.get_value(f"catcolor{input_id}")
        category.render()

        # Render the Add Task button
        with simple.group(f"cattasks{category.id}", parent=f"catgroup{category.id}"):
            dpg.add_indent()
            dpg.add_spacing(name=f"taskspace{category.id}")
            dpg.add_button(
                f"addtask{category.id}",
                label="Add New Task",
                callback=self.add_task,
                callback_data={"category": category.id},
            )
            dpg.unindent()

        dpg.delete_item(dpg.get_item_parent(sender))

    def add_task(self, sender, data):
        random_id = self.generate_random_string()
        parent = dpg.get_item_parent(sender)
        with simple.group(
            f"newtask{random_id}",
            parent=parent.replace("newtask", ""),
            before=f"taskspace{data.get('category')}",
        ):
            dpg.add_indent()
            dpg.add_input_text(f"tasklabel{random_id}", label="")
            dpg.add_same_line(spacing=10)
            dpg.add_button(
                f"taskdone{random_id}",
                label="Done",
                callback=self.submit_task,
                callback_data={"parent": parent},
            )
            dpg.unindent()

    def submit_task(self, sender, data):
        input_id = dpg.get_item_parent(sender).replace("newtask", "")
        parent = data.get("parent").replace("cattasks", "")
        task = trackers.Task(dpg.get_value(f"tasklabel{input_id}"), parent)
        category = self.category_tracker.get_category(parent)
        category.tasks.tasks.append(task)

        task.label = dpg.get_value(f"tasklabel{input_id}")
        task.render()

        dpg.delete_item(dpg.get_item_parent(sender))


def main():

    gui = MainGui(500, 500, theme="Dark")
    gui.make_gui()
    gui.start_gui()


if "__main__" in __name__:
    main()
