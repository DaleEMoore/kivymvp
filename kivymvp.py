from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager


class EventBus(object):
    def __init__(self):
        self.listeners = []

    def register(self, obj):
        self.listeners.append(obj)

    # TODO: The bus should emit events only to potentiall interested parties, not globally.
    def emit(self, event):
        for listener in self.listeners:
            listener.receive(event)


class Model(object):
    def get(self, id):
        raise Exception("not implemented")

    def set(self, id, data):
        raise Exception("not implemented")

class DictModel(Model):
    def __init__(self):
        self.data = {}

    def get(self, id):
        if id in self.data.keys():
            return self.data[id]
        else:
            return None

    def set(self, id, data):
        self.data[id] = data

# e.g. for MoviesModel you can just subclass DictModel and overload get, set
# s.t. you call super on get, if no hit, then fallback to http and call set of DictModel with result


class View(Screen):
    def __init__(self, presenter, **kwargs):
        super(View, self).__init__(**kwargs)
        self.presenter = presenter

    def emit(self, event):
        print "view emit:", event
        self.presenter.receive(event)

# a View is just a small wrapper around kivy screens; no need for lots of functionality here.


class Presenter(object):
    def __init__(self, ctrl, viewClass, model):
        self.viewClass = viewClass
        self.model = model
        self.bus = ctrl.bus

    def emit(self, event):
        self.bus.emit(event)

    def receive(self, e):
        raise Exception("not implemented")


class AppController(object):
    def __init__(self):
        self.bus = EventBus()
        self.bus.register(self)
        self.sm = ScreenManager()
        self.presenters = {}
        sm = self.sm

        class KivyMVPApp(App):
            def build(self):
                return sm
            def on_pause(self):
                pass
            def on_resume(self):
                pass

        self.app = KivyMVPApp()

    def _init_view(self, name):
        pres = self.presenters[name]
        pres.view = pres.viewClass(pres, name=name)
        print pres.view
        self.sm.add_widget(pres.view)

    def go(self, firstView):
        for pres in self.presenters:
            print "INIT *** " + pres
            self._init_view(pres)
        self.sm.current = firstView
        self.app.run()

    def receive(self, e):
        raise Exception("not implemented")

    def add(self, name, pres):
        if name in self.presenters:
            raise Exception("presenter with name %s exists" % name)
        self.presenters[name] = pres
        self.bus.register(pres)


if __name__ == '__main__':
    import time
    from kivy.graphics import Color, Rectangle
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.button import Button

    class TestAppController(AppController):
        def receive(self, e):
            print "testapp receive:", e
            if e == "switch":
                for p in self.presenters:
                    if self.sm.current != p:
                        self.sm.current = p
                        break

    ctrl = TestAppController()

    # TODO: use model in example
    model = DictModel()
    model.set(1, "string a")
    model.set(2, "string b")

    # These are very simple presenters in this example.
    class BlackPresenter(Presenter):
        def receive(self, e):
            print "black_pres receive:", e
            if e == "done":
                self.emit("switch")

    class WhitePresenter(Presenter):
        def receive(self, e):
            print "white_pres receive:", e
            if e == "done":
                self.emit("switch")

    class ColorLayout(FloatLayout):
        def __init__(self, color, **kwargs):
            super(ColorLayout, self).__init__(**kwargs)
            with self.canvas.before:
                Color(color[0], color[1], color[2], color[3])
                self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

        def _update_rect(self, instance, value):
            self.rect.pos = instance.pos
            self.rect.size = instance.size

    class BlackView(View):
        def __init__(self, presenter, **kwargs):
            super(BlackView, self).__init__(presenter, **kwargs)
            with self.canvas:
                f = ColorLayout((0,0,0,1))
                b = Button(text='to white', font_size=20, size_hint=(1, 0.25))
                b.bind(on_press=lambda x: self.emit("done"))
                f.add_widget(b)
                self.add_widget(f)

    class WhiteView(View):
        def __init__(self, presenter, **kwargs):
            super(WhiteView, self).__init__(presenter, **kwargs)
            with self.canvas:
                f = ColorLayout((1,1,1,1))
                b = Button(text='to black', font_size=20, size_hint=(1, 0.25))
                b.bind(on_press=lambda x: self.emit("done"))
                f.add_widget(b)
                self.add_widget(f)

    black_pres = BlackPresenter(ctrl, BlackView, model)
    white_pres = WhitePresenter(ctrl, WhiteView, model)

    # Instantiating the view triggers the display unfortunately, i.e. we can see
    # when starting the white view briefly. This should be fixed either by
    # not instantiating before actually viewing s.th. or in some other way.
    ctrl.add('white', white_pres)
    ctrl.add('black', black_pres)

    ctrl.go('black')