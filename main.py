import os
import json
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput

# Android permissions (agar Android pe chale)
try:
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE,
                         Permission.WRITE_EXTERNAL_STORAGE])
except Exception:
    pass

ADMIN_PASSWORD = "Ajaj@petown77"
DATA_FILE = "nucleus_data.json"

LIGHT = dict(
    bg=(0.96, 0.96, 0.97, 1), surface=(1.0, 1.0, 1.0, 1.0),
    text=(0.10, 0.10, 0.15, 1), subtext=(0.42, 0.42, 0.48, 1),
    primary=(0.13, 0.55, 0.85, 1), danger=(0.90, 0.30, 0.30, 1),
    border=(0.85, 0.85, 0.88, 1), accent=(0.20, 0.75, 0.50, 1),
    header=(0.13, 0.55, 0.85, 1), header_text=(1, 1, 1, 1),
)
DARK = dict(
    bg=(0.08, 0.09, 0.12, 1), surface=(0.14, 0.15, 0.19, 1),
    text=(0.95, 0.95, 0.98, 1), subtext=(0.65, 0.68, 0.75, 1),
    primary=(0.25, 0.65, 0.95, 1), danger=(0.95, 0.40, 0.40, 1),
    border=(0.25, 0.27, 0.32, 1), accent=(0.30, 0.85, 0.60, 1),
    header=(0.18, 0.20, 0.28, 1), header_text=(1, 1, 1, 1),
)


class Theme:
    dark = False
    @classmethod
    def c(cls, k):
        return DARK[k] if cls.dark else LIGHT[k]


def storage_dir():
    try:
        return App.get_running_app().user_data_dir
    except Exception:
        return os.path.expanduser("~")


def download_dir():
    for p in ("/storage/emulated/0/Download", "/sdcard/Download"):
        try:
            if os.path.isdir(p):
                return p
        except Exception:
            pass
    return storage_dir()


class Report:
    def __init__(self, name, price, tube="", code=""):
        self.name = name
        self.price = float(price)
        self.tube = tube
        self.code = code

    def to_dict(self):
        return {"name": self.name, "price": self.price,
                "tube": self.tube, "code": self.code}

    @staticmethod
    def from_dict(d):
        return Report(d.get("name", ""), d.get("price", 0),
                      d.get("tube", ""), d.get("code", ""))


def save_reports(reports):
    try:
        with open(os.path.join(storage_dir(), DATA_FILE), "w") as f:
            json.dump([r.to_dict() for r in reports], f, indent=2)
        return True
    except Exception as e:
        print("save error:", e)
        return False


def load_reports():
    path = os.path.join(storage_dir(), DATA_FILE)
    if not os.path.exists(path):
        # first-run sample data (admin can edit/delete)
        return [
            Report("CBC", 250, "EDTA"),
            Report("CRP", 350, "Plain"),
            Report("ESR", 150, "EDTA"),
        ]
    try:
        with open(path) as f:
            return [Report.from_dict(d) for d in json.load(f)]
    except Exception as e:
        print("load error:", e)
        return []


class Toast(Popup):
    def __init__(self, text="", duration=1.8, **kw):
        super().__init__(title="", separator_height=0,
                         size_hint=(0.85, None), height=dp(70),
                         background_color=(0, 0, 0, 0.85),
                         auto_dismiss=True, **kw)
        self.content = Label(text=text, color=(1, 1, 1, 1), font_size=dp(14))
        Clock.schedule_once(lambda dt: self._safe_close(), duration)

    def _safe_close(self):
        try:
            self.dismiss()
        except Exception:
            pass


class TopBar(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(58),
                         padding=[dp(12), dp(6), dp(12), dp(6)], spacing=dp(10), **kw)
        with self.canvas.before:
            self._clr = Color(*Theme.c("header"))
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._on, size=self._on)

        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(logo_path):
            self.add_widget(Image(source=logo_path,
                                  size_hint=(None, None), size=(dp(42), dp(42))))

        title = Label(text="[b]Nucleus PRL[/b]", markup=True,
                      color=Theme.c("header_text"), font_size=dp(20),
                      halign="left", valign="middle")
        title.bind(size=lambda *a: setattr(title, "text_size", (title.width, None)))
        self.add_widget(title)

    def _on(self, *a):
        self._rect.pos = self.pos
        self._rect.size = self.size


