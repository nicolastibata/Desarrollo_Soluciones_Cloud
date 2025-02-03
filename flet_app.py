import flet as ft
from datetime import datetime

def main(page: ft.Page):
    page.title = "Todo List App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Lista de tareas (simulada)
    todos = []

    # Función para agregar una tarea
    def add_task(e):
        task = task_input.value
        deadline = deadline_input.value
        category = category_dropdown.value
        if task:
            new_task = {
                "task": task,
                "done": False,
                "status": "sin iniciar",
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "deadline": deadline,
                "category": category
            }
            todos.append(new_task)
            update_task_list()
            task_input.value = ""
            deadline_input.value = ""
            category_dropdown.value = "Personal"
            page.update()

    # Función para actualizar la lista de tareas
    def update_task_list():
        task_list.controls.clear()
        for i, todo in enumerate(todos):
            task_list.controls.append(
                ft.Row(
                    controls=[
                        ft.Checkbox(value=todo["done"], on_change=lambda e, i=i: toggle_done(e, i)),
                        ft.Text(todo["task"], style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH if todo["done"] else None)),
                        ft.Text(f"Creada: {todo['created_at']}"),
                        ft.Text(f"Deadline: {todo['deadline']}"),
                        ft.Text(f"Categoría: {todo['category']}"),
                        ft.Dropdown(
                            value=todo["status"],
                            options=[
                                ft.dropdown.Option("sin iniciar"),
                                ft.dropdown.Option("iniciada"),
                                ft.dropdown.Option("finalizada"),
                            ],
                            on_change=lambda e, i=i: change_status(e, i),
                        ),
                        ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, i=i: edit_task(e, i)),
                        ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, i=i: delete_task(e, i)),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
        page.update()

    # Función para marcar/desmarcar una tarea como completada
    def toggle_done(e, index):
        todos[index]["done"] = not todos[index]["done"]
        update_task_list()

    # Función para cambiar el estado de una tarea
    def change_status(e, index):
        todos[index]["status"] = e.control.value
        update_task_list()

    # Función para editar una tarea
    def edit_task(e, index):
        # Aquí podrías abrir un diálogo para editar la tarea
        pass

    # Función para eliminar una tarea
    def delete_task(e, index):
        del todos[index]
        update_task_list()

    # Componentes de la interfaz
    task_input = ft.TextField(label="Nueva tarea", expand=True)
    deadline_input = ft.DatePicker()  # Corrección aquí
    category_dropdown = ft.Dropdown(
        label="Categoría",
        options=[
            ft.dropdown.Option("Hogar"),
            ft.dropdown.Option("Trabajo"),
            ft.dropdown.Option("Personal"),
        ],
        value="Personal",
    )
    add_button = ft.ElevatedButton("Agregar", on_click=add_task)
    task_list = ft.Column()

    # Diseño de la página
    page.add(
        ft.Column(
            controls=[
                ft.Row(controls=[task_input, deadline_input, category_dropdown, add_button]),
                task_list,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

# Ejecutar la aplicación
ft.app(target=main)