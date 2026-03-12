from es_map.analysis.models import SubnetRegistry


def assign_subnet_parents(registry: SubnetRegistry) -> None:
    """Assign parent relationships between subnets using CIDR containment."""

    subnets = list(registry._subnets.values())

    subnets.sort(key=lambda s: s.network.prefixlen)

    candidates = []

    for subnet in subnets:
        subnet.parent = None

        for parent in reversed(candidates):
            if subnet.network.subnet_of(parent.network):
                subnet.parent = parent
                parent.child_subnets.append(subnet)
                break

        candidates.append(subnet)
