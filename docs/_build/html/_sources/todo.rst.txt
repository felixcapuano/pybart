TODO list
=========

**27/03/2020**

- The MYB game has been modified to send trigger using zmq. But when the
  application quit, it crash. The issue seems to come from the closing of the
  context or/and the socket (location : Assets/Scripts/Generic/TriggerSender.cs)
  I tried a lot of things but none were easy to set up in the short term.
- Because of coronavirus I cannot test syncronize the trigger send using ZMQ on
  the EEG signal. In fact, with parallel port, this sycronization was made by
  BrainVision Recorder. Do do the syncronisation you have to run the game in
  both mode. Then it's possible to compare when of the to trigger is captured
  by pybart. I do it quickly and calculate a shift of ~50ms. But this result is
  probably depend on the machine.
