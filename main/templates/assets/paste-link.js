(() => {
    const bodyElem = document.querySelector('textarea[name="body"]')

    function formatOnPaste(e) {
        const {selectionStart: start, selectionEnd: end} = bodyElem;

        // nothing is selected, paste functions normally
        if (start === end) {
            return;
        }

        const clip = (e.clipboardData || window.clipboardData).getData('text')
        const url = clip.trim();

        const selectedText = bodyElem.value.slice(start, end) || url;
        const replacement = `[${selectedText}](${url})`;

        e.preventDefault();

        if (document.queryCommandSupported && document.queryCommandSupported('insertText')) {
            bodyElem.focus();
            // Ensure selection is still active before we insert
            const {selectionStart, selectionEnd} = bodyElem;
            if (selectionStart !== null && selectionEnd !== null) {
                document.execCommand('insertText', false, replacement);
                return;
            }
        }

        if (typeof bodyElem.setRangeText === 'function') {
            const start = bodyElem.selectionStart;
            const end = bodyElem.selectionEnd;
            bodyElem.setRangeText(replacement, start, end, 'end'); // place caret at end
            // Fire an input event so any listeners (e.g., frameworks) are notified
            bodyElem.dispatchEvent(new InputEvent('input', {
                bubbles: true,
                inputType: 'insertFromPaste',
                data: replacement
            }));
        }
    }

    bodyElem.addEventListener('paste', formatOnPaste)
})()