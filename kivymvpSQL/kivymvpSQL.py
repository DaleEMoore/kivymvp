#!/usr/bin/env python3

from kivy.app import App
from kivy.base import EventLoop
from kivy.uix.screenmanager import Screen, ScreenManager


class Model(object):
    def __init__(self, name):
        print("Model.__init__()")
        self.name = name
        self.presenters = []
        self.data = {}

    # return data for id here
    def get(self, id, callback=None, **cb_kwargs):
        print("Model.get()")
        if id in self.data:
            self._get(id, self.data[id], callback, **cb_kwargs)
            return True
        else:
            callback(None)
            return False

    def _get(self, id, data, callback, **cb_kwargs):
        print("Model._get()")
        if callback:
            callback((id, data), **cb_kwargs)

    # set data for id here
    def _set(self, id, data):
        print("Model._set()")
        self.data[id] = data

    def set(self, id, data):
        print("Model.set()")
        self._set(id, data)
        self._notifyPresenters("set", id, data)

    def _notifyPresenters(self, method, id, data):
        print("Model._notifyPresenters()")
        for p in self.presenters:
            p.modelEvent(self, (method, id, data))


# Transient Rest HTTP Model.
class RestModel(Model):
    # Request can be UrlRequest from kivy.network.urlrequest or UrlRequest specified to your needs.
    def __init__(self, name, Request):
        print("RestModel.__init__()")
        super(RestModel, self).__init__(name)
        self.Request = Request
        
    def get(self, id, url, callback=None, **cb_kwargs):
        print("RestModel.get()")
        def on_success(req, data):
            self.set(id, data)
            self._get(id, data, callback, **cb_kwargs)
        def on_failure(req, data):
            self._notifyPresenters("get-failure", id, data)
        def on_error(req, data):
            self._notifyPresenters("get-error", id, data)
        inModel = super(RestModel, self).get(id, callback, **cb_kwargs)
        if not inModel:
            self.Request(url + str(id), method="GET", on_success=on_success,
                on_failure=on_failure, on_error=on_error)
    
    def post(self, url, data):
        print("RestModel.post()")
        def on_success(req, data):
            self._notifyPresenters("post", None, data)
        def on_failure(req, data):
            self._notifyPresenters("post-failure", None, data)
        def on_error(req, data):
            self._notifyPresenters("post-error", None, data)
        req = self.Request(url, req_body=data, method="POST",
            on_success=on_success, on_failure=on_failure, on_error=on_error)

    def put(self, id, url, data, callback=None, **cb_kwargs):
        print("RestModel.put()")
        def on_success(req, data):
            self._notifyPresenters("put", id, data)
            if callback:
                callback(id, data, **cb_kwargs)
        def on_failure(req, data):
            self._notifyPresenters("put-failure", id, data)
        def on_error(req, data):
            self._notifyPresenters("put-error", id, data)
        if data:
            self.Request(url + str(id), req_body=data, method="PUT",
                on_success=on_success, on_failure=on_failure, on_error=on_error)

    def delete(self, id, url, callback=None, **cb_kwargs):
        print("RestModel.delete()")
        def on_success(req, data):
            print("RestModel.delete.on_success()")
            self._notifyPresenters("delete", id, data)
            if callback:
                callback(id, data, **cb_kwargs)
        def on_failure(req, data):
            print("RestModel.delete.on_failure()")
            self._notifyPresenters("delete-failure", id, data)
        def on_error(req, data):
            print("RestModel.delete.on_error()")
            self._notifyPresenters("delete-error", id, data)
        self.Request(url + str(id), method="DELETE", on_success=on_success,
            on_failure=on_failure, on_error=on_error)


class View(Screen):
    def __init__(self, presenter, **kwargs):
        print("View.__init__()")
        super(View, self).__init__(**kwargs)
        self.presenter = presenter

    # update view based on new data here
    def _update(self, data):
        print("View.update()")
        pass

    def update(self, data):
        print("View.data()")
        self._update(data)
        self.canvas.ask_update()

    def event(self, e):
        print("View.event()")
        self.presenter.userEvent(e)

# A View is just a small wrapper around kivy screens; no need for lots of functionality here.


class Runnable(object):
    # hook for kivy's on_pause
    def onPause(self):
        print("Runnable.onPause()")
        return True

    # hook for kivy's on_resume
    def onResume(self):
        print("Runnable.onResume()")
        pass

    # hook for kivy's on_start
    def onStart(self):
        print("Runnable.onStart()")
        pass

    # hook for kivy's on_stop
    def onStop(self):
        print("Runnable.onStop()")
        pass

    # generic event from app controller or other presenter
    def receive(self, e):
        print("Runnable.receive()")
        pass


class Presenter(Runnable):
    def __init__(self, ctrl, viewClass, models):
        print("Presenter.__init__()")
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
        print("Presenter._name()")
        raise Exception("not implemented")

    def emit(self, event):
        print("Presenter.emit()")
        self.bus.emit(event)

    # associated view notifies us of user event, update model appropriately
    def userEvent(self, e):
        print("Presenter.userEvent()")
        pass

    # model notfies us of update, refresh the view
    def modelEvent(self, model, e=None):
        print("Presenter.modelEvent()")
        pass


