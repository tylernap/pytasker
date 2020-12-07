import binascii
import os

from dearpygui import core as dpg
from dearpygui import simple


class CategoryTracker:
    def __init__(self, categories=[]):
        self.categories = categories

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


class TaskTracker:
    def __init__(self, tasks=[]):
        self.tasks = tasks

    def add_task(self, task):
        if type(task) == Task:
            self.task.append(task)
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


class Category:
    def __init__(self, label="", color=[0, 0, 0, -1]):
        self.id = generate_random_string()
        self.group = "catgroup" + self.id
        self.label = label
        self.color = color
        self.tasks = TaskTracker()
        self.complete = False

    def render(self):
        """
        Draw the Category to the screen
        """
        with simple.group(self.group, parent="Categories", before="AddCategorySpace"):
            # Render the Category group
            dpg.add_spacing(count=2)
            dpg.add_checkbox(self.id, label="")
            dpg.add_same_line(spacing=10)
            dpg.add_text(self.label, color=self.color)

    def remove(self):
        """
        Remove the Category object from the screen
        """
        if dpg.does_item_exist(self.group):
            dpg.delete_item(self.group)


class Task:
    def __init__(self, label, category_id):
        self.id = generate_random_string()
        self.group = "taskgroup" + self.id
        self.label = label
        self.category_id = category_id
        self.complete = False

    def render(self):
        with simple.group(
            self.group, parent=self.category_id, before=f"taskspace{self.category_id}"
        ):
            dpg.add_indent()
            dpg.add_checkbox(self.id, label=self.label)
            dpg.unindent()

    def remove(self):
        if dpg.does_item_exist(self.group):
            dpg.delete_item(self.group)


def generate_random_string():
    return binascii.b2a_hex(os.urandom(8)).decode("utf-8")
