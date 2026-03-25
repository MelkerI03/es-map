# Graphing

## Settings

- dark mode?
- show subnets?
- recency?
- Show hostnames?

## Forces

Pull clients out of the center, decreasing with the distance from the center.

## Generic

All hosts outside the local ip ranges (10.0.0.0–10.255.255.255, 172.16.0.0–172.31.255.255, and 192.168.0.0–192.168.255.255) should mark the hosts as external. These should be togglable in settings.

Host icon should be based on the hostname, if it contains client or server, it gets that icon. If not, set sensible default.

Infer roles from port usage. A host can have multiple roles

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

Start writing :-)
