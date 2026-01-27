# ==========================================
# Импорт необходимых библиотек и модулей
# ==========================================
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
import json
import os
from datetime import datetime


# ==========================================
# Классы экранов (View)
# Здесь определяются экраны, которые будут управляться ScreenManager
# ==========================================
class MainScreen(MDScreen):
    """Главный экран со списком записей"""
    pass


class DetailScreen(MDScreen):
    """Экран с детальной информацией о записи"""
    pass


class AddEditScreen(MDScreen):
    """Экран добавления/редактирования записи"""
    pass

# ==========================================
# Главный класс приложения (Controller + Model)
# Отвечает за логику, хранение данных и создание интерфейса
# ==========================================
class ReferenceApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_file = "data.json"
        self.settings_file = "settings.json"
        self.entries = []
        self.filtered_entries = []
        self.current_entry = None
        self.current_category = "Все"
        self.dialog = None
        
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        
        # Загружаем настройки и устанавливаем тему
        settings = self.load_settings()
        self.theme_cls.theme_style = settings.get("theme", "Light")
        
        # Загружаем данные
        self.load_data()
        
        # Создаем менеджер экранов
        sm = MDScreenManager()
        
        # Главный экран
        main_screen = self.build_main_screen()
        sm.add_widget(main_screen)
        
        # Экран деталей
        detail_screen = self.build_detail_screen()
        sm.add_widget(detail_screen)
        
        # Экран добавления/редактирования
        add_edit_screen = self.build_add_edit_screen()
        sm.add_widget(add_edit_screen)
        
        return sm
    
    # ------------------------------------------
    # Методы построения интерфейса (UI Building)
    # ------------------------------------------
    def build_main_screen(self):
        """Создание главного экрана"""
        screen = MainScreen(name='main')
        
        # Основной layout
        layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Электронный справочник",
            elevation=3,
            right_action_items=[
                ["sync", lambda x: self.sync_with_github()],
                ["filter-variant", lambda x: self.show_category_menu(x)],
                ["theme-light-dark", lambda x: self.toggle_theme()]
            ]
        )
        layout.add_widget(toolbar)
        
        # Поле поиска
        search_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            padding=[dp(16), dp(8)]
        )
        
        self.search_field = MDTextField(
            hint_text="Поиск...",
            mode="rectangle",
            size_hint_x=0.85
        )
        self.search_field.bind(text=self.on_search_text)
        
        search_btn = MDIconButton(
            icon="magnify",
            size_hint_x=0.15
        )
        
        search_layout.add_widget(self.search_field)
        search_layout.add_widget(search_btn)
        layout.add_widget(search_layout)
        
        # Список записей
        scroll = MDScrollView()
        self.entries_list = MDList()
        scroll.add_widget(self.entries_list)
        layout.add_widget(scroll)
        
        # Кнопка добавления
        fab = MDFloatingActionButton(
            icon="plus",
            pos_hint={"center_x": 0.9, "center_y": 0.1},
            on_release=lambda x: self.open_add_screen()
        )
        
        screen.add_widget(layout)
        screen.add_widget(fab)
        
        # Обновляем список
        self.update_entries_list()
        
        return screen
    
    def build_detail_screen(self):
        """Создание экрана деталей"""
        screen = DetailScreen(name='detail')
        
        layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Детали",
            elevation=3,
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[
                ["pencil", lambda x: self.edit_current_entry()],
                ["delete", lambda x: self.delete_current_entry()]
            ]
        )
        layout.add_widget(toolbar)
        
        # Контент
        scroll = MDScrollView()
        content_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(16),
            size_hint_y=None
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        self.detail_title = MDLabel(
            text="",
            font_style="H5",
            size_hint_y=None,
            height=dp(40)
        )
        
        self.detail_category = MDLabel(
            text="",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20)
        )
        
        self.detail_date = MDLabel(
            text="",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20)
        )
        
        self.detail_content = MDLabel(
            text="",
            font_style="Body1",
            size_hint_y=None
        )
        self.detail_content.bind(texture_size=self.detail_content.setter('size'))
        
        content_layout.add_widget(self.detail_title)
        content_layout.add_widget(self.detail_category)
        content_layout.add_widget(self.detail_date)
        content_layout.add_widget(MDLabel(size_hint_y=None, height=dp(10)))
        content_layout.add_widget(self.detail_content)
        
        scroll.add_widget(content_layout)
        layout.add_widget(scroll)
        
        screen.add_widget(layout)
        return screen
    
    def build_add_edit_screen(self):
        """Создание экрана добавления/редактирования"""
        screen = AddEditScreen(name='add_edit')
        
        layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar
        self.add_edit_toolbar = MDTopAppBar(
            title="Новая запись",
            elevation=3,
            left_action_items=[["close", lambda x: self.go_back()]]
        )
        layout.add_widget(self.add_edit_toolbar)
        
        # Форма
        scroll = MDScrollView()
        form_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(16),
            size_hint_y=None,
            height=dp(500)
        )
        
        self.title_field = MDTextField(
            hint_text="Название",
            mode="rectangle",
            required=True
        )
        
        self.category_field = MDTextField(
            hint_text="Категория",
            mode="rectangle",
            text="Общее"
        )
        
        self.content_field = MDTextField(
            hint_text="Содержание",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(200)
        )
        
        save_btn = MDRaisedButton(
            text="Сохранить",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.save_entry()
        )
        
        form_layout.add_widget(self.title_field)
        form_layout.add_widget(self.category_field)
        form_layout.add_widget(self.content_field)
        form_layout.add_widget(save_btn)
        
        scroll.add_widget(form_layout)
        layout.add_widget(scroll)
        
        screen.add_widget(layout)
        return screen
    
    # ------------------------------------------
    # Работа с данными (Data Layer)
    # Загрузка и сохранение в JSON файл
    # ------------------------------------------
    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.entries = json.load(f)
            except:
                self.entries = []
        else:
            # Создаем примеры данных
            self.entries = [
                {
                    "id": 1,
                    "title": "Python",
                    "category": "Программирование",
                    "content": "Python - высокоуровневый язык программирования общего назначения. Отличается простым и понятным синтаксисом, что делает его идеальным для начинающих.",
                    "date": "2026-01-19"
                },
                {
                    "id": 2,
                    "title": "Kivy",
                    "category": "Программирование",
                    "content": "Kivy - фреймворк для создания мультиплатформенных приложений на Python. Позволяет разрабатывать приложения для Windows, Linux, macOS, Android и iOS.",
                    "date": "2026-01-19"
                },
                {
                    "id": 3,
                    "title": "JSON",
                    "category": "Форматы данных",
                    "content": "JSON (JavaScript Object Notation) - текстовый формат обмена данными, основанный на JavaScript. Легко читается человеком и машиной.",
                    "date": "2026-01-19"
                }
            ]
            self.save_data()
        
        self.filtered_entries = self.entries.copy()
    
    def save_data(self):
        """Сохранение данных в JSON"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)

    def sync_with_github(self):
        """Синхронизация данных с GitHub"""
        url = "https://raw.githubusercontent.com/igris2212/project-on-college/refs/heads/main/data.json"
        
        # Показываем уведомление о начале загрузки
        self.show_alert("Синхронизация", "Загрузка обновлений из интернета...")
        
        # Добавляем заголовки, чтобы GitHub нас не блокировал
        headers = {'User-Agent': 'KivyMD-App'}
        
        # Выполняем запрос
        UrlRequest(
            url, 
            on_success=self.on_sync_success,
            on_failure=self.on_sync_error,
            on_error=self.on_sync_error,
            req_headers=headers
        )

    def on_sync_success(self, request, result):
        """Обработка успешной загрузки"""
        # Если GitHub вернул строку вместо списка (бывает при некоторых ошибках), попробуем её распарсить
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except:
                self.show_alert("Ошибка", "Не удалось прочитать JSON файл")
                return

        if isinstance(result, list):
            # Сохраняем скачанные данные
            self.entries = result
            self.save_data()
            self.filtered_entries = self.entries.copy()
            self.update_entries_list()
            self.show_alert("Готово", f"Синхронизация завершена! Всего записей: {len(self.entries)}")
        else:
            print(f"DEBUG: Получен неожиданный тип данных: {type(result)}")
            self.show_alert("Ошибка", "Получены данные в неизвестном формате")

    def on_sync_error(self, request, error):
        """Обработка ошибки загрузки"""
        self.show_alert("Ошибка", f"Не удалось обновить данные. Проверьте интернет. {error}")

    # ------------------------------------------
    # Работа с настройками (Settings)
    # ------------------------------------------
    def load_settings(self):
        """Загрузка настроек приложения"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"theme": "Light"}

    def save_settings(self):
        """Сохранение настроек приложения"""
        settings = {"theme": self.theme_cls.theme_style}
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    
    # ------------------------------------------
    # UI Логика и обновление отображения
    # ------------------------------------------
    def update_entries_list(self):
        """Обновление списка записей (оптимизировано)"""
        self.entries_list.clear_widgets()
        self._load_index = 0
        self._load_batch(0)

    def _load_batch(self, dt):
        """Порционная загрузка элементов списка для плавности UI"""
        batch_size = 20  # Количество элементов за один раз
        end_index = min(self._load_index + batch_size, len(self.filtered_entries))
        
        for i in range(self._load_index, end_index):
            entry = self.filtered_entries[i]
            item = TwoLineAvatarIconListItem(
                text=entry['title'],
                secondary_text=entry['category'],
                on_release=lambda x, e=entry: self.open_detail_screen(e)
            )
            icon = IconLeftWidget(icon="book-open-variant")
            item.add_widget(icon)
            self.entries_list.add_widget(item)
            
        self._load_index = end_index
        # Если остались еще элементы, планируем следующую порцию
        if self._load_index < len(self.filtered_entries):
            Clock.schedule_once(self._load_batch, 0.05)
    
    def on_search_text(self, instance, value):
        """Поиск по записям с задержкой (Debounce)"""
        # Отменяем предыдущий запланированный поиск
        Clock.unschedule(self._perform_search)
        # Планируем новый поиск через 300мс
        Clock.schedule_once(lambda dt: self._perform_search(value), 0.3)

    def _perform_search(self, search_text):
        """Фактическая логика поиска"""
        search_text = search_text.lower()
        if not search_text:
            self.filtered_entries = [e for e in self.entries if self.current_category == "Все" or e['category'] == self.current_category]
        else:
            self.filtered_entries = [
                e for e in self.entries 
                if (self.current_category == "Все" or e['category'] == self.current_category)
                and (search_text in e['title'].lower() or search_text in e['content'].lower())
            ]
        self.update_entries_list()
    
    def show_category_menu(self, caller):
        """Показать меню категорий"""
        categories = ["Все"] + list(set([e['category'] for e in self.entries]))
        
        menu_items = [
            {
                "text": cat,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=cat: self.filter_by_category(x)
            }
            for cat in categories
        ]
        
        self.category_menu = MDDropdownMenu(
            caller=caller,
            items=menu_items,
            width_mult=4
        )
        self.category_menu.open()
    
    def filter_by_category(self, category):
        """Фильтрация по категории"""
        self.current_category = category
        self.category_menu.dismiss()
        self.on_search_text(None, self.search_field.text)
    
    def toggle_theme(self):
        """Переключение темы"""
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        self.save_settings()
    
    # ------------------------------------------
    # Навигация и управление состоянием
    # ------------------------------------------
    def open_detail_screen(self, entry):
        """Открыть экран деталей"""
        self.current_entry = entry
        
        self.detail_title.text = entry['title']
        self.detail_category.text = f"Категория: {entry['category']}"
        self.detail_date.text = f"Дата: {entry['date']}"
        self.detail_content.text = entry['content']
        
        self.root.current = 'detail'
    
    def open_add_screen(self):
        """Открыть экран добавления"""
        self.current_entry = None
        self.add_edit_toolbar.title = "Новая запись"
        
        self.title_field.text = ""
        self.category_field.text = "Общее"
        self.content_field.text = ""
        
        self.root.current = 'add_edit'
    
    def edit_current_entry(self):
        """Редактировать текущую запись"""
        if self.current_entry:
            self.add_edit_toolbar.title = "Редактирование"
            
            self.title_field.text = self.current_entry['title']
            self.category_field.text = self.current_entry['category']
            self.content_field.text = self.current_entry['content']
            
            self.root.current = 'add_edit'
    
    # ------------------------------------------
    # Функции добавления, редактирования и удаления (CRUD)
    # ------------------------------------------
    def save_entry(self):
        """Сохранить запись"""
        if not self.title_field.text.strip():
            self.show_alert("Ошибка", "Название не может быть пустым!")
            return
        
        if self.current_entry:
            # Редактирование
            self.current_entry['title'] = self.title_field.text
            self.current_entry['category'] = self.category_field.text
            self.current_entry['content'] = self.content_field.text
        else:
            # Новая запись
            new_id = max([e['id'] for e in self.entries], default=0) + 1
            new_entry = {
                "id": new_id,
                "title": self.title_field.text,
                "category": self.category_field.text,
                "content": self.content_field.text,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            self.entries.append(new_entry)
        
        self.save_data()
        self.filtered_entries = self.entries.copy()
        self.update_entries_list()
        self.go_back()
    
    def delete_current_entry(self):
        """Удалить текущую запись"""
        if not self.current_entry:
            return
        
        self.dialog = MDDialog(
            title="Удаление",
            text=f"Вы уверены, что хотите удалить '{self.current_entry['title']}'?",
            buttons=[
                MDFlatButton(
                    text="ОТМЕНА",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="УДАЛИТЬ",
                    on_release=lambda x: self.confirm_delete()
                )
            ]
        )
        self.dialog.open()
    
    def confirm_delete(self):
        """Подтверждение удаления"""
        self.entries = [e for e in self.entries if e['id'] != self.current_entry['id']]
        self.save_data()
        self.filtered_entries = self.entries.copy()
        self.update_entries_list()
        self.dialog.dismiss()
        self.go_back()
    
    # ------------------------------------------
    # Вспомогательные функции (Utils)
    # ------------------------------------------
    def show_alert(self, title, text):
        """Показать уведомление"""
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def go_back(self):
        """Вернуться назад"""
        self.root.current = 'main'


# ==========================================
# Точка входа в приложение
# ==========================================
if __name__ == '__main__':
    ReferenceApp().run()
