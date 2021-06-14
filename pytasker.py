import os
import sys
import yaml

from dearpygui import core as dpg
from dearpygui import simple

import trackers
import util


class Page:
    def __init__(self, page_name, parent, path=None, filename=None):
        self.id = util.generate_random_string()
        self.page_name = page_name
        self.parent = parent
        self.path = path
        self.filename = filename

        self.category_tracker = trackers.CategoryTracker()
        self.changes = False

    def render(self, page_data=None):
        # Initiate page
        with simple.group(f"categories{self.id}", parent=self.parent):
            dpg.add_spacing(name=f"catspace{self.id}", count=1)
            dpg.add_button(
                f"addcat{self.id}",
                callback=self.add_category,
                label="Add New Category",
            )
        dpg.add_spacing(name="", count=10)

        if page_data:
            self.page_name = page_data.get("pagename")
            self.path = page_data.get("path")
            self.filename = page_data.get("filename")

            for category in page_data.get("categories"):
                category_id = self.submit_category(
                    "",
                    {
                        "label": category["label"],
                        "color": category["color"],
                        "complete": category["complete"],
                    },
                )
                for task in category["tasks"]:
                    self.submit_task(
                        category_id,
                        {
                            "label": task["label"],
                            "complete": task["complete"],
                            "parent": f"cattasks{category_id}",
                        },
                    )

        item = dpg.get_item_configuration(self.parent)
        dpg.configure_item(self.parent, label=item["label"].replace("!", ""))
        self.changes = False

    def render_data_dict(self):
        data = {}
        data["pagename"] = self.page_name
        data["id"] = self.id
        data["path"] = self.path
        data["filename"] = self.filename

        data["categories"] = []
        for category in self.category_tracker.categories:
            data_category = {}
            data_category["id"] = category.id
            data_category["group"] = category.group
            data_category["label"] = category.label
            data_category["color"] = category.color
            data_category["parent"] = category.parent
            data_category["complete"] = category.complete
            data_category["tasks"] = []
            for task in category.tasks.tasks:
                data_task = {}
                data_task["id"] = task.id
                data_task["group"] = task.group
                data_task["label"] = task.label
                data_task["category_id"] = task.category_id
                data_task["complete"] = task.complete

                data_category["tasks"].append(data_task)

            data["categories"].append(data_category)

        return data

    def add_category(self, sender, data):
        random_id = util.generate_random_string()
        with simple.group(f"newcategory{random_id}", parent=f"categories{self.id}"):
            dpg.add_input_text(f"catlabel{random_id}", label="")
            dpg.add_same_line(spacing=10)
            dpg.add_button(
                f"catdone{random_id}", callback=self.submit_category, label="Done"
            )
            dpg.add_color_picker4(
                f"catcolor{random_id}",
                default_value=[255, 0, 0, 255],
                height=200,
                width=200,
                label="",
            )

    def submit_category(self, sender, data):
        if data:
            category_label = data["label"]
            category_color = data["color"]
        else:
            parent = dpg.get_item_parent(sender)
            input_id = parent.replace("newcategory", "")
            category_label = dpg.get_value(f"catlabel{input_id}")
            category_color = dpg.get_value(f"catcolor{input_id}")
            dpg.delete_item(parent)

        category = trackers.Category(parent=f"categories{self.id}")
        self.category_tracker.add_category(category)
        category.label = category_label
        category.color = category_color
        if data:
            category.complete = data["complete"]
        category.render()

        if not self.changes:
            item = dpg.get_item_configuration(self.parent)
            dpg.configure_item(self.parent, label="!" + item["label"])
            self.changes = True

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

        return category.id

    def add_task(self, sender, data):
        random_id = util.generate_random_string()
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
                callback_data={"parent": parent, "category": data["category"]},
            )
            dpg.unindent()

    def submit_task(self, sender, data):
        if "label" in data and "complete" in data:
            task_label = data["label"]
        else:
            input_id = dpg.get_item_parent(sender).replace("newtask", "")
            task_label = dpg.get_value(f"tasklabel{input_id}")
            dpg.delete_item(dpg.get_item_parent(sender))
        task = trackers.Task(task_label, data["category"])
        if "complete" in data:
            task.complete = data["complete"]
        category = self.category_tracker.get_category(data["category"])
        category.tasks.tasks.append(task)

        task.render()

        if not self.changes:
            item = dpg.get_item_configuration(self.parent)
            dpg.configure_item(self.parent, label="!" + item["label"])
            self.changes = True