class AppController(Runnable):
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("AppController.__exit__()")
        pass
    def __init__(self):
        class EventBus(object):
            def __init__(self):
                print("AppController.__init__.EventBus.__init__()")
                self.listeners = []

            def register(self, obj):
                print("AppController.__init__.EventBus.register()")
                self.listeners.append(obj)

            def emit(self, event):
                print("AppController.__init__.EventBus.emit()")
                for listener in self.listeners:
                    listener.receive(event)

        print("AppController.__init__()")
        self.bus = EventBus()
        self.bus.register(self)
        self.sm = ScreenManager()
        self.presenters = {}
        self.key_hooks = {}

        bus = self.bus
        sm = self.sm
        key_hooks = self.key_hooks

        class KivyMVPsqlApp(App):
            def build(self):
                print("AppController.__init__.KivyMVPsqlApp.build()")
                return sm
            def on_pause(self):
                print("AppController.__init__.KivyMVPsqlApp.on_pause()")
                for listener in bus.listeners:
                    if not listener.onPause():
                        return False
                return True
            def on_resume(self):
                print("AppController.__init__.KivyMVPsqlApp.on_resume()")
                for listener in bus.listeners:
                    listener.onResume()
            def on_start(self):
                print("AppController.__init__.KivyMVPsqlApp.on_start()")
                EventLoop.window.bind(on_keyboard=self.hook_keyboard)
                for listener in bus.listeners:
                    listener.onStart()
            def on_stop(self):
                print("AppController.__init__.KivyMVPsqlApp.on_stop()")
                for listener in bus.listeners:
                    listener.onStop()
            def hook_keyboard(self, window, key, *largs):
                print("AppController.__init__.KivyMVPsqlApp.hook_keyboard()")
                if key in key_hooks:
                    return key_hooks[key]()
                return True

        self.app = KivyMVPsqlApp()

    def hook_key(self, key, func):
        print("AppController.hook_key()")
        self.key_hooks[key] = func

    def current(self):
        print("AppController.current()")
        return self.sm.current

    def switch(self, name):
        print("AppController.switch()")
        self.sm.current = name

    def go(self, first):
        print("AppController.go()")
        self.sm.current = first
        self.app.run()

    def add(self, pres):
        print("AppController.add()")
        if pres._name() in self.presenters:
            raise Exception("presenter with name %s exists" % pres._name())
        self.presenters[pres._name()] = pres
        self.bus.register(pres)

def main():
    print("main()")
    from kivy.graphics import Color, Rectangle
    from kivy.uix.button import Button
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.label import Label

    # Our app controller simply listens for "switch" events and switches between
    # the two presenters, if it receives one.
    class TestAppController(AppController):
        def receive(self, e):
            print("__main__.TestAppController.receive()")
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
    # and can response to events if required)
    # If it receives an "add" event it retrieves the current number from the model,
    # increments by one and puts it back into the model.
    # On receiving any event from the model it simply retrieves the currently stored
    # number and instructs the view to update based on it.
    class BlackPresenter(Presenter):
        def _name(self):
            print("__main__.BlackPresenter()")
            return "black"

        def userEvent(self, e):
            print("__main__.userEvent()")
            if e == "done":
                self.emit("switch")
            elif e == "add":
                self.models["aSingleNumber"].get(0, self.add)

        def add(self, response):
            print("__main__.add()")
            if response:
                (id, data) = response
                self.models["aSingleNumber"].set(id, data+1)
            
        def modelEvent(self, m, e=None):
            print("__main__.modelEvent()")
            if e == None:
                return
            method, id, data = e
            self.view.update(str(data))

    # The white presenter listens for two user events.
    # If it receives "done" it signals "switch" to the app controller's event bus.
    # If it receives an "subtract" event it retrieves the current number from the model,
    # decrements by one and puts it back into the model.
    # On receiving any event from the model it simply retrieves the currently stored
    # number and instructs the view to update based on it.
    class WhitePresenter(Presenter):
        def _name(self):
            print("__main__.WhitePresenter.name()")
            return "white"

        def userEvent(self, e):
            print("__main__.WhitePresenter.userEvent()")
            if e == "done":
                self.emit("switch")
            elif e == "subtract":
                self.models["aSingleNumber"].get(0, self.subtract)
                
        def subtract(self, response):
            print("__main__.WhitePresenter.subtract()")
            if response:
                (id, data) = response
                self.models["aSingleNumber"].set(id, data-1)

        def modelEvent(self, m, e=None):
            print("__main__.WhitePresenter.modelEvent()")
            if e == None:
                return
            method, id, data = e
            self.view.update(str(data))

    # This is just a simple layout with a background color such that we can easily
    # distinguish our two views.
    class ColorLayout(FloatLayout):
        def __init__(self, color, **kwargs):
            print("__main__.ColorLayout.__init__()")
            super(ColorLayout, self).__init__(**kwargs)
            with self.canvas.before:
                Color(color[0], color[1], color[2], color[3])
                self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

        def _update_rect(self, instance, value):
            print("__main__.ColorLayout._update_rect()")
            self.rect.pos = instance.pos
            self.rect.size = instance.size

    # The black view has a button "add" and a button "to_white" on a black background.
    # Pressing "add" triggers emits the event "add" and pressing "to white" triggers "done".
    # When it receives an update event it updates the label text with the new data.
    # Note that all kivy events should just trigger self.event with the appropriate data to
    # integrate into the MVP workflow.
    class BlackView(View):
        def __init__(self, presenter, **kwargs):
            print("__main__.BlackView.__init__()")
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
            print("__main__.BlackView._update()")
            self.l.text = data

    # The white view has a button "add" and a button "to_black" on a white background.
    # Pressing "add" triggers emits  the event "add" and pressing "to black" triggers "done".
    class WhiteView(View):
        def __init__(self, presenter, **kwargs):
            print("__main__.WhiteView.__init__()")
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
            print("__main__.WhiteView._update()")
            self.l.text = data

    black_pres = BlackPresenter(ctrl, BlackView, [model])
    white_pres = WhitePresenter(ctrl, WhiteView, [model])

    ctrl.add(white_pres)
    ctrl.add(black_pres)

    # Start black.
    ctrl.go('black')

if __name__ == '__main__':
    print("kivymvpSQL.__main__()")
    main()
