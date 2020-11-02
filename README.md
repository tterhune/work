# AFC Tools

## What is this?

* This also project also interacts with your Aruba switch fabric.

* You can:

    * Configure and discover a brand new fabric of switches

    * You can display your fabric of switches and their status

    * You can configure _AFC QoS policies_ and _qualifiers_

    * You can apply _AFC policies_ and _qualifiers_ to _LAGs_ and _Ports_

    * You can display the current _policy_ and _classifier_ configuration of your Aruba switches

    * You can display AFC learned _MAC attachments_ and also what was learned on your Aruba switches

## Fabrics and Switches

To display switch information:

*display-switches* [afc-hostname]

NOTE: if you do not pass in an _afc-hostname_ the script assumes _localhost_


## MAC Attachments

To display both AFC and switch MAC attachments:

*display-macs* [afc-hostname]


NOTE: if you do not pass in an _afc-hostname_ the script assumes _localhost_

## LLDP/CDP Neighbors

To display both AFC and switch LLDP/CDP neighbors:

*display-neighbors* [afc-hostname]


NOTE: if you do not pass in an _afc-hostname_ the script assumes _localhost_


## Policies and Classifiers


