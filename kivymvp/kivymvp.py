from kivy.app import App
from kivy.base import EventLoop
from kivy.uix.screenmanager import Screen, ScreenManager


class Model(object):
    def __init__(self, name):
        self.name = name
        self.presenters = []
        self.data = {}

    # return data for id here
    def get(self, id):
        if id in self.data:
            self._get(id, self.data[id])
            return True
        else:
            return False

    def _get(self, id, data):
        self._notifyPresenters("get", id, data)

    # set data for id here
    def _set(self, id, data):
        self.data[id] = data

    def set(self, id, data):
        self._set(id, data)
        self._notifyPresenters("set", id, data)

    def _notifyPresenters(self, method, id, data):
        for p in self.presenters:
            p.modelEvent(self, (method, id, data))


# Transient Rest HTTP Model.
class RestModel(Model):
    # Request can be UrlRequest from kivy.network.urlrequest or UrlRequest specified to your needs.
    def __init__(self, name, Request):
        super(RestModel, self).__init__(name)
        self.Request = Request
        
    def get(self, id, url):
        def on_success(req, data, postproc=None):
            if postproc:
                data = postproc(id, data)
            self.set(id, data)
            self._get(id, data)
        def on_failure(req, data):
            self._notifyPresenters("get-failure", id, data)
        def on_error(req, data):
            self._notifyPresenters("get-error", id, data)
        inModel = super(RestModel, self).get(id)
        if not inModel:
            self.Request(url + str(id), method="GET", on_success=on_success,
                on_failure=on_failure, on_error=on_error)
    
    def post(self, url, data):
        def on_success(req, data, postproc=None):
            if postproc:
                data = postproc(data)
            self._notifyPresenters("post", None, data)
        def on_failure(req, data):
            self._notifyPresenters("post-failure", None, data)
        def on_error(req, data):
            self._notifyPresenters("post-error", None, data)
        req = self.Request(url, req_body=data, method="POST",
            on_success=on_success, on_failure=on_failure, on_error=on_error)

    def put(self, id, url, data):
        def on_success(req, data, postproc=None):
            if postproc:
                data = postproc(id, data)
            self._notifyPresenters("put", id, data)
        def on_failure(req, data):
            self._notifyPresenters("put-failure", id, data)
        def on_error(req, data):
            self._notifyPresenters("put-error", id, data)
        if data:
            self.Request(url + str(id), req_body=data, method="PUT",
                on_success=on_success, on_failure=on_failure, on_error=on_error)

    def delete(self, id, url):
        def on_success(req, data, postproc=None):
            if postproc:
                data = postproc(id, data)
            self._notifyPresenters("delete", id, data)
        def on_failure(req, data):
            self._notifyPresenters("delete-failure", id, data)
        def on_error(req, data):
            self._notifyPresenters("delete-error", id, data)
        self.Request(url + str(id), method="DELETE", on_success=on_success,
            on_failure=on_failure, on_error=on_error)


class View(Screen):
    def __init__(self, presenter, **kwargs):
        super(View, self).__init__(**kwargs)
        self.presenter = presenter

    # update view based on new data here
    def _update(self, data):
        pass

    def update(self, data):
        self._update(data)
        self.canvas.ask_update()

    def event(self, e):
        self.presenter.userEvent(e)

# A View is just a small wrapper around kivy screens; no need for lots of functionality here.


class Runnable(object):
    # hook for kivy's on_pause
    def onPause(self):
        return True

    # hook for kivy's on_resume
    def onResume(self):
        pass

    # hook for kivy's on_start
    def onStart(self):
        pass

    # hook for kivy's on_stop
    def onStop(self):
        pass

    # generic event from app controller or other presenter
    def receive(self, e):
        pass


class Presenter(Runnable):
    def __init__(self, ctrl, viewClass, models):
        self.bus = ctrl.bus
        self.view = viewClass(self, name=self._name())
        ctrl.sm.add_widget(self.view)
        self.models = {}
        for model in models:
            self.models[model.name] = model
            model.presenters.append(self)
            self.modelEvent(model)

    # provide name here
    def _name(self):
        raise Exception("not implemented")

    def emit(self, event):
        self.bus.emit(event)

    # associated view notifies us of user event, update model appropriately
    def userEvent(self, e):
        pass

    # model notfies us of update, refresh the view
    def modelEvent(self, model, e=None):
        pass


class AppController(Runnable):
    def __init__(self):
        class EventBus(object):
            def __init__(self):
                self.listeners = []

            def register(self, obj):
                self.listeners.append(obj)

            def emit(self, event):
                for listener in self.listeners:
                    listener.receive(event)

        self.bus = EventBus()
        self.bus.register(self)
        self.sm = ScreenManager()
        self.presenters = {}
        self.key_hooks = {}

        bus = self.bus
        sm = self.sm
        key_hooks = self.key_hooks

        class KivyMVPApp(App):
            def build(self):
                return sm
            def on_pause(self):
                for listener in bus.listeners:
                    if not listener.onPause():
                        return False
                return True
            def on_resume(self):
                for listener in bus.listeners:
                    listener.onResume()
            def on_start(self):
                EventLoop.window.bind(on_keyboard=self.hook_keyboard)
                for listener in bus.listeners:
                    listener.onStart()
            def on_stop(self):
                for listener in bus.listeners:
                    listener.onStop()
            def hook_keyboard(self, window, key, *largs):
                if key in key_hooks:
                    return key_hooks[key]()
                return True

        self.app = KivyMVPApp()

    def hook_key(self, key, func):
        self.key_hooks[key] = func

    def current(self):
        return self.sm.current

    def switch(self, name):
        self.sm.current = name

    def go(self, first):
        self.sm.current = first
        self.app.run()

    def add(self, pres):
        if pres._name() in self.presenters:
            raise Exception("presenter with name %s exists" % pres._name())
        self.presenters[pres._name()] = pres
        self.bus.register(pres)