class BottomNav(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(58), **kw)
        with self.canvas.before:
            self._clr = Color(*Theme.c("surface"))
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._on, size=self._on)
        for label, screen in (("Home", "home"), ("Cart", "cart"),
                              ("Admin", "admin"), ("Settings", "settings")):
            b = Button(text=label, background_normal="", background_color=(0, 0, 0, 0),
                       color=Theme.c("primary"), font_size=dp(13), bold=True)
            b.bind(on_release=lambda *_, s=screen: self._go(s))
            self.add_widget(b)

    def _on(self, *a):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _go(self, screen):
        app = App.get_running_app()
        app.sm.current = screen
        if screen == "home":
            app.refresh_home()
        elif screen == "cart":
            app.refresh_cart()
        elif screen == "admin":
            app.admin.refresh()


class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        with root.canvas.before:
            self._clr = Color(*Theme.c("bg"))
            self._rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._rect, "pos", root.pos),
                  size=lambda *a: setattr(self._rect, "size", root.size))

        self.search = TextInput(hint_text="Search report...", multiline=False,
                                size_hint_y=None, height=dp(48),
                                background_color=Theme.c("surface"),
                                foreground_color=Theme.c("text"),
                                hint_text_color=Theme.c("subtext"),
                                cursor_color=Theme.c("primary"),
                                padding=[dp(12), dp(12), dp(12), dp(12)],
                                font_size=dp(15))
        self.search.bind(text=lambda *a: self.refresh())
        root.add_widget(self.search)

        self.scroll = ScrollView()
        self.list_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        self.scroll.add_widget(self.list_box)
        root.add_widget(self.scroll)
        self.add_widget(root)

    def refresh(self):
        self.list_box.clear_widgets()
        app = App.get_running_app()
        q = self.search.text.strip().lower()
        items = app.reports
        if q:
            items = [r for r in items
                     if q in r.name.lower() or q in r.tube.lower() or q in r.code.lower()]
        if not items:
            self.list_box.add_widget(Label(text="No reports found.\nAdd reports from Admin panel.",
                                           color=Theme.c("subtext"), font_size=dp(14),
                                           size_hint_y=None, height=dp(80)))
            return
        for r in items:
            self.list_box.add_widget(self._row(r))

    def _row(self, r):
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(72),
                        padding=[dp(12), dp(8), dp(8), dp(8)], spacing=dp(6))
        with row.canvas.before:
            Color(*Theme.c("surface"))
            rect = Rectangle(pos=row.pos, size=row.size)
        row.bind(pos=lambda *a: setattr(rect, "pos", row.pos),
                 size=lambda *a: setattr(rect, "size", row.size))

        left = BoxLayout(orientation="vertical", size_hint_x=0.55)
        n = Label(text=r.name, color=Theme.c("text"), bold=True, font_size=dp(15),
                  halign="left", valign="middle")
        n.bind(size=lambda *a: setattr(n, "text_size", (n.width, None)))
        t = Label(text=(r.tube or "-"), color=Theme.c("subtext"),
                  font_size=dp(12), halign="left", valign="middle")
        t.bind(size=lambda *a: setattr(t, "text_size", (t.width, None)))
        left.add_widget(n)
        left.add_widget(t)
        row.add_widget(left)

        p = Label(text=f"Rs {r.price:.0f}", color=Theme.c("primary"), bold=True,
                  font_size=dp(16), size_hint_x=0.25,
                  halign="right", valign="middle")
        p.bind(size=lambda *a: setattr(p, "text_size", (p.width, None)))
        row.add_widget(p)

        add = Button(text="+", size_hint=(None, None), size=(dp(46), dp(46)),
                     background_normal="", background_color=Theme.c("primary"),
                     color=(1, 1, 1, 1), font_size=dp(22), bold=True)
        add.bind(on_release=lambda *_: App.get_running_app().add_to_cart(r))
        row.add_widget(add)
        return row


class CartScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        with root.canvas.before:
            self._clr = Color(*Theme.c("bg"))
            self._rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._rect, "pos", root.pos),
                  size=lambda *a: setattr(self._rect, "size", root.size))

        title = Label(text="[b]Cart[/b]", markup=True, color=Theme.c("text"),
                      size_hint_y=None, height=dp(34), font_size=dp(18))
        root.add_widget(title)

        self.scroll = ScrollView(size_hint_y=0.5)
        self.items_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        self.items_box.bind(minimum_height=self.items_box.setter("height"))
        self.scroll.add_widget(self.items_box)
        root.add_widget(self.scroll)

        totals = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(260),
                           padding=dp(10), spacing=dp(6))
        with totals.canvas.before:
            Color(*Theme.c("surface"))
            tr = Rectangle(pos=totals.pos, size=totals.size)
        totals.bind(pos=lambda *a: setattr(tr, "pos", totals.pos),
                    size=lambda *a: setattr(tr, "size", totals.size))

        self.total_label = Label(text="Total: Rs 0", color=Theme.c("text"),
                                 size_hint_y=None, height=dp(28), font_size=dp(15),
                                 halign="left", valign="middle")
        self.total_label.bind(size=lambda *a: setattr(self.total_label, "text_size",
                                                      (self.total_label.width, None)))
        totals.add_widget(self.total_label)

        drow = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(6))
        dl = Label(text="Discount %:", color=Theme.c("text"), size_hint_x=0.5,
                   font_size=dp(14), halign="left", valign="middle")
        dl.bind(size=lambda *a: setattr(dl, "text_size", (dl.width, None)))
        drow.add_widget(dl)
        self.discount_input = TextInput(text="0", multiline=False, input_filter="float",
                                        size_hint_x=0.5,
                                        background_color=Theme.c("bg"),
                                        foreground_color=Theme.c("text"),
                                        cursor_color=Theme.c("primary"),
                                        padding=[dp(8), dp(8), dp(8), dp(8)],
                                        font_size=dp(15))
        self.discount_input.bind(text=lambda *a: self.update_totals())
        drow.add_widget(self.discount_input)
        totals.add_widget(drow)

        self.disc_amt_label = Label(text="Discount: Rs 0", color=Theme.c("danger"),
                                    size_hint_y=None, height=dp(28), font_size=dp(14),
                                    halign="left", valign="middle")
        self.disc_amt_label.bind(size=lambda *a: setattr(self.disc_amt_label, "text_size",
                                                         (self.disc_amt_label.width, None)))
        totals.add_widget(self.disc_amt_label)

        self.final_label = Label(text="[b]Final: Rs 0[/b]", markup=True,
                                 color=Theme.c("accent"),
                                 size_hint_y=None, height=dp(40), font_size=dp(20),
                                 halign="left", valign="middle")
        self.final_label.bind(size=lambda *a: setattr(self.final_label, "text_size",
                                                      (self.final_label.width, None)))
        totals.add_widget(self.final_label)

        clear = Button(text="Clear Cart", size_hint_y=None, height=dp(42),
                       background_normal="", background_color=Theme.c("danger"),
                       color=(1, 1, 1, 1), font_size=dp(14), bold=True)
        clear.bind(on_release=lambda *_: App.get_running_app().clear_cart())
        totals.add_widget(clear)

        root.add_widget(totals)
        self.add_widget(root)

    def refresh(self):
        self.items_box.clear_widgets()
        app = App.get_running_app()
        if not app.cart:
            self.items_box.add_widget(Label(text="Cart is empty.",
                                            color=Theme.c("subtext"),
                                            size_hint_y=None, height=dp(60)))
        else:
            for i, r in enumerate(app.cart):
                self.items_box.add_widget(self._item_row(i, r))
        self.update_totals()

    def _item_row(self, idx, r):
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48),
                        padding=[dp(10), dp(6), dp(6), dp(6)], spacing=dp(6))
        with row.canvas.before:
            Color(*Theme.c("surface"))
            rect = Rectangle(pos=row.pos, size=row.size)
        row.bind(pos=lambda *a: setattr(rect, "pos", row.pos),
                 size=lambda *a: setattr(rect, "size", row.size))
        n = Label(text=r.name, color=Theme.c("text"), size_hint_x=0.6,
                  font_size=dp(14), halign="left", valign="middle")
        n.bind(size=lambda *a: setattr(n, "text_size", (n.width, None)))
        row.add_widget(n)
        p = Label(text=f"Rs {r.price:.0f}", color=Theme.c("primary"),
                  size_hint_x=0.25, font_size=dp(14), bold=True)
        row.add_widget(p)
        rm = Button(text="X", size_hint=(None, None), size=(dp(36), dp(36)),
                    background_normal="", background_color=Theme.c("danger"),
                    color=(1, 1, 1, 1), font_size=dp(14), bold=True)
        rm.bind(on_release=lambda *_: App.get_running_app().remove_from_cart(idx))
        row.add_widget(rm)
        return row

    def update_totals(self):
        app = App.get_running_app()
        total = sum(r.price for r in app.cart)
        try:
            d = float(self.discount_input.text or 0)
        except Exception:
            d = 0
        d = max(0, min(100, d))
        disc = total * d / 100.0
        final = total - disc
        self.total_label.text = f"Total: Rs {total:.2f}"
        self.disc_amt_label.text = f"Discount ({d:.0f}%): -Rs {disc:.2f}"
        self.final_label.text = f"[b]Final: Rs {final:.2f}[/b]"


class AdminScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.unlocked = False
        self.root_box = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        with self.root_box.canvas.before:
            self._clr = Color(*Theme.c("bg"))
            self._rect = Rectangle(pos=self.root_box.pos, size=self.root_box.size)
        self.root_box.bind(pos=lambda *a: setattr(self._rect, "pos", self.root_box.pos),
                           size=lambda *a: setattr(self._rect, "size", self.root_box.size))
        self.add_widget(self.root_box)
        self.show_lock()

    def show_lock(self):
        self.root_box.clear_widgets()
        box = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12),
                        size_hint=(1, None), height=dp(260))
        box.add_widget(Label(text="Admin Access", color=Theme.c("text"),
                             bold=True, font_size=dp(20),
                             size_hint_y=None, height=dp(40)))
        self.pwd = TextInput(hint_text="Enter password", password=True, multiline=False,
                             size_hint_y=None, height=dp(48),
                             background_color=Theme.c("surface"),
                             foreground_color=Theme.c("text"),
                             cursor_color=Theme.c("primary"),
                             padding=[dp(12), dp(12), dp(12), dp(12)])
        box.add_widget(self.pwd)
        btn = Button(text="Unlock", size_hint_y=None, height=dp(48),
                     background_normal="", background_color=Theme.c("primary"),
                     color=(1, 1, 1, 1), bold=True, font_size=dp(16))
        btn.bind(on_release=lambda *_: self.try_unlock())
        box.add_widget(btn)
        self.root_box.add_widget(box)

    def try_unlock(self):
        if self.pwd.text == ADMIN_PASSWORD:
            self.unlocked = True
            self.refresh()
        else:
            Toast(text="Wrong password!").open()

    def lock(self):
        self.unlocked = False
        self.show_lock()

    def refresh(self):
        if not self.unlocked:
            self.show_lock()
            return
        self.root_box.clear_widgets()

        header = BoxLayout(orientation="horizontal", size_hint_y=None,
                           height=dp(44), spacing=dp(6))
        title = Label(text="[b]Manage Reports[/b]", markup=True, color=Theme.c("text"),
                      font_size=dp(16), halign="left", valign="middle")
        title.bind(size=lambda *a: setattr(title, "text_size", (title.width, None)))
        header.add_widget(title)
        add = Button(text="+ Add", size_hint=(None, None), size=(dp(84), dp(38)),
                     background_normal="", background_color=Theme.c("accent"),
                     color=(1, 1, 1, 1), bold=True, font_size=dp(13))
        add.bind(on_release=lambda *_: self.open_form(None))
        header.add_widget(add)
        lk = Button(text="Lock", size_hint=(None, None), size=(dp(70), dp(38)),
                    background_normal="", background_color=Theme.c("danger"),
                    color=(1, 1, 1, 1), bold=True, font_size=dp(13))
        lk.bind(on_release=lambda *_: self.lock())
        header.add_widget(lk)
        self.root_box.add_widget(header)

        scroll = ScrollView()
        list_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        list_box.bind(minimum_height=list_box.setter("height"))
        scroll.add_widget(list_box)
        self.root_box.add_widget(scroll)

        app = App.get_running_app()
        if not app.reports:
            list_box.add_widget(Label(text="No reports yet. Click + Add.",
                                      color=Theme.c("subtext"),
                                      size_hint_y=None, height=dp(60)))
        for r in app.reports:
            list_box.add_widget(self._admin_row(r))

    def _admin_row(self, r):
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(60),
                        padding=[dp(10), dp(6), dp(6), dp(6)], spacing=dp(6))
        with row.canvas.before:
            Color(*Theme.c("surface"))
            rect = Rectangle(pos=row.pos, size=row.size)
        row.bind(pos=lambda *a: setattr(rect, "pos", row.pos),
                 size=lambda *a: setattr(rect, "size", row.size))
        info = BoxLayout(orientation="vertical", size_hint_x=0.55)
        n = Label(text=r.name, color=Theme.c("text"), font_size=dp(14), bold=True,
                  halign="left", valign="middle")
        n.bind(size=lambda *a: setattr(n, "text_size", (n.width, None)))
        s = Label(text=f"{r.tube or '-'}  |  Rs {r.price:.0f}",
                  color=Theme.c("subtext"), font_size=dp(12),
                  halign="left", valign="middle")
        s.bind(size=lambda *a: setattr(s, "text_size", (s.width, None)))
        info.add_widget(n)
        info.add_widget(s)
        row.add_widget(info)
        e = Button(text="Edit", size_hint=(None, None), size=(dp(64), dp(38)),
                   background_normal="", background_color=Theme.c("primary"),
                   color=(1, 1, 1, 1), font_size=dp(12), bold=True)
        e.bind(on_release=lambda *_: self.open_form(r))
        row.add_widget(e)
        d = Button(text="Del", size_hint=(None, None), size=(dp(60), dp(38)),
                   background_normal="", background_color=Theme.c("danger"),
                   color=(1, 1, 1, 1), font_size=dp(12), bold=True)
        d.bind(on_release=lambda *_: self.confirm_delete(r))
        row.add_widget(d)
        return row

    def open_form(self, existing):
        content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        content.add_widget(Label(text=("Edit Report" if existing else "Add Report"),
                                 color=Theme.c("text"), bold=True, font_size=dp(16),
                                 size_hint_y=None, height=dp(30)))
        name_in = TextInput(text=(existing.name if existing else ""),
                            hint_text="Report name (e.g., CBC)",
                            multiline=False, size_hint_y=None, height=dp(44),
                            background_color=Theme.c("surface"),
                            foreground_color=Theme.c("text"),
                            cursor_color=Theme.c("primary"))
        content.add_widget(name_in)
        price_in = TextInput(text=(str(existing.price) if existing else ""),
                             hint_text="Price (e.g., 250)", input_filter="float",
                             multiline=False, size_hint_y=None, height=dp(44),
                             background_color=Theme.c("surface"),
                             foreground_color=Theme.c("text"),
                             cursor_color=Theme.c("primary"))
        content.add_widget(price_in)
        tube_in = TextInput(text=(existing.tube if existing else ""),
                            hint_text="Tube / Sample type (e.g., EDTA)",
                            multiline=False, size_hint_y=None, height=dp(44),
                            background_color=Theme.c("surface"),
                            foreground_color=Theme.c("text"),
                            cursor_color=Theme.c("primary"))
        content.add_widget(tube_in)

        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        save_b = Button(text="Save", background_normal="",
                        background_color=Theme.c("accent"),
                        color=(1, 1, 1, 1), bold=True)
        cancel_b = Button(text="Cancel", background_normal="",
                          background_color=Theme.c("danger"),
                          color=(1, 1, 1, 1), bold=True)
        btn_row.add_widget(save_b)
        btn_row.add_widget(cancel_b)
        content.add_widget(btn_row)

        popup = Popup(title="", content=content, size_hint=(0.92, 0.62),
                      background_color=Theme.c("bg"),
                      separator_color=Theme.c("primary"))
        cancel_b.bind(on_release=lambda *_: popup.dismiss())

        def on_save(*a):
            name = name_in.text.strip()
            if not name:
                Toast(text="Enter name").open()
                return
            try:
                price = float(price_in.text.strip())
            except Exception:
                Toast(text="Invalid price").open()
                return
            tube = tube_in.text.strip()
            app = App.get_running_app()
            if existing:
                existing.name = name
                existing.price = price
                existing.tube = tube
            else:
                app.reports.append(Report(name, price, tube))
            app.save()
            popup.dismiss()
            self.refresh()
            app.refresh_home()

        save_b.bind(on_release=on_save)
        popup.open()

    def confirm_delete(self, r):
        content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        content.add_widget(Label(text=f"Delete '{r.name}'?",
                                 color=Theme.c("text"),
                                 size_hint_y=None, height=dp(40)))
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        yes = Button(text="Delete", background_normal="",
                     background_color=Theme.c("danger"),
                     color=(1, 1, 1, 1), bold=True)
        no = Button(text="Cancel", background_normal="",
                    background_color=Theme.c("primary"),
                    color=(1, 1, 1, 1), bold=True)
        row.add_widget(yes)
        row.add_widget(no)
        content.add_widget(row)
        popup = Popup(title="", content=content, size_hint=(0.85, 0.3),
                      background_color=Theme.c("bg"))
        no.bind(on_release=lambda *_: popup.dismiss())

        def do_del(*a):
            app = App.get_running_app()
            if r in app.reports:
                app.reports.remove(r)
            app.save()
            popup.dismiss()
            self.refresh()
            app.refresh_home()

        yes.bind(on_release=do_del)
        popup.open()


class SettingsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        with root.canvas.before:
            self._clr = Color(*Theme.c("bg"))
            self._rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._rect, "pos", root.pos),
                  size=lambda *a: setattr(self._rect, "size", root.size))
        self.root_box = root
        self.add_widget(root)
        self.refresh()

    def refresh(self):
        self.root_box.clear_widgets()
        self.root_box.add_widget(Label(text="[b]Settings[/b]", markup=True,
                                       color=Theme.c("text"),
                                       size_hint_y=None, height=dp(40),
                                       font_size=dp(20)))

        row = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(10),
                        padding=[dp(12), dp(6), dp(12), dp(6)])
        with row.canvas.before:
            Color(*Theme.c("surface"))
            rect = Rectangle(pos=row.pos, size=row.size)
        row.bind(pos=lambda *a: setattr(rect, "pos", row.pos),
                 size=lambda *a: setattr(rect, "size", row.size))
        lbl = Label(text="Dark Mode", color=Theme.c("text"), font_size=dp(15),
                    halign="left", valign="middle")
        lbl.bind(size=lambda *a: setattr(lbl, "text_size", (lbl.width, None)))
        row.add_widget(lbl)
        sw = Switch(active=Theme.dark, size_hint_x=None, width=dp(70))
        sw.bind(active=lambda *a: self.toggle_theme(sw.active))
        row.add_widget(sw)
        self.root_box.add_widget(row)

        exp = Button(text="Export Data to JSON (Download folder)",
                     size_hint_y=None, height=dp(52),
                     background_normal="", background_color=Theme.c("primary"),
                     color=(1, 1, 1, 1), bold=True, font_size=dp(14))
        exp.bind(on_release=lambda *_: self.do_export())
        self.root_box.add_widget(exp)

        imp = Button(text="Import Data from JSON",
                     size_hint_y=None, height=dp(52),
                     background_normal="", background_color=Theme.c("accent"),
                     color=(1, 1, 1, 1), bold=True, font_size=dp(14))
        imp.bind(on_release=lambda *_: self.do_import())
        self.root_box.add_widget(imp)

        self.root_box.add_widget(
            Label(text="Nucleus PRL\nOffline Laboratory Report Price List\n\nAdmin password protected",
                  color=Theme.c("subtext"), font_size=dp(12),
                  size_hint_y=None, height=dp(120))
        )

    def toggle_theme(self, val):
        if Theme.dark != val:
            Theme.dark = val
            App.get_running_app().rebuild_ui()

    def do_export(self):
        app = App.get_running_app()
        path = os.path.join(download_dir(), "nucleus_prl_reports.json")
        try:
            with open(path, "w") as f:
                json.dump([r.to_dict() for r in app.reports], f, indent=2)
            Toast(text=f"Exported to:\n{path}").open()
        except Exception as e:
            Toast(text=f"Export failed: {e}").open()

    def do_import(self):
        path = os.path.join(download_dir(), "nucleus_prl_reports.json")
        if not os.path.exists(path):
            Toast(text=f"File not found:\n{path}").open()
            return
        try:
            with open(path) as f:
                data = json.load(f)
            app = App.get_running_app()
            app.reports = [Report.from_dict(d) for d in data]
            app.save()
            app.refresh_home()
            Toast(text=f"Imported {len(app.reports)} reports").open()
        except Exception as e:
            Toast(text=f"Import failed: {e}").open()


