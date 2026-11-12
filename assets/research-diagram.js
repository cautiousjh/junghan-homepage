// Highlight a connection on hover, keyboard focus, or a persistent touch/click.
document.querySelectorAll('.research-diagram').forEach((diagram) => {
  // Transparent layers must not stack after the full image has loaded.
  const fullImage = diagram.querySelector('.image-full');
  const preview = diagram.querySelector('.image-preview');
  const finishImage = () => {
    if (preview && fullImage.naturalWidth > 0) preview.hidden = true;
  };
  if (fullImage) {
    fullImage.addEventListener('load', finishImage);
    if (fullImage.complete) finishImage();
  }
  let selected = '';
  const buttons = [...diagram.querySelectorAll('button[data-route]')];
  const highlight = (key) => { diagram.dataset.highlight = key || ''; };
  const select = (key) => {
    selected = selected === key ? '' : key;
    buttons.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.route === selected)));
    highlight(selected);
  };
  diagram.querySelectorAll('[data-route]').forEach((element) => {
    element.addEventListener('pointerenter', () => highlight(element.dataset.route));
    element.addEventListener('pointerleave', () => highlight(selected));
    element.addEventListener('focus', () => highlight(element.dataset.route));
    element.addEventListener('blur', () => highlight(selected));
    element.addEventListener('click', () => select(element.dataset.route));
  });
  diagram.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      selected = '';
      buttons.forEach((button) => button.setAttribute('aria-pressed', 'false'));
      highlight('');
    }
  });
});
