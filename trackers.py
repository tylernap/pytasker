from dearpygui import core as dpg
from dearpygui import simple

import util


class TabTracker(object):
    def __init__(self, tabs=[]):
        self.tabs = TabList(tabs)

    def add_tab(self, tab):
        if type(tab) == Tab:
            self.tabs.append(tab)
        else:
            raise Exception("Input provided is not a Tab")

    def get_tab(self, tab_id):
        try:
            tab = list(filter(lambda x: x.id == tab_id, self.tabs))[0]
        except IndexError:
            tab = None

        return tab

    def find_tab(self, tab_name):
        try:
            tab = list(filter(lambda x: x.tab_name == tab_name, self.tabs))[0]
        except IndexError:
            tab = None

        return tab

    def remove_tab(self, tab_id):
        tab = self.get_tab(tab_id)
        self.tabs.remove(tab)


class CategoryTracker(object):
    def __init__(self, categories=[]):
        self.categories = CategoryList(categories)

    def add_category(self, category):
        if type(category) == Category:
            self.categories.append(category)
        else:
            raise Exception("Input provided is not a Category")

    def get_category(self, category_id):
        try:
            category = list(filter(lambda x: x.id == category_id, self.categories))[0]
        except IndexError:
            category = None

        return category

    def remove_category(self, category_id):
        category = self.get_category(category_id)
        self.categories.remove(category)


class TaskTracker(object):
    def __init__(self, tasks=[]):
        self.tasks = TaskList(tasks)

    def add_task(self, task):
        if type(task) == Task:
            self.tasks.append(task)
        else:
            raise Exception("Input provided is not a Task")

    def get_task(self, task_id):
        try:
            task = list(filter(lambda x: x.id == task_id, self.tasks))[0]
        except IndexError:
            task = None

        return task

    def remove_task(self, task_id):
        task = self.get_task(task_id)
        self.tasks.remove(task)


class TabList(list):
    pass


class CategoryList(list):
    pass


class TaskList(list):
    pass


class Tab(object):
    def __init__(self, tab_name, parent):
        self.id = util.generate_random_string()
        self.tab_name = tab_name
        self.parent = parent
        self.page = None

    def render(self, page, page_data=None):
        self.page = page
        with simple.tab(
            name=f"tab{self.id}", closable=True, parent=self.parent, label=self.tab_name
        ):
            page.render(page_data)


class Category(object):
    def __init__(self, parent, label="", color=[0, 0, 0, -1]):
        self.id = util.generate_random_string()
        self.group = "catgroup" + self.id
        self.parent = parent
        self.label = label
        self.color = color
        self.tasks = TaskTracker()
        self.complete = False

    def render(self):
        """
        Draw the Category to the screen
        """
        parent_id = self.parent.replace("categories", "")
        with simple.group(
            self.group, parent=self.parent, before=f"catspace{parent_id}"
        ):
            # Render the Category group
            dpg.add_spacing(count=2)
            dpg.add_checkbox(
                self.id,
                label="",
                default_value=self.complete,
                callback=self.checkbox_check,
            )
            dpg.add_same_line(spacing=10)
            dpg.add_text(self.label, color=self.color)

    def remove(self):
        """
        Remove the Category object from the screen
        """
        if dpg.does_item_exist(self.group):
            dpg.delete_item(self.group)

    def checkbox_check(self, sender, data):
        self.complete = dpg.get_value(sender)
        dpg.configure_item(self.id, enabled=not self.complete)
        for task in self.tasks.tasks:
            dpg.set_value(task.id, True)
            task.checkbox_check(task.id, None)


class Task(object):
    def __init__(self, label, category_id):
        self.id = util.generate_random_string()
        self.group = "taskgroup" + self.id
        self.label = label
        self.category_id = category_id
        self.complete = False

    def render(self):
        with simple.group(
            self.group, parent=self.category_id, before=f"taskspace{self.category_id}"
        ):
            dpg.add_indent()
            dpg.add_checkbox(
                self.id,
                label=self.label,
                default_value=self.complete,
                callback=self.checkbox_check,
            )
            dpg.unindent()

    def remove(self):
        if dpg.does_item_exist(self.group):
            dpg.delete_item(self.group)

    def checkbox_check(self, sender, data):
        self.complete = dpg.get_value(sender)
        dpg.configure_item(self.id, enabled=not self.complete)