if __name__ == '__main__':
    from kivy.graphics import Color, Rectangle
    from kivy.uix.button import Button
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.label import Label

    # Our app controller simply listens for "switch" events and switches between
    # the two presenters, if it receives one.
    class TestAppController(AppController):
        def receive(self, e):
            if e == "switch":
                for p in self.presenters:
                    if self.current() != p:
                        self.switch(p)
                        break

    ctrl = TestAppController()

    # Our model is a simple dictionary containing a single integer at key 0.
    model = Model("aSingleNumber")
    model.set(0, 0)

    # This is a very basic example. Of course we should not duplicate code
    # for such a small difference in functionality. It is just to outline
    # how the framework is intended to be used.

    # The black presenter listens for two user events.
    # If it receives "done" it signals "switch" to the app controller's event bus.
    # (Note: all presenters and the app controller are registered at the event bus
    #  and can response to events if required)
    # If it receives an "add" event it retrieves the current number from the model,
    # increments by one and puts it back into the model.
    # On receiving any event from the model it simply retrieves the currently stored
    # number and instructs the view to update based on it.
    class BlackPresenter(Presenter):
        def __init__(self, ctrl, viewClass, models):
            super(BlackPresenter, self).__init__(ctrl, viewClass, models)
            self.models["aSingleNumber"].get(0)

        def _name(self):
            return "black"

        def userEvent(self, e):
            if e == "done":
                self.emit("switch")
            elif e == "add":
                self.models["aSingleNumber"].set(0, self.number+1)

        def modelEvent(self, m, e=None):
            if e == None:
                return
            method, id_, data = e
            self.number = data
            self.view.update(str(data))

    # The white presenter listens for two user events.
    # If it receives "done" it signals "switch" to the app controller's event bus.
    # If it receives an "subtract" event it retrieves the current number from the model,
    # decrements by one and puts it back into the model.
    # On receiving any event from the model it simply retrieves the currently stored
    # number and instructs the view to update based on it.
    class WhitePresenter(Presenter):
        def __init__(self, ctrl, viewClass, models):
            super(WhitePresenter, self).__init__(ctrl, viewClass, models)
            self.models["aSingleNumber"].get(0)

        def _name(self):
            return "white"

        def userEvent(self, e):
            if e == "done":
                self.emit("switch")
            elif e == "subtract":
                self.models["aSingleNumber"].set(0, self.number-1)

        def modelEvent(self, m, e=None):
            if e == None:
                return
            method, id_, data = e
            self.number = data
            self.view.update(str(data))

    # This is just a simple layout with a background color such that we can easily
    # distinguish our two views.
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

    # The black view has a button "add" and a button "to_white" on a black background.
    # Pressing "add" triggers emits the event "add" and pressing "to white" triggers "done".
    # When it receives an update event it updates the label text with the new data.
    # Note that all kivy events should just trigger self.event with the appropriate data to
    # integrate into the MVP workflow.
    class BlackView(View):
        def __init__(self, presenter, **kwargs):
            super(BlackView, self).__init__(presenter, **kwargs)
            with self.canvas:
                f = ColorLayout((0,0,0,1))
                self.l = Label(text="TEST", size_hint=(1, 0.25), pos_hint={ "x":0, "y":0.8 },
                     color=(0.75, 0.75, 0.75, 1), font_size=60)
                f.add_widget(self.l)
                b = Button(text='add', font_size=20, size_hint=(1, 0.25),
                    pos_hint={ "x":0, "y":0.25 })
                b.bind(on_press=lambda x: self.event("add"))
                f.add_widget(b)
                b = Button(text='to white', font_size=20, size_hint=(1, 0.25))
                b.bind(on_press=lambda x: self.event("done"))
                f.add_widget(b)
                self.add_widget(f)

        def _update(self, data):
            self.l.text = data

    # The white view has a button "add" and a button "to_black" on a white background.
    # Pressing "add" triggers emits the event "add" and pressing "to black" triggers "done".
    # When it receives an update event it updates the label text with the new data.
    class WhiteView(View):
        def __init__(self, presenter, **kwargs):
            super(WhiteView, self).__init__(presenter, **kwargs)
            with self.canvas:
                f = ColorLayout((1,1,1,1))
                self.l = Label(text="TEST", size_hint=(1, 0.25), pos_hint={ "x":0, "y":0.8 },
                    color=(0.75, 0.75, 0.75, 1), font_size=60)
                f.add_widget(self.l)
                b = Button(text='subtract', font_size=20, size_hint=(1, 0.25),
                    pos_hint={ "x":0, "y":0.25 })
                b.bind(on_press=lambda x: self.event("subtract"))
                f.add_widget(b)
                b = Button(text='to black', font_size=20, size_hint=(1, 0.25))
                b.bind(on_press=lambda x: self.event("done"))
                f.add_widget(b)
                self.add_widget(f)

        def _update(self, data):
            self.l.text = data

    black_pres = BlackPresenter(ctrl, BlackView, [model])
    white_pres = WhitePresenter(ctrl, WhiteView, [model])

    ctrl.add(white_pres)
    ctrl.add(black_pres)

    # Start black.
    ctrl.go('black')
