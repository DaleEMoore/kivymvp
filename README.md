# kivymvp
ui framework for kivy following the MVP pattern

## why use it
It provides the M and P for Kivy's V.

## getting started
Just look at kivymvp.py for a simple example.

## how does it work
Views are essentially Kivy screens. They emit user events to and listen for redraw events from their presenter.

Presenters have a set of models at their disposal. They listen to model updates and trigger redraws of their view when needed. They listen to user events from the view and update models as necessary.

Models are just any kind of data storage. They provide CRUD operations and notify presenters using them of changes in data.

## roadmap
As necessary. We are currently building an app using kivymvp and will see how it develops.

## requirements
Kivy is of course required. It is not listed in install requirements for setup tools to avoid messing around with setups which use kivy separate from their main python distribution.
