# Graphing

## Settings

- dark mode?
- show subnets?
- recency?
- Show hostnames?

## Forces

Pull clients out of the center, decreasing with the distance from the center.

## Information

Operating system.
Agents installed?

Communication load between hosts.
Host role inference
-> Host icon should be based on the role.

## Generic

All hosts with ips only outside the local ip ranges (10.0.0.0–10.255.255.255, 172.16.0.0–172.31.255.255, and 192.168.0.0–192.168.255.255) should mark the hosts as external. These should be togglable in settings.

Data should be continuously gathered if connected to an elasticsearch instance. If connection is closed, this should be ignored.

## UI

Add search bar, to search for IP, hostnames
Also add filtering by subnet, roles, external/internal

Hovering over host, gives (hostname, IP, roles).

Connections are shown on host selection.

# Code base

## Testing

All components should be rigorously tested.
Both unit tests and system wide.
pytest

# Thesis

## Title

Passiv logganalys för nätverkskartläggning

## Subtitle

Design, implementation och utvärdering av ett system för att inferera nätverkstopologi från passiva loggkällor
