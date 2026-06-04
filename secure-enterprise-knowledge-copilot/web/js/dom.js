export function byId(id) {
  const node = document.getElementById(id);
  if (!node) {
    throw new Error(`Missing DOM node: ${id}`);
  }
  return node;
}

export function clear(node) {
  node.replaceChildren();
}

export function element(tagName, options = {}, children = []) {
  const node = document.createElement(tagName);
  if (options.className) {
    node.className = options.className;
  }
  if (options.textContent !== undefined) {
    node.textContent = String(options.textContent);
  }
  if (options.htmlFor) {
    node.htmlFor = options.htmlFor;
  }
  if (options.href) {
    node.href = options.href;
  }
  if (options.dataset) {
    Object.entries(options.dataset).forEach(([key, value]) => {
      node.dataset[key] = value;
    });
  }
  children.forEach((child) => node.append(child));
  return node;
}

export function tag(label, tone = "") {
  return element("span", {
    className: ["tag", tone].filter(Boolean).join(" "),
    textContent: label,
  });
}

export function renderList(container, items, renderItem, emptyText) {
  clear(container);
  if (!items.length) {
    container.append(element("div", { className: "item muted", textContent: emptyText }));
    return;
  }
  items.forEach((item) => container.append(renderItem(item)));
}
