function formatOnPaste(event) {
    const clipboardData = event.clipboardData || window.clipboardData;
    const pastedData = clipboardData.getData('text');

    const bodyElem = document.querySelector('textarea[name="body"]');

    const start = bodyElem.selectionStart;
    const end = bodyElem.selectionEnd;

    if (start !== end) {
        event.preventDefault(); // Stop the default paste

        const selectedText = bodyElem.value.substring(start, end);
        const before = bodyElem.value.substring(0, start);
        const after = bodyElem.value.substring(end);

        const markdownLink = `[${selectedText}](${pastedData})`;

        bodyElem.value = before + markdownLink + after;

        // Move cursor after inserted markdown
        const newCursorPosition = before.length + markdownLink.length;
        bodyElem.setSelectionRange(newCursorPosition, newCursorPosition);
    }
}

bodyElem.addEventListener('paste', formatOnPaste);