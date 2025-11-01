let CHARACTER_COUNTER_INPUT_SELECTOR_ATTR =
  'data-character-counter-input-selector';

let CHARACTER_COUNTER_INDICATOR_SELECTOR_ATTR =
  'data-character-counter-indicator-selector';

let CharacterCounter = function (inputElement, indicatorElement) {
  this.inputElement = inputElement;
  this.indicatorElement = indicatorElement;
};

CharacterCounter.prototype = {
  handleInputEvent: function (ev) {
    this.updateDOM();
  },

  updateDOM: function () {
    if (typeof this.inputElement.maxLength !== 'number') {
      return;
    }

    if (typeof this.inputElement.value !== 'string') {
      return;
    }

    const remaining =
      this.inputElement.maxLength - this.inputElement.value.length;
    this.indicatorElement.innerText = String(remaining);
  },
};

function setupCharacterCounter(counterElement) {
  let inputSelector = counterElement.getAttribute(
    CHARACTER_COUNTER_INPUT_SELECTOR_ATTR,
  );
  if (typeof inputSelector !== 'string') {
    return;
  }

  let indicatorSelector = counterElement.getAttribute(
    CHARACTER_COUNTER_INDICATOR_SELECTOR_ATTR,
  );
  if (typeof indicatorSelector !== 'string') {
    return;
  }

  let inputElement = document.querySelector(inputSelector);
  if (inputElement == null) {
    return;
  }

  let indicatorElement = document.querySelector(indicatorSelector);
  if (indicatorElement == null) {
    return;
  }

  let characterCounter = new CharacterCounter(inputElement, indicatorElement);

  inputElement.addEventListener(
    'input',
    characterCounter.handleInputEvent.bind(characterCounter),
  );
}

function setupCharacterCounters() {
  let counterElements = document.getElementsByClassName('character-counter');
  for (let i = 0; i < counterElements.length; i++) {
    setupCharacterCounter(counterElements[i]);
  }
}

document.addEventListener('DOMContentLoaded', function () {
  setupCharacterCounters();
});
