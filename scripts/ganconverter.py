import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

tree = ET.parse("Planeringsschema.gan")
root = tree.getroot()


def compute_end(start_str, duration):
    start_date = datetime.strptime(start_str, "%Y-%m-%d")
    end_date = start_date + timedelta(days=int(duration) - 1)
    return end_date.strftime("%Y-%m-%d")


tasks = []

for task in root.findall(".//task"):
    name = task.get("name", "Unnamed Task")
    start = task.get("start")
    duration = task.get("duration")

    if start is None or duration is None:
        print(f"Skipping task '{name}' due to missing start or duration")
        continue

    end = compute_end(start, duration)
    tasks.append((name, start, end))

# Output LaTeX pgfgantt code
print(
    r"\begin{ganttchart}[hgrid, vgrid, time slot format=isodate]{2026-02-01}{2026-06-01}"
)
print(r"\gantttitlecalendar{month=name, week} \\")

for name, start, end in tasks:
    print(f"\\ganttbar{{{name}}}{{{start}}}{{{end}}} \\\\")

print(r"\end{ganttchart}")
