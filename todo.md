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

communication load between hosts.
Host role inference
-> Host icon should be based on the role.

## Generic

All hosts with ips only outside the local ip ranges (10.0.0.0–10.255.255.255, 172.16.0.0–172.31.255.255, and 192.168.0.0–192.168.255.255) should mark the hosts as external. These should be togglable in settings.

## UI

add search bar, to search for IP, hostnames
also add filtering by subnet, roles, external/internal

hovering over host, gives (hostname, IP, roles)

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
