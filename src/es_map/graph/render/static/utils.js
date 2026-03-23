export function padHull(hull, padding) {
  const cx = d3.mean(hull, d => d[0]);
  const cy = d3.mean(hull, d => d[1]);

  return hull.map(([x, y]) => {
    const dx = x - cx;
    const dy = y - cy;
    const len = Math.sqrt(dx * dx + dy * dy) || 1;
    return [x + (dx / len) * padding, y + (dy / len) * padding];
  });
}
