async function saveDraft() {
    const titleEl = document.getElementById('id_title')
    const bodyEl = document.getElementById('id_body');
    const slugEl = document.getElementById('id_slug');
    const publishEl = document.getElementById('id_published_at');

    if (publishEl.value) {
        return
    }

    const formData = new FormData();
    formData.append('title', titleEl.value);
    formData.append('body', bodyEl.value);
    formData.append('slug', slugEl.value);
    formData.append('published_at', "");

    const {status} = await fetch('', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })

    if (status === 200 || status === 302) {
        console.log('successfully saved draft')
    }
}

function initSaveDraft() {
    console.log('started auto save for drafts...');
    setInterval(saveDraft, 10 * 1000);
}

initSaveDraft();