class MainGui:
    def __init__(self, width=200, height=200, theme="Dark"):
        self.theme = theme
        self.height = height
        self.width = width
        self.tab_tracker = trackers.TabTracker()

        self.last_tab_saved = None

    def make_gui(self):
        dpg.set_main_window_size(self.width, self.height)
        dpg.set_theme(self.theme)
        with simple.window("Main", no_title_bar=True):
            dpg.set_main_window_title("pytasker")
            with simple.menu_bar("Menu"):
                with simple.menu("File"):
                    dpg.add_menu_item("New Page", callback=self.new_tab)
                    dpg.add_menu_item("Load Page", callback=self.load_page)
                    dpg.add_menu_item("Save Page", callback=self.save_page_dialog)
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

            dpg.add_tab_bar(name="tab_bar_1", parent="Main")
            with simple.group("inittext"):
                dpg.add_text("Hello! Select File - New to get started")

    def new_tab(self, sender, data):
        with simple.child("NewPopup", height=60):
            dpg.add_text("Input your new tab name:")
            dpg.add_input_text("NewTabName", label="")
            dpg.add_same_line(spacing=2)
            dpg.add_button("NewTabGo", label="Go", callback=self.create_tab)

    def create_tab(self, sender, data):
        dpg.delete_item("NewPopup")
        if dpg.does_item_exist("inittext"):
            dpg.delete_item("inittext")
        tab_name = dpg.get_value("NewTabName")
        tab = trackers.Tab(tab_name, "tab_bar_1")
        self.tab_tracker.add_tab(tab)
        page = Page(f"{tab_name}Page", f"tab{tab.id}")
        tab.render(page)

    def start_gui(self):
        dpg.start_dearpygui(primary_window="Main")

    def theme_callback(self, sender, data):
        dpg.set_theme(sender)

    def exit_program(self, sender, data):
        sys.exit()

    def load_page(self, sender, data):
        dpg.open_file_dialog(self.__load_file, ".task,.*")

    def __load_file(self, sender, data):
        path = data[0]
        if data[1].endswith(".task"):
            filename = data[1]
        else:
            filename = data[1] + ".task"

        with open(os.path.join(path, filename)) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        self.__restore_tab(data)

    def save_page_dialog(self, sender, data):
        tabs = [{"name": tab.tab_name, "id": tab.id} for tab in self.tab_tracker.tabs]
        dialog_height = 30 * (len(tabs) + 2)
        with simple.child("SavePopup", height=dialog_height):
            dpg.add_text("Choose which tab to save:")
            dpg.add_radio_button("SaveRadio", items=[tab["name"] for tab in tabs])
            dpg.add_spacing(count=2)
            dpg.add_button("SaveButton", label="Save", callback=self.save_page)

    def save_page(self, sender, data):
        self.last_tab_saved = dpg.get_value("SaveRadio")
        dpg.delete_item("SavePopup")
        dpg.open_file_dialog(self.__save_file, ".task,.*")

    def __save_file(self, sender, data):
        try:
            path = data[0]
            if data[1].endswith(".task"):
                filename = data[1]
            else:
                filename = data[1] + ".task"

            tab = self.tab_tracker.tabs[self.last_tab_saved]
            page = tab.page

            page.path = path
            page.filename = filename

            data = page.render_data_dict()
            full_path = os.path.join(path, filename)

            if os.path.exists(full_path):
                os.remove(full_path)

            with open(full_path, "w") as file:
                yaml.dump(data, file)

            item = dpg.get_item_configuration(f"tab{tab.id}")
            dpg.configure_item(f"tab{tab.id}", label=item["label"].replace("!", ""))
            page.changes = False
        except Exception as e:
            # TODO: Do something about it
            raise e

    def __restore_tab(self, data):
        try:
            if dpg.does_item_exist("inittext"):
                dpg.delete_item("inittext")
            tab = trackers.Tab(data["pagename"].replace("Page", ""), "tab_bar_1")
            self.tab_tracker.add_tab(tab)
            page = Page(
                data["pagename"], f"tab{tab.id}", data["path"], data["filename"]
            )
            tab.render(page, data)
        except Exception as e:
            # TODO: Actually do something about this
            raise e


def main():

    gui = MainGui(800, 800, theme="Dark")
    gui.make_gui()
    gui.start_gui()


if "__main__" in __name__:
    main()
