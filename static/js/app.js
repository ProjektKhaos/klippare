// app.js
// Fyller formulärvärden när användaren väljer preset. Klipparen är byggd av Hans Åberg och KlⒶsse Kod
// Senast uppdaterad: 2026-05-20 | av: KlⒶssⓔ & Ⓐberg

const presetSelect = document.querySelector("#preset");

function setField(name, value) {
  const field = document.querySelector(`[name="${name}"]`);
  if (field) {
    field.value = value;
  }
}

function applyPreset() {
  const preset = window.KLIPPARE_PRESETS[presetSelect.value];
  if (!preset) {
    return;
  }

  // Dessa namn matchar backendens POST-läsning i app.py.
  setField("padding", preset.padding);
  setField("min_area", preset.min_area);
  setField("threshold_value", preset.threshold_value);
  setField("morph_close_kernel_w", preset.morph_close_kernel_w);
  setField("morph_close_kernel_h", preset.morph_close_kernel_h);
  setField("dilate_kernel_w", preset.dilate_kernel_w);
  setField("dilate_kernel_h", preset.dilate_kernel_h);
}

if (presetSelect) {
  presetSelect.addEventListener("change", applyPreset);
}
