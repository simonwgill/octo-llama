octo-llama
==========

Basic Python PaaS for experimentation

Desgned for Ubuntu Server 12.04 Precise Pangolin.

Usage
=====

1. Install necessary packages using install.sh

Development
===========

Using example_producer and example_consumer as guidelines, subclass Llama and override 

Currently, you will also need to write a harness script like run_brokerage_standalone.py to initialise the PikaPublisher and load the Llama subclass.
