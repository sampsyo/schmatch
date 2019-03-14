/**
 * Given a <select> element, set its accompanying "custom" text input field to
 * be visible iff the current selection is the "custom" option.
 */
function setCustomVisibility(select) {
  let selName = select.name;
  let slotId = parseInt(selName.split("_")[1]);
  let isCustom = select.value == "custom";

  // Find the corresponding text entry field.
  let fieldId = 'description_' + slotId;
  let customField = document.getElementsByName(fieldId)[0];

  // Set visibility.
  customField.hidden = !isCustom;
}

document.addEventListener("DOMContentLoaded", function () {
  let selects = document.querySelectorAll('select');


  for (let i = 0; i < selects.length; ++i) {
    let select = selects[i];

    // Initial visibility.
    setCustomVisibility(select);

    // Update visibility on change.
    select.addEventListener("change", function (e) {
      setCustomVisibility(e.target);
    });
  }
});
