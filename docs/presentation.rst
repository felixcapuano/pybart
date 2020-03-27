Presentation
============

Pybart is organized around three main classes:

 - The "ConfigPanel" is the main application.
 - The "StreamEngine" use `pyacq`_ to manage the BrainVision stream and triggers from the game and return epoch.
 - The pipeline is suitable for game. It process epoch and make links between pybart and the game.
  
.. _pyacq: https://github.com/pyacq/pyacq
