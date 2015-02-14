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
        self.presenter = presenter
        super(View, self).__init__(**kwargs)

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

    def _init_view(self, presName):
        pres = self.presenters[presName]
        pres.view = pres.viewClass(pres, name=presName)
        self.sm.add_widget(pres.view)

    def go(self, firstView):
        self.sm.current = firstView
        self.app.run()

    def receive(self, e):
        raise Exception("not implemented")

    def add(self, name, pres):
        if name in self.presenters.keys():
            raise Exception("presenter with name %s exists" % name)
        self.presenters[name] = pres
        self.bus.register(pres)
        self._init_view(name)


if __name__ == '__main__':
    import time
    from kivy.graphics import Color

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

    class BlackView(View):
        def __init__(self, presenter, **kwargs):
            super(BlackView, self).__init__(presenter, **kwargs)
            with self.canvas.before:
                Color(0, 0, 0, 1)

    class WhiteView(View):
        def __init__(self, presenter, **kwargs):
            super(WhiteView, self).__init__(presenter, **kwargs)
            with self.canvas.before:
                Color (1, 1, 1, 1)

    black_pres = BlackPresenter(ctrl, BlackView, model)
    white_pres = WhitePresenter(ctrl, WhiteView, model)

    ctrl.add('black', black_pres)
    ctrl.add('white', white_pres)

    ctrl.go('black')