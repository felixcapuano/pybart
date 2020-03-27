Tutorial
========

The configuration panel is divided in differents section.

To lauch the application go to the pybart folder an use the folowing command :

.. code-block:: 

  python -m pybart.run

.. image:: img/configpanel.png

------
Source
------

The source configure offers two choices:

- BrainVision Recorder mode is use to real-time EEG signal acquisition.
  This mode need an address and a port. If you running BrainVision on the same
  machine address has to be (127.0.0.1). The port is determine by BrainVision
  Recorder and differs on each machine.
 
- Simulate mode allow you to use a ".vhdr" file (BrainVision record file format)
  to simulate the streaming from a previously recorded session.

------
Filter
------

EEG signal is filtered by a passband filter.
You can set the high and low frequency.

-------
Trigger
-------

To understand this part I have to explain how the program work.
So when pybart is running BrainVision Recorder send a continuous stream.
Pybart receive the signal and wait trigger from the game.
This part configure this triggers.

The white table set some important parameter:

- **label :** To be detected by pybart the triggers label has to be registered in
  this configuration part.
- **right/left sweep :** This 2 values are the time of the EEG signal keeped before and
  after one trigger is captured by pybart. The 2 values are in seconds. This
  2 values added give the period of the epoch.
- **stack :** This value is often unnecessary. If this value is "1" pybart will
  drop epochs one by one. is you want stacked epoch you can modify this
  value. This will give to you epoch matrix size (time x channel x stack).

The triggers scrolling menu on the top is use to select a saved configuration.
The "configuration.json file allow you to add you own configuration setup.

.. code-block::

  {
      "Config example":
      {
          "label": { 
              "right_sweep": 0.5,
              "left_sweep": 0.5,
              "max_stock": 1
          },
          ...
  }

--------
Pipeline
--------

The pipeline scrolling menu allow you two select the `pipeline`_ used.
Currently there is only one pipeline developed working with Myb game

In this section you can setup the current pipeline thanks to the settings button.
This will open the pipeline setting.


Let take the Myb pipeline as example.


- The first part is a tool generating calibration file.
- The seconds is to select the calibration file you want to use.

.. image:: img/myb_setting.png