class NucleusApp(App):
    def build(self):
        self.title = "Nucleus PRL"
        Window.clearcolor = Theme.c("bg")
        self.reports = load_reports()
        self.cart = []
        self.root_wrap = BoxLayout(orientation="vertical")
        self.build_ui()
        return self.root_wrap

    def build_ui(self):
        Window.clearcolor = Theme.c("bg")
        self.root_wrap.clear_widgets()

        self.root_wrap.add_widget(TopBar())

        self.sm = ScreenManager()
        self.home = HomeScreen(name="home")
        self.cart_s = CartScreen(name="cart")
        self.admin = AdminScreen(name="admin")
        self.settings = SettingsScreen(name="settings")
        self.sm.add_widget(self.home)
        self.sm.add_widget(self.cart_s)
        self.sm.add_widget(self.admin)
        self.sm.add_widget(self.settings)
        self.root_wrap.add_widget(self.sm)

        self.root_wrap.add_widget(BottomNav())

        self.refresh_home()
        self.refresh_cart()
        save_reports(self.reports)

    def rebuild_ui(self):
        current = self.sm.current if hasattr(self, "sm") else "home"
        self.build_ui()
        try:
            self.sm.current = current
        except Exception:
            pass

    def refresh_home(self):
        if hasattr(self, "home"):
            self.home.refresh()

    def refresh_cart(self):
        if hasattr(self, "cart_s"):
            self.cart_s.refresh()

    def add_to_cart(self, report):
        self.cart.append(report)
        self.refresh_cart()
        Toast(text=f"Added: {report.name}").open()

    def remove_from_cart(self, idx):
        if 0 <= idx < len(self.cart):
            self.cart.pop(idx)
        self.refresh_cart()

    def clear_cart(self):
        self.cart = []
        self.refresh_cart()

    def save(self):
        save_reports(self.reports)


if __name__ == "__main__":
    NucleusApp().run()
