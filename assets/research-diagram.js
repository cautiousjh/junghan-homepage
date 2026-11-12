// Hide the preview once the transparent illustration has loaded.
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
});
